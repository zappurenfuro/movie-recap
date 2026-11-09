#!/usr/bin/env python3
"""Run independent media commands with dependencies and measured timings.

No shell expansion, automatic retries, cache reuse, or model downloads.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time


def validate(plan):
    jobs = plan['jobs']
    if not isinstance(jobs, list) or not jobs:
        raise ValueError('jobs must be a nonempty list')
    names = set()
    for job in jobs:
        name = job['id']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in names:
            raise ValueError('Job IDs must be unique safe filenames')
        names.add(name)
        argv = job['argv']
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            raise ValueError('argv must be a nonempty list of strings')
        for key in ('needs', 'resources'):
            values = job.get(key, [])
            if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
                raise ValueError(f'{key} must be a list of strings')
        timeout = job.get('timeout_seconds', 3600)
        if not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
            raise ValueError('timeout_seconds must be between 0 and 86400')
    done = set()
    while len(done) < len(jobs):
        ready = {j['id'] for j in jobs if set(j.get('needs', [])) <= done} - done
        if not ready:
            raise ValueError('Unknown dependency or dependency cycle')
        done.update(ready)
    return jobs


def run(plan, output, workers=2):
    jobs = validate(plan)
    if not 1 <= workers <= 16:
        raise ValueError('workers must be between 1 and 16')
    cwd = Path(plan['cwd']).expanduser().resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError('cwd must be a directory')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'jobs': {}}

    def execute(job):
        begin = time.perf_counter()
        result = {'start_seconds': begin - started}
        with (output / (job['id'] + '.log')).open('wb') as log:
            try:
                proc = subprocess.run(job['argv'], cwd=cwd, stdout=log,
                                      stderr=subprocess.STDOUT, shell=False,
                                      timeout=job.get('timeout_seconds', 3600))
                result.update(returncode=proc.returncode,
                              status='passed' if proc.returncode == 0 else 'failed')
            except (OSError, subprocess.TimeoutExpired) as exc:
                result.update(status='failed', error=str(exc))
        result['elapsed_seconds'] = time.perf_counter() - begin
        result['end_seconds'] = time.perf_counter() - started
        return result

    pending = list(jobs)
    running = {}
    completed = set()
    busy = set()
    failed = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or running:
            if not failed:
                for job in list(pending):
                    resources = set(job.get('resources', []))
                    if len(running) >= workers:
                        break
                    if set(job.get('needs', [])) <= completed and not resources & busy:
                        running[pool.submit(execute, job)] = job
                        busy.update(resources)
                        pending.remove(job)
            if not running:
                break
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in finished:
                job = running.pop(future)
                busy.difference_update(job.get('resources', []))
                result = future.result()
                report['jobs'][job['id']] = result
                if result['status'] == 'passed':
                    completed.add(job['id'])
                else:
                    failed = True
            report['elapsed_seconds'] = time.perf_counter() - started
            temp = output / 'timings.tmp'
            temp.write_text(json.dumps(report, indent=2), encoding='utf8')
            temp.replace(output / 'timings.json')
    for job in pending:
        report['jobs'][job['id']] = {'status': 'skipped', 'reason': 'A job failed'}
    report['elapsed_seconds'] = time.perf_counter() - started
    report['status'] = 'failed' if failed else 'passed'
    (output / 'timings.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New logs/timings directory')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    plan = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    result = run(plan, args.output, args.workers)
    print(f"{result['status']}: {result['elapsed_seconds']:.2f}s; {args.output / 'timings.json'}")
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
