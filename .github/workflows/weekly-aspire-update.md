---
on:
  schedule: weekly
  workflow_dispatch:

description: "Weekly check for new Aspire NuGet package versions and automated dependency update PR"

permissions:
  contents: read
  issues: read
  pull-requests: read

runtimes:
  dotnet:
    version: "9.0"

tools:
  edit:
  bash:
    - ":*"
  web-fetch:
  github:

network:
  allowed:
    - defaults
    - dotnet
    - github

safe-outputs:
  create-pull-request:
    title-prefix: "[aspire-update] "
    labels: [dependencies, automated]
    draft: false
    protected-files: allowed
---

## Weekly Aspire Dependency Update

You are a dependency-update agent for a .NET Aspire hosting extension project.
Your job is to check whether newer versions of key NuGet packages are available
and, if so, update the project to use them and open a pull request.

### Context

This repository (`azure-databases-aspire`) is a .NET Aspire hosting extension
for DocumentDB. It depends on the `Aspire.Hosting` NuGet meta-package
and several related Aspire packages. All package versions are centrally managed
in `Directory.Packages.props` using Central Package Management (CPM).

The `Aspire.AppHost.Sdk` version is pinned in individual project files (grep
for `Aspire.AppHost.Sdk` across `.csproj` files).

### Step 1 — Check for outdated packages

Run the .NET SDK's built-in outdated package check:

```bash
dotnet restore azure-databases-aspire.sln
dotnet list azure-databases-aspire.sln package --outdated --format json
```

This produces a JSON report listing every package with a newer stable version
available. Parse the output to identify which packages need updating and what
the latest versions are.

Also grep all `.csproj` files for `Aspire.AppHost.Sdk` and note its current
version. Then check NuGet for a newer stable version of that SDK:

```bash
curl -s "https://api.nuget.org/v3-flatcontainer/aspire.apphost.sdk/index.json"
```

Pick the highest version without a hyphen (`-`).

### Step 2 — Decide whether to update

- If `dotnet list package --outdated` reports no outdated packages AND
  `Aspire.AppHost.Sdk` is already at the latest version, report
  "No updates available" and stop (use noop safe output).
- If any package has a newer stable version, proceed to Step 3.

### Step 3 — Apply version updates

1. Edit `Directory.Packages.props` — update each `<PackageVersion>` `Version`
   attribute to the latest stable version found.
2. If `Aspire.AppHost.Sdk` has a newer version, update its version in every
   `.csproj` file that references it (e.g.,
   `<Project Sdk="Aspire.AppHost.Sdk/X.Y.Z">`).

**Important:** Keep all Aspire packages (`Aspire.Hosting`,
`Aspire.Hosting.Testing`, `Aspire.MongoDB.Driver`) on the **same version**
so they stay in sync.

### Step 4 — Validate the update

Run the solution build AND tests to make sure the update compiles and doesn't
break existing behavior:

```bash
dotnet restore azure-databases-aspire.sln
dotnet build azure-databases-aspire.sln --no-restore -c Release
dotnet test azure-databases-aspire.sln --no-build -c Release
```

The unit tests validate connection string formats, Aspire manifest output,
resource annotations, and public API surface — exactly the things most likely
to break during an Aspire version upgrade. Integration tests require Docker
and will skip themselves automatically if Docker is unavailable.

If the build or tests fail, read the error output, attempt to fix the issue
(e.g., API changes, renamed types, connection string format changes), and
re-run. If a fix isn't straightforward, still open the PR but clearly note
the failure details in the PR description so a human can investigate.

### Step 5 — Open a pull request

Create a pull request with:
- **Title:** `[aspire-update] Upgrade Aspire packages to <new-version>`
  (include other notable upgrades in the title if any).
- **Body:** A clear summary listing every package updated, its old version,
  and its new version in a markdown table. Include the build result status.
- **Branch name:** `chore/aspire-update-<new-version>`

If no packages need updating, do NOT create a PR. Just log a noop message.
