#!/usr/bin/env python3
"""Build a practical agent stack from the repository catalogue."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


DEFAULT_CATALOG = Path(__file__).with_name("all-categories-a-to-z.csv")

CAPABILITIES = {
    "orchestration": (
        "orchestration",
        "multi-agent",
        "agent harness",
        "workflow",
        "agentic",
    ),
    "memory": ("memory", "persistent context", "second brain", "knowledge graph"),
    "research": ("research", "search", "scrap", "crawl", "retriev", "internet"),
    "coding": ("coding agent", "codebase", "developer", "claude code", "software"),
    "automation": ("automation", "browser", "desktop", "computer use", "rpa"),
    "business_apps": ("business", "office", "dashboard", "low-code", "app generation"),
    "safety": ("security", "privacy", "sandbox", "red team", "vulnerab", "skill scanner"),
}

PRODUCT_HINTS = {
    "research": ("research", "academic", "paper", "evidence", "search"),
    "coding": ("coding", "developer", "software", "code", "engineering"),
    "business": ("business", "company", "crm", "sales", "operations", "automation"),
    "personal": ("personal", "assistant", "second brain", "life", "desktop"),
}


def load_repositories(path: Path) -> list[dict[str, str]]:
    """Load and de-duplicate catalogue entries by repository URL."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        url = row.get("url", "").strip()
        if url and url not in unique:
            unique[url] = row
    return list(unique.values())


def searchable_text(row: dict[str, str]) -> str:
    return " ".join(
        row.get(field, "") for field in ("name", "full_name", "description", "use_case", "strengths")
    ).lower()


def score(row: dict[str, str], capability: str, product: str) -> int:
    text = searchable_text(row)
    terms = CAPABILITIES[capability]
    points = sum(3 for term in terms if term in text)
    points += sum(2 for term in PRODUCT_HINTS.get(product, ()) if term in text)
    try:
        points += min(int(row.get("stars", "0") or 0) // 5000, 5)
    except ValueError:
        pass
    return points


def recommend(rows: Iterable[dict[str, str]], product: str, limit: int = 2) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for capability in CAPABILITIES:
        ranked = sorted(
            ((score(row, capability, product), row) for row in rows),
            key=lambda item: (item[0], int(item[1].get("stars", "0") or 0)),
            reverse=True,
        )
        result[capability] = [row for points, row in ranked if points > 0][:limit]
    return dict(result)


def safe_name(row: dict[str, str]) -> str:
    return row.get("full_name") or row.get("name") or row.get("url", "unknown")


def render(product_prompt: str, recommendations: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        f"# Agent architecture: {product_prompt}",
        "",
        "Generated from the local repository catalogue. Treat recommendations as candidates, not approvals.",
        "",
    ]
    for capability, rows in recommendations.items():
        label = capability.replace("_", " ").title()
        lines.append(f"## {label}")
        if not rows:
            lines.append("- No strong catalogue match; implement this layer directly.")
            lines.append("")
            continue
        for row in rows:
            license_name = row.get("license_spdx") or row.get("license_status") or "license unknown"
            lines.append(f"- **{safe_name(row)}** — {row.get('url', '')} ({license_name})")
            description = re.sub(r"\s+", " ", row.get("description", "")).strip()
            if description:
                lines.append(f"  {description[:220]}")
        lines.append("")
    lines.extend(
        [
            "## Build order",
            "1. Start with orchestration, one model adapter, and an explicit task state machine.",
            "2. Add memory and research tools behind permissioned interfaces.",
            "3. Add automation only inside a sandbox with audit logs and human approval.",
            "4. Run license, dependency, prompt-injection, and tool-permission reviews before deployment.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an agent architecture from the GitHub catalogue.")
    parser.add_argument("product", nargs="?", default="private AI business operating system")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--per-capability", type=int, default=2)
    args = parser.parse_args()
    if args.per_capability < 1:
        parser.error("--per-capability must be at least 1")
    rows = load_repositories(args.catalog)
    print(render(args.product, recommend(rows, args.product.lower(), args.per_capability)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
