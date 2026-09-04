---
name: guided-tour
description: "Write a German guided-tour.md in the repo root explaining the why and context of changes vs a base ref (default: main), for use as a commit message. Accepts a base ref argument (branch/tag/commit) for stacked branches. Verifies commit-safe markdown formatting with a checker script. Use when the user asks for a guided tour, a tour of changes, or a change summary vs a base."
---

# Guided Tour

Produce `guided-tour.md` in the **repository root** that explains the changes
on the current branch compared to a **base ref** (`main` by default; see
"Base ref" below). The file is later used verbatim as a **commit message**,
which is why its formatting is constrained and verified.

## What to write

- Focus on **relationships and the why**: why something changed, how parts fit
  together, what the intent is, what trade-offs were made.
- Do **not** restate the "what" — the diff already shows that. Do not narrate
  diffs line by line.
- Where a short snippet clarifies the point, include it as a fenced `diff`
  block. Keep snippets small and relevant.
- Write the whole file in **German**.
- If the **reason** for a change is not clear from the diff, **stop and ask the
  user**. Do not guess or invent a rationale.

## Formatting rules (hard requirements)

These are enforced by `scripts/check-guided-tour.py`. There is exactly one
allowed heading style — **setext** (underline) — because `#`/`##` become
invisible comments in a commit message.

1. **Exactly one H1**, and it is the **first line** of the file. Write the
   title, then a line of `=` underneath:

   ```text
   Titel der Änderung
   ==================
   ```

2. Every other section uses **H2**: heading text, then a line of `-`:

   ```text
   Abschnitt
   ---------
   ```

3. **Never use `#`, `##`, `###`, ...** (ATX headings). They are comments in a
   commit message and disappear.
4. **Every line ≤ 100 characters**, including lines inside `diff` code blocks.
   Wrap prose; trim or shorten diff snippets if needed.
5. No other heading styles. A line of `=` = H1, a line of `-` = H2. That is all.

### Full template

````markdown
Kurztitel der Änderung
======================

Ein kurzer Einleitungssatz zum Kontext der Änderung.

Warum wurde X geändert?
-----------------------

Die Motivation war ... Dadurch entsteht folgende Verbindung zu Y:

```diff
- alter Code
+ neuer Code
```

Warum wurde Z eingeführt?
-------------------------

(Wenn unklar: den Nutzer fragen. Nicht raten.)
````

## Base ref (what to compare against)

Determine **BASE** in this order, then use it everywhere below:

1. **Skill argument** — if invoked as `/skill:guided-tour <base>` or the user
   provided a trailing base after the skill content, use that `<base>`.
2. **Stated in the request** — if the user names a base in their message
   ("...vs feature-1", "compared to abc1234", "gegen den feature-x Branch"),
   use it.
3. **Default** — otherwise use `main` (the real integration branch name if it
   is not literally `main`).

`<base>` may be a branch name, tag, or commit hash. Use it for stacked work:
if this branch builds on an **unmerged** parent branch, pass that parent's tip
as BASE so the tour covers only this branch's additions, not the parent's.

If BASE does not resolve, report the git error to the user and ask for the
correct ref rather than guessing.

## Workflow

1. Confirm BASE (see "Base ref"). Verify it exists, then see what changed on
   this branch since it diverged from BASE:
   ```bash
   git rev-parse --verify BASE        # fails fast on a bad ref
   git diff BASE...HEAD               # changes introduced on this branch
   git log BASE..HEAD --oneline       # commits on this branch
   ```
   Use the three-dot `...` form for the diff so only this branch's changes
   since the merge-base with BASE are shown (works for both `main` and an
   unmerged parent branch).
2. Read the changes and identify the **intent** and **relationships**.
3. If a change's rationale is unclear, stop and ask the user before writing.
4. Write `guided-tour.md` in the repo root, in German, following the rules
   above. The tour describes changes vs BASE; if BASE is not `main`, the file
   itself stays the same (the base only affects which diff you read).
5. Validate and iterate until the checker passes. The checker lives next to
   this `SKILL.md` at `scripts/check-guided-tour.py`; resolve that against this
   skill's directory (the parent dir of this file) and run it with the repo's
   `guided-tour.md` as the argument:
   ```bash
   python3 <skill-dir>/scripts/check-guided-tour.py guided-tour.md
   ```
   Fix every reported issue, then re-run until it reports `OK`.
