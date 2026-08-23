import base64
import os

SRC_IMAGE = "/home/claude/banner_resized.jpg"
OUT_SVG = "/home/claude/animated-github-banner.svg"

CYAN = "#39c8ff"
BLUE = "#3b6fff"
PURPLE = "#a855f7"
GREEN = "#39ff8f"

WIDTH, HEIGHT = 1000, 354

# Roles cycle in place of the static "BSc (Hons) Computing Student" label.
ROLES = [
    "BSc (Hons) Computing Student",
    "Full-Stack Developer",
    "Open Source Contributor",
    "Problem Solver // Builder",
]
ROLE_HOLD = 2.2          # seconds each role stays fully visible
ROLE_FADE = 0.55         # seconds of the crossfade transition
ROLE_CYCLE = len(ROLES) * (ROLE_HOLD + ROLE_FADE)

# Bounding box of the original "BSc (Hons) Computing Student" text in the
# 1000x354 source image (measured via pixel-diff against the panel
# background), used to paint over it and re-draw animated text in its place.
ROLE_BOX = dict(x=428, y=120, w=310, h=50)
ROLE_BG_COLOR = "#10173f"
ROLE_TEXT_X = 436
ROLE_TEXT_Y = 149
ROLE_UNDERLINE_Y = 160
ROLE_UNDERLINE_X1 = 436
ROLE_UNDERLINE_X2 = 706


def b64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("ascii")


def build():
    img_b64 = b64_image(SRC_IMAGE)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    )

    # ---------------- defs ----------------
    parts.append('<defs>')
    parts.append(f'''
    <linearGradient id="borderCycle" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{CYAN}">
        <animate attributeName="stop-color" values="{CYAN};{PURPLE};{GREEN};{BLUE};{CYAN}" dur="9s" repeatCount="indefinite"/>
      </stop>
      <stop offset="50%" stop-color="{PURPLE}">
        <animate attributeName="stop-color" values="{PURPLE};{GREEN};{BLUE};{CYAN};{PURPLE}" dur="9s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{BLUE}">
        <animate attributeName="stop-color" values="{BLUE};{CYAN};{PURPLE};{GREEN};{BLUE}" dur="9s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>

    <linearGradient id="scanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{CYAN}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>

    <linearGradient id="sweepGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>

    <filter id="glowB" x="-200%" y="-200%" width="500%" height="500%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <clipPath id="frameClip">
      <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="14"/>
    </clipPath>
    ''')
    parts.append('</defs>')

    parts.append(f'<g clip-path="url(#frameClip)">')

    # ---- base image ----
    parts.append(
        f'<image href="data:image/jpeg;base64,{img_b64}" x="0" y="0" '
        f'width="{WIDTH}" height="{HEIGHT}" preserveAspectRatio="xMidYMid slice"/>'
    )

    # ---- cover the original static "BSc (Hons) Computing Student" text ----
    parts.append(
        f'<rect x="{ROLE_BOX["x"]}" y="{ROLE_BOX["y"]}" width="{ROLE_BOX["w"]}" '
        f'height="{ROLE_BOX["h"]}" fill="{ROLE_BG_COLOR}"/>'
    )
    # redraw the static underline accent so the label area still reads as designed
    parts.append(
        f'<line x1="{ROLE_UNDERLINE_X1}" y1="{ROLE_UNDERLINE_Y}" '
        f'x2="{ROLE_UNDERLINE_X2}" y2="{ROLE_UNDERLINE_Y}" '
        f'stroke="#eaf2ff" stroke-opacity="0.75" stroke-width="1.4"/>'
    )

    # ---- cycling role text: crossfades through each role, looping forever ----
    n = len(ROLES)
    for i, role in enumerate(ROLES):
        start = i * (ROLE_HOLD + ROLE_FADE)
        fade_in_end = start + ROLE_FADE
        hold_end = fade_in_end + ROLE_HOLD
        fade_out_end = hold_end + ROLE_FADE

        key_times = [0, start / ROLE_CYCLE, fade_in_end / ROLE_CYCLE,
                     hold_end / ROLE_CYCLE, fade_out_end / ROLE_CYCLE, 1]
        # guard against float drift causing non-monotonic keyTimes
        for k in range(1, len(key_times)):
            if key_times[k] <= key_times[k - 1]:
                key_times[k] = key_times[k - 1] + 0.0001
        key_times[-1] = 1
        values = [0, 0, 1, 1, 0, 0]

        kt_str = ";".join(f"{t:.4f}" for t in key_times)
        val_str = ";".join(str(v) for v in values)

        parts.append(
            f'<text x="{ROLE_TEXT_X}" y="{ROLE_TEXT_Y}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="15" '
            f'font-weight="700" letter-spacing="0.8" fill="#eaf2ff" opacity="0" '
            f'filter="url(#glowB)">{role}'
            f'<animate attributeName="opacity" begin="0s" dur="{ROLE_CYCLE:.3f}s" '
            f'repeatCount="indefinite" keyTimes="{kt_str}" values="{val_str}"/>'
            f'</text>'
        )

    # ---- diagonal light sweep across the whole banner ----
    parts.append(
        f'<rect x="{-WIDTH}" y="0" width="{WIDTH*0.5}" height="{HEIGHT}" '
        f'fill="url(#sweepGrad)" transform="skewX(-20)">'
        f'<animate attributeName="x" values="{-WIDTH};{WIDTH*1.3}" dur="6s" '
        f'repeatCount="indefinite" begin="0s"/>'
        f'</rect>'
    )

    # ---- vertical HUD scanline sweeping top to bottom ----
    parts.append(
        f'<rect x="0" y="-40" width="{WIDTH}" height="40" fill="url(#scanGrad)">'
        f'<animate attributeName="y" values="{-40};{HEIGHT}" dur="3.4s" '
        f'repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- drifting matrix-style particles (extra sparkle layered on top) ----
    import random
    random.seed(7)
    for i in range(26):
        px = random.uniform(20, WIDTH - 20)
        py = random.uniform(20, HEIGHT * 0.55)
        r = random.uniform(1.1, 2.3)
        color = random.choice([GREEN, CYAN])
        dur = random.uniform(1.8, 3.6)
        delay = random.uniform(0, 3)
        parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur:.2f}s" '
            f'begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # ---- energy pulses traveling along circuit-style trace paths (left & right) ----
    left_path = f"M 10,{HEIGHT-10} L 10,{HEIGHT*0.68} L 90,{HEIGHT*0.58} L 90,{HEIGHT*0.40}"
    right_path = f"M {WIDTH-10},{HEIGHT-10} L {WIDTH-10},{HEIGHT*0.68} L {WIDTH-90},{HEIGHT*0.58} L {WIDTH-90},{HEIGHT*0.40}"

    for path_id, d in [("leftTrace", left_path), ("rightTrace", right_path)]:
        parts.append(f'<path id="{path_id}" d="{d}" fill="none" stroke="none"/>')

    for i in range(3):
        for path_id, color, dur in [
            ("leftTrace", CYAN, 2.6 + i * 0.4),
            ("rightTrace", PURPLE, 2.9 + i * 0.4),
        ]:
            begin = i * (dur / 3)
            parts.append(
                f'<circle r="3" fill="{color}" filter="url(#glowB)">'
                f'<animateMotion dur="{dur:.2f}s" repeatCount="indefinite" begin="{begin:.2f}s">'
                f'<mpath href="#{path_id}"/>'
                f'</animateMotion>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" '
                f'dur="{dur:.2f}s" repeatCount="indefinite" begin="{begin:.2f}s"/>'
                f'</circle>'
            )

    # ---- pulsing glow along the neon horizon line area (subtle breathing light) ----
    parts.append(
        f'<rect x="0" y="{HEIGHT*0.66}" width="{WIDTH}" height="3" fill="{CYAN}" opacity="0.35" filter="url(#glowB)">'
        f'<animate attributeName="opacity" values="0.2;0.55;0.2" dur="2.4s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    parts.append('</g>')  # end clipped content

    # ---- animated neon frame border on top ----
    parts.append(
        f'<rect x="2" y="2" width="{WIDTH-4}" height="{HEIGHT-4}" rx="13" '
        f'fill="none" stroke="url(#borderCycle)" stroke-width="3" filter="url(#glowB)"/>'
    )

    parts.append('</svg>')
    return "".join(parts)


if __name__ == "__main__":
    svg = build()
    with open(OUT_SVG, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_SVG} ({len(svg)/1024:.1f} KB)")
