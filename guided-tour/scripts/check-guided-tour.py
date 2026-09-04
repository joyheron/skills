#!/usr/bin/env python3
"""Check guided-tour.md formatting for use as a commit message.

Rules (see SKILL.md):
  * Exactly one H1 at the top, setext style:  title line, then a line of '='
  * Other sections as H2, setext style:       heading line, then a line of '-'
  * No ATX headings ('#' .. '######')  -- they vanish as comments in commit msgs
  * No line longer than 100 characters (every line, incl. fenced code blocks)

Exit code: 0 = valid, 1 = formatting issues, 2 = file not found.
"""
import argparse
import re
import sys

ATX = re.compile(r"^ {0,3}#{1,6}(\s|$)")
H1UL = re.compile(r"^ {0,3}=+\s*$")
H2UL = re.compile(r"^ {0,3}-+\s*$")
FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})")
DEFAULT_MAX = 100


def check(text, max_line=DEFAULT_MAX, name="guided-tour.md"):
    lines = text.splitlines()
    issues = []
    in_fence = False
    fence_char = None
    prev_text = None      # line no. of last content line of current paragraph
    para_start = None     # first line no. of current paragraph
    first_nonblank = None
    h1_count = 0
    h1_title_line = None
    first_heading_kind = None

    def break_para():
        return None, None

    for i, raw in enumerate(lines, start=1):
        if len(raw) > max_line:
            issues.append(f"{name}:{i}: line too long ({len(raw)} > {max_line})")

        m = FENCE.match(raw)
        if m:
            ch = "`" if m.group(2).startswith("`") else "~"
            if not in_fence:
                in_fence, fence_char = True, ch
            elif fence_char == ch:
                in_fence, fence_char = False, None
            prev_text, para_start = break_para()
            continue
        if in_fence:
            continue  # code block: only the line-length check above applies

        if not raw.strip():
            prev_text, para_start = break_para()
            continue
        if first_nonblank is None:
            first_nonblank = i

        if ATX.match(raw):
            issues.append(f"{name}:{i}: '#' heading forbidden; use setext (= or - underline)")
            prev_text, para_start = break_para()
            continue

        if H1UL.match(raw):
            if prev_text is None:
                issues.append(f"{name}:{i}: '=' line with no heading text above")
            else:
                h1_count += 1
                if h1_count == 1:
                    h1_title_line = para_start
                    first_heading_kind = "h1"
                else:
                    issues.append(f"{name}:{i}: more than one H1 ('=' underline)")
            prev_text, para_start = break_para()
            continue

        if H2UL.match(raw):
            if prev_text is not None and first_heading_kind is None:
                first_heading_kind = "h2"
            # prev_text None -> thematic break (---), allowed
            prev_text, para_start = break_para()
            continue

        # regular content line
        if prev_text is None:
            para_start = i
        prev_text = i

    if first_nonblank is None:
        issues.append(f"{name}: file is empty")
    else:
        if h1_count == 0:
            issues.append(f"{name}: no H1 found; start with a title line followed by '===='")
        if h1_count == 1 and h1_title_line != first_nonblank:
            issues.append(f"{name}:{h1_title_line}: H1 must be the first line of the file")
        if first_heading_kind == "h2":
            issues.append(f"{name}: first heading is H2; the file must start with a single H1")
    return issues


def main():
    ap = argparse.ArgumentParser(description="Validate guided-tour.md formatting.")
    ap.add_argument("path", nargs="?", default="guided-tour.md",
                    help="path to guided-tour.md (default: ./guided-tour.md)")
    ap.add_argument("--max-line", type=int, default=DEFAULT_MAX,
                    help=f"max characters per line (default: {DEFAULT_MAX})")
    args = ap.parse_args()

    try:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"{args.path}: file not found", file=sys.stderr)
        sys.exit(2)

    issues = check(text, args.max_line, args.path)
    if issues:
        for msg in issues:
            print(msg)
        print(f"\n{len(issues)} issue(s) -- guided-tour formatting invalid.")
        sys.exit(1)
    print(f"{args.path}: OK (setext H1/H2, no '#', lines <= {args.max_line}ch)")
    sys.exit(0)


if __name__ == "__main__":
    main()
