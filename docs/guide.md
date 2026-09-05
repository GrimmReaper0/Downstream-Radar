# Downstream Radar guide

## Manifest and execution

A TOML manifest needs version = 1 and one or more [[projects]] tables. Each has a
unique name, a local path, a test argument array and optional setup argument arrays.
Consumer paths are relative to the manifest; package arguments to the calling shell.

Each phase gets independent copies of the consumer/package, temporary HOME and a
minimal environment. RADAR_PACKAGE, RADAR_WORKSPACE and RADAR_PHASE are provided.
Tokens {package}, {workspace} and {python} are substituted in command arguments.
Set --jobs 1..8 for parallel consumer runs. Commands are not implicit shell strings.

## Example npm recipe

```toml
version = 1

[[projects]]
name = "npm-consumer"
path = "consumer"
setup = [["npm", "install", "--no-audit", "--no-fund", "--ignore-scripts", "{package}"]]
test = ["npm", "test"]
```

This is an integration recipe, not a separately verified npm adapter. Installation
may contact registries; --ignore-scripts disables lifecycle hooks and may not suit
packages needing builds. Review code before enabling build steps. Never install
globally; for Python dependencies, use a temporary local target/venv and make tests
use that environment. Toolchains and dependency resolution are not automatic.

## Classification

A new regression requires a passing baseline and a completed failing candidate test.
Baseline test failures, setup errors and timeouts are separate states. Percentages
only include comparable cases, with inconclusive counts shown. This is a declared
sample, not an ecosystem census. Reports retain commands' output and input hashes.

## Trust and input limits

Copies exclude Git data, hidden configuration, credential-like files, venvs and
node_modules. Symlinks are refused. The copy limit is 50 MiB; evidence snapshots
allow 10,000 files and 2 MiB per file. Consumers requiring excluded configuration
need a reviewed setup step, not an assumption that it was silently copied.
Temporary directories do not isolate hostile tests from the host. Use a separately
managed disposable environment for third-party suites and inspect reports for secrets.
