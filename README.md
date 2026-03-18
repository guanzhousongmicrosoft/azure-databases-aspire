# .NET Aspire Azure Databases Integrations

This repository contains .NET Aspire hosting integrations for database services.

[.NET Aspire](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/integrations-overview) is an opinionated, cloud-ready stack for building observable, production-ready, distributed applications. [Aspire integrations](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/integrations-overview) are a curated suite of NuGet packages selected to facilitate the integration of cloud-native applications with prominent services and platforms, such as Redis and PostgreSQL. Each integration furnishes essential cloud-native functionalities through either automatic provisioning or standardized configuration patterns.

## Available Integrations

- `Aspire.Hosting.DocumentDB` - Provides extension methods and resource definitions for a .NET Aspire AppHost to configure a [DocumentDB](https://github.com/microsoft/documentdb) resource. Check [README](src/Aspire.Hosting.DocumentDB/README.md) for details.

## Dependency Updates

This repository uses two complementary systems to keep dependencies current:

### Aspire (dedicated workflow)

All Aspire versions are updated atomically by `.github/workflows/update-aspire.yml`:

- Runs weekly (Monday 9 AM UTC) and on manual `workflow_dispatch`
- Checks NuGet for the latest stable `Aspire.Hosting` version
- Updates all `Aspire.*` packages in `Directory.Packages.props` and `Aspire.AppHost.Sdk` in `global.json` `msbuild-sdks`
- Validates with `dotnet build` before creating a PR

This ensures Aspire NuGet packages and the AppHost SDK are always in sync — Dependabot cannot update MSBuild SDK versions reliably ([#8615](https://github.com/dependabot/dependabot-core/issues/8615), [#12824](https://github.com/dependabot/dependabot-core/issues/12824)).

### Everything else (Dependabot)

Dependabot handles non-Aspire dependencies via `.github/dependabot.yml`:

- **NuGet** — `Microsoft.Extensions.*`, `OpenTelemetry.*`, `MongoDB.*`, `xunit*`, `MinVer`, etc.
- **dotnet-sdk** — .NET SDK version in `global.json`
- **github-actions** — workflow action versions
