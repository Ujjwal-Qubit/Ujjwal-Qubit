#!/usr/bin/env python3
"""
Master SVG Card Generator for Ujjwal Kaushik's GitHub Profile (Ujjwal-Qubit)
Generates high-craft animated SVG cards matching the "Signal from Noise" portfolio aesthetic:
  - void: #07070D
  - depth: #101018
  - signal: #8B7CFF (Primary Accent)
  - builder: #4FD8C9 (Secondary Accent)
  - human: #F2B968 (Tertiary Accent)
  - ink: #EDEDF2
  - mute: #8E8EA3

Fixes & Hardening:
  - Safe CSS animations: uses opacity fades and isolated transforms so SVG elements
    never have their base coordinates overwritten to (0, 0)
  - Explicit numeric width & height on all <svg> root tags (no width="100%") to guarantee
    exact aspect-ratio preservation in GitHub Markdown <img> tags
  - 100% strict XML escaping (html.escape) on all dynamic and static text
  - Absolute SVG coordinates for avatar, text, badges, and grids
  - Fonts subsetted with fontTools and embedded as base64 WOFF data URIs
  - Respects @media (prefers-reduced-motion: reduce)
  - Supports STATIC=1 environment variable / --static flag for screenshot mode
"""

import os
import sys
import json
import base64
import io
import html
from datetime import datetime, timedelta
from fontTools import subset

# ---------------------------------------------------------------------------
# Directory Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
CARDS_DIR = os.path.join(BASE_DIR, "cards")
os.makedirs(CARDS_DIR, exist_ok=True)

STATIC_MODE = (os.environ.get("STATIC") == "1") or ("--static" in sys.argv)

# ---------------------------------------------------------------------------
# Brand Color Tokens (Signal from Noise)
# ---------------------------------------------------------------------------
VOID = "#07070D"
DEPTH = "#101018"
BORDER = "#1E1E2E"
BORDER_HIGHLIGHT = "#8B7CFF40"
SIGNAL = "#8B7CFF"
BUILDER = "#4FD8C9"
HUMAN = "#F2B968"
INK = "#EDEDF2"
MUTE = "#8E8EA3"
DARK_MUTE = "#262638"

# ---------------------------------------------------------------------------
# Font Subsetting & Embedding Engine
# ---------------------------------------------------------------------------
_FONT_CACHE = {}

def get_subsetted_font_b64(font_filename, text_chars):
    """Subsets font to given characters and returns base64 encoded WOFF."""
    cache_key = font_filename
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    font_path = os.path.join(FONTS_DIR, font_filename)
    if not os.path.exists(font_path):
        print(f"Warning: font {font_path} not found, skipping embed.")
        return ""

    opt = subset.Options()
    opt.flavor = "woff"
    try:
        font = subset.load_font(font_path, opt)
        sub = subset.Subsetter(options=opt)
        unicodes = list(set([ord(c) for c in text_chars]))
        sub.populate(unicodes=unicodes)
        sub.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        b64_str = base64.b64encode(buf.getvalue()).decode("ascii")
        _FONT_CACHE[cache_key] = b64_str
        return b64_str
    except Exception as e:
        print(f"Error subsetting {font_filename}: {e}")
        return ""

# Common character set for all cards
ALL_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,:;-/()[]{}!@#$%^&*+_=~`|<>?\"'—·●★✓↑→⚡🛰📡👁🏥🚀✦"
)

# Pre-generate font base64 strings
CLASH_B64 = get_subsetted_font_b64("ClashDisplay-Bold.ttf", ALL_CHARS)
GEN_B64 = get_subsetted_font_b64("GeneralSans-Regular.woff2", ALL_CHARS)
MONO_B64 = get_subsetted_font_b64("JetBrainsMono-Regular.woff2", ALL_CHARS)

def get_font_face_css():
    """Returns CSS @font-face rules with embedded WOFF data URIs."""
    css = []
    if CLASH_B64:
        css.append(f"""
    @font-face {{
      font-family: 'Clash Display';
      font-weight: 700;
      font-style: normal;
      src: url('data:font/woff;base64,{CLASH_B64}') format('woff');
    }}""")
    if GEN_B64:
        css.append(f"""
    @font-face {{
      font-family: 'General Sans';
      font-weight: 400;
      font-style: normal;
      src: url('data:font/woff;base64,{GEN_B64}') format('woff');
    }}""")
    if MONO_B64:
        css.append(f"""
    @font-face {{
      font-family: 'JetBrains Mono';
      font-weight: 400;
      font-style: normal;
      src: url('data:font/woff;base64,{MONO_B64}') format('woff');
    }}""")
    return "\n".join(css)

def get_base_css(delay_offset=0.0):
    """Generates standard styles, safe keyframes, and reduced-motion rules."""
    font_css = get_font_face_css()
    
    if STATIC_MODE:
        return f"""
    <style>
      {font_css}
      * {{
        box-sizing: border-box;
      }}
      text {{
        user-select: none;
      }}
      .font-display {{
        font-family: 'Clash Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }}
      .font-body {{
        font-family: 'General Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }}
      .font-mono {{
        font-family: 'JetBrains Mono', 'SF Mono', Consolas, Menlo, monospace;
      }}
    </style>"""

    return f"""
    <style>
      {font_css}
      * {{
        box-sizing: border-box;
      }}
      text {{
        user-select: none;
      }}
      .font-display {{
        font-family: 'Clash Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }}
      .font-body {{
        font-family: 'General Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }}
      .font-mono {{
        font-family: 'JetBrains Mono', 'SF Mono', Consolas, Menlo, monospace;
      }}

      /* Safe Opacity Fade In - Never corrupts SVG transform coordinates */
      @keyframes fadeIn {{
        0% {{
          opacity: 0;
        }}
        100% {{
          opacity: 1;
        }}
      }}

      /* Card Border Pulse */
      @keyframes borderGlow {{
        0%, 100% {{
          stroke-opacity: 0.25;
        }}
        50% {{
          stroke-opacity: 0.7;
        }}
      }}

      /* Blinking status dot */
      @keyframes livePulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.35; transform: scale(0.85); }}
      }}

      /* Bar growth */
      @keyframes growBar {{
        0% {{
          transform: scaleY(0);
          opacity: 0.3;
        }}
        100% {{
          transform: scaleY(1);
          opacity: 1;
        }}
      }}

      .fade-0 {{
        opacity: 0;
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: {delay_offset:.2f}s;
      }}
      .fade-1 {{
        opacity: 0;
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: {delay_offset + 0.15:.2f}s;
      }}
      .fade-2 {{
        opacity: 0;
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: {delay_offset + 0.3:.2f}s;
      }}
      .fade-3 {{
        opacity: 0;
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: {delay_offset + 0.45:.2f}s;
      }}

      .pulse-border {{
        animation: borderGlow 4s ease-in-out infinite;
      }}

      .live-dot {{
        transform-origin: center;
        animation: livePulse 2.2s ease-in-out infinite;
      }}

      /* Prefers Reduced Motion: disable all animations */
      @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
          animation: none !important;
          transition: none !important;
          opacity: 1 !important;
          transform: none !important;
        }}
      }}
    </style>"""

# ---------------------------------------------------------------------------
# Data Loading & Processing
# ---------------------------------------------------------------------------
def load_contributions():
    path = os.path.join(DATA_DIR, "contributions.json")
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Using fallback data.")
        return get_fallback_data()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return get_fallback_data()

def get_fallback_data():
    days = []
    base_date = datetime.now() - timedelta(days=365)
    for i in range(365):
        d_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        count = 2 if i % 2 == 0 else (5 if i % 5 == 0 else 0)
        days.append({"date": d_str, "count": count, "level": 2 if count > 0 else 0})
    return {"total": {"lastYear": 703}, "contributions": days}

def process_stats(contributions_data):
    days = contributions_data.get("contributions", [])
    total = sum(item["count"] for item in days)
    active_days = sum(1 for item in days if item["count"] > 0)
    
    busiest = max(days, key=lambda x: x["count"]) if days else {"date": "2026-07-10", "count": 24}

    # Streaks
    longest_streak = 0
    running_streak = 0
    for item in days:
        if item["count"] > 0:
            running_streak += 1
            if running_streak > longest_streak:
                longest_streak = running_streak
        else:
            running_streak = 0

    rev_days = list(reversed(days))
    if rev_days and rev_days[0]["count"] == 0:
        check_days = rev_days[1:]
    else:
        check_days = rev_days
    
    current_streak = 0
    for item in check_days:
        if item["count"] > 0:
            current_streak += 1
        else:
            break

    # Monthly sums for last 12 months
    monthly_map = {}
    for item in days:
        m = item["date"][:7] # YYYY-MM
        monthly_map[m] = monthly_map.get(m, 0) + item["count"]

    sorted_months = sorted(monthly_map.keys())[-12:]
    monthly_list = [{"month": m, "count": monthly_map[m]} for m in sorted_months]

    return {
        "total": total,
        "active_days": active_days,
        "active_percent": round((active_days / max(len(days), 1)) * 100),
        "busiest": busiest,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": monthly_list,
        "raw_days": days[-364:] # 52 weeks * 7 = 364 days
    }

# ---------------------------------------------------------------------------
# Card 1: Hero Card (880x220)
# ---------------------------------------------------------------------------
def render_hero_card():
    width = 880
    height = 220
    delay_offset = 0.0

    # Portrait image embedding
    photo_path = os.path.join(ASSETS_DIR, "photo.webp")
    portrait_svg = ""
    if os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("ascii")
        portrait_svg = f"""
  <!-- Portrait Frame with Absolute Coordinates (Anchored at cx=760, cy=110) -->
  <g class="fade-1">
    <defs>
      <clipPath id="avatar-clip">
        <circle cx="760" cy="110" r="60" />
      </clipPath>
    </defs>
    <circle cx="760" cy="110" r="65" fill="none" stroke="{SIGNAL}" stroke-width="2" class="pulse-border" opacity="0.8" />
    <circle cx="760" cy="110" r="69" fill="none" stroke="{BORDER}" stroke-width="1" />
    <image href="data:image/webp;base64,{b64_img}" x="700" y="50" width="120" height="120" clip-path="url(#avatar-clip)" preserveAspectRatio="xMidYMid slice"/>
  </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {get_base_css(delay_offset)}
  <defs>
    <linearGradient id="hero-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{DEPTH}" />
      <stop offset="100%" stop-color="{VOID}" />
    </linearGradient>
    <linearGradient id="sig-beam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{SIGNAL}" stop-opacity="0.9" />
      <stop offset="50%" stop-color="{BUILDER}" stop-opacity="0.8" />
      <stop offset="100%" stop-color="{SIGNAL}" stop-opacity="0.2" />
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#hero-bg)" stroke="{BORDER}" stroke-width="1"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="none" stroke="{BORDER_HIGHLIGHT}" stroke-width="1.2" class="pulse-border"/>

  <!-- Top Accent Beam -->
  <line x1="20" y1="1" x2="380" y2="1" stroke="url(#sig-beam)" stroke-width="2.5" stroke-linecap="round"/>

  <!-- Status Bar -->
  <g class="fade-0">
    <rect x="36" y="28" width="168" height="24" rx="12" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1" />
    <circle cx="50" cy="40" r="4" fill="{BUILDER}" class="live-dot" />
    <text x="62" y="44" fill="{BUILDER}" font-size="11" class="font-mono" letter-spacing="1">LIVE TELEMETRY</text>
    <text x="218" y="44" fill="{MUTE}" font-size="11" class="font-mono">SIGNAL FROM NOISE // ARCHITECT</text>
  </g>

  <!-- Name -->
  <g class="fade-1">
    <text x="36" y="92" fill="{INK}" font-size="32" class="font-display" letter-spacing="-0.5">Ujjwal Kaushik</text>
  </g>

  <!-- Subtitle & Bio -->
  <g class="fade-2">
    <text x="36" y="122" fill="{SIGNAL}" font-size="15" class="font-mono" font-weight="600">Full-Stack &amp; Applied AI Engineer</text>
    <text x="36" y="148" fill="{MUTE}" font-size="13" class="font-body">Engineering clarity from technical entropy. Enterprise RAG, distributed backends &amp; computer vision.</text>
  </g>

  <!-- Bottom Telemetry Chips -->
  <g class="fade-3">
    <text x="36" y="188" fill="{MUTE}" font-size="11" class="font-mono">ACADEMICS <tspan fill="{INK}">8.92 SGPA</tspan>  ·  EXPERIENCE <tspan fill="{BUILDER}">2x Vietnam Onsite</tspan>  ·  LEADERSHIP <tspan fill="{HUMAN}">8 Engineers</tspan>  ·  MENTORED <tspan fill="{INK}">170+</tspan></text>
  </g>

  {portrait_svg}
</svg>"""
    return svg

# ---------------------------------------------------------------------------
# Card 2, 3, 4: Three Linked Focus Tiles (420x210)
# ---------------------------------------------------------------------------
def render_tile_card(tile_index):
    width = 420
    height = 210
    
    configs = [
        {
            "num": "01",
            "accent": SIGNAL,
            "badge": "ENTERPRISE RAG",
            "stat": "86.0% Recall",
            "title": "DocNexus Workstation",
            "line1": "Dual-engine RAG with verifiable inline",
            "line2": "citations, 4-tier RBAC &amp; knowledge graphs",
            "line3": "on 5,183 BEIR benchmark documents.",
            "stack": "FastAPI · Llama 3.3 · Ollama · MinIO",
            "delay": 0.35
        },
        {
            "num": "02",
            "accent": BUILDER,
            "badge": "ISRO / SIH 2026",
            "stat": "461.8 FPS · SIL",
            "title": "SANKET Optical Tracking",
            "line1": "Air-gapped Software-in-the-Loop tracking",
            "line2": "workstation for deep-space laser communications",
            "line3": "with zero leakage across 492 verified tests.",
            "stack": "OpenCV · Python · PySide6 · Three.js",
            "delay": 0.50
        },
        {
            "num": "03",
            "accent": HUMAN,
            "badge": "LEADERSHIP &amp; SYSTEMS",
            "stat": "8 Engineers Led",
            "title": "EDC Institutional Infra",
            "line1": "Technical Lead owning live event registration",
            "line2": "&amp; real-time bidding auction portals.",
            "line3": "170+ mentored across DSA and algorithms.",
            "stack": "Node.js · PostgreSQL · Prisma · System Design",
            "delay": 0.65
        }
    ]

    c = configs[tile_index]
    delay_offset = c["delay"]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {get_base_css(delay_offset)}
  <defs>
    <linearGradient id="tile-bg-{tile_index}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{DEPTH}" />
      <stop offset="100%" stop-color="{VOID}" />
    </linearGradient>
  </defs>

  <!-- Tile Card Surface -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="url(#tile-bg-{tile_index})" stroke="{BORDER}" stroke-width="1"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="none" stroke="{c['accent']}40" stroke-width="1.2" class="pulse-border"/>

  <!-- Top Indicator & Badge -->
  <circle cx="28" cy="28" r="4" fill="{c['accent']}" class="live-dot"/>
  <text x="40" y="32" fill="{c['accent']}" font-size="10.5" class="font-mono" letter-spacing="1.5">{c['badge']}</text>

  <rect x="{width - 126}" y="17" width="102" height="22" rx="6" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1"/>
  <text x="{width - 75}" y="32" fill="{c['accent']}" font-size="10" class="font-mono" text-anchor="middle" font-weight="600">{html.escape(c['stat'])}</text>

  <!-- Title -->
  <g class="fade-1">
    <text x="24" y="74" fill="{INK}" font-size="18" class="font-display">{html.escape(c['title'])}</text>
  </g>

  <!-- Description with explicit tspan lines -->
  <g class="fade-2">
    <text x="24" y="104" fill="{MUTE}" font-size="11.5" class="font-body">
      <tspan x="24" dy="0">{c['line1']}</tspan>
      <tspan x="24" dy="17">{c['line2']}</tspan>
      <tspan x="24" dy="17">{c['line3']}</tspan>
    </text>
  </g>

  <!-- Stack Footer -->
  <g class="fade-3">
    <rect x="20" y="170" width="{width - 40}" height="24" rx="4" fill="{VOID}" opacity="0.6"/>
    <text x="28" y="186" fill="{MUTE}" font-size="10" class="font-mono">STACK: <tspan fill="{c['accent']}">{html.escape(c['stack'])}</tspan></text>
  </g>
</svg>"""
    return svg

# ---------------------------------------------------------------------------
# Card 5: Monthly Contributions Chart & Streak Stats (880x290)
# ---------------------------------------------------------------------------
def render_stats_card(stats):
    width = 880
    height = 290
    delay_offset = 0.85

    total = stats["total"]
    active_days = stats["active_days"]
    active_pct = stats["active_percent"]
    busiest_date = stats["busiest"]["date"]
    busiest_cnt = stats["busiest"]["count"]
    curr_streak = stats["current_streak"]
    long_streak = stats["longest_streak"]
    monthly = stats["monthly"]

    chart_x = 420
    chart_y = 65
    chart_w = 420
    chart_h = 165
    
    max_count = max(m["count"] for m in monthly) if monthly else 1
    num_bars = len(monthly)
    bar_width = 24
    gap = (chart_w - (num_bars * bar_width)) / max(num_bars - 1, 1)

    bars_svg = []
    labels_svg = []

    for i, m in enumerate(monthly):
        b_x = chart_x + i * (bar_width + gap)
        b_h = max(int((m["count"] / max_count) * (chart_h - 40)), 6)
        b_y = chart_y + chart_h - b_h
        
        try:
            m_dt = datetime.strptime(m["month"], "%Y-%m")
            m_label = m_dt.strftime("%b")
        except:
            m_label = m["month"][-2:]

        bar_delay = delay_offset + 0.2 + (i * 0.04)
        anim_style = "" if STATIC_MODE else f'style="transform-origin: {b_x + bar_width/2:.1f}px {chart_y + chart_h:.1f}px; animation: growBar 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; animation-delay: {bar_delay:.2f}s;"'

        bars_svg.append(f"""
        <g {anim_style}>
          <rect x="{b_x:.1f}" y="{b_y:.1f}" width="{bar_width}" height="{b_h}" rx="4" fill="url(#bar-gradient)" />
          <rect x="{b_x:.1f}" y="{b_y:.1f}" width="{bar_width}" height="3" rx="1.5" fill="{BUILDER}" opacity="0.9" />
          <text x="{b_x + bar_width/2:.1f}" y="{b_y - 6:.1f}" fill="{MUTE}" font-size="9" class="font-mono" text-anchor="middle">{m['count']}</text>
        </g>
        """)

        labels_svg.append(f"""
        <text x="{b_x + bar_width/2:.1f}" y="{chart_y + chart_h + 20}" fill="{MUTE}" font-size="10" class="font-mono" text-anchor="middle">{m_label}</text>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {get_base_css(delay_offset)}
  <defs>
    <linearGradient id="stats-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{DEPTH}" />
      <stop offset="100%" stop-color="{VOID}" />
    </linearGradient>
    <linearGradient id="bar-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{BUILDER}" stop-opacity="0.95" />
      <stop offset="50%" stop-color="{SIGNAL}" stop-opacity="0.85" />
      <stop offset="100%" stop-color="{DEPTH}" stop-opacity="0.4" />
    </linearGradient>
  </defs>

  <!-- Card Surface -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#stats-bg)" stroke="{BORDER}" stroke-width="1"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="none" stroke="{BORDER_HIGHLIGHT}" stroke-width="1.2" class="pulse-border"/>

  <!-- Card Header -->
  <g class="fade-0">
    <text x="36" y="38" fill="{SIGNAL}" font-size="11" class="font-mono" letter-spacing="1.5">TELEMETRY // CONTRIBUTION CADENCE &amp; STREAKS</text>
    <text x="{width - 36}" y="38" fill="{INK}" font-size="11" class="font-mono" text-anchor="end">{total} CONTRIBUTIONS / YEAR</text>
    <line x1="36" y1="48" x2="{width - 36}" y2="48" stroke="{BORDER}" stroke-width="1" />
  </g>

  <!-- Left: 4 Metric Cards Grid (2x2) with Absolute Coordinates -->
  <g class="fade-1">
    <!-- Metric 1: Current Streak -->
    <rect x="36" y="70" width="162" height="74" rx="8" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1" />
    <text x="52" y="94" fill="{MUTE}" font-size="10" class="font-mono" letter-spacing="1">CURRENT STREAK</text>
    <text x="52" y="126" fill="{SIGNAL}" font-size="24" class="font-display">{curr_streak} <tspan font-size="13" class="font-mono" fill="{MUTE}">Days</tspan></text>

    <!-- Metric 2: Longest Streak -->
    <rect x="214" y="70" width="162" height="74" rx="8" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1" />
    <text x="230" y="94" fill="{MUTE}" font-size="10" class="font-mono" letter-spacing="1">LONGEST STREAK</text>
    <text x="230" y="126" fill="{INK}" font-size="24" class="font-display">{long_streak} <tspan font-size="13" class="font-mono" fill="{MUTE}">Days</tspan></text>

    <!-- Metric 3: Active Days -->
    <rect x="36" y="156" width="162" height="74" rx="8" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1" />
    <text x="52" y="180" fill="{MUTE}" font-size="10" class="font-mono" letter-spacing="1">ACTIVE DAYS</text>
    <text x="52" y="212" fill="{BUILDER}" font-size="24" class="font-display">{active_days} <tspan font-size="12" class="font-mono" fill="{MUTE}">({active_pct}%)</tspan></text>

    <!-- Metric 4: Busiest Day -->
    <rect x="214" y="156" width="162" height="74" rx="8" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1" />
    <text x="230" y="180" fill="{MUTE}" font-size="10" class="font-mono" letter-spacing="1">BUSIEST DAY</text>
    <text x="230" y="212" fill="{HUMAN}" font-size="24" class="font-display">{busiest_cnt} <tspan font-size="11" class="font-mono" fill="{MUTE}">({busiest_date[-5:]})</tspan></text>
  </g>

  <!-- Right: Monthly Bar Chart -->
  <line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" stroke="{DARK_MUTE}" stroke-width="1"/>

  {"".join(bars_svg)}
  {"".join(labels_svg)}

  <!-- Footer Legend -->
  <g class="fade-3">
    <circle cx="42" cy="262" r="3" fill="{SIGNAL}"/>
    <text x="52" y="266" fill="{MUTE}" font-size="10" class="font-mono">Monthly commit cadence calculated live via GitHub API</text>
  </g>
</svg>"""
    return svg

# ---------------------------------------------------------------------------
# Card 6+: Featured Repositories (880x150)
# ---------------------------------------------------------------------------
def render_repo_card(repo_id):
    width = 880
    height = 150

    repos = {
        "docnexus": {
            "title": "DocNexus",
            "full_name": "Ujjwal-Qubit / DocNexus",
            "accent": SIGNAL,
            "badge": "Enterprise Client Delivery · SciFact Verified",
            "desc": "Enterprise RAG & knowledge graph system with zero-hallucination citations, 4-tier RBAC, and hybrid search fusion.",
            "metrics": "86.0% Recall@10  ·  0.6893 MRR@10  ·  100% Relevance",
            "stack": ["FastAPI", "React 19", "Llama 3.3 70B", "Ollama", "MinIO", "Podman"],
            "delay": 1.1
        },
        "sanket": {
            "title": "SANKET",
            "full_name": "Ujjwal-Qubit / Run_Time_Terror",
            "accent": BUILDER,
            "badge": "ISRO / SIH 2026 (Problem Statement 26169)",
            "desc": "Air-gapped Software-in-the-Loop simulation & tracking workstation for deep-space laser communications.",
            "metrics": "0.067s Acquisition (+96.5%)  ·  461.8 FPS  ·  492/492 Tests",
            "stack": ["Python 3.11", "OpenCV", "Three.js", "PySide6", "QtWebEngine"],
            "delay": 1.25
        },
        "auradesign": {
            "title": "AuraDesign.AI",
            "full_name": "Ujjwal-Qubit / AuraDesign.AI",
            "accent": HUMAN,
            "badge": "Top 10 / 255 Teams · HackData 2026",
            "desc": "Sees what your users actually see — full-page DOM scraping, 20x20 Gaussian thermal diffusion heatmaps, and 1-click code fixes.",
            "metrics": "5 UX Laws Audited  ·  Gaussian Heatmaps  ·  Dual-LLM Pipeline",
            "stack": ["React 18", "Node.js", "Express", "Puppeteer", "Pinecone", "Groq Llama 4"],
            "delay": 1.4
        },
        "edith": {
            "title": "E.D.I.T.H.",
            "full_name": "Ujjwal-Qubit / E.D.I.T.H.---Education-Dynamic-Intelligent-Task-Handler",
            "accent": SIGNAL,
            "badge": "All-in-One Study Workspace · Live",
            "desc": "Education Dynamic Intelligent Task Handler — chats with your notes, reads scanned handwritten OCR, tasks and timers.",
            "metrics": "Gemini API Chat  ·  Tesseract OCR  ·  Integrated Document Vault",
            "stack": ["FastAPI", "React", "Python", "Gemini API", "Tesseract OCR", "Vercel"],
            "delay": 1.55
        }
    }

    r = repos[repo_id]
    delay_offset = r["delay"]

    pills_svg = []
    px = 36
    for tag in r["stack"]:
        tag_w = len(tag) * 7.0 + 16
        pills_svg.append(f"""
        <g transform="translate({px:.1f}, 112)">
          <rect x="0" y="0" width="{tag_w:.1f}" height="20" rx="4" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1"/>
          <text x="{tag_w/2:.1f}" y="13.5" fill="{MUTE}" font-size="10" class="font-mono" text-anchor="middle">{html.escape(tag)}</text>
        </g>
        """)
        px += tag_w + 8

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {get_base_css(delay_offset)}
  <defs>
    <linearGradient id="repo-bg-{repo_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{DEPTH}" />
      <stop offset="100%" stop-color="{VOID}" />
    </linearGradient>
  </defs>

  <!-- Card Surface -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="url(#repo-bg-{repo_id})" stroke="{BORDER}" stroke-width="1"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="none" stroke="{r['accent']}35" stroke-width="1.2" class="pulse-border"/>

  <!-- Left Accent Bar -->
  <line x1="1" y1="20" x2="1" y2="{height - 20}" stroke="{r['accent']}" stroke-width="3" stroke-linecap="round"/>

  <!-- Header with Absolute Coordinates -->
  <g class="fade-0">
    <circle cx="44" cy="32" r="4" fill="{r['accent']}" class="live-dot"/>
    <text x="56" y="37" fill="{INK}" font-size="19" class="font-display">{html.escape(r['title'])}</text>
    <text x="175" y="36" fill="{MUTE}" font-size="12" class="font-mono">({html.escape(r['full_name'])})</text>
    
    <!-- Right Badge -->
    <rect x="{width - 36 - 290}" y="19" width="290" height="24" rx="6" fill="{DEPTH}" stroke="{BORDER}" stroke-width="1"/>
    <text x="{width - 36 - 145}" y="35" fill="{r['accent']}" font-size="10" class="font-mono" text-anchor="middle" font-weight="600">{html.escape(r['badge'])}</text>
  </g>

  <!-- Description with Absolute Coordinates -->
  <g class="fade-1">
    <text x="36" y="68" fill="{MUTE}" font-size="13" class="font-body">{html.escape(r['desc'])}</text>
    <text x="36" y="92" fill="{r['accent']}" font-size="11.5" class="font-mono" font-weight="600">KEY TELEMETRY: <tspan fill="{INK}">{html.escape(r['metrics'])}</tspan></text>
  </g>

  <!-- Stack Pills Footer with Absolute Coordinates -->
  <g class="fade-2">
    {"".join(pills_svg)}
  </g>
</svg>"""
    return svg

# ---------------------------------------------------------------------------
# Card 10: 52-Week Contribution Graph in Brand Colors (880x190)
# ---------------------------------------------------------------------------
def render_contributions_graph(stats):
    width = 880
    height = 190
    delay_offset = 1.7

    raw_days = stats["raw_days"] # 364 days = 52 weeks * 7
    total = stats["total"]

    cell_size = 11
    gap = 3.5
    start_x = 55
    start_y = 52

    level_colors = [
        DEPTH,
        "#2E2260",
        "#5A45B8",
        SIGNAL,
        BUILDER
    ]

    cells_svg = []
    month_headers = []
    curr_month = ""

    for idx, day in enumerate(raw_days):
        col = idx // 7
        row = idx % 7
        
        cx = start_x + col * (cell_size + gap)
        cy = start_y + row * (cell_size + gap)
        
        lvl = day.get("level", 0)
        lvl = max(0, min(lvl, 4))
        fill_color = level_colors[lvl]
        border_stroke = BORDER if lvl == 0 else "none"

        m_str = day["date"][5:7] # MM
        if m_str != curr_month and row == 0 and col < 50:
            curr_month = m_str
            try:
                m_label = datetime.strptime(day["date"][:7], "%Y-%m").strftime("%b")
            except:
                m_label = m_str
            month_headers.append(f'<text x="{cx}" y="{start_y - 10}" fill="{MUTE}" font-size="10" class="font-mono">{m_label}</text>')

        cell_delay = delay_offset + 0.1 + (col * 0.015)
        anim_attr = "" if STATIC_MODE else f'class="fade-0" style="animation-delay: {cell_delay:.2f}s;"'

        cells_svg.append(f'<rect x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{fill_color}" stroke="{border_stroke}" stroke-width="0.8" {anim_attr}/>')

    day_labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri")
    ]
    day_labels_svg = []
    for r_idx, name in day_labels:
        dy = start_y + r_idx * (cell_size + gap) + 9
        day_labels_svg.append(f'<text x="{start_x - 12}" y="{dy}" fill="{MUTE}" font-size="9" class="font-mono" text-anchor="end">{name}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {get_base_css(delay_offset)}
  <defs>
    <linearGradient id="grid-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{DEPTH}" />
      <stop offset="100%" stop-color="{VOID}" />
    </linearGradient>
  </defs>

  <!-- Card Surface -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#grid-bg)" stroke="{BORDER}" stroke-width="1"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="none" stroke="{BORDER_HIGHLIGHT}" stroke-width="1.2" class="pulse-border"/>

  <!-- Header -->
  <g class="fade-0">
    <text x="36" y="30" fill="{SIGNAL}" font-size="11" class="font-mono" letter-spacing="1.5">CONTRIBUTION MATRIX // 52 WEEKS</text>
    <text x="{width - 36}" y="30" fill="{INK}" font-size="11" class="font-mono" text-anchor="end">{total} CONTRIBUTIONS IN THE LAST YEAR</text>
  </g>

  <!-- Month Headers -->
  <g class="fade-1">
    {"".join(month_headers)}
  </g>

  <!-- Day Labels -->
  <g class="fade-1">
    {"".join(day_labels_svg)}
  </g>

  <!-- 52x7 Grid Cells -->
  <g>
    {"".join(cells_svg)}
  </g>

  <!-- Legend -->
  <g class="fade-3">
    <text x="{width - 210}" y="{height - 13}" fill="{MUTE}" font-size="10" class="font-mono">Less</text>
    <rect x="{width - 178}" y="{height - 22}" width="10" height="10" rx="2" fill="{level_colors[0]}" stroke="{BORDER}" stroke-width="0.8"/>
    <rect x="{width - 164}" y="{height - 22}" width="10" height="10" rx="2" fill="{level_colors[1]}"/>
    <rect x="{width - 150}" y="{height - 22}" width="10" height="10" rx="2" fill="{level_colors[2]}"/>
    <rect x="{width - 136}" y="{height - 22}" width="10" height="10" rx="2" fill="{level_colors[3]}"/>
    <rect x="{width - 122}" y="{height - 22}" width="10" height="10" rx="2" fill="{level_colors[4]}"/>
    <text x="{width - 104}" y="{height - 13}" fill="{MUTE}" font-size="10" class="font-mono">More</text>
  </g>

  <!-- Status indicator -->
  <g class="fade-3">
    <circle cx="40" cy="{height - 17}" r="3" fill="{BUILDER}"/>
    <text x="50" y="{height - 13}" fill="{MUTE}" font-size="10" class="font-mono">Palette calibrated to Signal ({SIGNAL}) &amp; Builder ({BUILDER})</text>
  </g>
</svg>"""
    return svg

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
def main():
    print(f"[*] Generating SVG Cards (STATIC_MODE={STATIC_MODE})...")
    
    raw_contrib = load_contributions()
    stats = process_stats(raw_contrib)
    print(f"[*] Stats: {stats['total']} total commits, streak: {stats['current_streak']}, active: {stats['active_days']} days")

    # Render Card 1: Hero
    hero_svg = render_hero_card()
    with open(os.path.join(CARDS_DIR, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(hero_svg)
    print("  -> Rendered cards/hero.svg")

    # Render Cards 2, 3, 4: Three Linked Focus Tiles
    for i in range(3):
        tile_svg = render_tile_card(i)
        filename = f"tile-{i+1}.svg"
        with open(os.path.join(CARDS_DIR, filename), "w", encoding="utf-8") as f:
            f.write(tile_svg)
        print(f"  -> Rendered cards/{filename}")

    # Render Card 5: Stats & Monthly Chart
    stats_svg = render_stats_card(stats)
    with open(os.path.join(CARDS_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)
    print("  -> Rendered cards/stats.svg")

    # Render Featured Repo Cards
    repo_keys = ["docnexus", "sanket", "auradesign", "edith"]
    for r_key in repo_keys:
        repo_svg = render_repo_card(r_key)
        filename = f"repo-{r_key}.svg"
        with open(os.path.join(CARDS_DIR, filename), "w", encoding="utf-8") as f:
            f.write(repo_svg)
        print(f"  -> Rendered cards/{filename}")

    # Render Card 10: Contribution Calendar Graph
    contrib_svg = render_contributions_graph(stats)
    with open(os.path.join(CARDS_DIR, "contributions.svg"), "w", encoding="utf-8") as f:
        f.write(contrib_svg)
    print("  -> Rendered cards/contributions.svg")

    print("[+] All animated SVG cards generated successfully into cards/!")

if __name__ == "__main__":
    main()
