#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$repo_root"

dotnet build src/Aspire.Hosting.DocumentDB/Aspire.Hosting.DocumentDB.csproj
dotnet test tests/Aspire.Hosting.DocumentDB.Tests/Aspire.Hosting.DocumentDB.Tests.csproj --logger "console;verbosity=minimal"
