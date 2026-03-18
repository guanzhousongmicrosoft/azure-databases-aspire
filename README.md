# .NET Aspire Azure Databases Integrations

This repository contains .NET Aspire hosting integrations for database services.

[.NET Aspire](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/integrations-overview) is an opinionated, cloud-ready stack for building observable, production-ready, distributed applications. [Aspire integrations](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/integrations-overview) are a curated suite of NuGet packages selected to facilitate the integration of cloud-native applications with prominent services and platforms, such as Redis and PostgreSQL. Each integration furnishes essential cloud-native functionalities through either automatic provisioning or standardized configuration patterns.

## Available Integrations

- `Aspire.Hosting.DocumentDB` - Provides extension methods and resource definitions for a .NET Aspire AppHost to configure a [DocumentDB](https://github.com/microsoft/documentdb) resource. Check [README](src/Aspire.Hosting.DocumentDB/README.md) for details.

## Dependency Updates

This repository uses GitHub Dependabot to keep its .NET dependencies current:

- `nuget` updates scan the repository root, which covers the centrally managed package versions in `Directory.Packages.props` and the `PackageReference` items in the project files.
- `dotnet-sdk` updates keep the SDK version in `global.json` current.

One Aspire-related dependency still needs a manual follow-up when an Aspire update PR is opened: Dependabot does not currently update `Aspire.AppHost.Sdk` when it is pinned in a `Project Sdk="Aspire.AppHost.Sdk/<version>"` attribute. Before merging an Aspire package update, update the matching SDK version in:

- `playground/Playground.csproj`
- `tests/Aspire.Hosting.DocumentDB.EndToEndApp/Aspire.Hosting.DocumentDB.EndToEndApp.csproj`
