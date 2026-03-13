# azure-cosmos-aspire

## Agentic Aspire updates

This repository now includes a weekly `gh-aw` workflow source at `.github/workflows/weekly-aspire-update.md`.

- The active scheduled workflow is `.github/workflows/weekly-aspire-update.lock.yml`.
- The source workflow schedule is `weekly on monday around 09:00`, and the current compiled workflow runs every Monday at `08:48 UTC`.
- Pull requests that change agentic workflow source run `Validate agentic workflows`.
- Pushes to `main` that change workflow source run `Sync agentic workflows`, which compiles the markdown workflow into its generated `.lock.yml` file.
- To let `Sync agentic workflows` push generated workflow files back to the repository, add a `GH_AW_SYNC_TOKEN` secret with `contents:write` and `workflows:write` access.
- Without `GH_AW_SYNC_TOKEN`, the sync workflow still uploads the generated `.lock.yml` files as an artifact so a maintainer can download and commit them manually.
- Without `GH_AW_SYNC_TOKEN`, the sync workflow also prints the generated lockfile content to the run log between `__BEGIN_GH_AW_LOCKFILE__` and `__END_GH_AW_LOCKFILE__` markers for manual recovery.
- Weekly no-op runs are intentionally silent: if the repository is already on the latest stable Aspire version, the workflow exits cleanly without opening a PR or issue.
- `COPILOT_GITHUB_TOKEN` is required for the weekly runtime workflow because the Copilot engine must authenticate before it can execute the update instructions.
- `eng/update-aspire-dependencies.py` provides a deterministic way to update the centralized Aspire and related dependency pins.
- `eng/validate-aspire-update.sh` runs the build and test validation path that the weekly upgrade workflow should use before it opens a PR.

### How the three workflows work together

1. `Validate agentic workflows`

   - File: `.github/workflows/validate-agentic-workflows.yml`
   - Trigger: pull requests that change `.github/workflows/*.md`, plus manual dispatch
   - Purpose: validates the markdown source workflows with `gh-aw validate --strict`
   - Use this to catch frontmatter or `gh-aw` schema problems before merging

2. `Sync agentic workflows`

   - File: `.github/workflows/sync-agentic-workflows.yml`
   - Trigger: pushes to `main` that change `.github/workflows/*.md`, plus manual dispatch
   - Purpose: compiles markdown source workflows into committed `.lock.yml` workflows with `gh-aw compile --validate --strict`
   - If `GH_AW_SYNC_TOKEN` is configured, it commits and pushes regenerated lock files automatically
   - If `GH_AW_SYNC_TOKEN` is not configured, it still succeeds but only uploads or prints the generated lock file for manual recovery

3. `Weekly Aspire update agent`

   - Files:
     - source: `.github/workflows/weekly-aspire-update.md`
     - runnable workflow: `.github/workflows/weekly-aspire-update.lock.yml`
   - Trigger: weekly schedule plus manual dispatch
   - Purpose: checks for a newer stable Aspire version, updates known version surfaces, runs validation, and opens a draft PR on success
   - If no newer stable Aspire version exists, it exits cleanly without opening a PR or issue

### Exact maintainer steps

#### Normal weekly operation

1. Do nothing unless the scheduled run produces output.
2. Each Monday, GitHub runs `Weekly Aspire update agent`.
3. If a newer stable Aspire version is found and validation passes, review the draft PR it creates.
4. If a newer version is found but validation fails, review the failure issue it creates.
5. If no newer version exists, expect a successful run with no PR and no issue.

#### When you want to change the agent behavior

1. Edit only the markdown source workflow: `.github/workflows/weekly-aspire-update.md`.
2. Do not hand-edit `.github/workflows/weekly-aspire-update.lock.yml` unless you are recovering a generated file from sync output.
3. Open a pull request with the markdown workflow change.
4. Wait for `Validate agentic workflows` to pass.
5. Merge the pull request to `main`.
6. Wait for `Sync agentic workflows` to compile the updated `.lock.yml`.
7. If `GH_AW_SYNC_TOKEN` is configured, confirm the sync workflow pushed the regenerated lock file automatically.
8. If `GH_AW_SYNC_TOKEN` is not configured:
   - download the `generated-agentic-workflows` artifact from the sync run, or
   - copy the lock file from the sync log between `__BEGIN_GH_AW_LOCKFILE__` and `__END_GH_AW_LOCKFILE__`
   - commit the regenerated `.github/workflows/*.lock.yml` file to `main`

#### When you want to test the weekly workflow immediately

1. Go to the GitHub Actions page for `Weekly Aspire update agent`.
2. Click `Run workflow`.
3. Choose the `main` branch.
4. Inspect the run result:
   - no output means the repository is already on the latest stable Aspire version
   - a draft PR means the update validated successfully
   - an issue means a newer version was found but the upgrade needs manual follow-up

#### Required secrets

- `COPILOT_GITHUB_TOKEN`: required for `Weekly Aspire update agent`
- `GH_AW_SYNC_TOKEN`: optional, but required for automatic lockfile pushback from `Sync agentic workflows`
