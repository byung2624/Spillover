#!/usr/bin/env python3
"""Builds the S7.16 stimulus pages (identical to the S7.13 and S7.15 pages: three written reviews, no star-rating breakdown).

Design: 2 (focal product rating: 3.1 vs. 4.9 stars)
      x 2 (shopping goal: visibility vs. warmth)
The recommended shirt is the same for everyone in the survey: the one with the same color as the focal
shirt (short-sleeve, yellow). Its shared attribute, color, is relevant under the visibility goal and not
under the warmth goal. The survey uses the two "color" pages (s716_31_color, s716_49_color). The two
"sleeve" pages are built as well, so the recommended shirt can be switched without rebuilding.

The focal shirt is a neon yellow long-sleeve shirt. The recommended shirt is either a
neon yellow short-sleeve shirt (same color) or a black long-sleeve shirt (same sleeve length).
The color is named "Neon Yellow", not "High Visibility Yellow", so the name does not state the benefit:
that the color serves the visibility goal has to be inferred from the shopping situation.
The names do not mention the fabric. In the images, the two long-sleeve shirts look thick and warm and
the short-sleeve shirt looks thin, so the same-sleeve-length shirt clearly serves the warmth goal.

The goal is set by the shopping task in the survey, not on the page, so each page serves both goals.

Each page has a header, title, image, rating row, price, a purchase box, "About this item" (a one-line
brand description and two product details), "Customer reviews for this item", and then "New arrivals"
(with a "Sponsored" tag) holding the recommended shirt. The review section sits above the recommended
shirt. It repeats the focal rating (score, stars, count) under its header and shows three short reviews, matched across the
two rating conditions: same reviewers, dates, and topics, with only the valence and the stars changed.
The review section is kept short so the recommended shirt appears early: the focal rating is centered on
its own line under the header, and each review is one line (stars, text, then reviewer and date in grey), with no divider
lines, indented to the level of the "About this item" bullets so the stars line up.
The two shirts come from different brands, shown only in their names, as on real shopping sites. The
brand names are written differently (Telvane in ordinary case; JUVARO in capitals, three syllables) and
do not rhyme, so they do not read as one catalog.
Neither the description nor the reviews mention color, sleeves, fabric weight, warmth, or being seen: those are
conveyed only by the shirts' names and images.

Usage:  python3 build.py <image folder> <output folder>
Output: four self-contained pages named  s716_<rating>_<rec>.html  and an index.html.
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
FOCAL_BRAND = "Telvane"        # made-up brand of the focal shirt
REC_BRAND = "JUVARO"               # made-up brand of the recommended shirt (same in both rec conditions)
PRICE = ("18", "90")           # dollars, cents; same for the focal and the recommended shirt
N_RATINGS = "473"              # focal rating count; same in both rating conditions
REC_RATING = 4.0               # recommended shirt's own rating; same on every page
REC_HEADER = "New arrivals"   # header above the recommended shirt, followed by a small grey "Sponsored" tag
REC_N_RATINGS = "451"          # recommended shirt's rating count; same on every page, close to the focal count

RATINGS = {"31": 3.1, "49": 4.9}

FOCAL = {"image": "focal_long_yellow.jpg",
         "name": "Long-Sleeve Shirt, Neon Yellow"}

RECS = {
    "color":  {"image": "rec_short_yellow.jpg", "name": "Lightweight T-Shirt, Neon Yellow"},
    "sleeve": {"image": "rec_long_black.jpg", "name": "Long-Sleeve Shirt, Black"},
}

# Constant on every page. Nothing here mentions color, fabric weight, warmth, or being seen.
# The first line is a very short description of the focal shirt's brand, so the brand reads as a company
# of its own. It makes no claim about quality.
DESCRIPTION = [
    f"{FOCAL_BRAND} makes everyday basics for men and women",
    "Relaxed fit, true to size",
    "Ribbed crew neck",
]

# Customer reviews for the focal shirt. Matched across rating conditions: the reviewer, date, and topic
# of each review are the same; only the valence and the stars differ.
# Like the description, nothing here mentions color, fabric weight, warmth, or being seen.
REVIEWERS = [("Robert C.", "November 9, 2026"), ("Lisa T.", "November 5, 2026"), ("Mark D.", "November 2, 2026")]
REVIEWS = {
    "31": [(3, "Poorly made and uncomfortable to wear."),
           (3, "Lost its shape after a few washes."),
           (3, "Very dissatisfied. Would not recommend!")],
    "49": [(5, "Well made and comfortable to wear."),
           (5, "Kept its shape after many washes."),
           (5, "Very satisfied. Would recommend!")],
}

LABELS = {
    "rating": {"31": "3.1 stars", "49": "4.9 stars"},
    "rec": {"color": "Same color (short-sleeve, yellow)", "sleeve": "Same sleeve length (long-sleeve, black)"},
}

# Layout note: the card under the recommendation header has a fixed minimum height (see ".card{min-height" in CSS),
# equal to its height when the shirt name takes two lines. A one-line name then sits right above the stars,
# and the spare room goes below the price, so all four pages keep the same height.
# ----------------------------------------------------------------------------
# Pieces
# ----------------------------------------------------------------------------
def data_uri(name):
    return "data:image/jpeg;base64," + base64.b64encode((IMG / name).read_bytes()).decode("ascii")


STAR = "M10 1.3l2.7 5.6 6.2.8-4.6 4.3 1.2 6.1L10 15.1l-5.5 3 1.2-6.1L1.1 7.7l6.2-.8z"


def stars(rating, size):
    """Whole stars, rounded to the nearest half as shopping sites do (3.1 -> 3, 4.9 -> 5)."""
    full = int(round(rating * 2) / 2)
    out = []
    for i in range(5):
        fill = "#DE7921" if i < full else "#fff"
        out.append(f'<svg viewBox="0 0 20 19.4" width="{size}" height="{size}" aria-hidden="true">'
                   f'<path d="{STAR}" fill="{fill}" stroke="#DE7921" stroke-width="1.1" stroke-linejoin="round"/></svg>')
    return f'<span class="stars" role="img" aria-label="{rating:g} out of 5 stars">{"".join(out)}</span>'


def nb(text):
    """Escapes text and keeps hyphenated words (Long-Sleeve) from breaking across lines."""
    return " ".join(f'<span class="nb">{html.escape(w)}</span>' if "-" in w else html.escape(w)
                    for w in text.split(" "))


def price(cls=""):
    return (f'<span class="price {cls}"><span class="sym">$</span>{PRICE[0]}'
            f'<span class="frac">{PRICE[1]}</span></span>')


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
.top{display:grid;grid-template-columns:29% 1fr 228px;column-gap:24px;align-items:start}
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
.buy{border:1px solid #D5D9D9;border-radius:8px;padding:14px 16px 16px}
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
.card .photo{width:180px;margin:0 auto}
.card{min-height:299px}
.card .name{margin-top:10px}
.card .recrating{display:flex;align-items:center;justify-content:center;gap:5px;margin-top:5px}
.card .reccount{font-size:12px;line-height:16px}
.card .price{display:inline-block;margin-top:2px}
@media (max-width:740px){
  .top{grid-template-columns:34% 1fr;row-gap:16px}
  .buy{grid-column:1 / -1;max-width:340px;width:100%;margin:0 auto}
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
  .card .photo{width:160px}
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
        f'<div class="review">{stars(n, 16)}<span class="text">{e(text)}</span>'
        f'<span class="who">{e(who)}, {e(date)}</span></div>'
        for (n, text), (who, date) in zip(REVIEWS[rating_key], REVIEWERS))


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
    <div class="top">
      <img class="photo" src="{data_uri(FOCAL['image'])}" alt="{e(focal_name)}">
      <div>
        <h1>{nb(focal_name)}</h1>
        <div class="rating"><span class="score">{rating}</span>{stars(rating, 24)}<span class="count link">({N_RATINGS})</span></div>
        <div class="midprice">{price()}</div>
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
    </div>

    <h2>About this item</h2>
    <ul>{"".join(f"<li>{e(d)}</li>" for d in DESCRIPTION)}</ul>

    <h2>Customer reviews for this item</h2>
    <div class="rating revsum"><span class="score">{rating}</span>{stars(rating, 24)}<span class="count link">({N_RATINGS})</span></div>
    <div class="reviews">{reviews(rating_key)}</div>

    <h2>{e(REC_HEADER)} <span class="spons">Sponsored {INFO_ICON}</span></h2>
    <div class="card">
      <img class="photo" src="{data_uri(rec['image'])}" alt="{e(rec_name)}">
      <div class="name link">{nb(rec_name)}</div>
      <div class="recrating">{stars(REC_RATING, 16)}<span class="reccount link">({REC_N_RATINGS})</span></div>
      <div>{price("small")}</div>
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
<title>S7.16 stimuli</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;font-size:14px;margin:24px;color:#111}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px;text-align:left}}th{{background:#f3f4f6}}</style>
</head><body>
<h1 style="font-size:18px">S7.16 stimuli: 2 (focal rating) × 2 (recommended shirt)</h1>
<p>For the researcher only. The goal is set by the shopping task in the survey, so each page serves both goal conditions.</p>
<table><tr><th>Page</th><th>Focal product rating</th><th>Recommended shirt</th></tr>{trs}</table>
</body></html>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in RATINGS:
        for c in RECS:
            name = f"s716_{r}_{c}.html"
            (OUT / name).write_text(page(r, c), encoding="utf-8")
            rows.append((name, r, c))
    (OUT / "index.html").write_text(index(rows), encoding="utf-8")
    print(f"wrote {len(rows)} pages + index.html to {OUT}")


if __name__ == "__main__":
    main()
