#!/usr/bin/env python3
"""Builds the S10.4.11 stimulus pages.

S10.4.11 is S10.4.7 with a second recommended product. Under "New arrivals - Sponsored" the page shows, side by side, both in
the helmet's fluorescent yellow:
  - "BagStudio Everyday Backpack" ($39.99, the S10.4.7 backpack), on the left;
  - "GloveWorks Cycling Gloves" ($24.99, the gloves photo of S10.8 and S10.4.3), on the right.
Both show 4.0 stars; the helmet costs $49.99. As in S10.4.7: brands that signal the product type, no color word in the product
names, and a star-rating breakdown in the review section (31%, 14%, 16%, 12%, 27% at 3.1 stars; 93%, 5%, 1%, 0%, 1% at 4.9 stars)
with no individual reviews. (S10.4.10 had two backpacks and three star-only reviews.)
What S10.4.7 was: S10.4.6 with the star-rating breakdown, the backpack's own rating back at 4.0 stars, and no color word in
the product names.
What S10.4.6 was:

S10.4.6 is S10.4.2 with four changes:
  1. both product names say "Yellow" (were "Fluorescent Yellow"); the helmet's "About this item" line still reads
     "Fluorescent yellow finish stays bright on the road, day or night";
  2. the three individual reviews of the helmet are removed. The "Customer reviews for this item" section shows the overall
     rating only (the REVIEWERS and REVIEW_STARS settings below are no longer used);
  3. the brand names are "HelmetPro" for the helmet (was "Telvane") and "BagStudio" for the backpack (was "JUVARO");
  4. the backpack's own rating is 3.5 stars (was 4.0). [S10.4.7: back to 4.0]
S10.4.2 used the S10.4 pages unchanged.
S10.4 is S10.1 with one change: the recommended backpack's photo is a plain backpack with no reflective tape
(the photo used in S10.2 and S10.3). Everything else on the page is as in S10.1.
Products, in the same page layout as S9.8:
  - focal product: "HelmetPro Bike Helmet" (a vented bike helmet);
  - recommended product: "BagStudio Everyday Backpack", under "New arrivals - Sponsored".
The helmet costs $49.99, the backpack $39.99 and the gloves $24.99. The three are different kinds of product; what they share is the fluorescent yellow color.
"About this item" has four lines. The first two point to what the vents and the color do ("force air through the helmet and
reduce sweating", "stays bright on the road, day or night") without using any wording from the shopping goals (no drivers, notice, cool, or heat).
There is no brand line.
There are no individual reviews: the review section shows its heading and the overall rating only.

Design: 2 (focal product rating: 3.1 vs. 4.9 stars)
      x 2 (shopping goal: bike gear to help drivers notice you on the road after dark
           vs. bike gear to help you stay cool on the road on hot afternoons)
The goal is set by the shopping task in the survey, not on the page, so the same page serves both goals.
There are two pages, one per rating: s10411_31.html and s10411_49.html.

Images (in img/): focal_helmet.jpg (brand lettering removed from the visor) and rec_backpack.jpg (a plain backpack with
no reflective parts; brand patch removed from the front pocket; recolored from mustard to the helmet's fluorescent yellow).

Usage:  python3 build.py <image folder> <output folder>
Output: two self-contained pages named  s10411_<rating>.html  and an index.html.
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
FOCAL_BRAND = "HelmetPro"      # made-up brand of the focal product
PRICE = ("49", "99")           # focal product: dollars, cents
N_RATINGS = "473"              # focal rating count; same in both rating conditions
REC_RATING = 4.0               # each recommended product's own rating; same on every page
REC_HEADER = "New arrivals"   # header above the recommended product, followed by a small grey "Sponsored" tag

RATINGS = {"31": 3.1, "49": 4.9}

FOCAL = {"image": "focal_helmet.jpg",
         "name": "Bike Helmet"}

# The two recommended products, in the order they appear on the page (left to right).
RECS = {
    "backpack": {"image": "rec_backpack.jpg", "brand": "BagStudio", "name": "Everyday Backpack", "n_ratings": "451", "price": ("39", "99")},
    "gloves": {"image": "rec_gloves.jpg", "brand": "GloveWorks", "name": "Cycling Gloves", "n_ratings": "438", "price": ("24", "99")},
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
REVIEW_STARS = {"31": [3, 3, 3], "49": [5, 5, 5]}

# Star-rating breakdown of the focal helmet (percent of ratings at 5, 4, 3, 2, and 1 stars), as on large shopping sites.
# Same numbers as S7.14. The percentages add to 100 and average to the displayed rating (4.9 stars: 4.89; 3.1 stars: 3.10).
BREAKDOWN = {
    "49": [93, 5, 1, 0, 1],
    "31": [31, 14, 16, 12, 27],
}
for _k, _v in BREAKDOWN.items():
    assert sum(_v) == 100 and abs(sum(st * p for st, p in zip((5, 4, 3, 2, 1), _v)) / 100 - float(_k) / 10) < 0.05

LABELS = {
    "rating": {"31": "3.1 stars", "49": "4.9 stars"},
    "rec": {"backpack": "Everyday backpack"},
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
li{margin:0 0 3px;font-size:15px;line-height:22px}
/* Same spacing for every section: the visible white space above a section header equals the white space below it. */
h2{margin:21px 0 21px;font-size:24px;line-height:32px;font-weight:700}
.revsum{margin:5px 0 10px 54px;justify-content:flex-start}
.hist{width:300px;max-width:calc(100% - 54px);margin:0 0 0 54px;padding-bottom:4px;text-align:left}
.hist .sum{display:flex;align-items:center;gap:9px}
.hist .total{margin:6px 0 9px;font-size:13px;line-height:18px;color:#565959}
.hist .row{display:flex;align-items:center;height:17px;margin:0 0 8px;font-size:13px;line-height:17px}
.hist .row:last-child{margin-bottom:0}
.hist .row .lab{flex:none;width:19px}
.hist .row .bar{flex:1;height:14px;border:1px solid #8D9096;border-radius:5px;background:#fff;overflow:hidden}
.hist .row .fill{height:100%;background:#DE7921;border-radius:4px 0 0 4px}
.hist .row .pct{flex:none;width:44px;text-align:right}
.reviews{margin:0 0 -2px 54px}
.review{display:flex;align-items:center;gap:9px;padding:4px 0}
.review .text{font-size:15px;line-height:22px;font-weight:700}
.review .who{font-size:12px;line-height:22px;color:#565959}
.spons{margin-left:4px;font-size:13px;line-height:20px;font-weight:400;color:#565959;white-space:nowrap}
.spons svg{position:relative;top:2px}
.cards{display:flex;justify-content:center;align-items:flex-start;gap:70px}
.card{width:250px;margin:0;text-align:center}
.card .photo{width:210px;height:260px;object-fit:contain;margin:0 auto}
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


def breakdown(rating_key):
    """Star-rating breakdown: score and stars, number of ratings, and one bar per star level."""
    rows = "".join(
        f'<div class="row"><span class="lab link">{st}</span>'
        f'<span class="bar"><span class="fill" style="display:block;width:{p}%"></span></span>'
        f'<span class="pct link">{p}%</span></div>'
        for st, p in zip((5, 4, 3, 2, 1), BREAKDOWN[rating_key]))
    return (f'<div class="hist"><div class="sum"><span class="score">{RATINGS[rating_key]}</span>{stars(RATINGS[rating_key], 24)}</div>'
            f'<div class="total">{N_RATINGS} global ratings</div>{rows}</div>')


def rec_card(rec):
    e = html.escape
    rec_name = f"{rec['brand']} {rec['name']}"
    return (f'<div class="card"><img class="photo" src="{data_uri(rec["image"])}" alt="{e(rec_name)}">'
            f'<div class="name link">{nb(rec_name)}</div>'
            f'<div class="recrating">{stars(REC_RATING, 16)}<span class="reccount link">({rec["n_ratings"]})</span></div>'
            f'<div>{price("small", rec["price"])}</div></div>')


def page(rating_key):
    rating = RATINGS[rating_key]
    focal_name = f"{FOCAL_BRAND} {FOCAL['name']}"
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
<body data-rating="{rating_key}">
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
    {breakdown(rating_key)}

    <h2>{e(REC_HEADER)} <span class="spons">Sponsored {INFO_ICON}</span></h2>
    <div class="cards">{"".join(rec_card(r) for r in RECS.values())}</div>
  </div>

</div>
</body>
</html>
'''


def index(rows):
    e = html.escape
    trs = "".join(
        f"<tr><td><a href='{e(f)}'>{e(f)}</a></td><td>{e(LABELS['rating'][r])}</td>"
        f"<td>Everyday backpack and cycling gloves, both fluorescent yellow</td></tr>"
        for f, r in rows)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">
<title>S10.4.11 stimuli</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;font-size:14px;margin:24px;color:#111}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px;text-align:left}}th{{background:#f3f4f6}}</style>
</head><body>
<h1 style="font-size:18px">S10.4.11 stimuli: focal rating (3.1 vs. 4.9 stars)</h1>
<p>Prices: helmet $49.99, backpack $39.99, gloves $24.99.</p>
<p>For the researcher only. The goal is set by the shopping task in the survey, so each page serves both goal conditions.</p>
<table><tr><th>Page</th><th>Focal product rating</th><th>Recommended products</th></tr>{trs}</table>
</body></html>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in RATINGS:
        name = f"s10411_{r}.html"
        (OUT / name).write_text(page(r), encoding="utf-8")
        rows.append((name, r))
    (OUT / "index.html").write_text(index(rows), encoding="utf-8")
    print(f"wrote {len(rows)} pages + index.html to {OUT}")


if __name__ == "__main__":
    main()
