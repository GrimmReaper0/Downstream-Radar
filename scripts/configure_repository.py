"""Apply prepared GitHub About text and topics using your own gh login."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--dry-run', action='store_true')
a = p.parse_args()
details = json.loads((Path(__file__).resolve().parents[1] / 'repository-details.json').read_text())
repo = details['repository']
update = {'description': details['description'], 'homepage': details['homepage']}
if a.dry_run:
    print(json.dumps({'repository': repo, **update, 'topics': details['topics']}, indent=2))
    raise SystemExit(0)
if not shutil.which('gh'):
    raise SystemExit('GitHub CLI (gh) is required. Install it and run gh auth login first.')

def api(method, endpoint, data=None):
    args = ['gh', 'api', '--method', method, endpoint]
    if data is not None:
        args += ['--input', '-']
    r = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                       text=True, capture_output=True, check=True)
    return json.loads(r.stdout) if r.stdout.strip() else {}

try:
    existing = api('GET', f'repos/{repo}/topics').get('names', [])
    topics = sorted(set(existing + details['topics']))
    if len(topics) > 20:
        raise SystemExit('Combined topics exceed 20. Review existing topics before applying.')
    api('PATCH', f'repos/{repo}', update)
    api('PUT', f'repos/{repo}/topics', {'names': topics})
    print(f'Updated description, homepage and topics for {repo}.')
except subprocess.CalledProcessError as exc:
    raise SystemExit('GitHub rejected the metadata update: ' + exc.stderr.strip())
