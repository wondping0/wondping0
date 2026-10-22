"""Build self-contained profile SVGs: python scripts/build-assets.py.

README pictures select compact compositions on phones and match GitHub's theme.
Project cards wrap naturally. CSS-only motion has a fully readable static fallback.
"""
import base64
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
PALETTES = {
    "dark": dict(bg="#050B18", surface="#0A1428", line="#1B2A47", ink="#E6F1FF",
                 muted="#8BA3C7", cyan="#38E1FF", blue="#3B82F6", green="#4ADE80"),
    "light": dict(bg="#F6F8FA", surface="#FFFFFF", line="#D0D7DE", ink="#172B4D",
                  muted="#425A76", cyan="#006B85", blue="#1D4ED8", green="#1A7F37"),
}


def svg(w, h, title, body, p, css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<defs><clipPath id="frame"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18"/></clipPath></defs>
<style>
text {{ font-family: {MONO}; fill: {p['ink']}; }}
.muted {{ fill: {p['muted']}; }}
.accent {{ fill: {p['cyan']}; }}
.spin {{ animation: spin 26s linear infinite; }}
.reverse {{ animation-direction: reverse; animation-duration: 18s; }}
.pulse {{ animation: pulse 3s ease-in-out infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes pulse {{ 50% {{ opacity: .45; }} }}
{css}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="{p['bg']}" stroke="{p['line']}" stroke-width="2"/>
<g clip-path="url(#frame)">{body}</g>
</svg>
'''


def avatar(cx, cy, r, p):
    data = base64.b64encode((ASSETS / "avatar.jpg").read_bytes()).decode()
    glyphs = []
    for i, symbol in enumerate("+ − × ÷ = ∑ ⊕ π".split()):
        a = i * 45
        glyphs.append(f'<g transform="rotate({a} {cx} {cy})"><text x="{cx}" y="{cy-r-24}" text-anchor="middle" font-size="18" class="accent" transform="rotate({-a} {cx} {cy-r-30})">{escape(symbol)}</text></g>')
    return f'''
<defs><clipPath id="avatar"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>
<g class="spin" style="transform-origin:{cx}px {cy}px">{''.join(glyphs)}<circle cx="{cx}" cy="{cy}" r="{r+17}" fill="none" stroke="{p['cyan']}" stroke-dasharray="2 8"/></g>
<g class="spin reverse" style="transform-origin:{cx}px {cy}px"><circle cx="{cx}" cy="{cy}" r="{r+8}" fill="none" stroke="{p['blue']}" stroke-width="2" stroke-dasharray="60 24 12 24"/></g>
<image href="data:image/jpeg;base64,{data}" x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" clip-path="url(#avatar)"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p['cyan']}" stroke-width="2"/>
'''


def header(p, compact=False):
    w, h = (400, 440) if compact else (900, 300)
    cx, cy, r = (200, 118, 66) if compact else (144, 150, 82)
    x, name_y = (200, 264) if compact else (300, 112)
    anchor = "middle" if compact else "start"
    fullname_y = 302 if compact else 153
    role_y = 350 if compact else 203
    body = avatar(cx, cy, r, p) + f'''
<path d="M18 2H{w-18}" stroke="{p['cyan']}" stroke-width="3"/>
<text x="{x}" y="{name_y}" text-anchor="{anchor}" font-size="{42 if compact else 56}" font-weight="800" class="accent">wondping0</text>
<text x="{x}" y="{fullname_y}" text-anchor="{anchor}" font-size="{19 if compact else 23}">Muhammad Faturrohman</text>
<text x="{x}" y="{role_y}" text-anchor="{anchor}" font-size="{21 if compact else 24}" class="muted">Breaking ciphers.</text>
<text x="{x}" y="{role_y+30}" text-anchor="{anchor}" font-size="{21 if compact else 24}" class="muted">Shipping tools.</text>
<text x="{x}" y="{416 if compact else 271}" text-anchor="{anchor}" font-size="{16 if compact else 18}" class="accent">CRYPTO / CTF / GO / TS</text>
'''
    return svg(w, h, "wondping0 — Muhammad Faturrohman. Breaking ciphers. Shipping tools.", body, p)


SESSION = [
    ("cmd", "whoami"),
    ("out", "Muhammad Faturrohman — security researcher & tool builder"),
    ("cmd", "cat focus.txt"),
    ("out", "Cryptanalysis / CTF authoring / agent tooling / fleet security"),
    ("cmd", "ls ~/shipping"),
    ("hi", "wondev / q-agent / ayas-playground / ctf-prompt-injection"),
    ("cmd", "echo $MOTTO"),
    ("out", "Add some code to this world ... although a little bit."),
]


def terminal(p, compact=False):
    w = 400 if compact else 900
    size, wrap, step = (18, 32, 28) if compact else (23, 59, 34)
    y = 87
    lines = []
    for i, (kind, content) in enumerate(SESSION):
        color = p['ink'] if kind == 'cmd' else p['green'] if kind == 'hi' else p['muted']
        content = '$ ' + content if kind == 'cmd' else content
        for line in textwrap.wrap(content, width=wrap, break_long_words=False):
            lines.append(f'<text x="24" y="{y}" font-size="{size}" style="fill:{color};animation-delay:{i * .12:.2f}s" class="line">{escape(line)}</text>')
            y += step
        y += 9 if kind != 'cmd' else 0
    h = y + 24
    body = f'''
<path d="M1 48H{w-1}" stroke="{p['line']}"/>
<circle cx="26" cy="25" r="5" fill="#E5534B"/><circle cx="44" cy="25" r="5" fill="#B8860B"/><circle cx="62" cy="25" r="5" fill="{p['green']}"/>
<text x="{w-24}" y="31" text-anchor="end" font-size="{14 if compact else 18}" class="muted">wondping0@github: ~</text>
{''.join(lines)}
<rect class="pulse" x="24" y="{y-8}" width="10" height="18" fill="{p['cyan']}"/>
'''
    css = '.line { animation: appear .5s ease-out both; } @keyframes appear { from { transform: translateY(4px); } to { transform: translateY(0); } }'
    return svg(w, h, "About me: security research, cryptanalysis, CTF authoring and developer tools.", body, p, css)


PROJECTS = [
    ("wondev", "wondev", "TYPESCRIPT / NPM", "Write AI agent knowledge once. Compile it to CLAUDE.md, AGENTS.md, .cursor/rules and more.", "#9A93FF", "#6F42C1"),
    ("q-agent", "q-agent", "GO / GRPC / PQC", "Native fleet agents with signed commands, local role ceilings and encrypted shells.", "#B8F779", "#3B6515"),
    ("ayas-playground", "aya's playground", "TYPESCRIPT / CTF", "Cryptography CTF marketplace with sandboxed verification and licensed challenge bundles.", "#7CCB7F", "#27743D"),
    ("research", "crypto research", "PYTHON / SAGE", "LCG cracking, algebraic attacks on SMALL-PRESENT, differential attacks on LOONG64 & Simeck.", "#38E1FF", "#006B85"),
]


def card(p, project, light=False):
    _, name, tag, description, dark_accent, light_accent = project
    accent = light_accent if light else dark_accent
    lines = textwrap.wrap(description, width=31, break_long_words=False)
    h = 240
    body = f'''
<rect x="1" y="1" width="398" height="{h-2}" rx="18" fill="{p['surface']}"/>
<path d="M2 18V{h-18}" stroke="{accent}" stroke-width="4"/>
<circle class="pulse" cx="27" cy="36" r="5" fill="{accent}"/>
<text x="42" y="43" font-size="{25 if len(name) > 14 else 28}" font-weight="700">{escape(name)}</text>
<text x="24" y="75" font-size="15" style="fill:{accent}">{escape(tag)}</text>
<path d="M24 94H376" stroke="{p['line']}"/>
'''
    for i, line in enumerate(lines):
        body += f'<text x="24" y="{123+i*27}" font-size="18" class="muted">{escape(line)}</text>'
    body += f'<text x="376" y="{h-16}" text-anchor="end" font-size="20" style="fill:{accent}">↗</text>'
    # The viewBox includes a gutter: GitHub removes custom image margin styles.
    return svg(400, h, f'{name}: {description}', body, p).replace(
        'width="400" height="240" viewBox="0 0 400 240"',
        'width="412" height="252" viewBox="-6 -6 412 252"', 1)


def footer(p):
    body = f'''<path d="M0 36H400" stroke="{p['cyan']}" opacity=".4"/>
<rect x="52" y="17" width="296" height="38" rx="19" fill="{p['bg']}" stroke="{p['line']}"/>
<text x="200" y="42" text-anchor="middle" font-size="16" class="muted">&lt;/&gt; THANKS FOR VISITING</text>'''
    return svg(400, 72, 'Thanks for visiting', body, p)


def main():
    for theme, p in PALETTES.items():
        suffix = '-light' if theme == 'light' else ''
        assets = {f'header{suffix}.svg': header(p),
                  f'header-mobile{suffix}.svg': header(p, True),
                  f'terminal{suffix}.svg': terminal(p),
                  f'terminal-mobile{suffix}.svg': terminal(p, True),
                  f'footer{suffix}.svg': footer(p)}
        for project in PROJECTS:
            assets[f'card-{project[0]}{suffix}.svg'] = card(p, project, theme == 'light')
        for name, content in assets.items():
            (ASSETS / name).write_text(content, encoding='utf-8', newline='\n')
            print(name)


if __name__ == '__main__':
    main()
