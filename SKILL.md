---
name: last30days-digital-report
description: Create evidence-backed personal digital-usage reports from Chronicle, Screen Time, browser history, shell history, Downloads, AI-tool footprint, or pre-aggregated usage JSON. Use when the user asks for a last-30-days computer-usage diagnosis, Chronicle-based self-audit, AI/tool-switching analysis, action advice, or Guizang/歸藏 magazine-web-ppt horizontal HTML deck. The only bundled visual template system is Guizang.
---

# Last30Days Digital Report

Turn local computer-usage traces into an evidence-first personal digital report. The skill borrows the strongest ideas from `mvanhorn/last30days-skill`: multi-source evidence, signal weighting, visible source boundaries, shareable HTML briefs, and quotable "best takes" instead of generic summaries.

The only bundled visual template system is Guizang/歸藏. Generated Chronicle HTML outputs or local mockups are not template assets for this skill.

## Core Workflow

1. Find the safest source artifact first.
   - Prefer `data/accessible_usage_summary*.json`, `artifacts/accessible_usage_summary*.json`, or another already-redacted aggregate JSON.
   - If only raw traces exist, do not read cookies, passwords, private keys, full private URLs, chat contents, email, messages, or note bodies. Produce aggregate counts only.
   - If Chronicle or Screen Time databases are missing or blocked, say so plainly and label substitute evidence as substitute evidence.

2. Inspect source shape before writing conclusions.
   - For this repo's schema, see `references/chronicle-data-contract.md`.
   - Use behavior as signal: visits, domain switches, late-night buckets, AI-tool category counts, Downloads/filesystem churn, shell-history patterns, install surface, and data-source coverage.
   - Never present browser visits as exact active screen time.

3. Choose the output surface.
   - Standard report renderer: `editorial`, `xhs-card`, `command-center`, `radar`, or `minimal`. Treat these as deterministic report modes, not reusable visual template assets.
   - Guizang deck: horizontal swipe magazine-web-ppt style. If the user mentions `歸藏`, `guizang`, `杂志风 PPT`, `横向翻页`, or `horizontal swipe deck`, read `references/guizang-ppt-integration.md`.
   - If the user asks for templates, use only the Guizang assets and references.

4. Render the report.
   ```bash
   python3 /path/to/last30days-digital-report/scripts/render_personal_digital_report.py \
     --input /path/to/data/accessible_usage_summary_2026-05-04.json \
     --output /path/to/output/report.html \
     --template editorial \
     --window 30d \
     --name "个人"
   ```

   For all five standard report modes:
   ```bash
   python3 /path/to/last30days-digital-report/scripts/render_personal_digital_report.py \
     --input /path/to/data/accessible_usage_summary_2026-05-04.json \
     --output /path/to/output/report-modes \
     --all-templates \
     --window 30d
   ```

   For a Guizang-style deck scaffold:
   ```bash
   python3 /path/to/last30days-digital-report/scripts/scaffold_guizang_deck.py \
     --output /path/to/output/chronicle-deck \
     --title "Chronicle 电脑使用整顿报告" \
     --theme ink
   ```

   Then fill slides using `references/guizang-ppt-layouts.md`, theme rules from `references/guizang-ppt-themes.md`, and the QA gate in `references/guizang-ppt-checklist.md`.

5. Verify the artifact, not just command success.
   - Confirm the generated `.html` exists and is non-empty.
   - Open or inspect the HTML enough to verify it contains: source boundary, hero metric, ranked risks, evidence cards, social share section, action advice, and output-specific styling.
   - For Guizang decks, confirm the page imports local `assets/motion.min.js`, has horizontal slides, and contains no unresolved `[必填]` placeholders.

## Output Contract

Every final report should include:

- A blunt one-line diagnosis derived from the data.
- A visible evidence boundary: what was analyzed, what was blocked, and what was intentionally not read.
- Ranked risks with numeric evidence, not vibes.
- A social-spread module: share headline, quote card, caption drafts, and a 4:5 cover block users can screenshot.
- Action advice for today, 7 days, and 30 days.
- For standard reports: offline HTML with inline CSS, no external JavaScript, and printable layout.
- For Guizang decks: horizontal swipe HTML, local `assets/motion.min.js`, explicit slide theme rhythm, and no unresolved `[必填]` placeholders.

## Resources

- `scripts/render_personal_digital_report.py`: deterministic HTML renderer for aggregate usage JSON.
- `scripts/scaffold_guizang_deck.py`: copies the bundled Guizang deck template, applies one of the five approved themes, and prepares local motion assets.
- `references/chronicle-data-contract.md`: supported schema, privacy limits, and evidence weighting.
- `references/template-inventory.md`: quick chooser that separates standard report modes from the only bundled template system, Guizang.
- `references/guizang-ppt-integration.md`: Chronicle-to-Guizang deck mapping and validation workflow.
- `references/guizang-ppt-layouts.md`: the 10 bundled Guizang slide layout skeletons.
- `references/guizang-ppt-themes.md`: the 5 bundled Guizang theme presets.
- `references/guizang-ppt-components.md`: Guizang component/class reference.
- `references/guizang-ppt-checklist.md`: Guizang deck quality checklist.
- `assets/guizang-ppt/template.html`: bundled Guizang HTML deck seed.
- `assets/guizang-ppt/motion.min.js`: local animation module copied into generated decks.
- `assets/examples/sample_usage_summary.json`: redacted shape reference for smoke tests.
- `assets/examples/sample-report.html`: generated example output from the redacted sample JSON; not a template.
- `assets/examples/sample-report.share-copy.md`: generated share-copy example paired with the sample report.
