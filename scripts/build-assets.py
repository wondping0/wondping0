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


def typing_css(name, text, size, start, duration, total, end):
    """Discrete CSS clip-width keyframes, with a full-width static fallback."""
    width = len(text) * size * .62 + 3
    frames = [f'0%,{start/total*100:.4f}% {{ width: 0px; }}']
    for i in range(1, len(text) + 1):
        frames.append(f'{(start+duration*i/len(text))/total*100:.4f}% {{ width: {width*i/len(text):.2f}px; }}')
    frames += [f'{end/total*100:.4f}% {{ width: {width:.2f}px; }}',
               f'{(end+.01)/total*100:.4f}%,100% {{ width: 0px; }}']
    return f'.{name} {{ width: {width:.2f}px; animation: {name} {total}s steps(1,end) infinite; }} @keyframes {name} {{ {" ".join(frames)} }}'


def reveal_css(name, start, end, total):
    return f'.{name} {{ animation: {name} {total}s steps(1,end) infinite; }} @keyframes {name} {{ 0%,{start/total*100:.4f}% {{ opacity: 0; }} {(start+.01)/total*100:.4f}%,{end/total*100:.4f}% {{ opacity: 1; }} {(end+.01)/total*100:.4f}%,100% {{ opacity: 0; }} }}'


def svg(w, h, title, body, p, css=""):
    if p['bg'].startswith('var('):
        # Embedded SVGs inherit the host element's color scheme, including a
        # manually selected GitHub theme that differs from the OS preference.
        variables = lambda theme: ';'.join(f'--{key}:{value}' for key, value in PALETTES[theme].items())
        css += f":root {{{variables('dark')}}} @media (prefers-color-scheme: light) {{ :root {{{variables('light')}}} }}"
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
.blink {{ animation: blink 1s steps(1,end) infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes pulse {{ 50% {{ opacity: .45; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
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
<defs><radialGradient id="glow"><stop stop-color="{p['cyan']}" stop-opacity=".3"/><stop offset="1" stop-color="{p['cyan']}" stop-opacity="0"/></radialGradient></defs>
<circle class="pulse" cx="{cx}" cy="{cy}" r="{r+40}" fill="url(#glow)"/>
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
    role_x, role_size = (30, 19) if compact else (324, 22)
    roles = ['cryptography & cryptanalysis', 'CTF player & challenge author',
             'building developer tools in Go / TS', 'breaking ciphers, shipping agents']
    role_svg, css = [], []
    for i, role in enumerate(roles):
        rows = textwrap.wrap(role, width=28 if compact else 40)
        start, end = i * 4.5 + .2, (i + 1) * 4.5 - .35
        css.append(reveal_css(f'role-{i}', i*4.5+.05, end, 18))
        group = []
        for j, row in enumerate(rows):
            name = f'type-role-{i}-{j}'
            y = role_y + j * 28
            css.append(typing_css(name, row, role_size, start+j*.8, 1.6/len(rows), 18, end))
            group.append(f'<clipPath id="{name}"><rect x="{role_x}" y="{y-24}" height="32" class="{name}"/></clipPath><text x="{role_x}" y="{y}" font-size="{role_size}" clip-path="url(#{name})">{escape(row)}</text>')
        role_svg.append(f'<g class="role role-{i}" style="opacity:{1 if i == 0 else 0}">{"".join(group)}</g>')
    css.append(f'''
.scan {{ animation: scan 6s linear infinite; }}
.rain {{ opacity: 0; animation: fall 9s linear infinite; }}
@keyframes scan {{ from {{ transform: translateY(-10px); }} to {{ transform: translateY({h+10}px); }} }}
@keyframes fall {{ 0% {{ transform: translateY(-20px); opacity: 0; }} 15%,85% {{ opacity: .15; }} 100% {{ transform: translateY({h+20}px); opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .role {{ display: none; }} .role-0 {{ display: inline; }} .scan {{ display: none; }} }}
''')
    rain = ''.join(f'<text x="{w-32-i*64}" y="0" font-size="13" class="rain accent" style="animation-delay:{-i*1.7}s">{escape(t)}</text>' for i,t in enumerate(['01101','0x3f','e≡1','10011','mod p']))
    body = f'<rect class="scan" width="{w}" height="2" fill="{p["cyan"]}" opacity=".18"/>{rain}' + avatar(cx, cy, r, p) + f'''
<path d="M18 2H{w-18}" stroke="{p['cyan']}" stroke-width="3"/>
<text x="{x}" y="{name_y}" text-anchor="{anchor}" font-size="{42 if compact else 56}" font-weight="800" class="accent">wondping0</text>
<text x="{x}" y="{fullname_y}" text-anchor="{anchor}" font-size="{19 if compact else 23}">Muhammad Faturrohman</text>
<text x="{role_x-18}" y="{role_y}" font-size="{role_size}" class="accent blink">›</text>
{''.join(role_svg)}
<text x="{x}" y="{416 if compact else 271}" text-anchor="{anchor}" font-size="{16 if compact else 18}" class="accent">CRYPTO / CTF / GO / TS</text>
'''
    return svg(w, h, "wondping0 — Muhammad Faturrohman. Cryptography, CTF and developer tools.", body, p, '\n'.join(css))


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
    lines, css = [], []
    t = .4
    for i, (kind, content) in enumerate(SESSION):
        color = p['ink'] if kind == 'cmd' else p['green'] if kind == 'hi' else p['muted']
        content = '$ ' + content if kind == 'cmd' else content
        group = []
        for j, line in enumerate(textwrap.wrap(content, width=wrap, break_long_words=False)):
            clip = ''
            if kind == 'cmd':
                name = f'type-command-{i}-{j}'
                duration = max(.6, len(line)*.07)
                css.append(typing_css(name, line, size, t, duration, 16, 15.52))
                group.append(f'<clipPath id="{name}"><rect x="24" y="{y-26}" height="36" class="{name}"/></clipPath>')
                clip = f' clip-path="url(#{name})"'
                t += duration + .25
            group.append(f'<text x="24" y="{y}" font-size="{size}" style="fill:{color}"{clip}>{escape(line)}</text>')
            y += step
        if kind != 'cmd':
            css.append(reveal_css(f'output-{i}', t, 15.52, 16))
            lines.append(f'<g class="output-{i}">{"".join(group)}</g>')
            t += .55
        else:
            lines.extend(group)
        y += 9 if kind != 'cmd' else 0
    h = y + 24
    body = f'''
<path d="M1 48H{w-1}" stroke="{p['line']}"/>
<circle cx="26" cy="25" r="5" fill="#E5534B"/><circle cx="44" cy="25" r="5" fill="#B8860B"/><circle cx="62" cy="25" r="5" fill="{p['green']}"/>
<text x="{w-24}" y="31" text-anchor="end" font-size="{14 if compact else 18}" class="muted">wondping0@github: ~</text>
{''.join(lines)}
<rect class="blink" x="24" y="{y-8}" width="10" height="18" fill="{p['cyan']}"/>
'''
    return svg(w, h, "About me: security research, cryptanalysis, CTF authoring and developer tools.", body, p, '\n'.join(css))


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
<defs><linearGradient id="sweep"><stop stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient></defs>
<rect class="sweep" width="400" height="{h}" fill="url(#sweep)"/>
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
    css = '.sweep { animation: sweep 5s ease-in-out infinite; } @keyframes sweep { 0% { transform: translateX(-400px); } 60%,100% { transform: translateX(400px); } }'
    return svg(400, h, f'{name}: {description}', body, p, css).replace(
        'width="400" height="240" viewBox="0 0 400 240"',
        'width="412" height="252" viewBox="-6 -6 412 252"', 1)


def footer(p):
    wave = ' '.join(f'Q{x+30} {20 if (x//60)%2 == 0 else 52} {x+60} 36' for x in range(-60,460,60))
    body = f'''<path class="wave" d="M-60 36 {wave}" fill="none" stroke="{p['cyan']}" opacity=".4"/>
<rect x="52" y="17" width="296" height="38" rx="19" fill="{p['bg']}" stroke="{p['line']}"/>
<text x="200" y="42" text-anchor="middle" font-size="16" class="muted">&lt;/&gt; THANKS FOR VISITING</text>'''
    css = '.wave { animation: wave 4s ease-in-out infinite; } @keyframes wave { 50% { transform: translateX(-60px); } }'
    return svg(400, 72, 'Thanks for visiting', body, p, css)


def main():
    for theme, p in PALETTES.items():
        suffix = '-light' if theme == 'light' else ''
        assets = {f'header{suffix}.svg': header(p),
                  f'terminal{suffix}.svg': terminal(p),
                  f'footer{suffix}.svg': footer(p)}
        if theme == 'dark':
            adaptive = {key: f'var(--{key})' for key in p}
            assets['header-mobile.svg'] = header(adaptive, True)
            assets['terminal-mobile.svg'] = terminal(adaptive, True)
        for project in PROJECTS:
            assets[f'card-{project[0]}{suffix}.svg'] = card(p, project, theme == 'light')
        for name, content in assets.items():
            (ASSETS / name).write_text(content, encoding='utf-8', newline='\n')
            print(name)


if __name__ == '__main__':
    main()
