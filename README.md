# azure-cosmos-aspire

## Agentic Aspire updates

This repository now includes a weekly `gh-aw` workflow source at `.github/workflows/weekly-aspire-update.md`.

- Pull requests that change agentic workflow source run `Validate agentic workflows`.
- Pushes to `main` that change workflow source run `Sync agentic workflows`, which compiles the markdown workflow into its generated `.lock.yml` file.
- To let `Sync agentic workflows` push generated workflow files back to the repository, add a `GH_AW_SYNC_TOKEN` secret with `contents:write` and `workflows:write` access.
- Without `GH_AW_SYNC_TOKEN`, the sync workflow still uploads the generated `.lock.yml` files as an artifact so a maintainer can download and commit them manually.
- Without `GH_AW_SYNC_TOKEN`, the sync workflow also prints the generated lockfile content to the run log between `__BEGIN_GH_AW_LOCKFILE__` and `__END_GH_AW_LOCKFILE__` markers for manual recovery.
- `eng/update-aspire-dependencies.py` provides a deterministic way to update the centralized Aspire and related dependency pins.
- `eng/validate-aspire-update.sh` runs the build and test validation path that the weekly upgrade workflow should use before it opens a PR.
