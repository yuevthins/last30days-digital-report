# Last30Days Digital Report

`last30days-digital-report` is a Codex/Codex App skill for turning local computer-usage traces into an evidence-backed personal digital report.

It can produce:

- Chronicle-style usage diagnosis reports from aggregate JSON.
- Last-30-days browser / shell / Downloads / AI-tool footprint summaries.
- Action advice for today, 7 days, and 30 days.
- Guizang/歸藏 magazine-web-ppt horizontal HTML decks.

The only bundled visual template system is Guizang/歸藏. Generated Chronicle HTML reports and local mockups are intentionally not shipped as templates, because their content and quality depend on the specific source data and design pass.

The skill is designed around aggregate or redacted data. It should not read or publish cookies, passwords, private keys, raw chat contents, emails, private note bodies, or full private URLs.

## What Is Included

```text
last30days-digital-report/
├── SKILL.md
├── README.md
├── INSTALL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── examples/
│   │   ├── sample_usage_summary.json
│   │   ├── sample-report.html
│   │   └── sample-report.share-copy.md
│   └── guizang-ppt/
│       ├── template.html
│       ├── motion.min.js
│       └── LICENSE
├── references/
│   ├── chronicle-data-contract.md
│   ├── guizang-ppt-integration.md
│   ├── guizang-ppt-layouts.md
│   ├── guizang-ppt-themes.md
│   ├── guizang-ppt-components.md
│   ├── guizang-ppt-checklist.md
│   └── template-inventory.md
└── scripts/
    ├── render_personal_digital_report.py
    └── scaffold_guizang_deck.py
```

## Install

### Codex

Clone or copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/yuevthins/last30days-digital-report.git \
  ~/.codex/skills/last30days-digital-report
```

Restart Codex after installing or updating a skill, because skill discovery happens at startup.

### Claude Code / Other Agents

Other local agents can use the same folder as a plain workflow package:

```bash
git clone https://github.com/yuevthins/last30days-digital-report.git
```

Then point the agent to `SKILL.md` and the scripts under `scripts/`.

## Quick Start

Render a standard report from aggregate JSON:

```bash
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output outputs/sample-report.html \
  --template editorial \
  --window 30d \
  --name "Demo"
```

Render all built-in report modes:

```bash
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output outputs/sample-report-modes \
  --all-templates \
  --window 30d \
  --name "Demo"
```

Scaffold a Guizang/歸藏 horizontal deck:

```bash
python3 scripts/scaffold_guizang_deck.py \
  --output outputs/guizang-deck \
  --title "Chronicle Computer Usage Report" \
  --theme ink
```

Open the generated HTML directly in a browser. No local server is required for standard reports. Guizang decks also work as static HTML and copy a local `assets/motion.min.js` file next to `index.html`.

## Example Output

The repo includes a deterministic sample report generated from the redacted demo JSON:

- `assets/examples/sample-report.html`
- `assets/examples/sample-report.share-copy.md`

These files are example outputs, not reusable templates. Use them to understand the renderer's finished artifact shape, source-boundary wording, action-advice structure, and share-copy format.

## Output Modes

Standard report modes:

- `editorial`: public long-form report.
- `xhs-card`: mobile screenshot-oriented report.
- `command-center`: dense founder/operator review.
- `radar`: risk radar and action protocol.
- `minimal`: printable memo.

Guizang/歸藏 deck template kit:

- 10 slide layout skeletons in `references/guizang-ppt-layouts.md`.
- 5 fixed theme presets in `references/guizang-ppt-themes.md`.
- Component guide in `references/guizang-ppt-components.md`.
- QA checklist in `references/guizang-ppt-checklist.md`.
- Seed HTML at `assets/guizang-ppt/template.html`.

## Data Contract

Preferred input is a redacted aggregate JSON with:

- `browser_history.event_summary.<window>.total_visits`
- `top_domains`
- `category_counts`
- `switch_rate`
- `top_sessions`
- `hour_buckets`
- `filesystem`
- `shell_history`
- `tool_surface`
- `data_source_inventory`

See `references/chronicle-data-contract.md` for the full schema and privacy rules.

## Privacy Rules

Do not read or expose:

- cookies, credentials, tokens, private keys, password managers
- email, messages, private note bodies, chat contents
- full private URLs when domain-level statistics are enough
- raw shell commands containing secrets

Browser visits are behavior events, not exact active screen time. Phrase conclusions as usage-trace signals unless you have a true screen-time source.

## Verification

Run these before publishing changes:

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
rg -n "\\[必填\\]|修复协议" outputs/verify-guizang/index.html outputs/verify-report.html
```

For Codex skill validation, if you have the OpenAI skill-creator helper installed:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## License

This repository is released under the MIT License.

The bundled Guizang/歸藏 template assets are also MIT licensed by `op7418 (歸藏)`. See `THIRD_PARTY_NOTICES.md` and `assets/guizang-ppt/LICENSE`.
