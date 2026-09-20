"""
Generate self-contained animated marquee SVG for GitHub README.
Rows scroll in opposite directions (zigzag effect).
"""

BADGES_ROW1 = [
    ("PHP",        "#777BB4", "#fff"),
    ("JAVASCRIPT", "#F7DF1E", "#000"),
    ("TYPESCRIPT", "#3178C6", "#fff"),
    ("HTML5",      "#E34F26", "#fff"),
    ("CSS3",       "#1572B6", "#fff"),
    ("GDSCRIPT",   "#478CBF", "#fff"),
    ("LARAVEL",    "#FF2D20", "#fff"),
    ("VUE.JS",     "#4FC08D", "#fff"),
    ("NODE.JS",    "#339933", "#fff"),
    ("BOOTSTRAP",  "#7952B3", "#fff"),
    ("BLADE",      "#FF2D20", "#fff"),
]

BADGES_ROW2 = [
    ("MYSQL",   "#4479A1", "#fff"),
    ("TIDB",    "#DD0031", "#fff"),
    ("GIT",     "#F05032", "#fff"),
    ("DOCKER",  "#2496ED", "#fff"),
    ("VS CODE", "#007ACC", "#fff"),
    ("VERCEL",  "#ffffff", "#000"),
    ("ARDUINO", "#00979D", "#fff"),
    ("MQTT",    "#660066", "#fff"),
]

H       = 28      # badge height
R       = 5       # border radius
FS      = 11      # font size
GAP     = 10      # gap between badges
PX      = 14      # horizontal padding per side
CW      = 7.8     # approx char width (Verdana bold 11px)
SVG_W   = 860
SVG_H   = 96
ROW1_Y  = 10
ROW2_Y  = 58
FADE_W  = 70
BG      = "#0d1117"


def bw(text):
    return max(52, int(len(text) * CW + PX * 2))


def row_total_w(badges):
    return sum(bw(b[0]) for b in badges) + GAP * (len(badges) - 1)


def render_badges_svg(badges, y, x_start=0):
    parts = []
    x = x_start
    for text, bg, fg in badges:
        w = bw(text)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{H}" rx="{R}" fill="{bg}"/>'
        )
        tx = x + w // 2
        ty = y + H // 2 + 4
        parts.append(
            f'<text x="{tx}" y="{ty}" fill="{fg}" '
            f'font-family="Verdana,sans-serif" font-size="{FS}" '
            f'font-weight="bold" text-anchor="middle" '
            f'letter-spacing="0.8">{text}</text>'
        )
        x += w + GAP
    return parts, x


def generate():
    w1 = row_total_w(BADGES_ROW1)
    w2 = row_total_w(BADGES_ROW2)

    # Animation durations (pixels per second = 60)
    dur1 = round(w1 / 60, 1)
    dur2 = round(w2 / 60, 1)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">',
        # background
        f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}"/>',
        # defs: clip + gradients
        "<defs>",
        f'  <clipPath id="clip">',
        f'    <rect width="{SVG_W}" height="{SVG_H}"/>',
        f'  </clipPath>',
        f'  <linearGradient id="gl" x1="0" x2="1">',
        f'    <stop offset="0%" stop-color="{BG}"/>',
        f'    <stop offset="100%" stop-color="{BG}" stop-opacity="0"/>',
        f'  </linearGradient>',
        f'  <linearGradient id="gr" x1="1" x2="0">',
        f'    <stop offset="0%" stop-color="{BG}"/>',
        f'    <stop offset="100%" stop-color="{BG}" stop-opacity="0"/>',
        f'  </linearGradient>',
        "</defs>",
        # CSS animations
        "<style>",
        f'.r1{{animation:m1 {dur1}s linear infinite;}}',
        f'.r2{{animation:m2 {dur2}s linear infinite;}}',
        f'@keyframes m1{{from{{transform:translateX(0)}}to{{transform:translateX(-{w1 + GAP}px)}}}}',
        f'@keyframes m2{{from{{transform:translateX(-{w2 + GAP}px)}}to{{transform:translateX(0)}}}}',
        "</style>",
        # clip group
        '<g clip-path="url(#clip)">',
    ]

    # Row 1 — scroll left
    lines.append('<g class="r1">')
    el1, end1 = render_badges_svg(BADGES_ROW1, ROW1_Y, 0)
    el1b, _   = render_badges_svg(BADGES_ROW1, ROW1_Y, end1 + GAP)
    lines.extend(el1)
    lines.extend(el1b)
    lines.append("</g>")

    # Row 2 — scroll right
    lines.append('<g class="r2">')
    el2, end2 = render_badges_svg(BADGES_ROW2, ROW2_Y, 0)
    el2b, _   = render_badges_svg(BADGES_ROW2, ROW2_Y, end2 + GAP)
    lines.extend(el2)
    lines.extend(el2b)
    lines.append("</g>")

    lines.append("</g>")  # end clip

    # Fade overlays
    lines.append(f'<rect width="{FADE_W}" height="{SVG_H}" fill="url(#gl)"/>')
    lines.append(f'<rect x="{SVG_W - FADE_W}" width="{FADE_W}" height="{SVG_H}" fill="url(#gr)"/>')

    lines.append("</svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "marquee.svg"
    os.makedirs(os.path.dirname(out) if os.path.dirname(out) else ".", exist_ok=True)
    svg = generate()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {out}")
