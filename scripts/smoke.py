"""Exercise installed CLI behavior, including deliberately failing examples."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def invoke(module, args, expected=0):
    result = subprocess.run([sys.executable, '-I', '-m', module, *map(str, args)], cwd=ROOT,
                            text=True, capture_output=True, timeout=60)
    if result.returncode != expected:
        raise SystemExit(f'Unexpected exit {result.returncode}, expected {expected}:\n{result.stdout}\n{result.stderr}')
    print(result.stdout.strip())
    return result

with tempfile.TemporaryDirectory() as d:
    bad, good, summary = Path(d)/'bad.json', Path(d)/'good.json', Path(d)/'summary.md'
    invoke('downstream_radar', ['run','examples/radar.toml','--trust','--baseline','examples/packages/v1','--candidate','examples/packages/v2','--json',bad,'--markdown',summary], expected=1)
    invoke('downstream_radar', ['run','examples/radar.toml','--trust','--baseline','examples/packages/v1','--candidate','examples/packages/v1','--json',good])
    assert json.loads(bad.read_text())['regressions'] == 1
    assert json.loads(good.read_text())['compatible'] == 2
    assert 'legacy-string-consumer' in summary.read_text()
print('Downstream Radar installed-package smoke checks passed.')
