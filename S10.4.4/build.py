#!/usr/bin/env python3
"""Builds the S10.4.4 stimulus pages.

S10.4.4 is S10.4.2 with four changes, all aimed at a lower evaluation of the recommended backpack when the helmet is rated 3.1 stars:
  1. the backpack's own rating is 3.5 stars (was 4.0);
  2. the three individual helmet reviews show 1, 1 and 2 stars at 3.1 stars (were 3, 3, 3) and 5, 5 and 4 stars at 4.9 stars (were 5, 5, 5),
     and the review summary reads "3.1 out of 5" / "4.9 out of 5";
  3. the backpack is a plainer one (new photo) and its name drops "Everyday";
  4. the backpack costs $13.90 (was $49.99). The helmet stays at $49.99.
S10.4.2 used the S10.4 pages unchanged.
S10.4 is S10.1 with one change: the recommended backpack's photo is a plain backpack with no reflective tape
(the photo used in S10.2 and S10.3). Everything else on the page is as in S10.1.
Products, in the same page layout as S9.8:
  - focal product: "Telvane Bike Helmet, Fluorescent Yellow" (a vented bike helmet);
  - recommended product: "JUVARO Backpack, Fluorescent Yellow", under "New arrivals - Sponsored".
The helmet costs $49.99 and the backpack $13.90. The two products are different kinds of product; what they share is the fluorescent yellow color.
"About this item" has four lines. The first two point to what the vents and the color do ("force air through the helmet and
reduce sweating", "stays bright on the road, day or night") without using any wording from the shopping goals (no drivers, notice, cool, or heat).
There is no brand line.
Individual reviews show their stars, the reviewer's name, and the date, with no review text (as in S9.6-S9.8).

Design: 2 (focal product rating: 3.1 vs. 4.9 stars)
      x 2 (shopping goal: bike gear to help drivers notice you on the road after dark
           vs. bike gear to help you stay cool on the road on hot afternoons)
The goal is set by the shopping task in the survey, not on the page, so the same page serves both goals.
There are two pages, one per rating: s1044_31.html and s1044_49.html.

Images (in img/): focal_helmet.jpg (brand lettering removed from the visor) and rec_backpack.jpg (a plain school-style backpack with
no reflective parts; leather patch removed from the front; recolored from neon green to the helmet's fluorescent yellow).

Usage:  python3 build.py <image folder> <output folder>
Output: two self-contained pages named  s1044_<rating>.html  and an index.html.
Each page holds its own styles and images. There are no outside files, links, or scripts.

To change wording, edit the block below and run the script again.
"""
import base64
import html
import pathlib
import sys

IMG = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("img")
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("out")

# ----------------------------------------------------------------------------
# Content. Edit here.
# ----------------------------------------------------------------------------
FOCAL_BRAND = "Telvane"        # made-up brand of the focal product
REC_BRAND = "JUVARO"               # made-up brand of the recommended product
PRICE = ("49", "99")           # focal product: dollars, cents
REC_PRICE = ("13", "90")       # recommended product: dollars, cents
N_RATINGS = "473"              # focal rating count; same in both rating conditions
REC_RATING = 3.5               # recommended product's own rating; same on every page
REC_HEADER = "New arrivals"   # header above the recommended product, followed by a small grey "Sponsored" tag
REC_N_RATINGS = "451"          # recommended product's rating count; same on every page, close to the focal count

RATINGS = {"31": 3.1, "49": 4.9}

FOCAL = {"image": "focal_helmet.jpg",
         "name": "Bike Helmet, Fluorescent Yellow"}

RECS = {
    "backpack": {"image": "rec_backpack.jpg", "name": "Backpack, Fluorescent Yellow"},
}

# Constant on every page. The first two lines point to what the vents and the color do, without using any wording
# from the shopping goals (no "drivers", "notice", "spot", "cool", "heat", or "hot").
DESCRIPTION = [
    "17 large air vents force air through the helmet and reduce sweating",
    "Fluorescent yellow finish stays bright on the road, day or night",
    "Lightweight, 9.5 oz",
    "Dial at the back for a snug fit",
]

# Individual reviews of the focal helmet, with no review text (S9.6): each shows its stars, the reviewer's name,
# and the date. Same reviewers and dates in both rating conditions; only the stars differ.
REVIEWERS = [("Robert C.", "November 9, 2026"), ("Lisa T.", "November 5, 2026"), ("Mark D.", "November 2, 2026")]
REVIEW_STARS = {"31": [1, 1, 2], "49": [5, 5, 4]}

LABELS = {
    "rating": {"31": "3.1 stars", "49": "4.9 stars"},
    "rec": {"backpack": "Backpack, fluorescent yellow"},
}

# Layout note: the card under the recommendation header has a fixed minimum height (see ".card{min-height" in CSS),
# equal to its height when the product name takes two lines. A one-line name then sits right above the stars,
# and the spare room goes below the price, so all four pages keep the same height.
# ----------------------------------------------------------------------------
# Pieces
# ----------------------------------------------------------------------------
def data_uri(name):
    return "data:image/jpeg;base64," + base64.b64encode((IMG / name).read_bytes()).decode("ascii")


STAR = "M10 1.3l2.7 5.6 6.2.8-4.6 4.3 1.2 6.1L10 15.1l-5.5 3 1.2-6.1L1.1 7.7l6.2-.8z"


def stars(rating, size):
    """Stars rounded to the nearest half as shopping sites do (3.1 -> 3, 4.9 -> 5, 3.5 -> 3 and a half)."""
    halves = int(round(rating * 2))
    full, half = halves // 2, halves % 2
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="halfstar">'
           '<stop offset="50%" stop-color="#DE7921"/><stop offset="50%" stop-color="#fff"/></linearGradient></defs></svg>'] if half else []
    for i in range(5):
        fill = "#DE7921" if i < full else ("url(#halfstar)" if half and i == full else "#fff")
        out.append(f'<svg viewBox="0 0 20 19.4" width="{size}" height="{size}" aria-hidden="true">'
                   f'<path d="{STAR}" fill="{fill}" stroke="#DE7921" stroke-width="1.1" stroke-linejoin="round"/></svg>')
    return f'<span class="stars" role="img" aria-label="{rating:g} out of 5 stars">{"".join(out)}</span>'


def nb(text):
    """Escapes text and keeps hyphenated words (Long-Sleeve) from breaking across lines."""
    return " ".join(f'<span class="nb">{html.escape(w)}</span>' if "-" in w else html.escape(w)
                    for w in text.split(" "))


def price(cls="", amount=None):
    amount = amount or PRICE
    return (f'<span class="price {cls}"><span class="sym">$</span>{amount[0]}'
            f'<span class="frac">{amount[1]}</span></span>')


CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:"Amazon Ember",Arial,sans-serif;font-size:14px;line-height:20px;color:#0F1111;-webkit-text-size-adjust:100%}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:16px;height:60px;padding:0 16px;background:#131921}
.menu{flex:none;width:22px;height:16px;border-top:2px solid #fff;border-bottom:2px solid #fff;position:relative}
.menu:after{content:"";position:absolute;left:0;right:0;top:5px;border-top:2px solid #fff}
.search{display:flex;flex:1;min-width:0;height:40px;border-radius:4px;overflow:hidden;background:#fff}
.scope{flex:none;display:flex;align-items:center;padding:0 10px;background:#e6e6e6;border-right:1px solid #cdcdcd;color:#555;font-size:12px}
.field{flex:1}
.go{flex:none;width:45px;background:#febd69;display:flex;align-items:center;justify-content:center}
.page{padding:32px 18px 24px}
/* The buy box sits in its own column on the right; "About this item" starts right under the photo, beside the buy box. */
.layout{display:grid;grid-template-columns:1fr 228px;column-gap:24px;align-items:start;grid-template-areas:"top buy" "about buy"}
.top{grid-area:top;display:grid;grid-template-columns:239px 1fr;column-gap:24px;align-items:start}
.about{grid-area:about}
.about h2{margin-top:34px}
.photo{display:block;width:100%;height:auto}
h1{margin:0 0 4px;font-size:24px;line-height:32px;font-weight:400}
.rating{display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin:12px 0 16px}
.score{font-size:23px;line-height:28px}
.count{font-size:14px;line-height:20px}
.stars{display:inline-flex;gap:1px}
.stars svg{display:block}
.link{color:#2162a1}
.nb{white-space:nowrap}
.price{font-size:28px;line-height:36px;white-space:nowrap}
.price .sym,.price .frac{position:relative;top:-.75em;font-size:13px}
.price.small{font-size:21px;line-height:28px}
.price.small .sym,.price.small .frac{font-size:12px;top:-.6em}
.buy{grid-area:buy;border:1px solid #D5D9D9;border-radius:8px;padding:14px 16px 16px}
.deliv{margin-top:6px}
.stock{margin:12px 0 10px;font-size:18px;line-height:24px;color:#007600}
.qty{display:flex;justify-content:space-between;align-items:center;height:31px;padding:0 9px 0 11px;border:1px solid #888C8C;border-radius:8px;background:#F0F2F2;box-shadow:0 2px 5px rgba(15,17,17,.15);font-size:13px}
.btn{display:flex;align-items:center;justify-content:center;height:34px;margin-top:9px;border-radius:100px;font-size:14px;cursor:default}
.cart{background:#FFD814}
.now{background:#FFA41C}
.meta{margin-top:12px;border-collapse:collapse;font-size:12px;line-height:16px}
.meta td{padding:2px 0;vertical-align:top}
.meta td:first-child{color:#565959;padding-right:12px;white-space:nowrap}
ul{margin:0 0 0 54px;padding:0}
li{margin:0 0 2px}
/* Same spacing for every section: the visible white space above a section header equals the white space below it. */
h2{margin:21px 0 21px;font-size:24px;line-height:32px;font-weight:700}
.revsum{margin:5px 0 10px;justify-content:center}
.reviews{margin:0 0 -2px 54px}
.review{display:flex;align-items:center;gap:9px;padding:4px 0}
.review .text{font-size:15px;line-height:22px;font-weight:700}
.review .who{font-size:12px;line-height:22px;color:#565959}
.spons{margin-left:4px;font-size:13px;line-height:20px;font-weight:400;color:#565959;white-space:nowrap}
.spons svg{position:relative;top:2px}
.card{width:250px;margin:0 auto;text-align:center}
.card .photo{width:210px;margin:0 auto}
.card{min-height:0}
.card .name{margin-top:10px}
.card .recrating{display:flex;align-items:center;justify-content:center;gap:5px;margin-top:5px}
.card .reccount{font-size:12px;line-height:16px}
.card .price{display:inline-block;margin-top:2px}
@media (max-width:740px){
  .layout{grid-template-columns:1fr;row-gap:16px;grid-template-areas:"top" "buy" "about"}
  .top{grid-template-columns:34% 1fr}
  .buy{max-width:340px;width:100%;margin:0 auto}
  .midprice{display:none}
}
@media (max-width:560px){
  .nav{height:48px;gap:12px;padding:0 12px}
  .search{height:36px}
  .page{padding:24px 14px 24px}
  .top{grid-template-columns:1fr;row-gap:12px}
  .top .photo{max-width:260px;margin:0 auto}
  h1{font-size:20px;line-height:28px}
  h2{font-size:20px;line-height:28px;margin:18px 0 18px}
  ul{margin-left:24px}
  .card{width:230px;margin:0 auto}
  .card .photo{width:200px}
}
"""

SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
               '<circle cx="10.2" cy="10.2" r="6.4" fill="none" stroke="#333" stroke-width="2.4"/>'
               '<path d="M15 15l5.6 5.6" stroke="#333" stroke-width="2.6" stroke-linecap="round"/></svg>')


INFO_ICON = ('<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">'
             '<circle cx="8" cy="8" r="8" fill="#8D9096"/><circle cx="8" cy="4.4" r="1.15" fill="#fff"/>'
             '<rect x="7" y="6.6" width="2" height="5.6" rx=".4" fill="#fff"/></svg>')


CHEVRON = ('<svg viewBox="0 0 12 8" width="11" height="8" aria-hidden="true">'
           '<path d="M1.5 1.5L6 6l4.5-4.5" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def reviews(rating_key):
    e = html.escape
    return "".join(
        f'<div class="review">{stars(n, 16)}'
        f'<span class="who">{e(who)}, {e(date)}</span></div>'
        for n, (who, date) in zip(REVIEW_STARS[rating_key], REVIEWERS))


def page(rating_key, rec_key):
    rating = RATINGS[rating_key]
    rec = RECS[rec_key]
    focal_name = f"{FOCAL_BRAND} {FOCAL['name']}"
    rec_name = f"{REC_BRAND} {rec['name']}"
    e = html.escape
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(focal_name)}</title>
<style>{CSS}</style>
</head>
<body data-rating="{rating_key}" data-rec="{rec_key}">
<div class="wrap">

  <div class="nav">
    <div class="menu"></div>
    <div class="search"><div class="scope">All &#9662;</div><div class="field"></div><div class="go">{SEARCH_ICON}</div></div>
  </div>

  <div class="page">
    <div class="layout">
    <div class="top">
      <img class="photo" src="{data_uri(FOCAL['image'])}" alt="{e(focal_name)}">
      <div>
        <h1>{nb(focal_name)}</h1>
        <div class="rating"><span class="score">{rating}</span>{stars(rating, 24)}<span class="count link">({N_RATINGS})</span></div>
        <div class="midprice">{price()}</div>
      </div>
    </div>
      <div class="buy">
        <div>{price()}</div>
        <div class="deliv">FREE delivery</div>
        <div class="stock">In Stock</div>
        <div class="qty"><span>Quantity: 1</span>{CHEVRON}</div>
        <div class="btn cart">Add to cart</div>
        <div class="btn now">Buy Now</div>
        <table class="meta">
          <tr><td>Shipper / Seller</td><td>{e(FOCAL_BRAND)}</td></tr>
          <tr><td>Returns</td><td class="link">30-day refund/replacement</td></tr>
        </table>
      </div>
      <div class="about">
        <h2>About this item</h2>
        <ul>{"".join(f"<li>{e(d)}</li>" for d in DESCRIPTION)}</ul>
      </div>
    </div>

    <h2>Customer reviews for this item</h2>
    <div class="rating revsum"><span class="score">{rating} out of 5</span>{stars(rating, 24)}<span class="count link">({N_RATINGS})</span></div>
    <div class="reviews">{reviews(rating_key)}</div>

    <h2>{e(REC_HEADER)} <span class="spons">Sponsored {INFO_ICON}</span></h2>
    <div class="card">
      <img class="photo" src="{data_uri(rec['image'])}" alt="{e(rec_name)}">
      <div class="name link">{nb(rec_name)}</div>
      <div class="recrating">{stars(REC_RATING, 16)}<span class="reccount link">({REC_N_RATINGS})</span></div>
      <div>{price("small", REC_PRICE)}</div>
    </div>
  </div>

</div>
</body>
</html>
'''


def index(rows):
    e = html.escape
    trs = "".join(
        f"<tr><td><a href='{e(f)}'>{e(f)}</a></td><td>{e(LABELS['rating'][r])}</td>"
        f"<td>{e(LABELS['rec'][c])}</td></tr>"
        for f, r, c in rows)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">
<title>S10.4.4 stimuli</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;font-size:14px;margin:24px;color:#111}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px;text-align:left}}th{{background:#f3f4f6}}</style>
</head><body>
<h1 style="font-size:18px">S10.4.4 stimuli: focal rating (3.1 vs. 4.9 stars)</h1>
<p>Prices: helmet $49.99, backpack $13.90.</p>
<p>For the researcher only. The goal is set by the shopping task in the survey, so each page serves both goal conditions.</p>
<table><tr><th>Page</th><th>Focal product rating</th><th>Recommended product</th></tr>{trs}</table>
</body></html>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in RATINGS:
        for c in RECS:
            name = f"s1044_{r}.html"
            (OUT / name).write_text(page(r, c), encoding="utf-8")
            rows.append((name, r, c))
    (OUT / "index.html").write_text(index(rows), encoding="utf-8")
    print(f"wrote {len(rows)} pages + index.html to {OUT}")


if __name__ == "__main__":
    main()
