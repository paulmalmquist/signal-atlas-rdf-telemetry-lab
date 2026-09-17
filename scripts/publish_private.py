"""Publish this synthetic-only project to a NEW private GitHub repository.
Requires a locally authenticated GitHub CLI. No credentials are stored here.
"""
from pathlib import Path
import argparse, json, shutil, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]

def command(args, *, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner', default='paulmalmquist')
    p.add_argument('--name', default='signal-atlas-rdf-telemetry-lab')
    args = p.parse_args()
    import re
    if not re.fullmatch(r'[A-Za-z0-9-]+', args.owner) or not re.fullmatch(r'[A-Za-z0-9_.-]+', args.name):
        p.error('Owner or repository name contains unsupported characters.')
    for tool in ('git', 'gh'):
        if not shutil.which(tool):
            raise RuntimeError(f'{tool} is required. Install it locally; no publication was attempted.')
    command(['gh', 'auth', 'status'])
    slug = f'{args.owner}/{args.name}'
    existing = command(['gh', 'repo', 'view', slug, '--json', 'nameWithOwner,visibility'], check=False)
    if existing.returncode == 0:
        raise RuntimeError(f'{slug} already exists. Refusing to reuse it. Choose a new --name.')
    # Only an explicit not-found response allows creation. Auth/network errors do not.
    if not any(s in existing.stderr.lower() for s in ('not found', 'could not resolve to a repository', 'http 404')):
        raise RuntimeError('Could not confirm repository absence. Check GitHub access; nothing was published.\n' + existing.stderr)
    if not (ROOT / '.git').exists():
        command(['git', 'init', '-b', 'main'])
    remote = command(['git', 'remote', 'get-url', 'origin'], check=False)
    if remote.returncode == 0:
        raise RuntimeError('An origin already exists. Verify/remove it manually before publication; it was not changed.')
    # Only the explicitly delivered synthetic snapshot may be published here.
    # This is a boundary reminder, not a substitute for a secret/data-classification scanner.
    if not (ROOT / 'data' / 'raw' / 'manifest.json').exists():
        raise RuntimeError('Expected synthetic manifest is missing. Refusing publication.')
    pending = command(['git', 'status', '--porcelain']).stdout
    if pending:
        print('Review these files before publishing:\n' + pending)
        if input('Confirm ALL files are synthetic and contain no company data or secrets [type SYNTHETIC]: ').strip() != 'SYNTHETIC':
            raise RuntimeError('Publication cancelled before any GitHub write.')
        command(['git', 'add', '.'])
        command(['git', '-c', 'user.name=Signal Atlas Lab', '-c', 'user.email=lab@example.org', 'commit', '-m', 'Add synthetic RDF telemetry teaching lab'])
    elif not command(['git', 'rev-parse', '--verify', 'HEAD'], check=False).returncode == 0:
        raise RuntimeError('No committed files to publish.')
    print('Creating a NEW PRIVATE repository: ' + slug)
    command(['gh', 'repo', 'create', slug, '--private', '--source', str(ROOT), '--remote', 'origin', '--push',
             '--description', 'Synthetic RDF telemetry and SPARQL teaching application'])
    data = json.loads(command(['gh', 'repo', 'view', slug, '--json', 'nameWithOwner,visibility,url']).stdout)
    if data.get('visibility') != 'PRIVATE':
        raise RuntimeError('Publication returned unexpected visibility. Check GitHub immediately; no further action taken.')
    print('Verified PRIVATE: ' + data['url'])
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr or exc.stdout, file=sys.stderr)
        raise SystemExit(1)
