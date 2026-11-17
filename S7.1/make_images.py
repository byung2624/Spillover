"""Makes the three product images for Study 5 from one base photo.

  focal_long_yellow.jpg   the base photo, unchanged
  rec_short_yellow.jpg    recommended shirt, same color as the focal shirt, short sleeves
  rec_long_black.jpg      recommended shirt, same sleeve length as the focal shirt, black

The two recommended shirts should look like another brand's product, so they also
differ from the focal photo in ways that do not bear on color or sleeve length:
mirrored, crew neck instead of a hood, smoother fabric, flatter shading with its
own folds, a slimmer cut, and a looser crop. These changes are the same for both
recommended shirts, so the two still differ from each other only in color and sleeves.

Usage: python3 make_images.py <base photo> <output folder>
"""
import pathlib
import sys

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

src, out = sys.argv[1], pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
base = cv2.imread(src, cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32)   # RGB
H, W, _ = base.shape
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
SS = 4                                                                     # supersampling for drawn shapes


def save(arr, name):
    cv2.imwrite(str(out / name), np.clip(arr, 0, 255).astype(np.uint8)[:, :, ::-1],
                [cv2.IMWRITE_JPEG_QUALITY, 93])


def coverage(img):
    """How much of each pixel is fabric (1) rather than white background (0)."""
    return np.clip((255.0 - img[..., 2]) / 90.0, 0, 1)


def lum(img):
    return 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


def sstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def bezier(p0, p1, p2, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t ** 2 * np.array(p2)


def poly_mask(points):
    m = np.zeros((H * SS, W * SS), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(points) * SS).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def line_mask(points, width):
    m = np.zeros((H * SS, W * SS), np.uint8)
    cv2.polylines(m, [np.round(np.array(points) * SS).astype(np.int32)], False, 255,
                  thickness=max(1, int(round(width * SS))), lineType=cv2.LINE_AA)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def black_version(img):
    """Keeps the photo's shading and changes only the color."""
    al = coverage(img)
    l = lum(img)
    p5, p50, p95 = np.percentile(l[al > 0.98], [5, 50, 95])
    g = np.interp(l, [p5 - 60, p5 - 25, p5, p50, p95, p95 + 25], [6, 13, 23, 40, 58, 70])
    blk = np.stack([g, g, g + 3], axis=-1)
    return al[..., None] * blk + (1 - al[..., None]) * 255.0


def shorten_sleeves(img, al):
    """Cuts both sleeves just below the underarm and adds a hem."""
    img = img.copy()
    al = al.copy()
    for side in ("L", "R"):
        if side == "L":
            region, u = xx <= 127, (xx - 1) / 115
        else:
            region, u = xx >= 480, (606 - xx) / 115
        hem_y = 404 + 5 * np.sin(np.clip(u, 0, 1) * np.pi) - 4 * u
        active = region & (yy > 372)
        below = np.clip(yy - hem_y + 0.5, 0, 1) * active
        al *= (1 - below)
        d = hem_y - yy
        edge = np.exp(-(d / 2.2) ** 2) * (d >= -0.5) * active
        stitch = np.exp(-((d - 11) / 0.9) ** 2) * active
        fold = np.clip(1 - np.abs(d - 5.5) / 5.5, 0, 1) * active
        img *= (1 - 0.20 * edge - 0.13 * stitch - 0.035 * fold)[..., None]
    return img, al


def recommended(short, black, seed=7):
    rng = np.random.default_rng(seed)
    a = base[:, ::-1].copy()                                  # mirrored
    al = coverage(a)
    c0 = np.median(a[al > 0.98], axis=0)                       # typical fabric color
    cx = 303.5

    # ---- crew neck in place of the hood -------------------------------------------------
    NL, NR = (230.0, 36.0), (377.0, 36.0)                      # where the collar meets the shoulders
    NLi, NRi = (243.0, 35.0), (364.0, 35.0)
    slope = 0.40
    def shoulder(d):                                           # straight near the neck, rounding off toward the sleeve
        return NL[1] + d * slope + 0.0035 * np.maximum(d - 85, 0) ** 2
    top = np.where(xx <= NL[0], shoulder(NL[0] - xx),
          np.where(xx >= NR[0], shoulder(xx - NR[0]),
                   NL[1] - 1 - 6 * np.sin(np.clip((xx - NLi[0]) / (NRi[0] - NLi[0]), 0, 1) * np.pi)))
    edge = gaussian_filter(np.argmax(al > 0.5, axis=0).astype(np.float32), 2)   # the photo's own top edge
    k = 0.15                                                   # rounds the shoulder where the two edges meet
    top = np.log(np.exp(k * top) + np.exp(k * edge[None, :])) / k
    keep = np.clip(yy - top + 0.5, 0, 1)

    # clean fabric over the upper chest and shoulders, where the hood lay
    ref = np.zeros((W, 3), np.float32)
    band = a[150:166]
    bal = al[150:166][..., None]
    ref = (band * bal).sum(0) / np.maximum(bal.sum(0), 1e-3)
    good = bal.sum(0)[:, 0] > 8
    for c in range(3):
        ref[:, c] = np.interp(np.arange(W), np.arange(W)[good], ref[good, c])
    ref = gaussian_filter(ref, sigma=(9, 0))
    fill = np.broadcast_to(ref[None, :, :], a.shape) * (1 - 0.02 * sstep((150 - yy) / 110))[..., None]
    w = sstep((160 - yy) / 26) * sstep((206 - np.abs(xx - cx)) / 40)
    a = a * (1 - w[..., None]) + fill * w[..., None]
    al = np.maximum(al, w * (keep > 0)) * keep                 # the old tag area is fabric now

    back = bezier(NLi, (cx, 22.0), NRi)                        # top edge of the back collar
    back_low = bezier((NLi[0] + 2, NLi[1] + 9), (cx, 35.0), (NRi[0] - 2, NRi[1] + 9))
    outer = bezier(NL, (cx, 138.0), NR)                        # lower edge of the front band
    inner = bezier(NLi, (cx, 113.0), NRi)                      # upper edge of the front band
    m_open = poly_mask(list(back) + list(inner[::-1]))
    m_backband = poly_mask(list(back) + list(back_low[::-1])) * m_open
    m_band = poly_mask([NL] + list(outer) + [NR, NRi] + list(inner[::-1]) + [NLi])

    shade = 0.76 - 0.20 * sstep((yy - 32) / 45)                # inside of the back, darker lower down
    a = a * (1 - m_open[..., None]) + (c0 * shade[..., None]) * m_open[..., None]
    a = a * (1 - m_backband[..., None]) + (c0 * 0.84) * m_backband[..., None]
    a *= (1 - 0.30 * line_mask(back_low, 1.2) * m_open)[..., None]
    ribs = 1 + 0.03 * np.sin(xx * 2.1)
    a = a * (1 - m_band[..., None]) + (c0 * 0.93 * ribs[..., None]) * m_band[..., None]
    a *= (1 - 0.24 * line_mask(outer, 1.4))[..., None]
    a *= (1 - 0.20 * line_mask(inner, 1.2))[..., None]
    under = gaussian_filter(np.roll(m_band, 5, axis=0), 4.5) * (1 - m_band) * (1 - m_open)
    a *= (1 - 0.16 * under)[..., None]
    al = np.maximum(al, np.maximum(m_open, m_band))
    tag = poly_mask([(cx - 8, 44), (cx + 8, 44), (cx + 8, 57), (cx - 8, 57)])
    a = a * (1 - tag[..., None]) + 246.0 * tag[..., None]
    a *= (1 - 0.35 * line_mask([(cx - 5, 50), (cx + 5, 50)], 1.0))[..., None]

    if short:
        a, al = shorten_sleeves(a, al)

    # ---- different fabric and shading ---------------------------------------------------
    sm = gaussian_filter(a * al[..., None], sigma=(1.25, 1.25, 0)) / np.maximum(
        gaussian_filter(al, 1.25), 1e-3)[..., None]
    a = np.where((al > 0.6)[..., None], 0.65 * sm + 0.35 * a, a)      # softens the mesh weave
    l = lum(a)
    low = gaussian_filter(l * al, 20) / np.maximum(gaussian_filter(al, 20), 1e-3)
    gain = (np.maximum(low, 1) / np.median(low[al > 0.98])) ** -0.35   # flatter overall shading
    gain *= 1 + 0.03 * (xx - cx) / 300 - 0.02 * (yy - 340) / 340       # light from another side
    folds = [  # (x0, y0, x1, y1, width, strength): soft creases in new places
        (250, 250, 205, 520, 13, -0.050), (345, 300, 395, 600, 15, 0.035),
        (300, 420, 330, 640, 11, -0.035), (190, 330, 175, 470, 9, 0.030),
        (70, 220, 50, 330, 8, -0.035), (540, 230, 562, 340, 8, 0.030),
    ]
    for x0, y0, x1, y1, wd, st in folds:
        dx, dy = x1 - x0, y1 - y0
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (dx * dx + dy * dy), 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        gain *= 1 + st * np.exp(-(d / wd) ** 2) * np.maximum(np.sin(np.pi * t), 0) ** 0.7
    a *= gain[..., None]
    a *= (c0 / np.median(a[al > 0.98], axis=0))[None, None, :]         # same color as the focal shirt
    a += gaussian_filter(rng.standard_normal((H, W)), 0.6)[..., None] * 1.6   # fine grain
    img = a * al[..., None] + 255.0 * (1 - al[..., None])

    # ---- slimmer cut, looser crop -------------------------------------------------------
    new_w = int(round(W * 0.93))
    img = cv2.resize(np.clip(img, 0, 255), (new_w, H), interpolation=cv2.INTER_AREA)
    canvas = np.full((H + 70, W + 60, 3), 255.0, np.float32)
    x0 = (canvas.shape[1] - new_w) // 2
    canvas[20:20 + H, x0:x0 + new_w] = img
    return black_version(canvas) if black else canvas


save(base, "focal_long_yellow.jpg")
save(recommended(short=True, black=False), "rec_short_yellow.jpg")
save(recommended(short=False, black=True), "rec_long_black.jpg")
# two more shirts in the same style, used only in the survey's sorting task (2 colors x 2 sleeve lengths)
save(recommended(short=False, black=False), "sort_long_yellow.jpg")
save(recommended(short=True, black=True), "sort_short_black.jpg")
print("ok")
