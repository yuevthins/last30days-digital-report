# Release Checklist

Use this checklist before publishing the skill to GitHub.

## Package Shape

- [ ] `SKILL.md` exists and has `name` and `description` frontmatter.
- [ ] `agents/openai.yaml` exists and mentions `$last30days-digital-report` in `default_prompt`.
- [ ] `README.md` explains what the skill does.
- [ ] `INSTALL.md` includes install and update commands.
- [ ] `LICENSE` exists.
- [ ] `THIRD_PARTY_NOTICES.md` exists and references the bundled Guizang assets.
- [ ] `assets/guizang-ppt/template.html` exists as the only bundled reusable visual template.
- [ ] `assets/guizang-ppt/motion.min.js` exists for offline deck playback.
- [ ] `assets/examples/sample_usage_summary.json` exists for repeatable smoke tests.
- [ ] `assets/examples/sample-report.html` exists as a generated report example.
- [ ] `assets/examples/sample-report.share-copy.md` exists as the paired generated share-copy example.
- [ ] User-specific Chronicle HTML reports, generated social cards, and mockup scripts are not staged for release.

## Commands

```bash
python3 -m py_compile scripts/render_personal_digital_report.py scripts/scaffold_guizang_deck.py
python3 scripts/render_personal_digital_report.py \
  --input assets/examples/sample_usage_summary.json \
  --output assets/examples/sample-report.html \
  --template editorial \
  --window 30d
python3 scripts/scaffold_guizang_deck.py \
  --output outputs/verify-guizang \
  --title "Verify Guizang Deck" \
  --theme indigo
rg -n "\\[必填\\]|修复协议" assets/examples/sample-report.html outputs/verify-guizang/index.html
```

The final `rg` command should return no matches.

If available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## GitHub Publishing

Recommended repository name:

```text
last30days-digital-report
```

Recommended description:

```text
Codex skill for Chronicle-style computer usage diagnosis, action advice, and Guizang magazine-web-ppt decks.
```

After pushing, verify the GitHub page shows:

- README rendered.
- `SKILL.md` visible.
- `assets/guizang-ppt/template.html` present.
- `INSTALL.md` present.
- `THIRD_PARTY_NOTICES.md` present.
