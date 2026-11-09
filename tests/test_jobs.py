"""Exercise real child scheduling, failure and resource boundaries."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('jobs', Path(__file__).resolve().parents[1] / 'scripts/run_jobs.py')
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)


class JobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='recap jobs ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def job(self, name, **kwargs):
        return {'id': name, 'argv': [sys.executable, '-c', 'import time; time.sleep(.25)'], **kwargs}

    def run_jobs(self, items):
        return jobs.run({'cwd': str(self.root), 'jobs': items}, self.root / 'logs')

    def test_independent_overlap_and_dependency_waits(self):
        result = self.run_jobs([self.job('a'), self.job('b'), self.job('c', needs=['a', 'b'])])
        a, b, c = [result['jobs'][x] for x in 'abc']
        self.assertEqual(result['status'], 'passed')
        self.assertLess(max(a['start_seconds'], b['start_seconds']), min(a['end_seconds'], b['end_seconds']))
        self.assertGreaterEqual(c['start_seconds'], max(a['end_seconds'], b['end_seconds']))

    def test_exclusive_resource_serializes(self):
        result = self.run_jobs([self.job('a', resources=['gpu']), self.job('b', resources=['gpu'])])
        self.assertGreaterEqual(result['jobs']['b']['start_seconds'], result['jobs']['a']['end_seconds'])

    def test_failure_blocks_dependent_and_captures_log(self):
        a = self.job('a')
        a['argv'] = [sys.executable, '-c', 'print("failure evidence"); raise SystemExit(7)']
        result = self.run_jobs([a, self.job('b', needs=['a'])])
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['jobs']['a']['returncode'], 7)
        self.assertEqual(result['jobs']['b']['status'], 'skipped')
        self.assertIn('failure evidence', (self.root / 'logs/a.log').read_text())

    def test_timeout_and_missing_executable_are_reported(self):
        a = self.job('a', timeout_seconds=.01)
        result = self.run_jobs([a, {'id': 'b', 'argv': [str(self.root / 'missing-executable')]}])
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['jobs']['a']['status'], 'failed')
        self.assertEqual(result['jobs']['b']['status'], 'failed')

    def test_invalid_graph_never_creates_output(self):
        for items in ([self.job('a', needs=['missing'])], [self.job('a', needs=['b']), self.job('b', needs=['a'])], [self.job('../escape')], [self.job('a'), self.job('a')]):
            with self.assertRaises(ValueError):
                self.run_jobs(items)
            self.assertFalse((self.root / 'logs').exists())

    def test_existing_output_not_overwritten(self):
        self.run_jobs([self.job('a')])
        with self.assertRaises(FileExistsError):
            self.run_jobs([self.job('a')])


if __name__ == '__main__':
    unittest.main()
