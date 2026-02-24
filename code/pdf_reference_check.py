\
#!/usr/bin/env python3

import argparse
import os
import re
import sys


def parse_args():
    ap = argparse.ArgumentParser(description="Validate that every listed reference is cited at least once in the PDF body.")
    ap.add_argument("pdf", help="Path to the paper PDF")
    ap.add_argument("--sanity-token", default=None, help="Optional token that must appear somewhere in extracted text")
    return ap.parse_args()


def extract_text(pdf_path: str) -> str:
    try:
        import PyPDF2  # type: ignore
    except Exception:
        raise SystemExit("PyPDF2 not installed. Install with: python3 -m pip install PyPDF2")

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        chunks = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            chunks.append(t)
        return "\n".join(chunks)


def split_body_and_refs(text: str) -> tuple[str, str]:
    # Use the *last* occurrence of REFERENCES to avoid false positives in headers/footers.
    matches = list(re.finditer(r"\bREFERENCES\b", text, flags=re.IGNORECASE))
    if not matches:
        raise SystemExit("[FAIL] Could not locate REFERENCES section in PDF text.")
    m = matches[-1]
    body = text[: m.start()]
    refs = text[m.end() :]
    return body, refs


def main():
    args = parse_args()
    pdf_path = args.pdf

    if not os.path.exists(pdf_path):
        raise SystemExit(f"Missing PDF: {pdf_path}")

    text = extract_text(pdf_path)

    if args.sanity_token is not None and args.sanity_token not in text:
        raise SystemExit(f"[FAIL] Sanity token not found in PDF text: {args.sanity_token!r}")

    body, refs = split_body_and_refs(text)

    cit = sorted({int(x) for x in re.findall(r"\[(\d{1,3})\]", body)})
    ref = sorted({int(x) for x in re.findall(r"\[(\d{1,3})\]", refs)})

    uncited = [r for r in ref if r not in cit]
    bad_cites = [c for c in cit if c not in ref]

    print(f"Citations used in body: {cit}")
    print(f"References listed:      {ref}")

    if uncited:
        raise SystemExit(f"[FAIL] Uncited references present: {uncited}")
    if bad_cites:
        raise SystemExit(f"[FAIL] Citations in body not in reference list: {bad_cites}")

    print("[OK] Every listed reference is cited at least once.")
    print("PDF validation PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
