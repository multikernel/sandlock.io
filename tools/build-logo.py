#!/usr/bin/env python3
"""Generate the sandlock logo assets from the master raster.

    pip install --user potracer pillow numpy
    tools/build-logo.py tools/sandlock-logo-source.png

Produces, in assets/images/:

    sandlock-mark.svg          shield only, brand colours (light backgrounds, favicon)
    sandlock-mark-inverse.svg  shield only, light steel (the navy site chrome)
    sandlock-logo.svg          full lockup, brand colours
    sandlock-logo.png          full lockup, transparent background
    og-image.png               1200x630 social card, lockup on navy

Two notes on the tracing, both learned the hard way. potracer treats high
values as white, so every mask is inverted before it is handed over. And a
shape touching the crop edge makes it emit a spurious full-canvas border
curve, so masks are padded with background first.
"""

import os
import sys

import numpy as np
import potrace
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images")
PAD = 2

# Brand palette, sampled from the master.
BLUE = "#265978"
ORANGE = "#cf6819"
# Lightened for the navy header and footer, where BLUE is near-invisible.
BLUE_INV = "#9cc2dd"
ORANGE_INV = "#e08a3c"
NAVY = (14, 30, 51)

# Element bounds in the master, found by scanning for rows that carry ink.
MARK = (523, 93, 885, 510)      # the shield
FULL = (352, 93, 1057, 695)     # shield + wordmark + tagline


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.int16)


def layers(a, box):
    """Split a crop into its blue and orange masks."""
    c = a[box[1]:box[3], box[0]:box[2]]
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    orange = (r > 110) & (r - b > 60) & (r - g > 35)
    inked = c.min(axis=2) < 200
    return inked & ~orange, orange, c.shape[1], c.shape[0]


def trace_d(mask, scale, offx, offy, turdsize):
    padded = np.pad(~mask, PAD, constant_values=True)
    x = lambda v: (v - PAD) * scale + offx
    y = lambda v: (v - PAD) * scale + offy
    out = []
    for curve in potrace.Bitmap(padded).trace(
        turdsize=turdsize, alphamax=1.0, opticurve=True, opttolerance=0.2
    ):
        p = curve.start_point
        out.append(f"M{x(p.x):.2f},{y(p.y):.2f}")
        for s in curve.segments:
            e = s.end_point
            if s.is_corner:
                out.append(f"L{x(s.c.x):.2f},{y(s.c.y):.2f}L{x(e.x):.2f},{y(e.y):.2f}")
            else:
                out.append(
                    f"C{x(s.c1.x):.2f},{y(s.c1.y):.2f} "
                    f"{x(s.c2.x):.2f},{y(s.c2.y):.2f} {x(e.x):.2f},{y(e.y):.2f}"
                )
        out.append("Z")
    return "".join(out)


def svg(a, box, name, blue, orange, label, vb_w, vb_h, pad, turdsize=4):
    bl, og, w, h = layers(a, box)
    # Contain the artwork in the viewBox and centre it on both axes.
    scale = min((vb_w - 2 * pad) / w, (vb_h - 2 * pad) / h)
    offx = (vb_w - w * scale) / 2
    offy = (vb_h - h * scale) / 2
    body = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" '
        f'fill="none" role="img" aria-label="{label}">\n'
        f'  <path fill="{blue}" fill-rule="evenodd" d="{trace_d(bl, scale, offx, offy, turdsize)}"/>\n'
        f'  <path fill="{orange}" fill-rule="evenodd" d="{trace_d(og, scale, offx, offy, turdsize)}"/>\n'
        f"</svg>\n"
    )
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        fh.write(body)
    print(f"  {name}  {len(body):,} bytes")


def transparent(src, box):
    """Recover straight alpha from ink composited over a white background."""
    c = np.asarray(Image.open(src).convert("RGB")).astype(np.float64)
    c = c[box[1]:box[3], box[0]:box[2]]
    alpha = 255.0 - c.min(axis=2)
    safe = np.maximum(alpha, 1.0)[..., None]
    rgb = np.clip((c - 255.0 * (1.0 - safe / 255.0)) / (safe / 255.0), 0, 255)
    out = np.dstack([rgb, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def main():
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <master.png>")
    src = sys.argv[1]
    a = load(src)
    print(f"source {src}")

    svg(a, MARK, "sandlock-mark.svg", BLUE, ORANGE, "Sandlock", 256, 256, 6, turdsize=9)
    svg(a, MARK, "sandlock-mark-inverse.svg", BLUE_INV, ORANGE_INV, "Sandlock", 256, 256, 6, turdsize=9)
    svg(a, FULL, "sandlock-logo.svg", BLUE, ORANGE,
        "Sandlock, a Linux process sandbox", 512, 438, 8, turdsize=6)

    lockup = transparent(src, FULL)
    lockup.thumbnail((880, 880), Image.LANCZOS)
    lockup.save(os.path.join(OUT, "sandlock-logo.png"), optimize=True)
    print(f"  sandlock-logo.png  {lockup.size[0]}x{lockup.size[1]}")

    # Social card: the lockup, inverted to read on navy, centred on 1200x630.
    card = Image.new("RGBA", (1200, 630), NAVY + (255,))
    art = transparent(src, FULL)
    rgba = np.asarray(art).astype(np.float64)
    ink = rgba[..., :3]
    is_orange = (ink[..., 0] > 110) & (ink[..., 0] - ink[..., 2] > 60)
    ink[~is_orange] = [232, 238, 244]
    ink[is_orange] = [224, 138, 60]
    art = Image.fromarray(np.dstack([ink, rgba[..., 3]]).astype(np.uint8), "RGBA")
    art.thumbnail((760, 460), Image.LANCZOS)
    card.alpha_composite(art, ((1200 - art.size[0]) // 2, (630 - art.size[1]) // 2))
    card.convert("RGB").save(os.path.join(OUT, "og-image.png"), optimize=True)
    print("  og-image.png  1200x630")


if __name__ == "__main__":
    main()
