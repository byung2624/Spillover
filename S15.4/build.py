#!/usr/bin/env python3
"""Builds the S15.4 stimulus pages.

S15.4 is S15.2 with three changes on the page: the recommended product is named "LindenHome Black Grommet Curtains" (was
"LindenHome Blackout Curtains"), the focal product's name ends in ", Black", and the header above the recommended product
reads "New Arrivals" (was "Products related to this item"). Both product names now state the color.
S15.2 is S15.1 with the recommended product renamed: "LindenHome Blackout Curtains" in place of "LindenHome Soundproof Curtains"
(same photo), so the recommended product fits the sleep goal only loosely. Its rating count stays at 3.
S15.1 was S14.1 with a different recommended product: soundproof curtains in place of the white noise machine.
The focal product, its ratings and reviews, the prices, and the layout are unchanged.
  - focal product: "BudStudio Noise-Cancelling Earbuds" (black), shown with its star rating (4.9 or 3.1 stars,
    473 ratings) and three individual reviews that show stars, the reviewer's name, and the date (no written text);
  - recommended product: "LindenHome Blackout Curtains" (black, shown folded), under "Products related to this item -
    Sponsored",
    with its own 4.0-star rating from 3 ratings (few ratings, so its own quality is less certain).
Both cost $29.99. The two products are different kinds of product and are both black. No color word appears in the
product names or in "About this item". "About this item" has four lines: one makes the earbuds fit the sleep goal ("comfortable to wear\nin bed"), one the gym goal ("secure fit during exercise"), without using the wording of the goal pages (street, night,\nsleeping, gym, working out, music).

Design: 2 (focal product rating: 4.9 vs. 3.1 stars)
      x 2 (shopping goal: products to use for sleeping through the noise at night vs. products to use for listening
           to music at the gym)
Both products serve the sleep goal; only the earbuds serve the gym goal.
The goal is set by the shopping task in the survey, not on the page, so the same page serves both goals.
There are two pages, one per rating: s154_31.html and s154_49.html.

Images (in img/): focal_earbuds.jpg (black earbuds photo supplied by the researcher, with the maker's three logos
removed) and rec_curtains.jpg (folded black curtains photo supplied by the researcher, unchanged).

Usage:  python3 build.py <image folder> <output folder>
Output: two self-contained pages named  s154_<rating>.html  and an index.html.
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
FOCAL_BRAND = "BudStudio"
REC_BRAND = "LindenHome"
PRICE = ("29", "99")           # focal product: dollars, cents
REC_PRICE = ("29", "99")       # recommended product: dollars, cents (matched to the focal product)
N_RATINGS = "473"              # focal rating count; same in both rating conditions
REC_RATING = 4.0               # recommended product's own rating; same on every page
REC_HEADER = "New Arrivals"
REC_N_RATINGS = "3"

RATINGS = {"31": 3.1, "49": 4.9}

FOCAL = {"image": "focal_earbuds.jpg",
         "name": "Noise-Cancelling Earbuds, Black"}

RECS = {
    "curtains": {"image": "rec_curtains.jpg", "name": "Black Grommet Curtains"},
}

# Constant on every page. Attributes only: no wording from the shopping goals (no "sleep", "night", "gym", "music",
# or "workout").
DESCRIPTION = [
    "Active noise cancellation that blocks background sounds",
    "Low-profile fit, comfortable to wear in bed",
    "Sweat-resistant, with a secure fit during exercise",
    "Up to 12 hours of playtime per charge",
]

# Individual reviews of the focal earbuds: each shows its stars, the reviewer's name, and the date. No written text.
# Same reviewers and dates in both rating conditions; only the stars differ.
REVIEWERS = [("Robert C.", "November 9, 2026"), ("Lisa T.", "November 5, 2026"), ("Mark D.", "November 2, 2026")]
REVIEW_STARS = {"31": [3, 3, 3], "49": [5, 5, 5]}
REVIEW_TEXT = {"31": ["", "", ""], "49": ["", "", ""]}   # leave empty for stars-only reviews

LABELS = {
    "rating": {"31": "3.1 stars", "49": "4.9 stars"},
    "rec": {"curtains": "Blackout curtains, black"},
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
        + (f'<span class="text">{e(text)}</span>' if text else "")
        + f'<span class="who">{e(who)}, {e(date)}</span></div>'
        for n, text, (who, date) in zip(REVIEW_STARS[rating_key], REVIEW_TEXT[rating_key], REVIEWERS))


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
    <div class="rating revsum"><span class="score">{rating}</span>{stars(rating, 24)}<span class="count link">({N_RATINGS})</span></div>
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
<title>S15.4 stimuli</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;font-size:14px;margin:24px;color:#111}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px;text-align:left}}th{{background:#f3f4f6}}</style>
</head><body>
<h1 style="font-size:18px">S15.4 stimuli: focal rating (3.1 vs. 4.9 stars)</h1>
<p>Prices: both products $29.99.</p>
<p>For the researcher only. The goal is set by the shopping task in the survey, so each page serves both goal conditions.</p>
<table><tr><th>Page</th><th>Focal product rating</th><th>Recommended product</th></tr>{trs}</table>
</body></html>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in RATINGS:
        for c in RECS:
            name = f"s154_{r}.html"
            (OUT / name).write_text(page(r, c), encoding="utf-8")
            rows.append((name, r, c))
    (OUT / "index.html").write_text(index(rows), encoding="utf-8")
    print(f"wrote {len(rows)} pages + index.html to {OUT}")


if __name__ == "__main__":
    main()
