# Install And Usage Details

## Install Into Codex

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/bigcongcong/last30days-digital-report.git \
  ~/.codex/skills/last30days-digital-report
```

Restart Codex after installation.

To verify the skill folder exists:

```bash
test -f ~/.codex/skills/last30days-digital-report/SKILL.md
```

Optional validation:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/last30days-digital-report
```

## Update Existing Install

```bash
git -C ~/.codex/skills/last30days-digital-report pull
```

Restart Codex after updating.

## Use With Codex

Example prompts:

```text
Use $last30days-digital-report to render my aggregate usage JSON into an editorial computer-usage report.
```

```text
Use $last30days-digital-report to build a Guizang-style horizontal deck from my computer usage diagnosis.
```

```text
Use $last30days-digital-report to inspect this Chronicle aggregate JSON and give action advice for today, 7 days, and 30 days.
```

## Use Without Codex

The scripts can be used directly.

### Standard HTML Report

```bash
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output outputs/report.html \
  --template editorial \
  --window 30d \
  --name "Demo"
```

Available `--template` values are report modes, not bundled visual templates:

- `editorial`
- `xhs-card`
- `command-center`
- `radar`
- `minimal`

### All Standard Report Modes

```bash
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output outputs/report-modes \
  --all-templates \
  --window 30d \
  --name "Demo"
```

### Guizang/歸藏 HTML Deck Scaffold

```bash
python3 scripts/scaffold_guizang_deck.py \
  --output outputs/guizang-deck \
  --title "Chronicle 电脑使用整顿报告" \
  --theme ink
```

This writes:

```text
outputs/guizang-deck/index.html
outputs/guizang-deck/assets/motion.min.js
outputs/guizang-deck/images/
```

Theme choices:

- `ink`
- `indigo`
- `forest`
- `kraft`
- `dune`

Open:

```bash
open outputs/guizang-deck/index.html
```

## Template Boundary

Only Guizang/歸藏 is shipped as a reusable visual template system:

- `assets/guizang-ppt/template.html`
- `assets/guizang-ppt/motion.min.js`
- `references/guizang-ppt-layouts.md`
- `references/guizang-ppt-themes.md`
- `references/guizang-ppt-components.md`
- `references/guizang-ppt-checklist.md`

Generated Chronicle HTML reports, generated social cards, and layout mockups are not part of the published template surface.

## Input Data Notes

Prefer a redacted aggregate JSON. Do not feed raw browser cookies, password manager exports, private keys, chat transcripts, emails, private note bodies, or raw secret-bearing shell commands into a public report workflow.

Use `assets/examples/sample_usage_summary.json` as the shape reference.

## Publishing Checklist

Before publishing or pushing changes:

```bash
python3 -m py_compile scripts/render_personal_digital_report.py scripts/scaffold_guizang_deck.py
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output outputs/verify-report.html \
  --template editorial \
  --window 30d
python3 scripts/scaffold_guizang_deck.py \
  --output outputs/verify-guizang \
  --title "Verify Guizang Deck" \
  --theme indigo
rg -n "\\[必填\\]|修复协议" outputs/verify-report.html outputs/verify-guizang/index.html
```

`rg` should return no matches for the placeholder/legacy terms.
