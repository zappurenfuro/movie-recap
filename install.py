#!/usr/bin/env python3
"""Install the skill, an isolated media runtime, and local voice/ASR models."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def setup_runtime(folder, repository):
    if not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise RuntimeError('Full setup requires Python 3.11, 3.12, or 3.13 (64-bit). Use --skill-only for instructions without the runtime.')
    if sys.maxsize <= 2**32:
        raise RuntimeError('The media runtime requires 64-bit Python.')
    requirements = repository / 'requirements-runtime.txt'
    setup = repository / 'runtime_setup.py'
    if not requirements.is_file() or not setup.is_file():
        raise RuntimeError('Runtime setup files are missing. Download the complete repository, not only install.py.')
    folder.mkdir(parents=True, exist_ok=True)
    env_dir = folder / 'venv'
    python = env_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        print('Creating isolated Python environment:', env_dir, flush=True)
        venv.EnvBuilder(with_pip=True).create(env_dir)
    env = os.environ.copy()
    env['PYTHONNOUSERSITE'] = '1'
    env.pop('PYTHONPATH', None)
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    manifest_path = folder / 'runtime.json'
    previous = {}
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding='utf8'))
        except (ValueError, OSError):
            pass
    manifest_path.write_text(json.dumps({'status': 'installing', 'manifest_path': str(manifest_path)}, indent=2), encoding='utf8')
    if previous.get('requirements_sha256') != digest:
        print('Installing media and speech packages (first setup downloads dependencies).', flush=True)
        subprocess.run([str(python), '-I', '-m', 'pip', '--isolated', '--disable-pip-version-check', 'install', '-r', str(requirements)], env=env, check=True)
    subprocess.run([str(python), '-I', '-m', 'pip', 'check'], env=env, check=True)
    subprocess.run([str(python), '-I', str(setup), '--runtime-dir', str(folder), '--requirements-sha256', digest], env=env, check=True)
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    if manifest.get('status') != 'ready':
        raise RuntimeError('Runtime did not pass its checks; skill installation was not completed.')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('claude', 'codex', 'both'), default='both')
    parser.add_argument('--project', type=Path, help='Install in this project instead of your home folder')
    parser.add_argument('--update', action='store_true', help='Back up and replace a different installed SKILL.md')
    parser.add_argument('--dry-run', action='store_true', help='Show destinations without writing anything')
    parser.add_argument('--skill-only', action='store_true', help='Install instructions only, without downloading dependencies or models')
    parser.add_argument('--runtime-dir', type=Path, default=Path.home() / '.movie-recap' / 'runtime-v1', help='Shared media runtime directory')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / 'SKILL.md'
    if not source.is_file():
        parser.error('SKILL.md is missing beside install.py. Download or clone the complete repository.')
    payload = source.read_bytes()
    root = (args.project if args.project else Path.home()).expanduser().resolve()
    targets = ('claude', 'codex') if args.target == 'both' else (args.target,)
    destinations = [root / ('.claude' if target == 'claude' else '.agents') / 'skills' / 'movie-recap' / 'SKILL.md' for target in targets]
    # Check every destination before making changes to any target.
    for dest in destinations:
        if dest.exists() and not dest.is_file():
            parser.error(f'Destination is not a file: {dest}')
        if dest.is_file() and dest.read_bytes() != payload and not args.update:
            parser.error(f'Existing skill differs: {dest}. Use --update to back it up and replace it.')
    runtime = None
    if not args.skill_only:
        runtime_dir = args.runtime_dir.expanduser().resolve()
        if args.dry_run:
            print(f'Would install media dependencies and download models into: {runtime_dir}')
        else:
            try:
                runtime = setup_runtime(runtime_dir, source.parent)
            except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
                print(f'Setup failed: {exc}\nFix the reported error and rerun the same command. Completed downloads are retained; this run has not changed installed skills.', file=sys.stderr)
                return 1
    for dest in destinations:
        if runtime is not None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            (dest.parent / 'runtime.json').write_text(json.dumps(runtime, indent=2), encoding='utf8')
        if dest.is_file() and dest.read_bytes() == payload:
            print(f'Already current: {dest}')
            continue
        if args.dry_run:
            print(f'Would install: {dest}')
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file():
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = dest.with_name(f'SKILL.md.backup-{stamp}')
            shutil.copy2(dest, backup)
            print(f'Backup: {backup}')
        dest.write_bytes(payload)
        print(f'Installed: {dest}')
    print('Claude Code: /movie-recap Lucky | Codex: $movie-recap Lucky')
    if runtime:
        print('Media runtime verified: FFmpeg, Kokoro am_michael, Whisper, and a narrated test MP4.')
    elif args.skill_only:
        print('Skill-only installation: rendering tools and voice models were not installed or verified.')
    print('Reopen your session if the skill does not appear.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
