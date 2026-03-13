# azure-cosmos-aspire

## Agentic Aspire updates

This repository now includes a weekly `gh-aw` workflow source at `.github/workflows/weekly-aspire-update.md`.

- Pull requests that change agentic workflow source run `Validate agentic workflows`.
- Pushes to `main` that change workflow source run `Sync agentic workflows`, which compiles the markdown workflow into its generated `.lock.yml` file.
- `eng/update-aspire-dependencies.py` provides a deterministic way to update the centralized Aspire and related dependency pins.
- `eng/validate-aspire-update.sh` runs the build and test validation path that the weekly upgrade workflow should use before it opens a PR.
