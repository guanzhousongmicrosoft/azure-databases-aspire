---
description: Checks for newer Aspire releases, updates repo version pins, runs validation, and opens a reviewable PR when the upgrade is clean.
on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 * * MON"
permissions:
  contents: read
  issues: read
  pull-requests: read
engine: copilot
network:
  allowed:
    - defaults
    - github
    - dotnet
    - containers
tools:
  github:
    toolsets: [repos, issues, pull_requests]
  edit:
  bash:
    - "bash"
    - "cat"
    - "dotnet:*"
    - "find"
    - "git:*"
    - "grep"
    - "head"
    - "ls"
    - "pwd"
    - "python3"
    - "tail"
safe-outputs:
  create-pull-request:
    title-prefix: "[aspire-update] "
    labels: [dependencies, aspire, automated]
    draft: true
    max: 1
    base-branch: main
    preserve-branch-name: true
    protected-files: allowed
    allowed-files:
      - Directory.Packages.props
      - global.json
      - azure-databases-aspire.sln
      - playground/**
      - ValidationApp/**
      - src/Aspire.Hosting.DocumentDB/**
      - tests/**
  create-issue:
    title-prefix: "[aspire-update] "
    labels: [dependencies, aspire, automated]
    close-older-issues: true
    max: 1
timeout-minutes: 45
strict: true
runtimes:
  dotnet:
    version: "9.0.100"
  python:
    version: "3.12"
tracker-id: aspire-weekly-update
---

# Weekly Aspire update agent

You maintain the Aspire version and tightly related direct dependencies in this repository.

## Goal

Check whether a newer stable Aspire version (minor or major) is available.

- If no newer stable Aspire version exists, call `noop`.
- If a newer version exists:
  1. update the repo version pins and any tightly related direct dependencies that need to move with the upgrade
  2. make only the minimum source or test compatibility edits required for the repo to build and test cleanly
  3. run validation
  4. open one draft PR if validation passes
  5. otherwise open one issue with actionable failure diagnostics

Ignore preview, RC, beta, or nightly versions.

## Files and helpers

- `Directory.Packages.props` contains the central package version pins
- `global.json` contains the AppHost SDK version via `msbuild-sdks.Aspire.AppHost.Sdk`
- `eng/update-aspire-dependencies.py` updates the known version surfaces deterministically
- `eng/validate-aspire-update.sh` runs the build and test validation path

## Required workflow

1. Read the current Aspire version from `Directory.Packages.props`.
2. Check for newer stable Aspire packages with `dotnet list azure-databases-aspire.sln package --outdated` and use the current direct package graph in this repository as the source of truth for what needs updating.
3. Search for open pull requests whose title starts with `[aspire-update] `. If one already targets the same Aspire version, call `noop` instead of opening a duplicate PR.
4. If the repository is already on the latest stable Aspire version, call `noop`.
5. Update the Aspire version and any tightly related direct dependency versions with `python3 eng/update-aspire-dependencies.py ...`.
6. Review the changed files and make any minimal source or test compatibility edits needed for the new version.
7. Run `bash eng/validate-aspire-update.sh`.
8. If validation passes, create one draft PR that includes:
   - the target Aspire version
   - the related dependency updates you made
   - the exact validation commands you ran
   - the key test results
9. If validation fails, create one issue that includes:
   - the target Aspire version
   - the exact failing command or commands
   - the most important error output
   - the files most likely to need manual follow-up

## Update rules

- Update the Aspire family together:
  - `Aspire.Hosting`
  - `Aspire.Hosting.Testing`
  - `Aspire.MongoDB.Driver`
  - `Aspire.AppHost.Sdk` through `global.json`
- For non-Aspire direct dependencies in `Directory.Packages.props`, update only packages that are directly referenced by this repo and shown as outdated by the .NET tooling during the same upgrade.
- Do not add or remove packages unless that is required to make the upgrade build and test successfully.
- Keep the changes narrow and specific to the current Aspire upgrade.

## Important constraints

- Never edit `.github/**`
- Never change secrets, tokens, repository settings, or CI permissions
- Never open more than one PR or one issue in a single run
- Prefer the deterministic helper and validation script over ad hoc file edits
- If you create no PR and no issue, you must call `noop`
