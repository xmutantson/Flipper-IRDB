"""Verify the three 2022 contributions using local Git objects only; no IR I/O."""
import argparse
from collections import Counter
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTION = "7ee1a9f68f85a9da81bb2b3a21bdc58774061d9b"
REVIEWED_FORK = "e2175d56eef342e5eea2fa246a840d992b670973"
REVIEWED_UPSTREAM = "d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d"
FILES = (
    "Projectors/BenQ/BenQ_W1070.ir",
    "TVs/Hitachi/Hitachi_LE46H508.ir",
    "TVs/Toshiba/Toshiba_43LF421U21.ir",
)


def records(text):
    """Strictly read the parsed-record format used by these three contributions.

    Names/comments are labels, while type/protocol/address/command form a payload.
    A Counter preserves duplicate payload multiplicity; a set would lose records.
    This deliberately does not claim to lint every IR format in the full database.
    """
    headers, result, current = {}, [], None
    for line_number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"line {line_number}: expected key: value")
        key, value = (part.strip() for part in line.split(":", 1))
        if key == "name":
            if current is not None:
                result.append(current)
            current = {"name": value}
        else:
            target = headers if current is None else current
            if key in target:
                raise ValueError(f"line {line_number}: duplicate key {key}")
            target[key] = value
    if current is not None:
        result.append(current)
    if headers != {"Filetype": "IR signals file", "Version": "1"}:
        raise ValueError("expected IR signals file, Version 1 headers")
    if not result:
        raise ValueError("no signal records")
    expected = {"name", "type", "protocol", "address", "command"}
    for record in result:
        if set(record) != expected:
            raise ValueError("expected name/type/protocol/address/command fields")
        if not record["name"] or record["type"] != "parsed":
            raise ValueError("expected a named parsed signal")
        if record["protocol"] not in {"NEC", "NECext"}:
            raise ValueError("unexpected protocol for these contributions")
        for key in ("address", "command"):
            value = record[key]
            if not re.fullmatch(r"[0-9a-fA-F]{2}(?:\s+[0-9a-fA-F]{2}){3}", value):
                raise ValueError(f"{key}: expected four hex bytes")
            record[key] = bytes.fromhex(value)
    return result


def payloads(items):
    return Counter((r["type"], r["protocol"], r["address"], r["command"]) for r in items)


def git(*arguments):
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, text=True,
        encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def verify(target):
    # Resolve to a commit before composing object names. No fetch, merge or writes.
    commit = git("rev-parse", "--verify", "--end-of-options", target + "^{commit}").strip()
    total = 0
    for path in FILES:
        original = records(git("show", f"{CONTRIBUTION}:{path}"))
        candidate = records(git("show", f"{commit}:{path}"))
        before, after = payloads(original), payloads(candidate)
        if before != after:
            missing, added = sum((before - after).values()), sum((after - before).values())
            raise ValueError(f"{path}: payload mismatch ({missing} missing, {added} added)")
        total += len(original)
        print(f"PASS {path}: {len(original)} payload records preserved")
    print(f"PASS {commit}: all {total} original payload records preserved")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=REVIEWED_UPSTREAM,
                        help="local Git revision to compare (default: pinned reviewed upstream)")
    args = parser.parse_args()
    try:
        verify(args.target)
    except (ValueError, subprocess.CalledProcessError) as error:
        message = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
        print(f"FAIL: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
