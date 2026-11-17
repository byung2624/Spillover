"""Makes the S7.2 product images.

  focal_long_yellow.jpg   the focal shirt: long sleeves, high-visibility yellow
  rec_short_yellow.jpg    recommended shirt, same color as the focal shirt, short sleeves
  rec_long_black.jpg      recommended shirt, same sleeve length as the focal shirt, black
  sort_long_yellow.jpg, sort_short_black.jpg   the other two color x sleeve combinations (not on the pages)

Three photos go in:
  color reference   the hooded shirt used as the focal shirt in S7.1. Only its yellow is used
                    (from its shadows to its highlights), so the yellow is the same as in S7.1.
  focal base        a product photo of a plain long-sleeve tee on a light grey background: wide ribbed
                    collar, dropped shoulders, ribbed cuffs, side slits at the hem.
  rec base          a product photo of another plain long-sleeve crew-neck tee on white, with a narrow
                    collar and the sleeves hanging down. Both recommended shirts are made from this one,
                    so they look like a different product from the focal shirt and differ from each
                    other only in color and sleeve length.

What is changed in the photos:
  1. Color. The fabric's own light and dark (folds, seams, the knit's grain) is kept and only the color
     is replaced: yellow from the color reference, or dark greys for black.
  2. The brand labels inside the collar are removed, and the background is made white.
  3. For the short-sleeve versions, the sleeves are cut to a regular short-sleeve length (SLEEVE_OUTER,
     SLEEVE_INNER) and finished with a hem copied from the shirt's own bottom hem. Below the hem the
     side of the body is shown.

Usage: python3 make_images.py <color reference> <focal base> <rec base> <output folder>
"""
import pathlib
import sys

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, label

color_src, focal_src, rec_src, out = sys.argv[1], sys.argv[2], sys.argv[3], pathlib.Path(sys.argv[4])
out.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
# focal base (pixels of that photo)
FOCAL_LABEL_BOX = (716, 476, 818, 503)   # brand label and size tag inside the collar: left, top, right, bottom
FOCAL_DEPTH = 1.2                        # shadows relative to the photo's (folds show more on a light color)
FOCAL_MARGIN = 40                        # white margin around the shirt

# rec base (pixels after the photo is enlarged REC_ENLARGE times; the photo is small)
REC_ENLARGE = 2
REC_TAG_BOX = (334, 44, 384, 72)         # brand tag inside the collar
REC_DEPTH = 0.7                          # yellow: shadows relative to the photo's (this photo is more contrasty)
REC_CRISP, REC_GRAIN = 0.6, 0.5          # firming of folds and seams; fine grain (in lightness steps)
REC_MARGIN = 24
SLEEVE_OUTER, SLEEVE_INNER = 366, 398    # short sleeve: height of the hem at the outer edge and at the body
HEM_DEPTH = 30                           # height of the hem band copied from the bottom hem
HEM_OVERLAP = 3                          # how far the sleeve hem runs onto the body

YELLOW_TOP = 97.5                        # lightness (0-100) that the yellow's highlights level off under
BLACK_L, BLACK_DEPTH = 15.0, 0.85        # black: typical lightness; share of the photo's light-dark steps kept


def read(path):
    return cv2.imread(path, cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32)


def save(arr, name):
    cv2.imwrite(str(out / name), np.clip(arr, 0, 255).astype(np.uint8)[:, :, ::-1], [cv2.IMWRITE_JPEG_QUALITY, 95])


def sstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------------
# Colors. Work is done in Lab, where equal steps in lightness (L) look equally large.
# ----------------------------------------------------------------------------
def to_lab(rgb):
    return cv2.cvtColor(np.clip(rgb / 255.0, 0, 1).astype(np.float32), cv2.COLOR_RGB2Lab)


def to_rgb(lab):
    return cv2.cvtColor(lab.astype(np.float32), cv2.COLOR_Lab2RGB) * 255.0


# the yellow, from shadow to highlight, taken from the color reference
ref = read(color_src)
f_lab = to_lab(ref)[np.clip((255.0 - ref[..., 2]) / 90.0, 0, 1) > 0.98]
grid = np.percentile(f_lab[:, 0], np.linspace(1, 99, 50))
ramp = np.array([np.median(f_lab[np.abs(f_lab[:, 0] - g) <= 0.6], axis=0) for g in grid])
F_L = float(np.median(f_lab[:, 0]))


def yellow(depth):
    """The reference yellow, d lightness steps away from its typical lightness. Shadows are scaled by
    `depth`. Highlights are eased in under the brightest yellow the reference shows, so they do not burn out."""
    def color(d):
        room = YELLOW_TOP - F_L
        L = F_L + np.where(d < 0, depth * d, room * np.tanh(d / room))
        a = np.interp(L, grid, ramp[:, 1])
        b = np.interp(L, grid, ramp[:, 2])
        fade = np.clip(L / grid[0], 0, 1)                   # darker than the reference's darkest: lower the color with it
        return np.stack([L, a * fade, b * fade], axis=-1)
    return color


def black(d):
    room = BLACK_L - 3.0
    L = BLACK_L + BLACK_DEPTH * np.where(d > 0, d, room / BLACK_DEPTH * np.tanh(BLACK_DEPTH * d / room))
    return np.stack([L, np.zeros_like(L), np.full_like(L, -1.0)], axis=-1)


def recolor(img, al, solid, color, smooth=0.0, crisp=0.0, grain=0.0):
    """Replaces the fabric's color and puts the shirt on white. `solid` marks pixels that are fully fabric.
    For a small, enlarged photo: `smooth` eases its compression blocks, `crisp` firms up its soft folds
    and seams, and `grain` adds a fine knit-like grain, which the enlargement has blurred away."""
    L = to_lab(img)[..., 0]
    if smooth:
        L = gaussian_filter(L, smooth)
    if crisp:
        L = L + crisp * (L - gaussian_filter(L, 2.5))
    if grain:
        rng = np.random.default_rng(11)
        L = L + grain * gaussian_filter(rng.standard_normal(L.shape), 0.6) / 0.47
    d = L - np.median(L[solid])
    return to_rgb(color(d)) * al[..., None] + 255.0 * (1 - al[..., None])


def remove_label(img, box, radius, grain_from=None):
    """Fills a label inside the collar from the fabric around it, then gives it the fabric's grain."""
    x0, y0, x1, y1 = box
    mask = np.zeros(img.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = 255
    filled = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), mask, radius, cv2.INPAINT_TELEA).astype(np.float32)
    soft = gaussian_filter((mask > 0).astype(np.float32), radius / 4.0)[..., None]
    img = img * (1 - soft) + filled * soft
    if grain_from is not None:
        gx, gy = grain_from
        patch = img[gy:gy + (y1 - y0), gx:gx + (x1 - x0)]
        img[y0:y1, x0:x1] += patch - gaussian_filter(patch, sigma=(2.5, 2.5, 0))
    return img


def matte(img, bg, threshold):
    """Separates the shirt from the photo's background.
    Returns the photo with its edge pixels given the fabric's color (in the photo they are a mix of fabric
    and background, which would leave a pale fringe once recolored), how much of each pixel is shirt
    (0 to 1), and which pixels are fully fabric."""
    dist = np.abs(img - bg).max(axis=2)
    lab, _ = label(dist > threshold)
    shirt = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)       # the largest area: drops a logo in the corner
    outside, _ = label(~shirt)
    shirt = outside != outside[0, 0]                                 # fills holes, such as a white label in the collar
    solid = gaussian_filter(shirt.astype(np.float32), 1.5) > 0.97    # away from the edge
    wgt = gaussian_filter(solid.astype(np.float32), 3.0)
    near = wgt > 0.01
    fab_dist = gaussian_filter(dist * solid, 3.0) / np.maximum(wgt, 1e-3)
    fab_col = gaussian_filter(img * solid[..., None], sigma=(3.0, 3.0, 0)) / np.maximum(wgt, 1e-3)[..., None]
    al = np.where(solid, 1.0, np.clip(dist / np.maximum(0.9 * fab_dist, 1.0), 0, 1) * near).astype(np.float32)
    fab_col = np.where(near[..., None], fab_col, np.median(img[solid], axis=0))   # far from the shirt: its typical color
    img = np.where(solid[..., None], img, fab_col).astype(np.float32)
    return img, al, solid


def frame(res, al, margin):
    """Crops to the shirt and adds a white margin."""
    ys, xs = np.where(al > 0.5)
    res = res[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return cv2.copyMakeBorder(res, margin, margin, margin, margin, cv2.BORDER_CONSTANT, value=(255.0, 255.0, 255.0))


# ----------------------------------------------------------------------------
# The focal shirt
# ----------------------------------------------------------------------------
def make_focal():
    img = read(focal_src)
    bg = np.median(np.concatenate([img[:40, -200:].reshape(-1, 3), img[-40:, :200].reshape(-1, 3)]), axis=0)
    img, al, solid = matte(img, bg, 14)
    img = remove_label(img, FOCAL_LABEL_BOX, 7, grain_from=(FOCAL_LABEL_BOX[0], FOCAL_LABEL_BOX[3] + 12))
    res = recolor(img, al, solid, yellow(FOCAL_DEPTH))
    return frame(res, al, FOCAL_MARGIN)


# ----------------------------------------------------------------------------
# The recommended shirts
# ----------------------------------------------------------------------------
rec = read(rec_src)
rec = np.clip(cv2.resize(rec, None, fx=REC_ENLARGE, fy=REC_ENLARGE, interpolation=cv2.INTER_LANCZOS4), 0, 255)
H, W, _ = rec.shape
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rec, rec_al, rec_solid = matte(rec, np.array([255.0, 255.0, 255.0], np.float32), 40)
rec = remove_label(rec, REC_TAG_BOX, 5)


def short_sleeve_left(img, al):
    """Cuts the left sleeve to short-sleeve length and hems it. Works on the left side of whatever
    it is given, so the right sleeve is done by passing the mirrored image."""
    img, al = img.copy(), al.copy()
    fab = al > 0.5
    rows = np.arange(H, dtype=np.float32)
    outer_x = gaussian_filter(np.argmax(fab, axis=1).astype(np.float32), 2)          # the sleeve's outer edge, per row
    # the body's side edge, where it shows beside the sleeve: the start of the second run of fabric in a row
    ys, xs = [], []
    for y in range(int(H * 0.52), int(H * 0.92), 2):
        r = fab[y, : W // 2]
        gaps = np.where(~r[1:] & r[:-1])[0]
        if len(gaps):
            ys.append(y), xs.append(np.argmax(r[gaps[0] + 1:]) + gaps[0] + 1)
    slope, base = np.polyfit(ys, xs, 1)
    body = lambda y: base + slope * y
    split = min(ys)
    while split > SLEEVE_INNER:                                                       # first row with a gap
        r = fab[split - 1, : W // 2]
        gaps = np.where(~r[1:] & r[:-1])[0]
        if not len(gaps) or gaps[0] > body(split) + 6:
            break
        split -= 1
    # line between the sleeve and the body: the body's edge below the split, straight up above it
    line = np.where(yy >= split, body(yy) - 1.0, body(split) - 1.0)

    p_out = np.array([outer_x[SLEEVE_OUTER], SLEEVE_OUTER], np.float32)
    p_in = np.array([body(split) - 1.0 + HEM_OVERLAP, SLEEVE_INNER], np.float32)
    length = float(np.hypot(*(p_in - p_out)))
    e = (p_in - p_out) / length                                                       # along the hem, toward the body
    n = np.array([e[1], -e[0]], np.float32)                                           # up the sleeve
    u = ((xx - p_out[0]) * e[0] + (yy - p_out[1]) * e[1]) / length
    v = (xx - p_out[0]) * n[0] + (yy - p_out[1]) * n[1]                               # pixels above the hem

    # the hem band, taken from the bottom hem of the body
    sx = body(H * 0.9) + 14.0 + u * length
    bottom = gaussian_filter((H - 1 - np.argmax(fab[::-1, :], axis=0)).astype(np.float32), 2)   # last fabric row
    sy = np.interp(sx, np.arange(W), bottom) - np.maximum(v, 2.0)                      # never below the hem's edge
    band = cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    band_al = cv2.remap(al, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    lum = lambda a: 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    low = lambda a: gaussian_filter(a, 5)
    match = (low(lum(img) * al) / np.maximum(low(al), 1e-3)) / np.maximum(low(lum(band) * band_al) / np.maximum(low(band_al), 1e-3), 1)
    band = band * np.clip(match, 0.8, 1.25)[..., None]

    sleeve = np.clip(line + HEM_OVERLAP - xx + 0.5, 0, 1) * (u > -0.1) * (u < 1.1)
    w = sstep((HEM_DEPTH - v) / 8.0) * (v > -3) * sleeve * sstep((line + HEM_OVERLAP - xx) / 3.0)
    img = img * (1 - w[..., None]) + band * w[..., None]
    near_edge = (v > -3) & (v < 3) & (sleeve > 0)
    al = np.where(near_edge, np.minimum(al, np.clip(v + 0.5, 0, 1)), al)             # a clean edge along the hem
    # nothing below the hem, left of the line
    below = np.clip(-v - 2.5, 0, 1) * np.clip(line - xx + 0.5, 0, 1) * (yy > SLEEVE_OUTER - 40)
    al = al * (1 - below)
    # the side of the body that was under the sleeve: replace the fold's dark line with fabric from
    # just inside, then shade it slightly, like an edge
    into = xx - line
    inner = np.roll(img, -6, axis=1)
    w = sstep((5 - into) / 3.0) * (into >= -1.5) * (v < -2) * sstep((split + 14 - yy) / 8.0)
    img = img * (1 - w[..., None]) + inner * w[..., None]
    side = np.exp(-(np.maximum(into, 0) / 2.0) ** 2) * (into >= -0.5) * (v < 0) * (yy < split + 6)
    img = img * (1 - 0.07 * side)[..., None]
    return img, al


def short_sleeves(img, al):
    img, al = short_sleeve_left(img, al)
    img, al = short_sleeve_left(img[:, ::-1], al[:, ::-1])
    return img[:, ::-1], al[:, ::-1]


def make_rec(short, color):
    img, al = short_sleeves(rec, rec_al) if short else (rec, rec_al)
    res = recolor(img, al, rec_solid, color, smooth=1.0, crisp=REC_CRISP, grain=REC_GRAIN)
    return frame(res, rec_al, REC_MARGIN)                                 # same crop for long and short sleeves


save(make_focal(), "focal_long_yellow.jpg")
save(make_rec(True, yellow(REC_DEPTH)), "rec_short_yellow.jpg")
save(make_rec(False, black), "rec_long_black.jpg")
save(make_rec(False, yellow(REC_DEPTH)), "sort_long_yellow.jpg")
save(make_rec(True, black), "sort_short_black.jpg")
print("ok")
