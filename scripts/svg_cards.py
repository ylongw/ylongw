"""Self-contained SVG instruments for the ylongw profile."""

from html import escape


THEMES = {
    "dark": {
        "background": "#0a111a", "panel": "#101e2a", "ink": "#e7f2f5",
        "muted": "#91acbb", "line": "#263d4c", "accent": "#54e6b5",
        "blue": "#64c9f5", "amber": "#f0c779", "grid": "#182c39",
    },
    "light": {
        "background": "#f5faf9", "panel": "#e8f2f1", "ink": "#122e3a",
        "muted": "#4e6b78", "line": "#c5dbd9", "accent": "#08785c",
        "blue": "#096d98", "amber": "#986319", "grid": "#e1eeeb",
    },
}


def text(x, y, value, size=14, fill="ink", weight=400, family="sans", extra=""):
    return (
        f'<text x="{x}" y="{y}" class="{fill} {family}" font-size="{size}" '
        f'font-weight="{weight}" {extra}>{escape(str(value))}</text>'
    )


def rect(x, y, width, height, fill="panel", radius=12, extra=""):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'class="{fill}" {extra}/>'
    )


def shell(theme, height, title, description, body):
    colors = THEMES[theme]
    palette = "".join(f'.{key}{{fill:{value}}}' for key, value in colors.items())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 1000 {height}" fill="none" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M 24 0 H 0 V 24" stroke="{colors['grid']}" stroke-width="1"/></pattern>
  <linearGradient id="signal"><stop stop-color="{colors['accent']}"/><stop offset="1" stop-color="{colors['blue']}"/></linearGradient>
  <clipPath id="card"><rect x="1" y="1" width="998" height="{height - 2}" rx="22"/></clipPath>
</defs>
<style>
  .sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif}}
  .mono{{font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace}}
  {palette}
  .trace{{stroke:{colors['accent']};stroke-width:1.5;fill:none}}
  .edge{{stroke:{colors['line']};stroke-width:1}}
  .flow{{stroke-dasharray:8 14;animation:flow 12s linear infinite}}
  .cursor{{animation:blink 1.8s steps(2,end) infinite}}
  @keyframes flow{{to{{stroke-dashoffset:-220}}}}
  @keyframes blink{{50%{{opacity:0.15}}}}
  @media(prefers-reduced-motion:reduce){{.flow,.cursor{{animation:none}}}}
</style>
<rect x="1" y="1" width="998" height="{height - 2}" rx="22" fill="{colors['background']}" stroke="{colors['line']}"/>
<g clip-path="url(#card)"><rect width="1000" height="{height}" fill="url(#grid)" opacity="0.6"/>
{body}
</g></svg>
'''


def chips(labels, x, y):
    parts = []
    for label in labels:
        width = 22 + len(label) * 8.2
        parts.append(rect(x, y, width, 29, radius=7))
        parts.append(text(x + width / 2, y + 19, label, 13, "accent", 500, "mono", 'text-anchor="middle"'))
        x += width + 8
    return "".join(parts)


def hero(theme):
    parts = [
        text(36, 38, "YL / ENGINEERING LOG", 12, "muted", 500, "mono", 'letter-spacing="2"'),
        text(964, 38, "01 — IDENTITY", 12, "muted", 500, "mono", 'text-anchor="end"'),
        '<path d="M36 54 H964" class="edge"/>',
        text(35, 132, "ylongw", 68, "ink", 750, extra='letter-spacing="-3"'),
        text(39, 170, "Embedded Engineer · AI Agent Builder", 23, "accent", 650),
        text(39, 212, "Embedded engineer by day,", 21, "ink", 500),
        text(39, 240, "AI tinkerer by night.", 21, "ink", 500),
        text(39, 280, "I build STM32 / Cortex-M / FreeRTOS firmware and tools,", 15, "muted"),
        text(39, 304, "and experiment with AI agents, self-hosted services,", 15, "muted"),
        text(39, 328, "and media automation on macOS and Linux.", 15, "muted"),
        chips(["FIRMWARE", "AGENTS", "AUTOMATION"], 39, 352),
        rect(630, 78, 334, 302, radius=15, extra='stroke="'+THEMES[theme]["line"]+'"'),
        text(650, 106, "SIGNAL / WORKBENCH", 11, "muted", 500, "mono", 'letter-spacing="1.5"'),
        '<circle cx="941" cy="102" r="4" class="accent cursor"/>',
        '<path d="M650 121 H944" class="edge"/>',
        '<path d="M650 175 H676 L687 155 L700 195 L713 143 L728 175 H751" stroke="url(#signal)" stroke-width="2.5"/>',
        '<path d="M845 175 H868 V148 H898 V175 H944" stroke="url(#signal)" stroke-width="2.5"/>',
        '<path d="M650 175 H750 M845 175 H944" class="trace flow"/>',
        rect(752, 137, 92, 78, fill="background", radius=9),
        text(798, 169, "MCU", 19, "accent", 700, "mono", 'text-anchor="middle"'),
        text(798, 193, "CORTEX-M", 10, "muted", 400, "mono", 'text-anchor="middle"'),
        '<path d="M768 129 V137 M788 129 V137 M808 129 V137 M828 129 V137 M768 215 V223 M788 215 V223 M808 215 V223 M828 215 V223 M744 151 H752 M744 174 H752 M744 197 H752 M844 151 H852 M844 174 H852 M844 197 H852" class="trace"/>',
        '<path d="M798 224 V242 H650" class="edge"/>',
        text(650, 270, "$ firmware + agent tools", 13, "accent", 500, "mono"),
        text(650, 296, "J-Link / RTT / GDB", 13, "muted", 400, "mono"),
        text(650, 322, "build → flash → inspect", 13, "muted", 400, "mono"),
        text(650, 353, "$", 14, "accent", 500, "mono"),
        '<rect x="668" y="340" width="8" height="15" class="accent cursor"/>',
        text(39, 413, "FROM BARE METAL TO AGENT LOOPS", 11, "muted", 500, "mono", 'letter-spacing="1.6"'),
        '<path d="M650 409 H964" stroke="url(#signal)" stroke-width="2"/>',
    ]
    return shell(theme, 440, "ylongw — Embedded Engineer · AI Agent Builder",
                 "Embedded engineer by day, AI tinkerer by night. STM32, Cortex-M and FreeRTOS firmware; AI agents, self-hosted services and media automation.", "".join(parts))


def skills(theme):
    parts = [
        text(36, 38, "02 — ACTIVE CHANNELS", 12, "muted", 500, "mono", 'letter-spacing="2"'),
        text(36, 83, "What I'm working on", 28, "ink", 700),
        text(964, 82, "FOUR THREADS / ONE WORKBENCH", 11, "accent", 500, "mono", 'text-anchor="end"'),
    ]
    topics = [
        ("01", "Embedded tooling", "AI-assisted C/C++ review, J-Link flash/debug loops,", "and STM32 framebuffer capture.", "C / C++ · J-LINK · STM32"),
        ("02", "AI agent reliability", "Investigating model routing, classifier fallbacks,", "and quota freshness in Magpie.", "MODEL ROUTING · AGENT TOOLS"),
        ("03", "Self-hosted infra", "Ubuntu VPS deployment and Linux/fnOS", "fan-control automation.", "UBUNTU · LINUX / FNOS"),
        ("04", "Camera workflows", "Organizing Sony uploads and turning Shot Mark", "clips into Apple Live Photos.", "SONY · MEDIA AUTOMATION"),
    ]
    for index, (number, title, line_one, line_two, tag) in enumerate(topics):
        x = 36 + (index % 2) * 474
        y = 110 + (index // 2) * 162
        parts.extend([
            rect(x, y, 454, 144, extra='stroke="'+THEMES[theme]["line"]+'"'),
            text(x + 18, y + 32, number, 13, "accent", 500, "mono"),
            text(x + 52, y + 32, title, 19, "ink", 650),
            text(x + 18, y + 63, line_one, 14, "muted"),
            text(x + 18, y + 85, line_two, 14, "muted"),
            text(x + 18, y + 121, tag, 10, "accent", 500, "mono", 'letter-spacing="0.8"'),
        ])
    parts.extend([
        text(36, 460, "TECH STACK", 12, "muted", 500, "mono", 'letter-spacing="2"'),
        chips(["C", "C++", "Python", "Shell", "Swift", "STM32", "GD32", "FreeRTOS", "CMake", "J-Link"], 36, 479),
    ])
    return shell(theme, 534, "What I'm working on + Tech Stack",
                 "Embedded tooling, AI agent reliability, self-hosted infrastructure and camera workflows. C, C++, Python, Shell, Swift, STM32, GD32, FreeRTOS, CMake and J-Link.", "".join(parts))


def language_shares(sizes):
    total = sum(sizes.values())
    if total == 0:
        return []
    ordered = sorted(sizes.items(), key=lambda item: (-item[1], item[0]))
    rows = ordered[:5]
    remaining = sum(value for _, value in ordered[5:])
    if remaining:
        rows.append(("Other", remaining))
    return [(name, value / total * 100) for name, value in rows]


def stats(theme, data):
    colors = THEMES[theme]
    parts = [
        text(36, 38, "04 — PUBLIC TELEMETRY", 12, "muted", 500, "mono", 'letter-spacing="2"'),
        text(964, 38, "GITHUB API / PUBLIC ONLY", 11, "accent", 500, "mono", 'text-anchor="end"'),
        text(36, 82, "Open-source, measured.", 28, "ink", 700),
    ]
    metrics = [
        ("PUBLIC REPOS", data["public_repositories"]),
        ("STARS", data["stars"]),
        ("FOLLOWERS", data["followers"]),
        ("CONTRIBUTIONS / 365D", data["total_contributions"]),
    ]
    for index, (label, value) in enumerate(metrics):
        x = 36 + index * 236
        parts.extend([
            rect(x, 108, 220, 106, extra='stroke="'+colors["line"]+'"'),
            text(x + 16, 135, label, 10.5, "muted", 500, "mono", 'letter-spacing="0.5"'),
            text(x + 16, 190, f"{value:,}", 42, "accent" if index == 3 else "ink", 650, "mono"),
        ])
    counts = data["contributions"]
    activity = "  /  ".join(f"{counts[key]:,} {label}" for key, label in (
        ("commits", "commits"), ("pull_requests", "PRs"), ("issues", "issues"),
        ("reviews", "reviews"), ("repositories_created", "repos created"),
    ))
    parts.extend([
        text(36, 248, activity, 12, "muted", 400, "mono"),
        '<path d="M36 269 H964" class="edge"/>',
        text(36, 304, "LANGUAGE MIX", 12, "ink", 600, "mono", 'letter-spacing="1"'),
        text(964, 304, "BY BYTES · OWNED PUBLIC REPOS · FORKS EXCLUDED", 10.5, "muted", 400, "mono", 'text-anchor="end"'),
        '<clipPath id="languages"><rect x="36" y="323" width="928" height="13" rx="6"/></clipPath>',
        '<g clip-path="url(#languages)">',
    ])
    palette = [colors["accent"], colors["blue"], "#aa8ae3", colors["amber"], "#df869a", colors["muted"]]
    shares = language_shares(data["language_bytes"])
    x = 36.0
    for index, (name, share) in enumerate(shares):
        width = 928 * share / 100
        parts.append(f'<rect x="{x:.3f}" y="323" width="{width:.3f}" height="13" fill="{palette[index]}"/>')
        x += width
    parts.append("</g>")
    for index, (name, share) in enumerate(shares):
        x = 36 + (index % 3) * 316
        y = 369 + (index // 3) * 31
        parts.extend([
            f'<circle cx="{x + 5}" cy="{y - 5}" r="4" fill="{palette[index]}"/>',
            text(x + 18, y, f"{name} {share:.1f}%", 13, "ink", 500, "mono"),
        ])
    if not shares:
        parts.append(text(36, 369, "No public language data yet.", 14, "muted"))
    parts.extend([
        '<path d="M36 423 H964" class="edge"/>',
        text(36, 450, f"WINDOW {data['period_start'][:10]} → {data['period_end'][:10]} / UTC", 10.5, "muted", 400, "mono"),
        text(964, 450, f"SYNC {data['updated_at'][:16].replace('T', ' ')} UTC", 10.5, "muted", 400, "mono", 'text-anchor="end"'),
        text(36, 476, "Repo + star totals include forks. Contributions are filtered by repository visibility.", 12, "muted"),
    ])
    description = "; ".join(f"{label}: {value}" for label, value in metrics)
    return shell(theme, 500, "ylongw — public GitHub statistics", description, "".join(parts))
