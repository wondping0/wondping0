"""Generate the animated SVGs used by the profile README.

Run from the repository root:  python scripts/build-assets.py
Everything is self-contained (no external fonts or images) so GitHub's
image proxy renders it exactly as written.
"""

import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG = "#050B18"
SURFACE = "#0A1428"
LINE = "#1B2A47"
INK = "#E6F1FF"
MUTED = "#8BA3C7"
CYAN = "#38E1FF"
BLUE = "#3B82F6"
GREEN = "#4ADE80"
AMBER = "#FBBF24"
MONO = "'JetBrains Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
CHAR_W = 0.6  # monospace advance as a fraction of font size


def typed_width(text, size):
    return len(text) * size * CHAR_W


def typing_animation(text, size, begin, dur, total, hold_end=None):
    """SMIL width animation that reveals `text` one character at a time.

    The reveal starts at `begin`, types for `dur` seconds, holds, then
    hides at `hold_end` (fraction of `total`). Loops every `total` seconds.
    """
    n = len(text)
    full = typed_width(text, size) + 2
    hold_end = hold_end if hold_end is not None else 0.98
    times, values = [0.0], [0.0]
    start = begin / total
    times.append(start)
    values.append(0)
    for i in range(1, n + 1):
        times.append((begin + dur * i / n) / total)
        values.append(min(full, i * size * CHAR_W + 2))
    times.append(hold_end)
    values.append(full)
    times.append(min(hold_end + 0.001, 0.999))
    values.append(0)
    times.append(1.0)
    values.append(0)
    kt = ";".join(f"{t:.4f}" for t in times)
    vs = ";".join(f"{v:.1f}" for v in values)
    return (
        f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" '
        f'calcMode="discrete" keyTimes="{kt}" values="{vs}"/>'
    )


def avatar_data_uri():
    data = (ASSETS / "avatar.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


# ---------------------------------------------------------------- header ---

ROLES = [
    "cryptography & cryptanalysis",
    "CTF player & challenge author",
    "building developer tools in Go / TS",
    "breaking ciphers, shipping agents",
]


def header():
    w, h = 1200, 380
    cx, cy, r = 220, 190, 112
    slot = 4.5
    total = slot * len(ROLES)
    role_size = 26
    roles = []
    for i, role in enumerate(ROLES):
        begin = i * slot
        hold_end = (begin + slot - 0.35) / total
        anim = typing_animation(role, role_size, begin + 0.2, 1.6, total, hold_end)
        roles.append(
            f'<clipPath id="r{i}"><rect x="470" y="196" height="40" width="0">{anim}</rect></clipPath>'
            f'<text x="470" y="226" clip-path="url(#r{i})" class="role">{escape(role)}</text>'
        )
    # A blinking cursor that follows the longest role is visually noisy, so it
    # sits at a fixed spot after the prompt instead.

    glyphs = "+ − × ÷ = ∑ ⊕ π".split()
    orbit = []
    for i, g in enumerate(glyphs):
        a = i * 360 / len(glyphs)
        orbit.append(
            f'<g transform="rotate({a:.1f} {cx} {cy})"><text x="{cx}" y="{cy - r - 30}" '
            f'class="glyph" text-anchor="middle" transform="rotate({-a:.1f} {cx} {cy - r - 36})">{escape(g)}</text></g>'
        )

    rain = []
    cols = [(800, "01101"), (880, "0x3f"), (960, "e≡1"), (1040, "10011"), (1120, "mod p")]
    for i, (x, t) in enumerate(cols):
        rain.append(
            f'<text x="{x}" y="0" class="rain" style="animation-delay:{-i * 1.7:.1f}s">{escape(t)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="wondping0 — Muhammad Faturrohman. Cryptography, CTF and developer tools.">
<title>wondping0 — Muhammad Faturrohman</title>
<defs>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{LINE}" stroke-width="1" opacity=".55"/></pattern>
  <radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset=".55" stop-color="{BG}" stop-opacity=".2"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient>
  <linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".6" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  <clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<style>
  text {{ font-family: {MONO}; }}
  .label {{ fill: {MUTED}; font-size: 14px; letter-spacing: 3px; }}
  .name {{ font-size: 64px; font-weight: 800; letter-spacing: -1px; }}
  .prompt {{ fill: {CYAN}; font-size: 26px; }}
  .role {{ fill: {INK}; font-size: 26px; }}
  .glyph {{ fill: {CYAN}; font-size: 20px; font-weight: 700; }}
  .chip {{ fill: {MUTED}; font-size: 13px; letter-spacing: 1px; }}
  .rain {{ fill: {CYAN}; font-size: 13px; opacity: .0; animation: fall 9s linear infinite; }}
  .spin {{ transform-origin: {cx}px {cy}px; animation: spin 26s linear infinite; }}
  .spin-rev {{ transform-origin: {cx}px {cy}px; animation: spin 14s linear infinite reverse; }}
  .pulse {{ transform-origin: {cx}px {cy}px; animation: pulse 3.2s ease-in-out infinite; }}
  .scan {{ animation: scan 6s linear infinite; }}
  .blink {{ animation: blink 1s steps(1) infinite; }}
  .dot {{ animation: blink 2s ease-in-out infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes pulse {{ 0%,100% {{ opacity: .55; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.06); }} }}
  @keyframes scan {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY({h + 40}px); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes fall {{ 0% {{ transform: translateY(-20px); opacity: 0; }} 15% {{ opacity: .35; }} 85% {{ opacity: .35; }} 100% {{ transform: translateY({h + 20}px); opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .spin, .spin-rev, .pulse, .scan, .blink, .dot, .rain {{ animation: none; }} }}
</style>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
  {"".join(rain)}
  <rect width="{w}" height="{h}" fill="url(#fade)"/>
  <rect class="scan" x="0" y="0" width="{w}" height="2" fill="{CYAN}" opacity=".18"/>

  <circle class="pulse" cx="{cx}" cy="{cy}" r="{r + 46}" fill="url(#glow)"/>
  <g class="spin"><circle cx="{cx}" cy="{cy}" r="{r + 22}" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-dasharray="3 9" opacity=".7"/></g>
  <g class="spin-rev"><circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="70 30 12 30" opacity=".85"/></g>
  <g class="spin">{"".join(orbit)}</g>
  <circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="{CYAN}" opacity=".5" filter="url(#soft)"/>
  <image href="{avatar_data_uri()}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CYAN}" stroke-width="2.5"/>

  <text x="470" y="92" class="label">MUHAMMAD FATURROHMAN</text>
  <text x="466" y="160" class="name" fill="url(#name)">wondping0</text>
  <text x="440" y="226" class="prompt">›</text>
  {"".join(roles)}

  <g transform="translate(470 286)">
    <rect width="132" height="34" rx="17" fill="{SURFACE}" stroke="{LINE}"/>
    <circle class="dot" cx="20" cy="17" r="5" fill="{GREEN}"/>
    <text x="34" y="22" class="chip">ONLINE</text>
    <rect x="146" width="196" height="34" rx="17" fill="{SURFACE}" stroke="{LINE}"/>
    <text x="164" y="22" class="chip">ID · INDONESIA</text>
    <rect x="356" width="262" height="34" rx="17" fill="{SURFACE}" stroke="{LINE}"/>
    <text x="374" y="22" class="chip">CRYPTO · CTF · GO · TS</text>
  </g>
  <rect width="{w}" height="{h}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>
  <rect x="0" y="0" width="{w}" height="3" fill="{CYAN}" opacity=".9"/>
</g>
</svg>
'''
    return svg


# -------------------------------------------------------------- terminal ---

SESSION = [
    ("cmd", "whoami"),
    ("out", "Muhammad Faturrohman — security researcher & tool builder"),
    ("cmd", "cat focus.txt"),
    ("out", "cryptanalysis · CTF authoring · agent tooling · fleet security"),
    ("cmd", "ls ~/shipping"),
    ("hi", "wondev/  q-agent/  ayas-playground/  ctf-prompt-injection/"),
    ("cmd", "echo $MOTTO"),
    ("out", "Add some code to this world ... although a little bit."),
]


def terminal():
    w = 1200
    size = 19
    top = 74
    step = 40
    h = top + step * len(SESSION) + 40
    total = 16.0
    t = 0.4
    lines = []
    for i, (kind, text) in enumerate(SESSION):
        y = top + step * i + 22
        x = 64 if kind == "cmd" else 40
        if kind == "cmd":
            dur = max(0.6, len(text) * 0.07)
            anim = typing_animation(text, size, t, dur, total, 0.97)
            lines.append(
                f'<text x="40" y="{y}" class="ps" opacity="0">$'
                f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;{t / total:.4f};0.97;1" values="0;1;0;0"/></text>'
                f'<clipPath id="t{i}"><rect x="{x}" y="{y - 24}" height="34" width="0">{anim}</rect></clipPath>'
                f'<text x="{x}" y="{y}" class="cmd" clip-path="url(#t{i})">{escape(text)}</text>'
            )
            t += dur + 0.25
        else:
            show = t / total
            cls = "hi" if kind == "hi" else "out"
            lines.append(
                f'<text x="{x}" y="{y}" class="{cls}" opacity="0">{escape(text)}'
                f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;{show:.4f};0.97;1" values="0;1;0;0"/></text>'
            )
            t += 0.55
    cursor_y = top + step * len(SESSION) + 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Terminal: whoami — Muhammad Faturrohman, security engineer and tool builder focused on cryptanalysis, CTF authoring and agent tooling.">
<title>wondping0 terminal</title>
<style>
  text {{ font-family: {MONO}; font-size: {size}px; }}
  .ps {{ fill: {CYAN}; }}
  .cmd {{ fill: {INK}; }}
  .out {{ fill: {MUTED}; }}
  .hi {{ fill: {GREEN}; }}
  .bar {{ fill: {MUTED}; font-size: 13px; letter-spacing: 1px; }}
  .blink {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .blink {{ animation: none; }} }}
</style>
<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="15" fill="none" stroke="{LINE}" stroke-width="2"/>
<path d="M1 46H{w - 1}" stroke="{LINE}"/>
<circle cx="30" cy="24" r="6" fill="#FF5F57"/><circle cx="50" cy="24" r="6" fill="{AMBER}"/><circle cx="70" cy="24" r="6" fill="{GREEN}"/>
<text x="{w / 2}" y="29" text-anchor="middle" class="bar">wondping0@github: ~</text>
{"".join(lines)}
<text x="40" y="{cursor_y + 20}" class="ps">$</text>
<rect class="blink" x="64" y="{cursor_y + 2}" width="11" height="22" fill="{CYAN}"/>
</svg>
'''
    return svg


# ------------------------------------------------------------- projects ---

PROJECTS = [
    ("wondev", "TypeScript · npm", "Write AI agent knowledge once.", "Compile it to CLAUDE.md, AGENTS.md,", ".cursor/rules and more.", "#9A93FF"),
    ("q-agent", "Go · gRPC · PQC", "Native fleet agents with signed", "commands, local role ceilings and", "encrypted shells.", "#B8F779"),
    ("aya's playground", "TypeScript · CTF", "Cryptography CTF marketplace", "with sandboxed verification and", "licensed challenge bundles.", "#7CCB7F"),
    ("crypto research", "Python · Sage", "LCG cracking, algebraic attacks", "on SMALL-PRESENT, differential", "attacks on LOONG64 & Simeck.", CYAN),
]


def card(name, tag, l1, l2, l3, accent):
    w, h = 580, 200
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(name)}: {escape(l1 + ' ' + l2 + ' ' + l3)}">
<title>{escape(name)}</title>
<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath>
<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient></defs>
<style>
  text {{ font-family: {MONO}; }}
  .n {{ fill: {INK}; font-size: 26px; font-weight: 800; }}
  .t {{ fill: {accent}; font-size: 13px; letter-spacing: 1px; }}
  .d {{ fill: {MUTED}; font-size: 16px; }}
  .sweep {{ animation: sweep 5s ease-in-out infinite; }}
  .dot {{ animation: blink 2s ease-in-out infinite; }}
  @keyframes sweep {{ 0% {{ transform: translateX(-{w}px); }} 60%,100% {{ transform: translateX({w}px); }} }}
  @keyframes blink {{ 50% {{ opacity: .25; }} }}
  @media (prefers-reduced-motion: reduce) {{ .sweep, .dot {{ animation: none; }} }}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{SURFACE}"/>
  <rect class="sweep" width="{w}" height="{h}" fill="url(#sweep)"/>
  <rect width="4" height="{h}" fill="{accent}"/>
  <circle class="dot" cx="38" cy="44" r="6" fill="{accent}"/>
  <text x="56" y="53" class="n">{escape(name)}</text>
  <text x="{w - 28}" y="50" text-anchor="end" class="t">{escape(tag.upper())}</text>
  <path d="M30 76H{w - 28}" stroke="{LINE}"/>
  <text x="30" y="112" class="d">{escape(l1)}</text>
  <text x="30" y="138" class="d">{escape(l2)}</text>
  <text x="30" y="164" class="d">{escape(l3)}</text>
  <text x="{w - 28}" y="170" text-anchor="end" class="t">→</text>
  <rect width="{w}" height="{h}" rx="14" fill="none" stroke="{LINE}" stroke-width="2"/>
</g>
</svg>
'''


def footer():
    w, h = 1200, 90
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Thanks for visiting">
<title>thanks for visiting</title>
<style>
  text {{ font-family: {MONO}; font-size: 15px; fill: {MUTED}; letter-spacing: 2px; }}
  .wave {{ animation: wave 4s ease-in-out infinite; }}
  @keyframes wave {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(-60px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .wave {{ animation: none; }} }}
</style>
<g class="wave"><path d="M-60 45 {' '.join(f'Q{x + 30} {25 if (x // 60) % 2 == 0 else 65} {x + 60} 45' for x in range(-60, w + 60, 60))}" fill="none" stroke="{CYAN}" stroke-width="1.5" opacity=".45"/></g>
<rect x="{w / 2 - 190}" y="27" width="380" height="36" rx="18" fill="{BG}" stroke="{LINE}"/>
<text x="{w / 2}" y="50" text-anchor="middle">&lt;/&gt; THANKS FOR VISITING</text>
</svg>
'''


# ------------------------------------------------------------- writeups ---

WRITEUPS = [
    ("2023-11", "ASEAN Cyber Shield 2023", "quals + finals", 8),
    ("2023-11", "National Cyber Week 2023", "quals", 3),
    ("2023-10", "TCP1P CTF 2023", "crypto", 7),
    ("2023-09", "COMPFEST 15", "quals", 4),
    ("2023-08", "HackToday 2023", "quals", 4),
]


def writeups():
    w = 1200
    top = 96
    step = 46
    h = top + step * len(WRITEUPS) + 30
    total = 12.0
    rows = []
    for i, (date, name, note, n) in enumerate(WRITEUPS):
        y = top + step * i
        show = (0.8 + i * 0.35) / total
        bar = 18 * n
        rows.append(
            f'<g opacity="0"><animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="0;{show:.4f};0.96;1" values="0;1;0;0"/>'
            f'<text x="40" y="{y + 20}" class="date">{date}</text>'
            f'<text x="160" y="{y + 20}" class="name">{escape(name)}</text>'
            f'<text x="560" y="{y + 20}" class="note">{escape(note)}</text>'
            f'<rect x="760" y="{y + 7}" width="{bar}" height="16" rx="3" fill="{CYAN}" opacity=".85">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" '
            f'keyTimes="0;{show:.4f};{show + 0.06:.4f};1" values="0;0;{bar};{bar}"/></rect>'
            f'<text x="{w - 40}" y="{y + 20}" text-anchor="end" class="n">{n} solves</text></g>'
            f'<path d="M40 {y + step - 8}H{w - 40}" stroke="{LINE}"/>'
        )
    total_solves = sum(r[3] for r in WRITEUPS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Writeups: {len(WRITEUPS)} CTF events, {total_solves} challenge solves, mostly cryptography.">
<title>wondping0 writeups</title>
<style>
  text {{ font-family: {MONO}; font-size: 17px; }}
  .ps {{ fill: {CYAN}; }}
  .cmd {{ fill: {INK}; }}
  .date {{ fill: {MUTED}; font-size: 15px; }}
  .name {{ fill: {INK}; font-weight: 700; }}
  .note {{ fill: {MUTED}; font-size: 15px; }}
  .n {{ fill: {MUTED}; font-size: 15px; }}
  .bar {{ fill: {MUTED}; font-size: 13px; letter-spacing: 1px; }}
</style>
<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="15" fill="none" stroke="{LINE}" stroke-width="2"/>
<path d="M1 46H{w - 1}" stroke="{LINE}"/>
<circle cx="30" cy="24" r="6" fill="#FF5F57"/><circle cx="50" cy="24" r="6" fill="{AMBER}"/><circle cx="70" cy="24" r="6" fill="{GREEN}"/>
<text x="{w / 2}" y="29" text-anchor="middle" class="bar">wondping0.github.io/writeups</text>
<text x="40" y="78" class="ps">$</text><text x="64" y="78" class="cmd">ls ~/writeups --sort=date  # {total_solves} solves, mostly crypto</text>
{"".join(rows)}
</svg>
'''


def main():
    (ASSETS / "header.svg").write_text(header(), encoding="utf-8")
    (ASSETS / "terminal.svg").write_text(terminal(), encoding="utf-8")
    (ASSETS / "footer.svg").write_text(footer(), encoding="utf-8")
    (ASSETS / "writeups.svg").write_text(writeups(), encoding="utf-8")
    slugs = ["wondev", "q-agent", "ayas-playground", "research"]
    for slug, p in zip(slugs, PROJECTS):
        (ASSETS / f"card-{slug}.svg").write_text(card(*p), encoding="utf-8")
    for f in sorted(ASSETS.glob("*.svg")):
        print(f.name, f.stat().st_size)


if __name__ == "__main__":
    main()
