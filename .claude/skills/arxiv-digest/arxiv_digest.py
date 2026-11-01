#!/usr/bin/env python3
"""Read-only arXiv research digest with abstracts and provenance."""

import argparse
import datetime as dt
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}


def fetch(query: str, max_results: int):
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ME-CE-AM-295-lab4-digest/1.1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def clean(text):
    return " ".join((text or "").split())


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)

    for entry in root.findall("a:entry", NS):
        title = clean(entry.findtext("a:title", "", NS))
        link = clean(entry.findtext("a:id", "", NS))
        published = entry.findtext("a:published", "", NS)[:10]
        abstract = clean(entry.findtext("a:summary", "", NS))

        authors = [
            clean(author.findtext("a:name", "", NS))
            for author in entry.findall("a:author", NS)
        ]

        if not title or not link:
            continue

        paper_id = re.sub(
            r"v\d+$", "",
            link.rstrip("/").split("/")[-1],
        )

        if paper_id.startswith("errors"):
            raise ValueError(f"arXiv API error: {abstract}")

        yield {
            "id": paper_id,
            "title": title,
            "link": link,
            "date": published,
            "author": (
                authors[0] + (" et al." if len(authors) > 1 else "")
                if authors else "Unknown"
            ),
            "abstract": abstract,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        action="append",
        required=True,
        help="arXiv query; repeat for multiple research tracks",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=2,
        help="Publication lookback in days",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=8,
        help="Maximum results per query",
    )
    args = parser.parse_args(argv)

    if args.days < 1 or not 1 <= args.max <= 100:
        parser.error("--days must be positive and --max must be 1-100")

    today = dt.date.today()
    since = today - dt.timedelta(days=args.days)
    papers = {}

    try:
        for index, query in enumerate(args.query):
            if index:
                time.sleep(3.2)

            for paper in parse(fetch(query, args.max)):
                if paper["date"] < since.isoformat():
                    continue

                if paper["id"] not in papers:
                    paper["tracks"] = []
                    papers[paper["id"]] = paper

                papers[paper["id"]]["tracks"].append(index + 1)

    except Exception as exc:
        print(
            f"**arXiv digest failed**: "
            f"{type(exc).__name__}: {exc}\n\n"
            "Retrieval incomplete. No results should be used."
        )
        return 1

    selected = sorted(
        papers.values(),
        key=lambda paper: paper["date"],
        reverse=True,
    )

    print(f"### arXiv candidate digest — {today.isoformat()}")
    print(f"\nCandidates: {len(selected)}")

    if not selected:
        print("\nNo new matching submissions.")

    for paper in selected:
        tracks = ", ".join(map(str, paper["tracks"]))

        print(
            f"\n- **{paper['title']}** — "
            f"{paper['author']} ({paper['date']}). "
            f"{paper['link']}"
        )
        print(f"  - arXiv ID: `{paper['id']}`")
        print(f"  - Search tracks: {tracks}")
        print(f"  - Abstract: {paper['abstract']}")

    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="minutes"
    )

    print(
        f"\n_Source: arXiv API · "
        f"queries: {len(args.query)} · "
        f"window: {args.days} d · "
        f"max/query: {args.max} · "
        f"fetched: {timestamp}_"
    )

    print("\n_Queries:_")
    for index, query in enumerate(args.query, 1):
        print(f"\n{index}. `{query}`")

    return 0


if __name__ == "__main__":
    sys.exit(main())
