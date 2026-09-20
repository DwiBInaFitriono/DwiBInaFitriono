#!/usr/bin/env python3
"""
Generate snake animation SVG that navigates through empty contribution cells.
Contribution cells = walls (dark green), empty cells = path for the snake.
"""
import os
import sys
import json
import urllib.request

USERNAME = os.environ.get("GITHUB_USER", "DwiBInaFitriono")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

CELL = 11
GAP = 3
STEP = CELL + GAP
SNAKE_LEN = 6
SPEED = 0.12   # seconds per cell

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_grid():
    payload = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())

    weeks = (
        data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    )
    grid = []
    for week in weeks:
        col = [day["contributionCount"] for day in week["contributionDays"]]
        while len(col) < 7:
            col.append(0)
        grid.append(col)
    return grid


def build_path(grid):
    """
    Boustrophedon traversal (column by column, alternating direction).
    Snake weaves up-down through every empty cell, treating filled cells as walls.
    """
    cols = len(grid)
    path = []
    for c in range(cols):
        row_order = range(7) if c % 2 == 0 else range(6, -1, -1)
        for r in row_order:
            if c < len(grid) and grid[c][r] == 0:
                path.append((c, r))
    return path


def generate_svg(grid, path, dark=True):
    cols = len(grid)
    W = cols * STEP + GAP
    H = 7 * STEP + GAP

    BG      = "#0d1117" if dark else "#ffffff"
    EMPTY   = "#161b22" if dark else "#ebedf0"
    WALLS   = ["#0e4429", "#006d32", "#26a641", "#39d353"] if dark \
              else ["#9be9a8", "#40c463", "#30a14e", "#216e39"]
    S_BODY  = "#58A6FF"
    S_HEAD  = "#ffffff"

    total    = len(path)
    duration = round(total * SPEED, 1)

    idx_map = {pos: i for i, pos in enumerate(path)}

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        "<style>",
    ]

    rects = []
    for c in range(cols):
        for r in range(7):
            x = c * STEP + GAP
            y = r * STEP + GAP
            cid = f"c{c}_{r}"

            if c < len(grid) and grid[c][r] > 0:
                level = min(grid[c][r], 4)
                base = WALLS[level - 1]
            else:
                base = EMPTY

            rects.append((cid, x, y, base))

            if (c, r) not in idx_map:
                continue

            idx = idx_map[(c, r)]
            p0 = idx / total * 100          # snake head arrives
            p1 = min((idx + 1) / total * 100, 100)          # head -> body
            p2 = min((idx + SNAKE_LEN) / total * 100, 100)  # body leaves
            p3 = min(p2 + 100 / total, 100)                  # fade back

            kf = []
            if p0 > 0:
                kf.append(f"0%{{fill:{base}}}")
                if p0 > 0.05:
                    kf.append(f"{p0 - 0.05:.2f}%{{fill:{base}}}")
            kf.append(f"{p0:.2f}%{{fill:{S_HEAD}}}")
            if p1 < p2:
                kf.append(f"{p1:.2f}%{{fill:{S_BODY}}}")
            kf.append(f"{p2:.2f}%{{fill:{S_BODY}}}")
            if p3 < 100:
                kf.append(f"{p3:.2f}%{{fill:{base}}}")
                kf.append(f"100%{{fill:{base}}}")

            name = f"a{c}_{r}"
            lines.append(f"@keyframes {name}{{{' '.join(kf)}}}")
            lines.append(
                f"#{cid}{{animation:{name} {duration}s linear infinite;}}"
            )

    lines.append("</style>")

    for cid, x, y, base in rects:
        lines.append(
            f'<rect id="{cid}" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" rx="2" fill="{base}"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    print(f"Fetching contributions for {USERNAME}...")
    grid = fetch_grid()
    print(f"Grid: {len(grid)} weeks")

    path = build_path(grid)
    print(f"Snake path: {len(path)} empty cells")

    os.makedirs("dist", exist_ok=True)

    for dark, suffix in [(True, "dark"), (False, "light")]:
        fname = (
            f"dist/github-contribution-grid-snake-{suffix}.svg"
            if suffix == "dark"
            else "dist/github-contribution-grid-snake.svg"
        )
        svg = generate_svg(grid, path, dark=dark)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Written: {fname}")


if __name__ == "__main__":
    main()
