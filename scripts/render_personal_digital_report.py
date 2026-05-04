#!/usr/bin/env python3
"""Render a shareable personal digital-usage report from aggregate JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import re
from pathlib import Path
from typing import Any


TEMPLATES = ("editorial", "xhs-card", "command-center", "radar", "minimal")

THEMES = {
    "editorial": {
        "label": "Editorial Diagnosis",
        "bg": "#f7f2e8",
        "surface": "#fffaf0",
        "surface2": "#efe6d7",
        "ink": "#171513",
        "muted": "#665e53",
        "line": "#d7cab9",
        "accent": "#d83a24",
        "accent2": "#245bd6",
        "accent3": "#087f69",
        "hero": "#171513",
        "hero_ink": "#fffaf0",
    },
    "xhs-card": {
        "label": "XHS Card Report",
        "bg": "#fff7f1",
        "surface": "#ffffff",
        "surface2": "#ffe7dc",
        "ink": "#191413",
        "muted": "#6b5b55",
        "line": "#f0c8bb",
        "accent": "#f04438",
        "accent2": "#111827",
        "accent3": "#0f9f7a",
        "hero": "#f04438",
        "hero_ink": "#fffdf8",
    },
    "command-center": {
        "label": "Command Center",
        "bg": "#111111",
        "surface": "#1b1b1b",
        "surface2": "#26231f",
        "ink": "#f7f0df",
        "muted": "#b9ad9b",
        "line": "#3a352e",
        "accent": "#f0b429",
        "accent2": "#37d6b0",
        "accent3": "#ff5c8a",
        "hero": "#f7f0df",
        "hero_ink": "#111111",
    },
    "radar": {
        "label": "Risk Radar",
        "bg": "#f5f7f2",
        "surface": "#ffffff",
        "surface2": "#e7efe3",
        "ink": "#16201b",
        "muted": "#536158",
        "line": "#c8d7cf",
        "accent": "#1b8a5a",
        "accent2": "#d74b2f",
        "accent3": "#245bd6",
        "hero": "#16201b",
        "hero_ink": "#f8fff8",
    },
    "minimal": {
        "label": "Minimal Print",
        "bg": "#f9f9f6",
        "surface": "#ffffff",
        "surface2": "#ededE7".lower(),
        "ink": "#181818",
        "muted": "#64645f",
        "line": "#d6d6cf",
        "accent": "#111111",
        "accent2": "#3166d6",
        "accent3": "#b05a00",
        "hero": "#ffffff",
        "hero_ink": "#181818",
    },
}

AI_DOMAINS = {
    "chatgpt.com",
    "claude.ai",
    "gemini.google.com",
    "grok.com",
    "kimi.com",
    "chat.b.ai",
    "platform.deepseek.com",
    "auth.openai.com",
    "platform.xiaomimimo.com",
    "lovart.ai",
    "youmind.com",
}

SOCIAL_DOMAINS = {
    "x.com",
    "t.co",
    "twitter.com",
    "youtube.com",
    "tiktok.com",
    "xiaohongshu.com",
    "school.xiaohongshu.com",
    "bilibili.com",
    "pinterest.com",
    "producthunt.com",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(part: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 1)


def fmt_int(value: Any) -> str:
    return f"{as_int(value):,}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text.strip()).strip("-")
    return slug[:80] or "last30days-digital-report"


def list_pairs(value: Any) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    if not isinstance(value, list):
        return pairs
    for item in value:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            pairs.append((str(item[0]), as_int(item[1])))
    return pairs


def category_count(window_data: dict[str, Any], key: str) -> int:
    for name, count in list_pairs(window_data.get("category_counts")):
        if name == key:
            return count
    return 0


def find_first_dict(items: Any, predicate) -> dict[str, Any]:
    if not isinstance(items, list):
        return {}
    for item in items:
        if isinstance(item, dict) and predicate(item):
            return item
    return {}


def source_boundary(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    inventory = data.get("data_source_inventory", {})
    analyzed: list[str] = []
    blocked: list[str] = []

    if inventory.get("browser_history_files_discovered"):
        analyzed.append(f"{len(inventory.get('browser_history_files_discovered', []))} browser history files")
    if inventory.get("bookmarks_files_discovered"):
        analyzed.append(f"{len(inventory.get('bookmarks_files_discovered', []))} bookmark files")
    if inventory.get("top_sites_files_discovered"):
        analyzed.append(f"{len(inventory.get('top_sites_files_discovered', []))} top-sites files")
    if "shell_history" in data:
        analyzed.append("shell history aggregate")
    if "filesystem" in data:
        analyzed.append("filesystem metadata")
    if "tool_surface" in data:
        analyzed.append("installed tool surface")
    if "deepl" in data:
        analyzed.append("DeepL aggregate")
    if "hapigo" in data:
        analyzed.append("HapiGo aggregate")

    knowledge_db = inventory.get("knowledge_db")
    if isinstance(knowledge_db, dict) and knowledge_db.get("read_status"):
        blocked.append(f"Knowledge DB: {knowledge_db.get('read_status')}")

    if not analyzed:
        analyzed.append("aggregate JSON fields available in the input file")
    if not blocked:
        blocked.append("No blocked source declared in the input JSON")

    return analyzed, blocked


def derive(data: dict[str, Any], window: str) -> dict[str, Any]:
    events = data.get("browser_history", {}).get("event_summary", {})
    if window not in events:
        available = ", ".join(sorted(events.keys())) or "none"
        raise SystemExit(f"ERROR: window {window!r} not found. Available windows: {available}")

    w = events.get(window, {})
    total = as_int(w.get("total_visits"))
    top_domains = list_pairs(w.get("top_domains"))
    categories = list_pairs(w.get("category_counts"))
    sessions = as_int(w.get("sessions"))
    switches = as_int(w.get("switches"))
    switch_rate = as_float(w.get("switch_rate")) * 100
    hour_buckets = w.get("hour_buckets") if isinstance(w.get("hour_buckets"), dict) else {}

    social = category_count(w, "social_feeds")
    ai = category_count(w, "ai_tools")
    dev_ops = category_count(w, "dev_ops")
    knowledge = category_count(w, "knowledge_docs")
    design_ref = category_count(w, "design_ref")
    shopping = category_count(w, "shopping")
    search = category_count(w, "search")
    late_22_03 = as_int(hour_buckets.get("22_03"))
    late_00_03 = as_int(hour_buckets.get("00_03"))

    downloads = find_first_dict(data.get("filesystem"), lambda item: str(item.get("path", "")).endswith("/Downloads"))
    desktop = find_first_dict(data.get("filesystem"), lambda item: str(item.get("path", "")).endswith("/Desktop"))
    shell = data.get("shell_history", [{}])
    shell0 = shell[0] if isinstance(shell, list) and shell and isinstance(shell[0], dict) else {}
    tool_surface = data.get("tool_surface", {}) if isinstance(data.get("tool_surface"), dict) else {}

    ai_domain_hits = [(d, c) for d, c in top_domains if d in AI_DOMAINS or "ai" in d or "openai" in d]
    social_domain_hits = [(d, c) for d, c in top_domains if d in SOCIAL_DOMAINS]

    social_pct = pct(social, total)
    ai_pct = pct(ai, total)
    night_pct = pct(late_22_03, total)
    deep_night_pct = pct(late_00_03, total)
    downloads_recent_30d = as_int(downloads.get("recent_files_30d"))
    downloads_files = as_int(downloads.get("files"))
    shell_secret_like = as_int(shell0.get("secret_like_lines"))
    shell_ai_cli = as_int(shell0.get("ai_cli_lines"))
    npm_global_count = as_int(tool_surface.get("npm_global_count"))

    focus_score = 100
    focus_score -= min(24, social_pct * 0.9)
    focus_score -= min(18, ai_pct * 0.65)
    focus_score -= min(22, switch_rate * 0.75)
    focus_score -= min(16, night_pct * 0.38)
    focus_score -= min(10, downloads_recent_30d / 80)
    focus_score -= min(10, shell_secret_like * 0.35)
    focus_score = max(8, min(96, round(focus_score)))

    risks = [
        {
            "id": "attention_sink",
            "name": "信息流黑洞",
            "score": social_pct * 1.6 + sum(c for _, c in social_domain_hits[:4]) / max(total, 1) * 200,
            "metric": f"{fmt_int(social)} social-feed visits / {window}",
            "detail": "社交与视频入口在工作流里太靠前，容易把卡住变成继续刷资料。",
        },
        {
            "id": "ai_fragmentation",
            "name": "AI 工具试吃",
            "score": ai_pct * 1.4
            + sum(c for _, c in ai_domain_hits[:6]) / max(total, 1) * 130
            + min(12, len(ai_domain_hits) * 1.6)
            + min(6, shell_ai_cli / 30),
            "metric": f"{fmt_int(ai)} AI-tool visits, {len(ai_domain_hits)} AI domains",
            "detail": "AI 入口数量过多时，任务会从交付转成换工具和比模型。",
        },
        {
            "id": "context_switching",
            "name": "上下文切换",
            "score": switch_rate * 1.15 + min(18, as_int(w.get("unique_domains")) / 32),
            "metric": f"{fmt_pct(switch_rate)} switch rate, {fmt_int(w.get('unique_domains'))} domains",
            "detail": "域名切换和混合会话越高，越难形成稳定判断和可复用产物。",
        },
        {
            "id": "late_night_drift",
            "name": "深夜漂移",
            "score": night_pct * 1.05 + deep_night_pct * 0.55,
            "metric": f"{fmt_int(late_22_03)} visits from 22:00-03:00",
            "detail": "深夜适合收尾，不适合开新工具、新配置和大范围整理。",
        },
        {
            "id": "landing_debt",
            "name": "落盘债务",
            "score": min(38, downloads_recent_30d / 24) + min(16, downloads_files / 900),
            "metric": f"{fmt_int(downloads_recent_30d)} recent Downloads files in 30d",
            "detail": "下载和项目入口越散，每次开工前的找版本、找路径成本越高。",
        },
        {
            "id": "command_debt",
            "name": "终端债务",
            "score": min(24, shell_secret_like * 0.65) + min(12, as_int(shell0.get("long_lines_over_160")) / 10),
            "metric": f"{fmt_int(shell_secret_like)} secret-like shell-history lines",
            "detail": "终端适合执行，不适合当长期记忆或密钥暂存地。",
        },
    ]
    risks = sorted(risks, key=lambda item: item["score"], reverse=True)

    top_risk = risks[0]
    diagnosis = diagnosis_sentence(top_risk["id"], focus_score)
    share_headline = share_headline_for(top_risk["id"], focus_score)

    evidence_cards = [
        ("访问事件", fmt_int(total), f"{window} browser events"),
        ("唯一域名", fmt_int(w.get("unique_domains")), "attention surface"),
        ("切换率", fmt_pct(switch_rate), f"{fmt_int(switches)} switches"),
        ("AI 工具", fmt_int(ai), f"{fmt_pct(ai_pct)} of visits"),
        ("信息流", fmt_int(social), f"{fmt_pct(social_pct)} of visits"),
        ("深夜段", fmt_int(late_22_03), f"{fmt_pct(night_pct)} from 22-03"),
        ("Downloads", fmt_int(downloads_files), f"{fmt_int(downloads_recent_30d)} recent 30d"),
        ("Shell 风险", fmt_int(shell_secret_like), "secret-like patterns"),
    ]

    actions_today = [
        "写一个当前任务状态文件，包含目标、产物路径、下一步。",
        "工作块内只保留资料源、目标产物、执行工具三类页面。",
        "45 分钟内只允许一个主 AI；想换工具必须先写失败证据。",
        "把 Downloads 当天新增内容分成删除、归项目、入资料库。",
    ]
    actions_7d = [
        "建立信息流窗口：12:30-12:50 和 21:30-21:50，其余时间屏蔽。",
        "把重复 3 次以上的终端命令落成脚本或文档。",
        "给高频项目补 `STATUS.md`，每天只更新一个事实状态。",
        "把 AI 工具固定分工，减少中途试吃。",
    ]
    actions_30d = [
        "每周生成一次本报告，比较切换率、信息流占比、AI 占比、Downloads 增量。",
        "维护一个入口账本：每个新项目必须有唯一根目录和状态文件。",
        "轮换已进入历史的敏感 token，并把密钥输入迁移到 Keychain 或专用配置。",
    ]

    analyzed, blocked = source_boundary(data)
    return {
        "generated_at": data.get("generated_at") or dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "window": window,
        "window_data": w,
        "total": total,
        "top_domains": top_domains,
        "categories": categories,
        "top_sessions": w.get("top_sessions") if isinstance(w.get("top_sessions"), list) else [],
        "focus_score": focus_score,
        "diagnosis": diagnosis,
        "share_headline": share_headline,
        "risks": risks,
        "evidence_cards": evidence_cards,
        "actions_today": actions_today,
        "actions_7d": actions_7d,
        "actions_30d": actions_30d,
        "analyzed": analyzed,
        "blocked": blocked,
        "downloads": downloads,
        "desktop": desktop,
        "shell": shell0,
        "tool_surface": tool_surface,
        "social_pct": social_pct,
        "ai_pct": ai_pct,
        "night_pct": night_pct,
        "deep_night_pct": deep_night_pct,
        "switch_rate": switch_rate,
        "sessions": sessions,
        "switches": switches,
        "dev_ops": dev_ops,
        "knowledge": knowledge,
        "design_ref": design_ref,
        "shopping": shopping,
        "search": search,
    }


def diagnosis_sentence(top_risk_id: str, focus_score: int) -> str:
    if top_risk_id == "attention_sink":
        return "你的电脑不是缺信息，而是信息流入口太靠前，正在抢走收束能力。"
    if top_risk_id == "ai_fragmentation":
        return "你不是缺 AI 工具，而是 AI 入口过多，把完成任务拖成了模型试吃。"
    if top_risk_id == "context_switching":
        return "你看起来很忙，但上下文切换太密，很多工作块没有沉到产物里。"
    if top_risk_id == "late_night_drift":
        return "你的深夜不是高效加班，而是最容易开新坑和乱配置的危险时段。"
    if top_risk_id == "landing_debt":
        return "资料不是少，而是入口太散，找路径和找版本已经变成隐形成本。"
    if top_risk_id == "command_debt":
        return "终端正在承担太多临时记忆，效率问题已经碰到安全边界。"
    return f"本轮专注分约 {focus_score}/100，最大问题是收束机制不够硬。"


def share_headline_for(top_risk_id: str, focus_score: int) -> str:
    mapping = {
        "attention_sink": "过去 30 天，我的电脑告诉我：最大黑洞不是忙，是信息流。",
        "ai_fragmentation": "我以为自己在用 AI 提效，数据说我在不停试吃工具。",
        "context_switching": "一个月的使用记录暴露了真问题：忙，不等于推进。",
        "late_night_drift": "深夜电脑记录比自律打卡诚实：很多混乱从 00:30 后开始。",
        "landing_debt": "Downloads 和项目入口，正在吞掉我每天开工前的专注。",
        "command_debt": "终端历史提醒我：临时命令太多时，效率和安全都会下滑。",
    }
    return mapping.get(top_risk_id, f"过去 30 天，我的电脑专注分只有 {focus_score}/100。")


def render_bar(label: str, value: int, max_value: int, detail: str = "") -> str:
    width = 0 if max_value <= 0 else max(4, min(100, round(value / max_value * 100)))
    return (
        '<div class="bar-row">'
        f'<div class="bar-label"><span>{esc(label)}</span><b>{fmt_int(value)}</b></div>'
        f'<div class="bar-track"><i style="width:{width}%"></i></div>'
        f'<div class="bar-detail">{esc(detail)}</div>'
        "</div>"
    )


def css_for(template: str) -> str:
    t = THEMES[template]
    density_class = "compact" if template in {"command-center", "minimal"} else "expressive"
    radius = "4px" if template == "minimal" else "8px"
    return f"""
    :root {{
      --bg: {t['bg']};
      --surface: {t['surface']};
      --surface2: {t['surface2']};
      --ink: {t['ink']};
      --muted: {t['muted']};
      --line: {t['line']};
      --accent: {t['accent']};
      --accent2: {t['accent2']};
      --accent3: {t['accent3']};
      --hero: {t['hero']};
      --hero-ink: {t['hero_ink']};
      --radius: {radius};
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(90,90,90,.055) 1px, transparent 1px),
        linear-gradient(180deg, rgba(90,90,90,.045) 1px, transparent 1px),
        var(--bg);
      background-size: 28px 28px;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
      line-height: 1.5;
      letter-spacing: 0;
    }}
    a {{ color: inherit; }}
    .page {{
      width: min(1420px, calc(100% - 40px));
      margin: 0 auto;
      padding: 26px 0 72px;
    }}
    .topline {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 0 0 16px;
      border-bottom: 2px solid var(--ink);
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
    }}
    .hero {{
      min-height: {"72vh" if template != "xhs-card" else "86vh"};
      display: grid;
      grid-template-columns: minmax(0, 1.08fr) minmax(380px, .92fr);
      gap: 28px;
      padding: 34px 0 38px;
      border-bottom: 3px solid var(--ink);
    }}
    .hero-copy {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 28px;
    }}
    .kicker {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .kicker:before {{
      content: "";
      width: 42px;
      height: 4px;
      background: var(--accent);
    }}
    h1 {{
      margin: 18px 0 20px;
      max-width: 930px;
      font-size: clamp({"44px" if template == "minimal" else "54px"}, 7.8vw, {"98px" if density_class == "compact" else "116px"});
      line-height: .92;
      font-weight: 950;
      letter-spacing: 0;
    }}
    .lede {{
      max-width: 860px;
      margin: 0;
      font-size: clamp(20px, 2.2vw, 32px);
      line-height: 1.24;
      font-weight: 820;
    }}
    .lede strong {{ color: var(--accent); }}
    .source-note {{
      max-width: 860px;
      color: var(--muted);
      font-size: 14px;
      margin: 0;
    }}
    .hero-panel {{
      background: var(--hero);
      color: var(--hero-ink);
      border-radius: var(--radius);
      border: 1px solid var(--line);
      min-height: 600px;
      padding: 24px;
      display: grid;
      grid-template-rows: auto 1fr auto;
      overflow: hidden;
      box-shadow: 0 24px 70px rgba(0,0,0,.14);
    }}
    .panel-head, .panel-foot {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      opacity: .72;
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
    }}
    .score {{
      align-self: center;
    }}
    .score-number {{
      font-size: clamp(82px, 10vw, 156px);
      line-height: .86;
      font-weight: 950;
    }}
    .score-label {{
      max-width: 540px;
      margin-top: 14px;
      opacity: .74;
      font-size: 15px;
      font-weight: 720;
    }}
    .evidence-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 26px;
    }}
    .evidence-item {{
      min-height: 106px;
      border: 1px solid color-mix(in srgb, var(--hero-ink) 22%, transparent);
      background: color-mix(in srgb, var(--hero-ink) 8%, transparent);
      border-radius: var(--radius);
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .evidence-item b {{
      font-size: clamp(30px, 4vw, 44px);
      line-height: 1;
      font-weight: 950;
    }}
    .evidence-item span {{
      opacity: .70;
      font-size: 12px;
      font-weight: 760;
    }}
    section {{
      padding: 42px 0;
      border-bottom: 1px solid var(--line);
    }}
    .section-head {{
      display: grid;
      grid-template-columns: minmax(240px, .34fr) minmax(0, .66fr);
      gap: 24px;
      margin-bottom: 22px;
    }}
    h2 {{
      margin: 0;
      font-size: clamp(28px, 3.4vw, 54px);
      line-height: 1;
      letter-spacing: 0;
    }}
    .section-head p {{
      margin: 0;
      color: var(--muted);
      font-size: 17px;
      max-width: 800px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
      min-height: 160px;
    }}
    .card h3 {{
      margin: 0 0 10px;
      font-size: 19px;
      line-height: 1.15;
    }}
    .card .metric {{
      font-size: 34px;
      line-height: 1;
      font-weight: 950;
      color: var(--accent);
      margin: 12px 0 8px;
    }}
    .card p, .card li {{
      color: var(--muted);
      font-size: 14px;
      margin: 0;
    }}
    .risk-list {{
      display: grid;
      gap: 10px;
    }}
    .risk {{
      display: grid;
      grid-template-columns: 52px minmax(0, .7fr) minmax(220px, .3fr);
      gap: 16px;
      align-items: stretch;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 14px;
    }}
    .rank {{
      width: 52px;
      height: 52px;
      display: grid;
      place-items: center;
      background: var(--accent);
      color: white;
      border-radius: var(--radius);
      font-weight: 950;
      font-size: 20px;
    }}
    .risk h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .risk p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .risk-meta {{
      border-left: 1px solid var(--line);
      padding-left: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: var(--muted);
      font-size: 13px;
      font-weight: 760;
    }}
    .bars {{ display: grid; gap: 12px; }}
    .bar-row {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 12px;
    }}
    .bar-label {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-weight: 850;
      margin-bottom: 8px;
    }}
    .bar-track {{
      height: 14px;
      background: var(--surface2);
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid var(--line);
    }}
    .bar-track i {{
      display: block;
      height: 100%;
      background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
    }}
    .bar-detail {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
    }}
    .protocol {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .protocol ol {{
      margin: 12px 0 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    .protocol li {{ margin: 8px 0; }}
    .share {{
      display: grid;
      grid-template-columns: minmax(320px, .45fr) minmax(0, .55fr);
      gap: 18px;
      align-items: stretch;
    }}
    .cover {{
      aspect-ratio: 4 / 5;
      background: var(--hero);
      color: var(--hero-ink);
      border-radius: var(--radius);
      border: 1px solid var(--line);
      padding: 26px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 520px;
    }}
    .cover h3 {{
      margin: 0;
      font-size: clamp(34px, 5vw, 68px);
      line-height: .96;
      letter-spacing: 0;
    }}
    .cover b {{
      font-size: clamp(72px, 10vw, 132px);
      line-height: .85;
    }}
    .captions {{
      display: grid;
      gap: 10px;
    }}
    .caption {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 16px;
      font-size: 15px;
      color: var(--muted);
    }}
    .caption strong {{ color: var(--ink); }}
    .boundary {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .boundary ul {{
      margin: 12px 0 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    .footer {{
      padding-top: 26px;
      color: var(--muted);
      font-size: 12px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
    }}
    @media (max-width: 900px) {{
      .page {{ width: min(100% - 24px, 760px); }}
      .hero, .section-head, .share, .boundary {{ grid-template-columns: 1fr; }}
      .hero-panel {{ min-height: 520px; }}
      .cards, .protocol {{ grid-template-columns: 1fr; }}
      .risk {{ grid-template-columns: 46px minmax(0, 1fr); }}
      .risk-meta {{ grid-column: 2; border-left: 0; padding-left: 0; border-top: 1px solid var(--line); padding-top: 10px; }}
      .cover {{ min-height: 460px; }}
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ width: 100%; padding: 0; }}
      .hero {{ min-height: auto; }}
      .card, .risk, .bar-row, .cover, .hero-panel {{ break-inside: avoid; box-shadow: none; }}
    }}
    """


def render_html(payload: dict[str, Any], template: str, title: str, name: str, source_name: str) -> str:
    theme = THEMES[template]
    top_domains = payload["top_domains"][:10]
    categories = payload["categories"][:9]
    max_domain = max([c for _, c in top_domains] or [1])
    max_category = max([c for _, c in categories] or [1])
    score = payload["focus_score"]
    generated_date = esc(payload["generated_at"])
    report_title = title or f"{name} Last30Days 个人数字化报告"
    og_desc = payload["diagnosis"]

    evidence_html = "".join(
        f'<div class="evidence-item"><b>{esc(value)}</b><span>{esc(label)} · {esc(detail)}</span></div>'
        for label, value, detail in payload["evidence_cards"]
    )
    risk_html = "\n".join(
        f"""
        <article class="risk">
          <div class="rank">{idx}</div>
          <div>
            <h3>{esc(risk['name'])}</h3>
            <p>{esc(risk['detail'])}</p>
          </div>
          <div class="risk-meta">
            <span>{esc(risk['metric'])}</span>
            <span>risk signal {round(as_float(risk['score']), 1)}</span>
          </div>
        </article>
        """.strip()
        for idx, risk in enumerate(payload["risks"], start=1)
    )
    domain_bars = "\n".join(render_bar(domain, count, max_domain, "top domain") for domain, count in top_domains)
    category_bars = "\n".join(render_bar(cat, count, max_category, "behavior category") for cat, count in categories)

    session_cards = ""
    for session in payload["top_sessions"][:6]:
        if not isinstance(session, dict):
            continue
        session_cards += (
            '<article class="card">'
            f"<h3>{esc(session.get('start'))} -> {esc(session.get('end'))}</h3>"
            f"<div class='metric'>{fmt_int(session.get('minutes'))}m</div>"
            f"<p>{fmt_int(session.get('visits'))} visits · {fmt_int(session.get('switches'))} switches · "
            f"{fmt_int(session.get('unique_domains'))} domains</p>"
            "</article>"
        )

    protocol_html = (
        protocol_block("今天", payload["actions_today"])
        + protocol_block("7 天", payload["actions_7d"])
        + protocol_block("30 天", payload["actions_30d"])
    )
    analyzed = "".join(f"<li>{esc(item)}</li>" for item in payload["analyzed"])
    blocked = "".join(f"<li>{esc(item)}</li>" for item in payload["blocked"])
    captions = social_captions(payload)
    captions_html = "".join(f'<div class="caption">{caption}</div>' for caption in captions)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{esc(og_desc)}" />
  <meta property="og:title" content="{esc(payload['share_headline'])}" />
  <meta property="og:description" content="{esc(og_desc)}" />
  <meta property="og:type" content="article" />
  <meta name="twitter:card" content="summary_large_image" />
  <title>{esc(report_title)} · {esc(theme['label'])}</title>
  <style>{css_for(template)}</style>
</head>
<body class="template-{esc(template)}">
  <main class="page">
    <div class="topline">
      <span>{esc(theme['label'])}</span>
      <span>{esc(payload['window'])} · source: {esc(source_name)}</span>
    </div>

    <header class="hero">
      <div class="hero-copy">
        <div>
          <div class="kicker">Personal Digital Trace Report</div>
          <h1>{esc(payload['share_headline'])}</h1>
          <p class="lede"><strong>结论：</strong>{esc(payload['diagnosis'])}</p>
        </div>
        <p class="source-note">生成时间：{generated_date}。本报告只使用聚合统计和脱敏元数据，不读取 cookie、私钥、密码、聊天正文或邮件正文。浏览器 visits 是行为事件，不等于精确屏幕时长。</p>
      </div>
      <aside class="hero-panel">
        <div class="panel-head"><span>Focus Score</span><span>{esc(payload['window'])}</span></div>
        <div class="score">
          <div class="score-number">{score}</div>
          <div class="score-label">不是道德评分，而是基于信息流占比、AI 工具占比、切换率、深夜段和落盘债务估算出的收束压力。</div>
          <div class="evidence-grid">{evidence_html}</div>
        </div>
        <div class="panel-foot"><span>{fmt_int(payload['sessions'])} sessions</span><span>{fmt_int(payload['switches'])} switches</span></div>
      </aside>
    </header>

    <section>
      <div class="section-head">
        <h2>风险排序</h2>
        <p>排序来自可重复行为信号，而不是泛泛建议。越靠前，越应该先加硬规则。</p>
      </div>
      <div class="risk-list">{risk_html}</div>
    </section>

    <section>
      <div class="section-head">
        <h2>域名与类别</h2>
        <p>这部分是 last30days 风格的"群众投票"转译：不是别人投票，而是你的电脑使用行为在投票。</p>
      </div>
      <div class="cards">
        <article class="card">
          <h3>信息流占比</h3>
          <div class="metric">{fmt_pct(payload['social_pct'])}</div>
          <p>社交、视频、内容流入口的访问事件占比。</p>
        </article>
        <article class="card">
          <h3>AI 占比</h3>
          <div class="metric">{fmt_pct(payload['ai_pct'])}</div>
          <p>AI 工具相关入口访问事件占比。高不一定坏，问题是没有固定分工。</p>
        </article>
        <article class="card">
          <h3>深夜段</h3>
          <div class="metric">{fmt_pct(payload['night_pct'])}</div>
          <p>22:00-03:00 的访问事件占比，重点看是否在开新坑。</p>
        </article>
      </div>
      <div style="height:18px"></div>
      <div class="cards">
        <div class="card" style="grid-column: span 2;"><h3>Top domains</h3><div class="bars">{domain_bars}</div></div>
        <div class="card"><h3>Behavior categories</h3><div class="bars">{category_bars}</div></div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>高切换会话</h2>
        <p>长会话不等于深度工作。真正要看的是访问量、切换数和唯一域名是否同时升高。</p>
      </div>
      <div class="cards">{session_cards}</div>
    </section>

    <section>
      <div class="section-head">
        <h2>行动建议</h2>
        <p>目标不是更努力，而是把"继续找、继续试、继续开页面"强制改成"落到文件、状态和下一步"。</p>
      </div>
      <div class="protocol">{protocol_html}</div>
    </section>

    <section>
      <div class="section-head">
        <h2>社交传播包</h2>
        <p>这个模块用于截图、发小红书、朋友圈、飞书群或内部复盘。传播内容必须带证据边界，避免变成鸡汤。</p>
      </div>
      <div class="share">
        <div class="cover">
          <div>
            <div class="kicker" style="color: currentColor;">Screenshot Cover</div>
            <h3>{esc(payload['share_headline'])}</h3>
          </div>
          <b>{score}</b>
          <p>{esc(payload['diagnosis'])}</p>
        </div>
        <div class="captions">{captions_html}</div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>证据边界</h2>
        <p>这里决定报告可信度。缺失数据不能伪装成已分析数据。</p>
      </div>
      <div class="boundary">
        <article class="card">
          <h3>已纳入</h3>
          <ul>{analyzed}</ul>
        </article>
        <article class="card">
          <h3>缺失 / 被挡 / 不读取</h3>
          <ul>{blocked}<li>不读取 cookie、密码、私钥、邮件、聊天正文和私密正文。</li></ul>
        </article>
      </div>
    </section>

    <footer class="footer">
      <span>Generated by last30days-digital-report · template {esc(template)}</span>
      <span>Self-contained HTML · no external CDN · printable</span>
    </footer>
  </main>
</body>
</html>
"""


def protocol_block(title: str, items: list[str]) -> str:
    lis = "".join(f"<li>{esc(item)}</li>" for item in items)
    return f'<article class="card"><h3>{esc(title)}</h3><ol>{lis}</ol></article>'


def social_captions(payload: dict[str, Any]) -> list[str]:
    top = payload["risks"][0]
    return [
        f"<strong>小红书版：</strong>{esc(payload['share_headline'])} 我把浏览器、AI 工具、Downloads、Shell 历史做了脱敏聚合，最刺痛的一点是：{esc(top['detail'])}",
        f"<strong>朋友圈版：</strong>这份报告不是算命，是电脑行为记录。{esc(top['metric'])}，说明我的下一步不是换工具，而是加收束规则。",
        f"<strong>内部复盘版：</strong>本周先改三个指标：切换率 {fmt_pct(payload['switch_rate'])}、AI 占比 {fmt_pct(payload['ai_pct'])}、信息流占比 {fmt_pct(payload['social_pct'])}。每周复跑一次。",
    ]


def write_share_copy(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Last30Days Digital Report Share Copy",
        "",
        f"## Headline",
        "",
        payload["share_headline"],
        "",
        "## Diagnosis",
        "",
        payload["diagnosis"],
        "",
        "## Captions",
        "",
    ]
    for caption in social_captions(payload):
        clean = re.sub(r"<[^>]+>", "", caption)
        lines.append(f"- {clean}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            "Analyzed:",
        ]
    )
    lines.extend(f"- {item}" for item in payload["analyzed"])
    lines.append("")
    lines.append("Blocked or intentionally excluded:")
    lines.extend(f"- {item}" for item in payload["blocked"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Redacted aggregate usage JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML file, or output directory with --all-templates")
    parser.add_argument("--template", choices=TEMPLATES, default="editorial")
    parser.add_argument("--all-templates", action="store_true", help="Render all five selectable templates")
    parser.add_argument("--window", choices=("1d", "3d", "7d", "14d", "30d"), default="30d")
    parser.add_argument("--name", default="个人", help="Report owner label")
    parser.add_argument("--title", default="", help="Optional HTML title prefix")
    parser.add_argument("--no-share-copy", action="store_true", help="Do not write share-copy markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    payload = derive(data, args.window)
    source_name = args.input.name
    title = args.title or f"{args.name} Last30Days 个人数字化报告"

    written: list[Path] = []
    if args.all_templates:
        args.output.mkdir(parents=True, exist_ok=True)
        for template in TEMPLATES:
            out = args.output / f"{slugify(title)}-{template}.html"
            out.write_text(render_html(payload, template, title, args.name, source_name), encoding="utf-8")
            written.append(out)
        if not args.no_share_copy:
            share_path = args.output / f"{slugify(title)}-share-copy.md"
            write_share_copy(payload, share_path)
            written.append(share_path)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_html(payload, args.template, title, args.name, source_name), encoding="utf-8")
        written.append(args.output)
        if not args.no_share_copy:
            share_path = args.output.with_suffix(".share-copy.md")
            write_share_copy(payload, share_path)
            written.append(share_path)

    print("last30days-digital-report render complete")
    print(f"window: {args.window}")
    print(f"focus_score: {payload['focus_score']}")
    print(f"top_risk: {payload['risks'][0]['name']} - {payload['risks'][0]['metric']}")
    for path in written:
        print(f"wrote: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
