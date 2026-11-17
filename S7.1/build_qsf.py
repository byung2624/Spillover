#!/usr/bin/env python3
"""Builds the Study 5 Qualtrics survey (.qsf) from the earlier genre-match survey.

Design: 2 (focal product rating: 3.1 vs. 4.9 stars)
      x 2 (active goal: walks after dark vs. walks on cold mornings)
      x 2 (recommended shirt: same color vs. same sleeve length as the focal shirt)

Kept from the earlier survey: survey options, embedded-data fields, the mobile and
duplicate/fraud screens, the timed webpage question, the three-item attitude scale,
the "What did you do in today's survey?" check, age, gender, and browser info.

Usage: python3 build_qsf.py <earlier survey .qsf> <output .qsf>
"""
import copy
import html
import json
import re
import sys

SRC, OUT = sys.argv[1], sys.argv[2]

# ----------------------------------------------------------------------------
# Content. Edit here.
# ----------------------------------------------------------------------------
SURVEY_NAME = "S7.1 Focal Rating x Goal x Recommended Shirt"
# Folder that holds s5_31_color.html, s5_31_sleeve.html, s5_49_color.html, s5_49_sleeve.html and img/
STIM_URL = "https://raw.githubusercontent.com/byung2624/Spillover/main/S7.1/"
MIN_SECONDS_ON_PAGE = 30

FOCAL_NAME = "TELVANE Long-Sleeve Shirt, High Visibility Yellow"
FOCAL_IMG = "focal_long_yellow.jpg"

GOALS = {   # Goal -> (GoalText, GoalUse)
    "Dark": ("a shirt for your walks on busy roads after dark, where drivers need to see you",
             "walks on busy roads after dark, where drivers need to see you"),
    "Cold": ("a shirt for your walks on cold winter mornings, where you need to stay warm",
             "walks on cold winter mornings, where you need to stay warm"),
}
RECS = {    # Rec -> (RecName, RecImg)
    "Color":  ("BRELLIN Short-Sleeve Shirt, High Visibility Yellow", "rec_short_yellow.jpg"),
    "Sleeve": ("BRELLIN Long-Sleeve Shirt, Black", "rec_long_black.jpg"),
}
SORT_ITEMS = [  # sorting task: 2 colors x 2 sleeve lengths, same style, no brand
    ("Long-Sleeve Shirt, High Visibility Yellow", "sort_long_yellow.jpg"),
    ("Short-Sleeve Shirt, High Visibility Yellow", "rec_short_yellow.jpg"),
    ("Long-Sleeve Shirt, Black", "rec_long_black.jpg"),
    ("Short-Sleeve Shirt, Black", "sort_short_black.jpg"),
]

# piped fields
P_STIM = "${e://Field/StimURL}"
P_GOAL = "${e://Field/GoalText}"
P_USE = "${e://Field/GoalUse}"
P_RECNAME = "${e://Field/RecName}"
P_RECIMG = "${e://Field/RecImg}"

# ----------------------------------------------------------------------------
q = json.load(open(SRC, encoding="utf-8"))
SID = q["SurveyEntry"]["SurveyID"]
old = {e["PrimaryAttribute"]: e["Payload"] for e in q["SurveyElements"] if e["Element"] == "SQ"}
VIS = {"Private": False, "Hidden": False}
FORCE = {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}}


def describe(text):
    t = html.unescape(re.sub(r"<[^>]+>", " ", text))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= 100 else t[:97] + "..."


def img(file, style):
    return f'<img src="{P_STIM}img/{file}" style="{style}">'


def shirt(file, name, height=200):
    return (f'<div style="text-align:center;">{img(file, f"height:{height}px; width:auto;")}'
            f'<br>{name}</div>')


def pair():
    cell = "width:48%; text-align:center;"
    return (f'<div style="display:flex; justify-content:space-between; width:100%;">'
            f'<div style="{cell}">{img(FOCAL_IMG, "height:200px; width:auto;")}<br>{FOCAL_NAME}</div>'
            f'<div style="{cell}">{img(P_RECIMG, "height:200px; width:auto;")}<br>{P_RECNAME}</div></div>')


questions = {}


def add(qid, payload):
    payload["QuestionID"] = qid
    payload.setdefault("QuestionDescription", describe(payload["QuestionText"]))
    payload.setdefault("DataVisibility", dict(VIS))
    payload.setdefault("Language", [])
    questions[qid] = payload


def text_block(qid, tag, text):
    add(qid, {"QuestionText": text, "DefaultChoices": False, "DataExportTag": tag, "QuestionType": "DB",
              "Selector": "TB", "Configuration": {"QuestionDescriptionOption": "UseText"}, "ChoiceOrder": [],
              "Validation": {"Settings": {"Type": "None"}}, "GradingData": [], "NextChoiceId": 4, "NextAnswerId": 1})


def scale(qid, tag, text, labels, recode=None, vertical=False):
    choices = {str(i + 1): {"Display": lab} for i, lab in enumerate(labels)}
    p = {"QuestionText": text, "DataExportTag": tag, "QuestionType": "MC",
         "Selector": "SAVR" if vertical else "SAHR", "SubSelector": "TX",
         "Configuration": {"QuestionDescriptionOption": "UseText"}, "Choices": choices,
         "ChoiceOrder": [str(i + 1) for i in range(len(labels))], "Validation": copy.deepcopy(FORCE),
         "NextChoiceId": len(labels) + 1, "NextAnswerId": 1}
    if not vertical:
        p["Configuration"]["LabelPosition"] = "BELOW"
    if recode:
        p["RecodeValues"] = {str(i + 1): str(v) for i, v in enumerate(recode)}
    add(qid, p)


def attitude(qid, tag, text):
    p = copy.deepcopy(old["QID1840"])          # three 9-point bipolar items, as in the earlier studies
    p.pop("QuestionText_Unsafe", None)
    p.pop("QuestionDescription", None)
    p.update({"QuestionText": text, "DataExportTag": tag})
    add(qid, p)


# ---- 1. Welcome and shopping task (goal manipulation) --------------------------------------
text_block("QID1841", "intro",
           "<b>Welcome.</b><br><br>In this study, you will imagine a shopping situation, look at a product page "
           "from an online store, and answer some questions about it.<br><br>There are no right or wrong answers. "
           "We are interested in your own opinions.")
text_block("QID1842", "task",
           f"Please imagine the following situation.<br><br><b>You are shopping online for {P_GOAL}.</b><br><br>"
           "Keep this situation in mind. On the next page, you will see a product page that came up while you were shopping.")

# ---- 2. Product page (focal rating x recommended shirt), shown in an iframe ----------------
page = copy.deepcopy(old["QID1802"])
page.pop("QuestionDescription", None)
page["DataExportTag"] = "webpage"
page["QuestionText"] = (
    f'<p style="text-align:left; margin:0 0 6px 0;">You are shopping for {P_GOAL}.</p>\n'
    f'<p style="text-align:left; margin:0 0 10px 0;">Please look at the product page below carefully. '
    f'Take at least {MIN_SECONDS_ON_PAGE} seconds to examine it.</p>\n'
    '<div id="stimBox" style="max-width:880px; margin:0 auto; border:2px solid #000; padding:6px;"></div>\n'
    '<div id="stimNote" style="display:none; color:#b00000; text-align:center; margin-top:8px;">'
    'The product page could not be loaded. Please check your connection and reload this page.</div>')
page["QuestionJS"] = """Qualtrics.SurveyEngine.addOnload(function () {

  var focal   = "${e://Field/Focal}";    // Pos = 4.9 stars, Neg = 3.1 stars
  var rec     = "${e://Field/Rec}";      // Color = same color, Sleeve = same sleeve length
  var baseURL = "${e://Field/StimURL}";  // folder with the four pages; set in the Survey Flow

  // Fallback for Preview
  if (focal !== "Pos" && focal !== "Neg") { focal = "Neg"; }
  if (rec !== "Color" && rec !== "Sleeve") { rec = "Color"; }
  if (baseURL.indexOf("http") !== 0) { baseURL = "%s"; }

  var fileName = "s5_" + (focal === "Pos" ? "49" : "31") + "_" + (rec === "Color" ? "color" : "sleeve") + ".html";

  // The page is shown inside an iframe. Its height follows its content, so there is no inner scroll bar.
  var frame = document.createElement("iframe");
  frame.setAttribute("title", "Product page");
  frame.style.cssText = "display:block; width:100%%; height:900px; border:0;";
  document.getElementById("stimBox").appendChild(frame);

  function fit() {
    try {
      var d = frame.contentWindow.document;
      frame.style.height = Math.max(d.documentElement.scrollHeight, d.body.scrollHeight) + "px";
    } catch (e) {}
  }
  frame.addEventListener("load", function () { fit(); setTimeout(fit, 300); setTimeout(fit, 1500); });
  window.addEventListener("resize", fit);

  function failed() { document.getElementById("stimNote").style.display = "block"; }

  var xhr = new XMLHttpRequest();
  xhr.open("GET", baseURL + fileName, true);
  xhr.onload = function () {
    if (xhr.status === 200 && xhr.responseText.indexOf("<html") !== -1) { frame.srcdoc = xhr.responseText; }
    else { failed(); }
  };
  xhr.onerror = failed;
  xhr.send();

});

Qualtrics.SurveyEngine.addOnReady(function()
{
	/*Place your JavaScript here to run when the page is fully displayed*/

});

Qualtrics.SurveyEngine.addOnUnload(function()
{
	/*Place your JavaScript here to run when the page is unloaded*/

});""" % STIM_URL
add("QID1802", page)

timer = copy.deepcopy(old["QID1754"])
timer["Configuration"]["MinSeconds"] = MIN_SECONDS_ON_PAGE
add("QID1754", timer)

# ---- 3. DV1: attitude toward the recommended shirt -----------------------------------------
attitude("QID1843", "Rec_att",
         "The page also showed this shirt under “More items to explore.” We will call it the "
         f"<b>recommended shirt</b>.<br>&nbsp;{shirt(P_RECIMG, P_RECNAME)}<br>"
         "Please provide your opinions about the recommended shirt:")

add("QID1844", {"QuestionText": "Please list the factors, product attributes, or other considerations, if any, "
                                "that you used in forming your opinions about the recommended shirt.",
                "DefaultChoices": False, "DataExportTag": "considerations", "QuestionType": "TE", "Selector": "ESTB",
                "Configuration": {"QuestionDescriptionOption": "UseText"}, "Validation": copy.deepcopy(FORCE),
                "GradingData": [], "NextChoiceId": 4, "NextAnswerId": 1, "SearchSource": {"AllowFreeResponse": "false"}})

# ---- 4. Process measures -------------------------------------------------------------------
scale("QID1845", "similarity",
      "Now consider these two shirts together: the first shirt (the main product on the page) on the left and "
      f"the recommended shirt on the right.<br>&nbsp;{pair()}<br>"
      f"In the context of shopping for {P_GOAL}, how similar or dissimilar are these two shirts?",
      ["0 = Very dissimilar"] + [str(i) for i in range(1, 10)] + ["10 = Very similar"], recode=range(0, 11))

scale("QID1846", "pros_cons",
      "How much do you agree or disagree with the following statement?<br><br>"
      "The recommended shirt and the first shirt have the same pros and cons.",
      ["1 = Strongly disagree", "2", "3", "4", "5", "6", "7 = Strongly agree"])

scale("QID1847", "next_action",
      f"If you were really shopping for {P_GOAL}, what would you most likely do next?",
      [f"Buy the first shirt ({FOCAL_NAME})",
       f"Look more closely at the recommended shirt ({P_RECNAME})",
       "Go back and search for other shirts",
       "Not buy anything for now"], vertical=True)

sort = copy.deepcopy(old["QID1811"])           # matrix: one row per shirt, one column per pile
sort.pop("QuestionDescription", None)
sort.update({
    "QuestionText": "Below are four shirts. Please sort them into piles so that the shirts in each pile "
                    f"<b>go together</b> for what you are shopping for ({P_GOAL}).<br><br>"
                    "You may use as many or as few piles as you like. Shirts that you give the same pile number are in the same pile.",
    "DataExportTag": "sort",
    "Choices": {str(i + 1): {"Display": f'{img(f, "height:90px; width:auto; vertical-align:middle;")} {n}'}
                for i, (n, f) in enumerate(SORT_ITEMS)},
    "ChoiceOrder": [str(i + 1) for i in range(len(SORT_ITEMS))],
    "Answers": {str(i): {"Display": f"Pile {i}"} for i in range(1, 5)},
    "AnswerOrder": ["1", "2", "3", "4"],
    "NextChoiceId": len(SORT_ITEMS) + 1, "NextAnswerId": 5,
    "Randomization": {"Advanced": None, "Type": "All", "TotalRandSubset": ""},
})
sort["Configuration"]["ChoiceColumnWidth"] = 45
add("QID1848", sort)

# ---- 5. Checks -----------------------------------------------------------------------------
attitude("QID1840", "Focal_rating",
         "Now think about the first shirt (the main product on the page):<br>&nbsp;"
         f"{shirt(FOCAL_IMG, FOCAL_NAME)}<br>Please provide your opinions about the first shirt:")

scale("QID1849", "recall_rec",
      "What star rating did the recommended shirt (the one under “More items to explore”) have on the page?",
      ["1 star", "2 stars", "3 stars", "4 stars", "5 stars", "I don't remember"], vertical=True)

APPROPRIATE = ["1 = Not at all appropriate"] + [str(i) for i in range(2, 11)] + ["11 = Very appropriate"]
scale("QID1850", "approp_rec",
      f"{shirt(P_RECIMG, P_RECNAME, 160)}<br>How appropriate is the recommended shirt for {P_USE}?", APPROPRIATE)
scale("QID1851", "approp_focal",
      f"{shirt(FOCAL_IMG, FOCAL_NAME, 160)}<br>How appropriate is the first shirt for {P_USE}?", APPROPRIATE)

check = copy.deepcopy(old["QID1826"])
check["Choices"]["1"]["Display"] = "Viewed a product page for a 4.9-star shirt"
check["Choices"]["7"]["Display"] = "Viewed a product page for a 3.1-star shirt"
add("QID1826", check)

for qid in ("QID29", "QID30", "QID31", "QID74"):       # demographics, unchanged
    add(qid, copy.deepcopy(old[qid]))

# ----------------------------------------------------------------------------
# Blocks
# ----------------------------------------------------------------------------
Q = lambda qid: {"Type": "Question", "QuestionID": qid}
BREAK = {"Type": "Page Break"}
OPTS = {"BlockLocking": "false", "RandomizeQuestions": "false", "BlockVisibility": "Expanded"}
B_INTRO, B_PAGE, B_DV = "BL_82LjNDO6XfJvoai", "BL_e9UK4pFAPoEGzZk", "BL_3CQOuiS2BD9GMxU"
B_PROCESS, B_CHECKS, B_DEMO = "BL_9Zq7mW2xK4pT8aV", "BL_cHAHE63LpCpStKu", "BL_bvyaJpwcS2qa5Nj"


def block(bid, name, elements):
    return {"Type": "Standard", "SubType": "", "Description": name, "ID": bid,
            "BlockElements": elements, "Options": dict(OPTS)}


blocks = {
    "1": {"Type": "Trash", "Description": "Trash / Unused Questions", "ID": "BL_eONUJdN5PYUpZxH",
          "BlockElements": [], "Options": dict(OPTS)},
    "2": block(B_INTRO, "Welcome and shopping task (goal)", [Q("QID1841"), BREAK, Q("QID1842")]),
    "3": block(B_PAGE, "Product page (rating x recommended shirt)", [Q("QID1802"), Q("QID1754")]),
    "4": block(B_DV, "DV1 Attitude toward recommended shirt", [Q("QID1843"), BREAK, Q("QID1844")]),
    "5": block(B_PROCESS, "Process measures",
               [Q("QID1845"), Q("QID1846"), BREAK, Q("QID1847"), BREAK, Q("QID1848")]),
    "6": block(B_CHECKS, "Checks",
               [Q("QID1840"), BREAK, Q("QID1849"), BREAK, Q("QID1850"), Q("QID1851"), BREAK, Q("QID1826")]),
    "7": block(B_DEMO, "Demographics", [Q("QID29"), Q("QID30"), Q("QID31"), Q("QID74")]),
}

# ----------------------------------------------------------------------------
# Survey flow
# ----------------------------------------------------------------------------
flow_el = next(e for e in q["SurveyElements"] if e["Element"] == "FL")
old_flow = {f["FlowID"]: f for f in flow_el["Payload"]["Flow"]}


def field(name, value):
    return {"Description": name, "Type": "Custom", "Field": name, "VariableType": "String",
            "DataVisibility": [], "AnalyzeText": False, "Value": value}


def setter(fid, pairs):
    return {"Type": "EmbeddedData", "FlowID": fid, "EmbeddedData": [field(k, v) for k, v in pairs]}


def randomizer(fid, branches):
    return {"Type": "BlockRandomizer", "FlowID": fid, "SubSet": 1, "EvenPresentation": True, "Flow": branches}


first = copy.deepcopy(old_flow["FL_67"])
first["EmbeddedData"].append(field("StimURL", STIM_URL))

flow = [
    first,
    old_flow["FL_101"],                                   # screen out mobile devices
    old_flow["FL_65"],                                    # screen out duplicates and likely fraud
    old_flow["FL_71"],                                    # Focal: Pos (4.9 stars) vs. Neg (3.1 stars)
    randomizer("FL_292", [setter(fid, [("Goal", g), ("GoalText", GOALS[g][0]), ("GoalUse", GOALS[g][1])])
                          for fid, g in (("FL_293", "Dark"), ("FL_294", "Cold"))]),
    randomizer("FL_417", [setter(fid, [("Rec", r), ("RecName", RECS[r][0]), ("RecImg", RECS[r][1])])
                          for fid, r in (("FL_418", "Color"), ("FL_419", "Sleeve"))]),
    {"Type": "Standard", "ID": B_INTRO, "FlowID": "FL_411", "Autofill": []},
    {"Type": "Block", "ID": B_PAGE, "FlowID": "FL_348", "Autofill": []},
    {"Type": "Standard", "ID": B_DV, "FlowID": "FL_413", "Autofill": []},
    {"Type": "Standard", "ID": B_PROCESS, "FlowID": "FL_420", "Autofill": []},
    {"Type": "Standard", "ID": B_CHECKS, "FlowID": "FL_415", "Autofill": []},
    {"Type": "Standard", "ID": B_DEMO, "FlowID": "FL_11", "Autofill": []},
    old_flow["FL_13"],                                    # end of survey (redirect)
]

# ----------------------------------------------------------------------------
# Assemble
# ----------------------------------------------------------------------------
def element(kind, primary, secondary, payload, tertiary=None):
    return {"SurveyID": SID, "Element": kind, "PrimaryAttribute": primary, "SecondaryAttribute": secondary,
            "TertiaryAttribute": tertiary, "Payload": payload}


keep = {e["Element"]: e for e in q["SurveyElements"] if e["Element"] in ("PL", "PROJ", "RS", "SCO", "SO", "STAT")}
keep["SO"]["Payload"]["SurveyName"] = SURVEY_NAME
top = max(int(k[3:]) for k in questions)

elements = [
    element("BL", "Survey Blocks", None, blocks),
    element("FL", "Survey Flow", None, {"Type": "Root", "FlowID": "FL_1", "Flow": flow, "Properties": {"Count": 420}}),
    keep["PL"], keep["PROJ"],
    element("QC", "Survey Question Count", str(top), None),
    keep["RS"], keep["SCO"], keep["SO"],
]
for qid in sorted(questions, key=lambda k: int(k[3:])):
    elements.append(element("SQ", qid, questions[qid]["QuestionDescription"], questions[qid]))
elements.append(keep["STAT"])

q["SurveyEntry"]["SurveyName"] = SURVEY_NAME
q["SurveyElements"] = elements
json.dump(q, open(OUT, "w", encoding="utf-8"), ensure_ascii=True, separators=(",", ":"))
print(f"wrote {OUT}: {len(questions)} questions, {len(blocks) - 1} blocks")
