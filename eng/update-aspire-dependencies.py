#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DIRECTORY_PACKAGES_PROPS = REPO_ROOT / "Directory.Packages.props"
GLOBAL_JSON = REPO_ROOT / "global.json"

PACKAGE_PROPERTY_MAP = {
    "AspNetCore.HealthChecks.MongoDb": "AspNetCoreHealthChecksMongoDbVersion",
    "Microsoft.Extensions.Configuration.Binder": "MicrosoftExtensionsConfigurationBinderVersion",
    "Microsoft.Extensions.Diagnostics.HealthChecks": "MicrosoftExtensionsDiagnosticsHealthChecksVersion",
    "Microsoft.Extensions.Hosting": "MicrosoftExtensionsHostingVersion",
    "Microsoft.Extensions.Hosting.Abstractions": "MicrosoftExtensionsHostingAbstractionsVersion",
    "Microsoft.Extensions.Http.Resilience": "MicrosoftExtensionsHttpResilienceVersion",
    "MinVer": "MinVerVersion",
    "MongoDB.Driver": "MongoDBDriverVersion",
    "OpenTelemetry.Extensions.Hosting": "OpenTelemetryExtensionsHostingVersion",
}

ASPIRE_PACKAGES = {
    "Aspire.Hosting",
    "Aspire.Hosting.Testing",
    "Aspire.MongoDB.Driver",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Update the centralized Aspire version plus selected direct dependency version "
            "pins used by this repository."
        )
    )
    parser.add_argument(
        "--aspire-version",
        help="Target version for Aspire.Hosting, Aspire.Hosting.Testing, Aspire.MongoDB.Driver, and Aspire.AppHost.Sdk.",
    )
    parser.add_argument(
        "--package-version",
        action="append",
        default=[],
        metavar="PACKAGE=VERSION",
        help="Set a direct package version pin in Directory.Packages.props. May be passed multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned updates without writing files.",
    )
    args = parser.parse_args()
    if not args.aspire_version and not args.package_version:
        parser.error("Specify --aspire-version, --package-version, or both.")
    return args


def parse_package_updates(raw_updates: list[str]) -> dict[str, str]:
    package_updates: dict[str, str] = {}
    for raw_update in raw_updates:
        if "=" not in raw_update:
            raise ValueError(f"Invalid --package-version value '{raw_update}'. Use PACKAGE=VERSION.")

        package_name, version = raw_update.split("=", 1)
        package_name = package_name.strip()
        version = version.strip()

        if not package_name or not version:
            raise ValueError(f"Invalid --package-version value '{raw_update}'. Use PACKAGE=VERSION.")

        if package_name in ASPIRE_PACKAGES:
            raise ValueError(
                f"Use --aspire-version to update {package_name}; do not pass it via --package-version."
            )

        if package_name not in PACKAGE_PROPERTY_MAP:
            supported = ", ".join(sorted(PACKAGE_PROPERTY_MAP | {package: 'AspireVersion' for package in ASPIRE_PACKAGES}))
            raise ValueError(
                f"Unsupported package '{package_name}'. Supported packages: {supported}."
            )

        package_updates[package_name] = version

    return package_updates


def replace_property(content: str, property_name: str, value: str) -> str:
    pattern = rf"(<{re.escape(property_name)}>)([^<]+)(</{re.escape(property_name)}>)"
    replacement = rf"\g<1>{value}\g<3>"
    updated_content, replacements = re.subn(pattern, replacement, content, count=1)
    if replacements != 1:
        raise ValueError(f"Could not update property '{property_name}' in {DIRECTORY_PACKAGES_PROPS}.")
    return updated_content


def update_directory_packages_props(
    aspire_version: str | None,
    package_updates: dict[str, str],
    dry_run: bool,
) -> None:
    content = DIRECTORY_PACKAGES_PROPS.read_text(encoding="utf-8")

    if aspire_version:
        content = replace_property(content, "AspireVersion", aspire_version)

    for package_name, version in package_updates.items():
        property_name = PACKAGE_PROPERTY_MAP[package_name]
        content = replace_property(content, property_name, version)

    if dry_run:
        return

    DIRECTORY_PACKAGES_PROPS.write_text(content, encoding="utf-8")


def update_global_json(aspire_version: str, dry_run: bool) -> None:
    global_json = json.loads(GLOBAL_JSON.read_text(encoding="utf-8"))
    msbuild_sdks = global_json.setdefault("msbuild-sdks", {})
    msbuild_sdks["Aspire.AppHost.Sdk"] = aspire_version

    if dry_run:
        return

    GLOBAL_JSON.write_text(json.dumps(global_json, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()

    try:
        package_updates = parse_package_updates(args.package_version)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    planned_updates: list[str] = []
    if args.aspire_version:
        planned_updates.append(
            f"AspireVersion={args.aspire_version} (also updates global.json msbuild-sdks.Aspire.AppHost.Sdk)"
        )
    planned_updates.extend(
        f"{package_name}={version}" for package_name, version in sorted(package_updates.items())
    )

    print("Planned version updates:")
    for update in planned_updates:
        print(f"  - {update}")

    try:
        update_directory_packages_props(args.aspire_version, package_updates, args.dry_run)
        if args.aspire_version:
            update_global_json(args.aspire_version, args.dry_run)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("Dry run only; no files were written.")
    else:
        print("Updated version pins successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
