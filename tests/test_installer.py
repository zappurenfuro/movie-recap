"""Offline installer checks; run with python -m unittest discover -s tests."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load('movie_recap_install', 'install.py')
runtime = load('movie_recap_runtime', 'runtime_setup.py')


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='movie-recap-test-')
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / 'project with spaces'

    def invoke(self, *args):
        with patch('sys.argv', ['install.py', '--project', str(self.project), *args]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return installer.main()

    def test_dry_run_does_not_download_or_write(self):
        with patch.object(installer, 'setup_runtime') as setup:
            self.assertEqual(self.invoke('--dry-run'), 0)
            setup.assert_not_called()
        self.assertFalse(self.project.exists())

    def test_skill_only_idempotency_and_backed_up_update(self):
        with patch.object(installer, 'setup_runtime') as setup:
            self.assertEqual(self.invoke('--skill-only'), 0)
            self.assertEqual(self.invoke('--skill-only'), 0)
            setup.assert_not_called()
        a = self.project / '.agents/skills/movie-recap/SKILL.md'
        b = self.project / '.claude/skills/movie-recap/SKILL.md'
        self.assertEqual(a.read_bytes(), b.read_bytes())
        a.write_text('custom edit', encoding='utf8')
        with self.assertRaises(SystemExit):
            self.invoke('--skill-only')
        self.assertEqual(a.read_text(), 'custom edit')
        self.assertEqual(self.invoke('--skill-only', '--update'), 0)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(next(a.parent.glob('SKILL.md.backup-*')).read_text(), 'custom edit')

    def test_failed_runtime_does_not_install_skill(self):
        with patch.object(installer, 'setup_runtime', side_effect=RuntimeError('offline')):
            self.assertEqual(self.invoke(), 1)
        self.assertFalse(self.project.exists())

    def test_verified_runtime_is_registered_for_both_apps(self):
        value = {'status': 'ready', 'manifest_path': str(Path(self.temporary.name) / 'runtime.json')}
        with patch.object(installer, 'setup_runtime', return_value=value):
            self.assertEqual(self.invoke(), 0)
        for app in ['.agents', '.claude']:
            import json
            self.assertEqual(json.loads((self.project / app / 'skills/movie-recap/runtime.json').read_text()), value)

    def test_download_checksum_prevents_replacing_existing_file(self):
        target = Path(self.temporary.name) / 'model.onnx'
        target.write_bytes(b'existing model')
        good = b'valid model bytes'
        with patch.object(runtime.urllib.request, 'urlopen', side_effect=lambda *a, **k: io.BytesIO(b'bad')), patch.object(runtime.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                runtime.download_asset(target, len(good), hashlib.sha256(good).hexdigest())
        self.assertEqual(target.read_bytes(), b'existing model')

    def test_verified_download_is_reused(self):
        target = Path(self.temporary.name) / 'voices.bin'
        data = b'valid voice data'
        digest = hashlib.sha256(data).hexdigest()
        with patch.object(runtime.urllib.request, 'urlopen', side_effect=lambda *a, **k: io.BytesIO(data)) as network, contextlib.redirect_stdout(io.StringIO()):
            runtime.download_asset(target, len(data), digest)
            runtime.download_asset(target, len(data), digest)
            self.assertEqual(network.call_count, 1)
        self.assertEqual(target.read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
