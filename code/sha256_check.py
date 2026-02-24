\
#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
from typing import Dict


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def parse_args():
    ap = argparse.ArgumentParser(description="Compute SHA-256 hashes for files and optionally verify expected values.")
    ap.add_argument("files", nargs="+", help="Files to hash (paths)")
    ap.add_argument("--expected-json", default=os.path.join(os.path.dirname(__file__), "expected_values.json"))
    ap.add_argument("--check", action="store_true", help="Verify against expected SHA-256 values in expected_values.json")
    return ap.parse_args()


def main():
    args = parse_args()

    for p in args.files:
        if not os.path.exists(p):
            raise SystemExit(f"Missing file: {p}")

    expected: Dict[str, str] = {}
    if args.check:
        with open(args.expected_json, "r", encoding="utf-8") as f:
            expected = json.load(f)["sha256"]

    ok = True
    for p in args.files:
        base = os.path.basename(p)
        digest = sha256_file(p)
        print(f"{digest}  {p}")

        if args.check:
            if base not in expected:
                print(f"[WARN] No expected SHA-256 found for basename: {base} (skipping strict check)")
            else:
                exp = expected[base]
                if digest.lower() != exp.lower():
                    ok = False
                    print(f"[FAIL] {base}: expected {exp} got {digest}")
                else:
                    print(f"[OK]   {base}: {digest}")

    if args.check and not ok:
        raise SystemExit("SHA-256 check FAILED.")
    if args.check:
        print("SHA-256 check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
