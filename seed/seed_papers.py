#!/usr/bin/env python3
"""Populate the reviewer screen with real papers from arXiv.

The reviewer dashboard reads conference_papers rows for the current year. A
fresh database has none, so the screen is empty with nothing to review. This
fetches genuine papers from arXiv, optionally runs them through the same review
pipeline a student upload would use, and inserts them.

    python3 seed/seed_papers.py --conference ICML --count 3
    python3 seed/seed_papers.py --conference ACL --count 2 --no-review

--no-review is fast and needs no Gemini key: it stores the arXiv abstract as
the summary and leaves the AI review empty. The default runs the real pipeline,
which takes roughly 30 seconds per paper.

Papers are inserted with status "Pending" so they appear in the review queue.
They are real publications that were not actually submitted to these venues;
this is sample data for exercising the interface.
"""

import argparse
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import get_sessionmaker, init_models  # noqa: E402
from models.conference import Conference  # noqa: E402
from models.conference_paper import ConferencePaper  # noqa: E402

ATOM = {"a": "http://www.w3.org/2005/Atom"}

# Rough topical fit, so seeded papers suit the venue they are filed under.
CATEGORY = {
    "ACL": "cs.CL",
    "ICML": "cs.LG",
    "NEURIPS": "cs.LG",
    "ICLR": "cs.LG",
}


def fetch_arxiv(category, count):
    url = (
        "https://export.arxiv.org/api/query?"
        f"search_query=cat:{category}&start=0&max_results={count}"
        "&sortBy=submittedDate&sortOrder=descending"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "crab-ai-seed/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        root = ET.fromstring(resp.read())

    papers = []
    for entry in root.findall("a:entry", ATOM):
        pdf = next(
            (l.get("href") for l in entry.findall("a:link", ATOM) if l.get("title") == "pdf"),
            None,
        )
        if not pdf:
            continue
        papers.append({
            "title": " ".join(entry.find("a:title", ATOM).text.split()),
            "authors": [a.find("a:name", ATOM).text for a in entry.findall("a:author", ATOM)],
            "abstract": " ".join(entry.find("a:summary", ATOM).text.split()),
            "pdf_url": pdf if pdf.endswith(".pdf") else pdf + ".pdf",
        })
    return papers


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "crab-ai-seed/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conference", required=True, help="Conference name as stored in the database")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--category", help="arXiv category, defaults to one matching the venue")
    ap.add_argument("--no-review", action="store_true", help="Skip Gemini; store the abstract only")
    ap.add_argument("--year", type=int, default=datetime.utcnow().year)
    args = ap.parse_args()

    init_models()
    session = get_sessionmaker()()

    conference = session.query(Conference).filter(Conference.name == args.conference).first()
    if not conference:
        names = [c.name for c in session.query(Conference).all()]
        sys.exit(f"No conference named {args.conference!r}. Known: {names}")

    category = args.category or CATEGORY.get(args.conference.upper(), "cs.LG")
    print(f"Fetching {args.count} papers from arXiv {category} for {conference.name}")
    papers = fetch_arxiv(category, args.count)

    tmp = Path("uploads/seed")
    tmp.mkdir(parents=True, exist_ok=True)
    added = 0

    for i, paper in enumerate(papers, 1):
        exists = (
            session.query(ConferencePaper)
            .filter(
                ConferencePaper.title == paper["title"],
                ConferencePaper.conference_id == conference.id,
                ConferencePaper.year == args.year,
            )
            .first()
        )
        if exists:
            print(f"  [{i}/{len(papers)}] already present, skipping: {paper['title'][:55]}")
            continue

        summary = {
            "title": paper["title"],
            "author": paper["authors"],
            "summary": paper["abstract"],
        }
        review = None

        if not args.no_review:
            from utils.student_paper_review import (  # imported lazily so --no-review needs no key
                generate_paper_summary,
                get_paper_review,
                upload_to_gemini,
            )

            local = tmp / f"{conference.name.lower()}_{i}.pdf"
            print(f"  [{i}/{len(papers)}] downloading {paper['title'][:50]}")
            try:
                download(paper["pdf_url"], local)
                handle = upload_to_gemini(str(local))
                summary = generate_paper_summary(str(local), handle=handle)
                review = get_paper_review(
                    conference.name, summary.get("title", paper["title"]),
                    str(local), conference.guidelines, handle=handle,
                )
                print(f"        reviewed: {review.get('final_score')} {review.get('decision')}")
            except Exception as exc:  # noqa: BLE001 - one bad paper should not stop the run
                print(f"        review failed ({type(exc).__name__}), storing the abstract instead")
                review = None

        session.add(ConferencePaper(
            title=paper["title"],
            conference_id=conference.id,
            summary=summary,
            review_gemini=review,
            status="Pending",
            year=args.year,
            path=paper["pdf_url"],
        ))
        session.commit()
        added += 1
        print(f"  [{i}/{len(papers)}] added: {paper['title'][:55]}")

    total = (
        session.query(ConferencePaper)
        .filter(ConferencePaper.conference_id == conference.id, ConferencePaper.year == args.year)
        .count()
    )
    print(f"\nAdded {added}. {conference.name} now has {total} paper(s) for {args.year}.")


if __name__ == "__main__":
    main()
