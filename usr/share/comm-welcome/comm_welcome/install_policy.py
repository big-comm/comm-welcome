"""Conservative validation of prepared browser transactions."""

from .catalog import BROWSERS


def browser_reference(reference: str) -> bool:
    if not reference.startswith("alpm:") or "/" not in reference:
        return False
    repository, package = reference[5:].split("/", 1)
    return bool(repository) and package in {p for b in BROWSERS for p in b.packages}


def validate_plan(plan: dict, reference: str) -> bool:
    """Accept only explicit native installs; unknown plans fail closed."""
    if not browser_reference(reference) or plan.get("preparation_interactions"):
        return False
    sections = plan.get("sections")
    if not isinstance(sections, list) or not sections:
        return False
    packages = []
    for section in sections:
        if not isinstance(section, dict) or section.get("removes"):
            return False
        rows = section.get("planned_packages")
        if not isinstance(rows, list) or not rows:
            return False
        packages.extend(rows)
    for row in packages:
        if not isinstance(row, dict):
            return False
        if not str(row.get("ref", "")).startswith("alpm:"):
            return False
        if row.get("action") not in {"install", "upgrade", "reinstall"}:
            return False
    return any(row.get("ref") == reference for row in packages)
