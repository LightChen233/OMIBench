# Contributing to OMI-Bench

Thank you for your interest in improving OMI-Bench. Contributions via issues,
pull requests, reproducibility reports, and source-attribution notes are welcome.

## Good First Contributions

- Fix typos or unclear documentation.
- Improve dataset source attribution in `dataset/SOURCES.md`.
- Report malformed records, missing images, or answer-key concerns.
- Improve `omi_bench.py` validation, sampling, or manifest utilities.
- Share reproducibility notes for benchmark evaluation.

## Development Setup

```bash
git clone https://github.com/LightChen233/omi-bench-code.git
cd omi-bench-code
python -m pip install -r requirements.txt
```

## Validation Before Pull Requests

Run the public CLI validator before submitting changes:

```bash
python omi_bench.py validate
```

You can also inspect summary statistics and sample records:

```bash
python omi_bench.py info
python omi_bench.py sample -n 3 --subject biology
```

## Data Contribution Guidelines

- Include source information for every new record and image.
- Do not submit copyrighted scans or cropped figures unless redistribution is permitted.
- Preserve the `[IMAGE0]`, `[IMAGE1]`, ... placeholder convention.
- Keep `image_list` ordered exactly as referenced by placeholders.
- Do not include full reasoning chains in prompts used for clean model evaluation.

## Repository Scope

The public repository is intentionally minimal. Please avoid adding raw data,
intermediate data-processing artifacts, editor apps, local experiment outputs,
or private model-testing scripts unless they are polished as a documented public
entry point.

## API Keys and Secrets

Never commit real API keys, tokens, passwords, cookies, or private endpoints.
Use environment variables or local-only configuration files for credentials.

## Pull Request Checklist

- [ ] The change is focused and documented.
- [ ] `python omi_bench.py validate` passes.
- [ ] New or changed records include source and license notes where relevant.
- [ ] No private credentials or large generated artifacts are included.
- [ ] The README or related docs are updated when user-facing behavior changes.
