#!/usr/bin/env python3
"""Export top Search Console sites, queries, and pages across every GSC property."""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from monitoring import google_credentials


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_ROOT = ROOT / ".deploy" / "reports"
MAX_API_PAGE_SIZE = 25_000


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected YYYY-MM-DD, got {value!r}"
        ) from exc


def report_dates(args: argparse.Namespace) -> tuple[date, date]:
    end = args.end_date or (date.today() - timedelta(days=3))
    start = args.start_date or (end - timedelta(days=args.days - 1))
    if start > end:
        raise SystemExit("--start-date must be on or before --end-date")
    return start, end


def gsc_api(method: str, url: str, token: str, body=None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        exc.response_detail = raw.decode("utf-8", errors="replace") if raw else ""
        raise
    return json.loads(raw) if raw else {}


def list_properties(token: str) -> list[dict[str, str]]:
    response = gsc_api(
        "GET",
        "https://www.googleapis.com/webmasters/v3/sites",
        token,
    )
    return [
        {
            "siteUrl": str(item.get("siteUrl", "")),
            "permissionLevel": str(item.get("permissionLevel", "")),
        }
        for item in (response.get("siteEntry") or [])
        if item.get("siteUrl")
    ]


def select_properties(
    properties: list[dict[str, str]],
    *,
    property_kind: str,
    requested: set[str],
) -> list[dict[str, str]]:
    accessible = [
        item
        for item in properties
        if item["permissionLevel"] != "siteUnverifiedUser"
    ]
    available = {item["siteUrl"] for item in accessible}
    missing = requested - available
    if missing:
        raise SystemExit(
            "Requested GSC property is unavailable: " + ", ".join(sorted(missing))
        )
    if requested:
        accessible = [item for item in accessible if item["siteUrl"] in requested]
    elif property_kind == "url-prefix":
        accessible = [
            item for item in accessible if not item["siteUrl"].startswith("sc-domain:")
        ]
    elif property_kind == "domain":
        accessible = [
            item for item in accessible if item["siteUrl"].startswith("sc-domain:")
        ]
    return sorted(accessible, key=lambda item: item["siteUrl"])


def search_analytics(
    token: str,
    property_url: str,
    start: date,
    end: date,
    *,
    dimension: str | None,
    search_type: str,
    data_state: str,
    max_rows: int,
) -> list[dict[str, Any]]:
    encoded = urllib.parse.quote(property_url, safe="")
    endpoint = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        f"{encoded}/searchAnalytics/query"
    )
    rows: list[dict[str, Any]] = []
    start_row = 0
    while start_row < max_rows:
        page_size = min(MAX_API_PAGE_SIZE, max_rows - start_row)
        body: dict[str, Any] = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "type": search_type,
            "dataState": data_state,
            "rowLimit": page_size,
            "startRow": start_row,
        }
        if dimension:
            body["dimensions"] = [dimension]
        response = gsc_api("POST", endpoint, token, body)
        page = list(response.get("rows") or [])
        rows.extend(page)
        if len(page) < page_size:
            break
        start_row += len(page)
    return rows


def metric_row(
    *,
    clicks: float,
    impressions: float,
    position_numerator: float,
) -> dict[str, float]:
    return {
        "clicks": clicks,
        "impressions": impressions,
        "ctr": clicks / impressions if impressions else 0.0,
        "position": position_numerator / impressions if impressions else 0.0,
    }


def normalized_metrics(row: dict[str, Any]) -> dict[str, float]:
    clicks = float(row.get("clicks", 0.0))
    impressions = float(row.get("impressions", 0.0))
    position = float(row.get("position", 0.0))
    return metric_row(
        clicks=clicks,
        impressions=impressions,
        position_numerator=position * impressions,
    )


def aggregate_queries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "clicks": 0.0,
            "impressions": 0.0,
            "positionNumerator": 0.0,
            "properties": set(),
        }
    )
    for row in rows:
        query = str(row["query"])
        clicks = float(row["clicks"])
        impressions = float(row["impressions"])
        totals[query]["clicks"] += clicks
        totals[query]["impressions"] += impressions
        totals[query]["positionNumerator"] += float(row["position"]) * impressions
        totals[query]["properties"].add(str(row["property"]))
    result = []
    for query, values in totals.items():
        result.append(
            {
                "query": query,
                "propertyCount": len(values["properties"]),
                **metric_row(
                    clicks=values["clicks"],
                    impressions=values["impressions"],
                    position_numerator=values["positionNumerator"],
                ),
            }
        )
    return sorted(
        result,
        key=lambda row: (-row["clicks"], -row["impressions"], row["query"]),
    )


def collect_report(
    token: str,
    properties: list[dict[str, str]],
    start: date,
    end: date,
    *,
    search_type: str,
    data_state: str,
    max_rows: int,
    fail_fast: bool,
) -> dict[str, Any]:
    sites: list[dict[str, Any]] = []
    site_queries: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for index, item in enumerate(properties, 1):
        property_url = item["siteUrl"]
        print(f"[{index}/{len(properties)}] Querying {property_url}", flush=True)
        try:
            totals = search_analytics(
                token,
                property_url,
                start,
                end,
                dimension=None,
                search_type=search_type,
                data_state=data_state,
                max_rows=1,
            )
            total_metrics = normalized_metrics(totals[0] if totals else {})
            sites.append(
                {
                    "property": property_url,
                    "permissionLevel": item["permissionLevel"],
                    **total_metrics,
                }
            )
            for row in search_analytics(
                token,
                property_url,
                start,
                end,
                dimension="query",
                search_type=search_type,
                data_state=data_state,
                max_rows=max_rows,
            ):
                site_queries.append(
                    {
                        "property": property_url,
                        "query": str((row.get("keys") or [""])[0]),
                        **normalized_metrics(row),
                    }
                )
            for row in search_analytics(
                token,
                property_url,
                start,
                end,
                dimension="page",
                search_type=search_type,
                data_state=data_state,
                max_rows=max_rows,
            ):
                pages.append(
                    {
                        "property": property_url,
                        "page": str((row.get("keys") or [""])[0]),
                        **normalized_metrics(row),
                    }
                )
        except Exception as exc:
            if fail_fast:
                raise
            detail = str(getattr(exc, "response_detail", "")).strip()
            errors.append(
                {
                    "property": property_url,
                    "error": f"{type(exc).__name__}: {exc}",
                    "detail": detail,
                }
            )
            print(f"  Skipped after error: {type(exc).__name__}: {exc}", file=sys.stderr)
    sites.sort(key=lambda row: (-row["clicks"], -row["impressions"], row["property"]))
    site_queries.sort(
        key=lambda row: (-row["clicks"], -row["impressions"], row["property"], row["query"])
    )
    pages.sort(key=lambda row: (-row["clicks"], -row["impressions"], row["page"]))
    return {
        "sites": sites,
        "queries": aggregate_queries(site_queries),
        "siteQueries": site_queries,
        "pages": pages,
        "errors": errors,
    }


def sort_rankings(report: dict[str, Any], sort_by: str) -> None:
    secondary = "impressions" if sort_by == "clicks" else "clicks"
    labels = {
        "sites": "property",
        "queries": "query",
        "siteQueries": "property",
        "pages": "page",
    }
    for key, label in labels.items():
        report[key].sort(
            key=lambda row: (
                -row[sort_by],
                -row[secondary],
                str(row[label]),
            )
        )


def csv_value(value: Any) -> Any:
    if isinstance(value, float):
        return f"{value:.6f}" if 0 < abs(value) < 1 else f"{value:.3f}"
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def write_report(
    output_dir: Path,
    report: dict[str, Any],
    *,
    start: date,
    end: date,
    search_type: str,
    data_state: str,
    sort_by: str,
    property_count: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metric_fields = ["clicks", "impressions", "ctr", "position"]
    write_csv(
        output_dir / "sites.csv",
        report["sites"],
        ["property", "permissionLevel", *metric_fields],
    )
    write_csv(
        output_dir / "queries.csv",
        report["queries"],
        ["query", "propertyCount", *metric_fields],
    )
    write_csv(
        output_dir / "site-queries.csv",
        report["siteQueries"],
        ["property", "query", *metric_fields],
    )
    write_csv(
        output_dir / "pages.csv",
        report["pages"],
        ["property", "page", *metric_fields],
    )
    if report["errors"]:
        write_csv(
            output_dir / "errors.csv",
            report["errors"],
            ["property", "error", "detail"],
        )
    summary = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "searchType": search_type,
        "dataState": data_state,
        "sortBy": sort_by,
        "propertiesSelected": property_count,
        "propertiesReported": len(report["sites"]),
        "propertiesErrored": len(report["errors"]),
        "queryRows": len(report["queries"]),
        "pageRows": len(report["pages"]),
        "topSites": report["sites"][:20],
        "topQueries": report["queries"][:20],
        "topPages": report["pages"][:20],
        "errors": report["errors"],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def print_ranking(title: str, rows: list[dict[str, Any]], label: str, top: int) -> None:
    print(f"\n{title}")
    if not rows:
        print("  No Search Console data in this date range.")
        return
    for index, row in enumerate(rows[:top], 1):
        value = str(row[label])
        print(
            f"{index:>3}. {row['clicks']:>9.0f} clicks  "
            f"{row['impressions']:>11.0f} impressions  "
            f"pos {row['position']:>6.1f}  {value}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank sites, queries, and pages across all accessible Search Console "
            "properties, including properties no longer present in this repository."
        )
    )
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--start-date", type=parse_date)
    parser.add_argument("--end-date", type=parse_date)
    parser.add_argument("--top", type=int, default=20, help="Rows shown in the terminal")
    parser.add_argument(
        "--sort-by",
        choices=["clicks", "impressions"],
        default="clicks",
        help="Metric used to rank terminal and CSV results",
    )
    parser.add_argument(
        "--max-rows-per-property",
        type=int,
        default=25_000,
        help="Maximum query rows and page rows fetched for each property",
    )
    parser.add_argument(
        "--property-kind",
        choices=["url-prefix", "domain", "all"],
        default="url-prefix",
        help="URL-prefix avoids double-counting matching domain properties",
    )
    parser.add_argument(
        "--site",
        action="append",
        help="Exact GSC property URL to query; repeat to select several",
    )
    parser.add_argument(
        "--search-type",
        choices=["web", "image", "video", "news", "discover", "googleNews"],
        default="web",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Include fresh/partial data instead of finalized data only",
    )
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be positive")
    if args.top < 1:
        parser.error("--top must be positive")
    if args.max_rows_per_property < 1:
        parser.error("--max-rows-per-property must be positive")
    return args


def main() -> None:
    args = parse_args()
    start, end = report_dates(args)
    credentials = google_credentials()
    properties = select_properties(
        list_properties(credentials.token),
        property_kind=args.property_kind,
        requested=set(args.site or []),
    )
    if not properties:
        raise SystemExit("No accessible Search Console properties matched the selection.")
    output_dir = args.output_dir or (
        DEFAULT_REPORT_ROOT / f"gsc-{start.isoformat()}-to-{end.isoformat()}"
    )
    print(
        f"Querying {len(properties)} GSC properties from {start} through {end}.\n"
        "Properties come from Search Console, not local sites/.",
        flush=True,
    )
    report = collect_report(
        credentials.token,
        properties,
        start,
        end,
        search_type=args.search_type,
        data_state="all" if args.fresh else "final",
        max_rows=args.max_rows_per_property,
        fail_fast=args.fail_fast,
    )
    sort_rankings(report, args.sort_by)
    write_report(
        output_dir,
        report,
        start=start,
        end=end,
        search_type=args.search_type,
        data_state="all" if args.fresh else "final",
        sort_by=args.sort_by,
        property_count=len(properties),
    )
    print_ranking(f"Top sites by {args.sort_by}", report["sites"], "property", args.top)
    print_ranking(f"Top queries by {args.sort_by}", report["queries"], "query", args.top)
    print_ranking(f"Top pages by {args.sort_by}", report["pages"], "page", args.top)
    print(f"\nReport written to {output_dir.resolve()}")
    if report["errors"]:
        print(f"Completed with {len(report['errors'])} property error(s); see errors.csv.")


if __name__ == "__main__":
    main()
