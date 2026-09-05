# Verification record

Local verification on **2026-09-05**, Linux x86_64, Python 3.13.5.

| Check | Observed result |
| --- | --- |
| Unit/integration suite | 12 tests, 0 skipped, exit 0 |
| Build | Wheel built offline without runtime dependencies |
| Installation | Wheel installed into a fresh virtual environment |
| Installed CLI | Version command passed from outside the source directory |
| End-to-end smoke | Passed, including intentionally failing fixtures |
| Listing metadata | Dry-run validation passed; no account settings changed |

Smoke tests launch `python -I -m ...`, so they verify the installed wheel rather
than accidentally importing the current source directory. Expected demo failures
are asserted explicitly; they are not hidden with unconditional success exits.

## What this does not establish

The declared local Python consumers were tested. The npm guide is an integration recipe, not a verified adapter.

GitHub CI is configured for Python 3.11/3.13 on Linux/macOS. This record describes
the local run only; consult the live Actions result for remote CI status. Tests
are evidence for exercised behavior, not a guarantee of correctness, security,
virality or compatibility with every project.

## Repeat the checks

```sh
python -m pip install .
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/configure_repository.py --dry-run
```
