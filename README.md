# Downstream Radar

**Test your next release against real downstream consumers before users find the breakage.**

Downstream Radar runs a declared consumer test suite twice: once against a known-good baseline package and once against your release candidate. It classifies only baseline-passing consumers as comparable, so pre-existing failures do not become fake regressions.

## Install

```sh
git clone https://github.com/GrimmReaper0/Downstream-Radar.git
cd Downstream-Radar
python3 -m venv .venv && . .venv/bin/activate
python -m pip install .
downstream-radar --help
```

## Demo

```sh
downstream-radar run examples/radar.toml --trust --baseline examples/packages/v1 --candidate examples/packages/v2 --json report.json --markdown report.md
```

The included candidate intentionally breaks one consumer, so the demo exits 1 and produces evidence. Consumer setup/tests execute locally after explicit `--trust`; temporary directories are not a security sandbox. This source release tests declared local consumers rather than claiming ecosystem-wide discovery.

Python 3.11+; Linux/macOS; MIT licensed.
