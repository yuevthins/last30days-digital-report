# Chronicle Data Contract

Use this when rendering a last-30-days personal digital report from local usage traces.

## Preferred Input

Prefer a redacted aggregate JSON shaped like:

- `generated_at`
- `data_source_inventory`
- `browser_history.event_summary.{1d,3d,7d,14d,30d}`
- `browser_history.event_summary.<window>.top_domains`
- `browser_history.event_summary.<window>.category_counts`
- `browser_history.event_summary.<window>.switch_rate`
- `browser_history.event_summary.<window>.top_sessions`
- `browser_history.event_summary.<window>.hour_buckets`
- `filesystem[]`
- `shell_history[]`
- `tool_surface`
- optional `deepl`, `hapigo`, `spotlight_recent`, `extensions`, `top_sites`, `bookmarks`

If this schema is absent, adapt carefully but preserve the evidence categories:

1. Attention destinations: browser domains and categories.
2. Fragmentation: unique domains, switches, sessions, tab/page churn.
3. AI-tool surface: AI domains, AI CLI commands, installed AI tools.
4. File landing hygiene: Downloads/Desktop/project-root churn.
5. Command hygiene: shell history volume, repeated commands, secret-like patterns.
6. Data boundary: missing or blocked sources.

## Privacy Rules

Do not read or expose:

- cookies, credentials, tokens, private keys, password managers
- email, messages, private note bodies, chat contents
- full private URLs when domain-level statistics are enough
- raw shell commands containing secrets

If raw evidence contains sensitive path names or labels, redact them before display. It is acceptable to show aggregate counts such as `secret_like_lines=33`, but not the underlying secret text.

## Evidence Weighting

Borrow the `last30days` idea: stronger signals are repeated, recent, cross-source, and behavior-backed.

- High weight: repeated 7d/30d patterns, high switch rate, late-night buckets, repeated Downloads churn, repeated AI-tool entries, source categories that agree with the written report.
- Medium weight: one profile's top domains, one long session, one install list.
- Low weight: single-source anecdotes, old files, isolated commands, inferred intent.

Never equate browser visits with exact active screen time. Phrase it as "visits/events" or "usage trace signals".

## Standard Risk Axes

- `attention_sink`: social feeds, video, shopping, distraction domains.
- `ai_fragmentation`: too many AI tools or AI domains in one window.
- `context_switching`: switch rate, unique domains, long mixed sessions.
- `late_night_drift`: 22:00-03:00 and 00:00-03:00 browsing share.
- `landing_debt`: Downloads/Desktop/project roots with high recent churn.
- `command_debt`: repeated shell operations, long commands, secret-like history.
- `source_coverage`: what data is missing, blocked, or intentionally excluded.

## Completion Gate

A report is not complete unless it includes:

- data boundary
- at least five evidence cards
- ranked risks
- social-share module
- concrete today/7-day/30-day action advice
- generated HTML file path
