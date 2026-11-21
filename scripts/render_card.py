"""Renders the profile activity card as an animated SVG.

Data comes from generate_stats.fetch_stats. Everything here is pure
string building with the standard library, so the card can be previewed
locally from a fixture without a token.
"""

from __future__ import annotations

import html
from datetime import date, datetime, timezone
from typing import Any

W = 1000
H = 566
P = 36
INNER = W - 2 * P

FONT = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, "
    "Helvetica, Arial, sans-serif"
)
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

BG = "#0a0d14"
TILE = "#0f141d"
LINE = "#1c2330"
TEXT = "#f0f3f8"
MUTED = "#8b95a7"
DIM = "#5b6474"
HEAT = ["#151b26", "#4a1e18", "#8f2a1c", "#e2431f", "#ff9a5a"]
BRAND = ["#ff8a3d", "#ec3b21", "#d9327c", "#8b5cf6"]


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _date(iso: str) -> date:
    return datetime.strptime(iso, "%Y-%m-%d").date()


def _short(d: date, with_year: bool = False) -> str:
    text = f"{d.strftime('%b')} {d.day}"
    return f"{text}, {d.year}" if with_year else text


def _levels(days: list[list[Any]]) -> list[int]:
    nonzero = sorted(c for _, c in days if c > 0)
    if not nonzero:
        return [0] * len(days)

    def q(p: float) -> int:
        return nonzero[min(len(nonzero) - 1, int(len(nonzero) * p))]

    cuts = [q(0.25), q(0.5), q(0.75)]
    levels = []
    for _, count in days:
        if count == 0:
            levels.append(0)
        elif count <= cuts[0]:
            levels.append(1)
        elif count <= cuts[1]:
            levels.append(2)
        elif count <= cuts[2]:
            levels.append(3)
        else:
            levels.append(4)
    return levels


def _defs() -> str:
    stops = "".join(
        f'<stop offset="{i / (len(BRAND) - 1):.2f}" stop-color="{c}"/>'
        for i, c in enumerate(BRAND)
    )
    return f"""
  <defs>
    <linearGradient id="brand" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
      {stops}
      <animateTransform attributeName="gradientTransform" type="rotate"
        values="0 .5 .5;360 .5 .5" dur="12s" repeatCount="indefinite"/>
    </linearGradient>
    <radialGradient id="glowA" cx="0" cy="0" r="1">
      <stop offset="0" stop-color="#ec3b21" stop-opacity=".20"/>
      <stop offset="1" stop-color="#ec3b21" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowB" cx="1" cy="1" r="1">
      <stop offset="0" stop-color="#8b5cf6" stop-opacity=".16"/>
      <stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="20"/></clipPath>
    <clipPath id="bar"><rect x="{P}" y="452" width="{INNER}" height="10" rx="5"/></clipPath>
  </defs>"""


def _style() -> str:
    return f"""
  <style>
    text {{ font-family: {FONT}; }}
    .label {{ font-size: 11px; font-weight: 700; letter-spacing: 1.6px; fill: {MUTED}; }}
    .value {{ font-size: 38px; font-weight: 800; font-variant-numeric: tabular-nums; }}
    .unit {{ font-size: 15px; font-weight: 600; fill: {MUTED}; }}
    .sub {{ font-size: 12px; fill: {DIM}; }}
    .lang {{ font-size: 13px; fill: {TEXT}; font-weight: 600; }}
    .pct {{ font-size: 13px; fill: {MUTED}; font-family: {MONO}; }}
    .mono {{ font-family: {MONO}; }}
    .rise {{ animation: rise .8s cubic-bezier(.2,.7,.2,1) backwards; }}
    .pop {{ animation: pop .5s ease-out backwards; }}
    .grow {{ transform-origin: {P}px 0; animation: grow 1.4s cubic-bezier(.2,.7,.2,1) .9s backwards; }}
    .pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} }}
    @keyframes pop {{ from {{ opacity: 0; }} }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} }}
    @keyframes pulse {{ 0% {{ transform: scale(1); opacity: .7; }} 100% {{ transform: scale(3); opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .rise, .pop, .grow, .pulse {{ animation: none; }}
    }}
  </style>"""


def _tile(
    index: int,
    label: str,
    value: str,
    unit: str,
    sub: str,
    live: bool = False,
) -> str:
    gap = 16
    w = (INNER - 3 * gap) / 4
    x = P + index * (w + gap)
    y = 70
    h = 116
    dot = ""
    label_x = x + 20
    if live:
        cx, cy = x + 24, y + 27
        dot = (
            f'<circle class="pulse" cx="{cx}" cy="{cy}" r="3.5" fill="#ff8a3d"/>'
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#ff8a3d"/>'
        )
        label_x = x + 36
    unit_part = f'<tspan class="unit" dx="6">{esc(unit)}</tspan>' if unit else ""
    return f"""
    <g class="rise" style="animation-delay:{0.1 + index * 0.12:.2f}s">
      <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="14" fill="{TILE}" stroke="{LINE}"/>
      <rect x="{x + 20:.1f}" y="{y}" width="{w - 40:.1f}" height="2" rx="1" fill="url(#brand)" opacity=".9"/>
      {dot}
      <text x="{label_x:.1f}" y="{y + 31}" class="label">{esc(label)}</text>
      <text x="{x + 20:.1f}" y="{y + 78}" class="value" fill="url(#brand)">{esc(value)}{unit_part}</text>
      <text x="{x + 20:.1f}" y="{y + 100}" class="sub">{esc(sub)}</text>
    </g>"""


def _heatmap(days: list[list[Any]], today: date) -> str:
    step = 17.5
    cell = 13.5
    top = 258
    levels = _levels(days)
    first = _date(days[0][0])
    columns: dict[int, list[str]] = {}
    months = []
    last_month = None
    for i, ((iso, count), level) in enumerate(zip(days, levels)):
        d = _date(iso)
        col, row = i // 7, i % 7
        x = P + col * step
        y = top + row * step
        title = f"{count} contribution{'s' if count != 1 else ''} on {_short(d, True)}"
        columns.setdefault(col, []).append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3.5" '
            f'fill="{HEAT[level]}"><title>{esc(title)}</title></rect>'
        )
        if row == 0 and d.month != last_month and col < 52:
            if last_month is not None or d.day <= 7:
                months.append(
                    f'<text x="{x:.1f}" y="{top - 10}" class="sub">{d.strftime("%b")}</text>'
                )
            last_month = d.month
        if d == today:
            columns[col].append(
                f'<rect class="pulse" x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" '
                f'rx="3.5" fill="none" stroke="#ff9a5a" stroke-width="1.5"/>'
            )
    cols = "".join(
        f'<g class="pop" style="animation-delay:{0.5 + col * 0.018:.3f}s">{"".join(rects)}</g>'
        for col, rects in sorted(columns.items())
    )

    active = sum(1 for _, c in days if c > 0)
    best_iso, best = max(days, key=lambda item: item[1])
    summary = f"{active} active days"
    if best > 0:
        summary += f"  ·  best day {best} on {_short(_date(best_iso))}"

    legend_x = W - P - 5 * step - 34
    legend = "".join(
        f'<rect x="{legend_x + i * step:.1f}" y="{top + 7 * step + 12:.1f}" width="{cell}" '
        f'height="{cell}" rx="3.5" fill="{c}"/>'
        for i, c in enumerate(HEAT)
    )
    legend_y = top + 7 * step + 23
    return f"""
    <text x="{P}" y="222" class="label">LAST 12 MONTHS</text>
    <text x="{W - P}" y="222" class="sub" text-anchor="end">{esc(summary)}</text>
    {''.join(months)}
    {cols}
    <text x="{legend_x - 8:.1f}" y="{legend_y:.1f}" class="sub" text-anchor="end">Less</text>
    {legend}
    <text x="{legend_x + 5 * step + 4:.1f}" y="{legend_y:.1f}" class="sub">More</text>
    <text x="{P}" y="{legend_y:.1f}" class="sub">Since {_short(first, True)}</text>"""


def _languages(languages: list[dict[str, Any]]) -> str:
    segments = []
    x = float(P)
    for lang in languages:
        width = INNER * lang["percentage"] / 100
        segments.append(
            f'<rect x="{x:.2f}" y="452" width="{max(width, 0):.2f}" height="10" fill="{esc(lang["color"])}"/>'
        )
        x += width
    legend = []
    col_w = INNER / 4
    for i, lang in enumerate(languages[:8]):
        cx = P + (i % 4) * col_w
        cy = 492 + (i // 4) * 26
        legend.append(
            f'<g class="rise" style="animation-delay:{1.2 + i * 0.06:.2f}s">'
            f'<circle cx="{cx + 5:.1f}" cy="{cy - 4.5}" r="5" fill="{esc(lang["color"])}"/>'
            f'<text x="{cx + 18:.1f}" y="{cy}" class="lang">{esc(lang["name"])}</text>'
            f'<text x="{cx + col_w - 24:.1f}" y="{cy}" class="pct" text-anchor="end">'
            f'{lang["percentage"]:.1f}%</text></g>'
        )
    return f"""
    <text x="{P}" y="436" class="label">LANGUAGES</text>
    <text x="{W - P}" y="436" class="sub" text-anchor="end">by code size, public repos</text>
    <rect x="{P}" y="452" width="{INNER}" height="10" rx="5" fill="{LINE}"/>
    <g clip-path="url(#bar)"><g class="grow">{''.join(segments)}</g></g>
    {''.join(legend)}"""


def build_svg(
    username: str,
    stats: dict[str, Any],
    config: dict[str, Any],
    fingerprint: str,
    now: datetime | None = None,
) -> str:
    now = now or datetime.now(timezone.utc)
    today = now.date()
    year = today.year
    ranges = stats.get("streak_ranges") or {}

    current = stats["current_streak"]
    if current and ranges.get("current"):
        current_sub = f"since {_short(_date(ranges['current'][0]))}"
    else:
        current_sub = "starts with the next commit"

    longest_sub = ""
    if ranges.get("longest"):
        start, end = (_date(v) for v in ranges["longest"])
        same_year = start.year == end.year
        longest_sub = (
            f"{_short(start)} to {_short(end)}, {end.year}"
            if same_year
            else f"{_short(start, True)} to {_short(end, True)}"
        )

    tiles = "".join(
        [
            _tile(0, "THIS YEAR", f"{stats['contributed_this_year']:,}", "", f"contributions in {year}"),
            _tile(1, "ALL TIME", f"{stats['total_contributions']:,}", "", f"contributions since {stats.get('first_year', year)}"),
            _tile(2, "CURRENT STREAK", f"{current:,}", "days" if current != 1 else "day", current_sub, live=current > 0),
            _tile(3, "LONGEST STREAK", f"{stats['longest_streak']:,}", "days", longest_sub),
        ]
    )

    updated = now.strftime("%d %b %Y, %H:%M UTC").lstrip("0")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d" data-fingerprint="{esc(fingerprint)}">
  <title id="t">{esc(username)} GitHub activity</title>
  <desc id="d">Contributions, streaks, the last twelve months of activity and most used languages.</desc>
  {_defs()}
  {_style()}
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glowA)"/>
    <rect width="{W}" height="{H}" fill="url(#glowB)"/>
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="url(#ring)" stroke-width="1.5" opacity=".75"/>

  <g class="rise">
    <circle cx="{P + 5}" cy="38" r="5" fill="url(#brand)"/>
    <text x="{P + 18}" y="43" font-size="15" font-weight="700" fill="{TEXT}">{esc(username)}</text>
    <text x="{W - P}" y="43" class="sub mono" text-anchor="end">github activity</text>
  </g>
  {tiles}
  {_heatmap(stats['days'], today)}
  {_languages(stats['languages'])}
  <text x="{W / 2}" y="{H - 16}" class="sub" text-anchor="middle">Updated {esc(updated)}</text>
</svg>
"""
