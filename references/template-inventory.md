# Template Inventory

This skill has two output surfaces. Do not treat generated local reports as reusable templates.

## 1. Deterministic Report Renderer

Script:

- `scripts/render_personal_digital_report.py`

Report modes:

- `editorial`
- `xhs-card`
- `command-center`
- `radar`
- `minimal`

Use this when the user wants a complete offline HTML report from aggregate JSON. These are renderer modes, not bundled visual template assets.

## 2. Guizang Magazine Web PPT Template Kit

Scaffold script:

- `scripts/scaffold_guizang_deck.py`

Assets:

- `assets/guizang-ppt/template.html`
- `assets/guizang-ppt/motion.min.js`
- `assets/guizang-ppt/LICENSE`

References:

- `references/guizang-ppt-layouts.md`: 10 slide layouts.
- `references/guizang-ppt-themes.md`: 5 themes.
- `references/guizang-ppt-components.md`: component guide.
- `references/guizang-ppt-checklist.md`: QA checklist.
- `references/guizang-ppt-integration.md`: Chronicle-to-Guizang mapping.

Use this when the user wants a horizontal swipe deck, presentation, `网页 PPT`, or `歸藏` style output. This is the only bundled reusable visual template system in the skill.

## Non-Release Materials

Generated Chronicle reports, generated social cards, and mockup explorations may exist in local working folders, but they are not part of the published template surface.
