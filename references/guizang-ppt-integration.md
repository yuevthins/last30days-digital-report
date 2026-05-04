# Guizang PPT Integration

This skill bundles the local `guizang-ppt-skill` template kit so agents can build Chronicle-style reports as magazine-like horizontal HTML decks without relying on another skill being visible. Guizang/歸藏 is the only bundled reusable visual template system in this skill.

## Bundled Files

- `assets/guizang-ppt/template.html`: single-file horizontal swipe deck seed.
- `assets/guizang-ppt/motion.min.js`: local Motion One module used by the deck template.
- `assets/guizang-ppt/LICENSE`: upstream license for the bundled template assets.
- `references/guizang-ppt-layouts.md`: all 10 Guizang slide layout skeletons.
- `references/guizang-ppt-themes.md`: all 5 Guizang theme presets.
- `references/guizang-ppt-components.md`: component and class usage guide.
- `references/guizang-ppt-checklist.md`: quality checklist.

## When To Use This Mode

Use the Guizang deck mode when the user asks for:

- `歸藏`, `guizang`, `杂志风 PPT`, `横向翻页`, `horizontal swipe deck`, `电子杂志`, or `网页 PPT`.
- A share/presentation version of a Chronicle or Last30Days diagnosis.
- A stronger visual artifact than the default report renderer.

Use the normal renderer when the user asks for a plain HTML report, printable memo, or multiple report modes.

## Scaffold Command

```bash
python3 /path/to/last30days-digital-report/scripts/scaffold_guizang_deck.py \
  --output /path/to/output/deck \
  --title "Chronicle 电脑使用整顿报告" \
  --theme ink
```

If `--output` is a directory, the script writes `index.html`. It also creates `assets/motion.min.js` and `images/` next to the deck because the Guizang template imports `./assets/motion.min.js`.

Theme choices:

- `ink`: 墨水经典
- `indigo`: 靛蓝瓷
- `forest`: 森林墨
- `kraft`: 牛皮纸
- `dune`: 沙丘

## Chronicle Report Mapping

Map Chronicle/Last30Days content into the 10 Guizang layouts like this:

| Report Section | Guizang Layout |
|---|---|
| Share headline / top diagnosis | Layout 1: 开场封面 |
| Data-source boundary | Layout 3: 数据大字报 or Layout 10: 图文混排 |
| Focus score / top metrics | Layout 3: 数据大字报 |
| Risk ranking | Layout 9: 并列对比 or Layout 10: 图文混排 |
| Top domains / behavior categories | Layout 3: 数据大字报 |
| High-switch sessions | Layout 6: 两列流水线 or Layout 9: 并列对比 |
| AI tool triage | Layout 6: Pipeline |
| Action advice | Layout 6: Pipeline, Layout 7: 悬念收束, or Layout 8: 大引用 |
| Evidence boundary / privacy note | Layout 10: 图文混排 |
| Ending quote | Layout 8: 大引用页 |

## Required Preflight

Before writing slides:

1. Read `references/guizang-ppt-layouts.md`.
2. Read `references/guizang-ppt-themes.md` and choose exactly one preset.
3. Read `assets/guizang-ppt/template.html` enough to confirm required classes exist.
4. Write a theme rhythm table: every slide must be `hero dark`, `hero light`, `dark`, or `light`.
5. Keep the source boundary visible: browser visits are behavior events, not exact screen time.

## Quality Gate

After writing the deck:

```bash
rg -n "\\[必填\\]|修复协议" /path/to/output/index.html
rg -n "class=\"slide" /path/to/output/index.html
```

Then inspect the HTML in a browser. If the page looks like unstyled defaults, the class preflight failed. If the deck feels flat, the theme rhythm probably has too many consecutive light pages.
