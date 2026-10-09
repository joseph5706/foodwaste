import streamlit as st
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import os, json, urllib.request, urllib.error, re

st.set_page_config(page_title="FoodWise AI — Save Food. Save Money.", page_icon="🥬", layout="wide")

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
/* Restore the original soft green-and-cream page background. */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .stApp {
  background: linear-gradient(135deg,#f7f8f3 0%,#e8f3e8 48%,#f2eee4 100%) !important;
  background-attachment: fixed !important;
  color: #202b22;
}
[data-testid="stMainBlockContainer"], .block-container {background: transparent !important;}
[data-testid="stVerticalBlock"] > div {background-color: transparent;}
/* Premium loading splash with three multi-item food orbits. */
.foodwise-splash {position:fixed;inset:0;z-index:999999;background:radial-gradient(ellipse at 50% 43%,#174c78 0%,#0b2850 44%,#041126 100%);display:flex;align-items:center;justify-content:center;flex-direction:column;color:#fff;overflow:hidden;animation:splashOut .75s cubic-bezier(.7,0,.3,1) 4.2s forwards;pointer-events:none;}
.foodwise-splash:before,.foodwise-splash:after {content:"";position:absolute;width:min(72vw,620px);aspect-ratio:1;border-radius:50%;border:1px solid #7ccaff18;box-shadow:0 0 90px #2e9cff0c,inset 0 0 80px #2e9cff0a;}
.foodwise-splash:after {width:min(54vw,450px);border-style:dashed;border-color:#9bdcff20;animation:orbitSpin 28s linear infinite;}
.foodwise-splash .brand {font-family:Manrope,sans-serif;font-size:clamp(27px,4vw,44px);font-weight:800;letter-spacing:2.5px;text-shadow:0 0 22px #6ec8ff66;}
.foodwise-splash .tagline {color:#c4dcf7;font-size:13px;letter-spacing:2px;margin-top:9px;text-transform:uppercase;}
.food-orbit {position:absolute;width:220px;height:220px;border:1px solid #8ccaff60;border-radius:50%;animation:orbitSpin 4.8s linear infinite;box-shadow:0 0 28px #3aabff0b;}
.food-orbit.two {width:310px;height:310px;animation-duration:7.2s;animation-direction:reverse;border-color:#8ccaff40;}
.food-orbit.three {width:400px;height:400px;animation-duration:10.5s;border-color:#8ccaff2b;}
.food-orbit span {position:absolute;display:grid;place-items:center;width:48px;height:48px;border:1px solid #d8f0ff45;border-radius:16px;background:linear-gradient(145deg,#ffffff24,#ffffff0a);backdrop-filter:blur(7px);font-size:29px;filter:drop-shadow(0 8px 12px #0008);left:calc(50% - 24px);top:-24px;animation:foodBob 1.8s ease-in-out infinite;}
.food-orbit span:nth-child(2){left:auto;right:-22px;top:calc(50% - 24px);animation-delay:-.45s}
.food-orbit span:nth-child(3){left:calc(50% - 24px);top:auto;bottom:-24px;animation-delay:-.9s}
.food-orbit span:nth-child(4){left:-22px;top:calc(50% - 24px);animation-delay:-1.35s}
.food-orbit.two span {width:43px;height:43px;font-size:26px;left:calc(50% - 21px);top:-21px}
.food-orbit.two span:nth-child(2){left:auto;right:-20px;top:calc(50% - 21px)}
.food-orbit.two span:nth-child(3){left:calc(50% - 21px);top:auto;bottom:-21px}
.food-orbit.two span:nth-child(4){left:-20px;top:calc(50% - 21px)}
.food-orbit.three span {width:39px;height:39px;font-size:23px;left:calc(50% - 19px);top:-19px}
.food-orbit.three span:nth-child(2){left:auto;right:-18px;top:calc(50% - 19px)}
.food-orbit.three span:nth-child(3){left:calc(50% - 19px);top:auto;bottom:-19px}
.food-orbit.three span:nth-child(4){left:-18px;top:calc(50% - 19px)}
.loading-center {position:relative;z-index:3;text-align:center;padding:34px 42px;border:1px solid #9edbff2c;border-radius:28px;background:radial-gradient(ellipse at top,#2d74a833,#0a234600 75%);box-shadow:0 20px 90px #0002;}
.loading-logo {font-size:50px;margin-bottom:10px;filter:drop-shadow(0 0 18px #79d5ff88);animation:logoFloat 2.3s ease-in-out infinite;}
.loading-dots {display:flex;gap:7px;justify-content:center;margin-top:25px;}
.loading-dots i {width:7px;height:7px;border-radius:50%;background:#75d5ff;box-shadow:0 0 12px #75d5ff;animation:dotPulse 1s ease-in-out infinite;}
.loading-dots i:nth-child(2){animation-delay:.15s}.loading-dots i:nth-child(3){animation-delay:.3s}
@keyframes orbitSpin {to{transform:rotate(360deg)}}
@keyframes foodBob {0%,100%{margin-top:0;transform:scale(1)}50%{margin-top:-5px;transform:scale(1.08)}}
@keyframes logoFloat {0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-5px) scale(1.04)}}
@keyframes dotPulse {0%,80%,100%{transform:scale(.6);opacity:.45}40%{transform:scale(1.2);opacity:1}}
@keyframes splashOut {to{opacity:0;visibility:hidden}}
@media(max-width:560px){.food-orbit{width:170px;height:170px}.food-orbit.two{width:240px;height:240px}.food-orbit.three{width:305px;height:305px}.loading-center{padding:24px 26px}.foodwise-splash .tagline{font-size:10px;letter-spacing:1.3px}}
@media(prefers-reduced-motion:reduce){.food-orbit,.food-orbit span,.loading-logo,.loading-dots i{animation-duration:20s}.foodwise-splash{animation-delay:1.5s}}

/* Improve contrast for select menus, dropdown options, and radio/checkbox labels. */
[data-baseweb="select"] > div {background:#ffffff !important;color:#202b22 !important;border-color:#cbd8ca !important;}
[data-baseweb="select"] input, [data-baseweb="select"] span, [data-baseweb="popover"] li, [role="option"] {color:#202b22 !important;-webkit-text-fill-color:#202b22 !important;}
[data-baseweb="popover"], ul[role="listbox"] {background:#ffffff !important;}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {color:#202b22 !important;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f0f7ec 0%,#e3efe0 100%) !important;border-right:1px solid #d7e5d2;}
[data-testid="stSidebar"] * {color:#263a2b;}
[data-testid="stSidebar"] .tip {background:#e0edda;color:#526750;}
[data-testid="stSidebar"] h1 {font-family:Manrope,sans-serif;font-weight:800;letter-spacing:-1px;color:#202b22;}
.block-container {padding-top:1.6rem;padding-bottom:2rem;max-width:1500px;}
h1,h2,h3 {font-family:Manrope,sans-serif!important;letter-spacing:-.7px!important;color:#202b22;}
.eyebrow {font-size:10px;font-weight:800;letter-spacing:1.5px;color:#648067;text-transform:uppercase;margin-bottom:8px;}
.hero {background:#fff;border:1px solid #e8ebe4;border-radius:18px;padding:28px 30px;margin:0 0 20px;}
.hero h1 {font-size:38px;line-height:1.16;margin:8px 0 12px;}
.green {color:#2e7547;}
.sub {font-size:13px;color:#788078;line-height:1.7;}
.metric-card {background:#fff;border:1px solid #e8ebe4;border-radius:14px;padding:17px 18px;min-height:112px;}
.metric-card.warn {background:#f0f7ed;border-color:#dfebd9;}
.metric-label {font-size:12px;color:#778177;font-weight:600;}
.metric-value {font-family:Manrope,sans-serif;font-size:29px;font-weight:800;letter-spacing:-1px;margin:9px 0 2px;color:#202b22;}
.metric-foot {font-size:10px;color:#899188;}
.panel {background:#fff;border:1px solid #e8ebe4;border-radius:15px;padding:20px 22px;margin-bottom:16px;}
.food-row {padding:12px 0;border-bottom:1px solid #f0f1ed;}
.pill {display:inline-block;border-radius:30px;padding:5px 9px;font-size:10px;font-weight:800;background:#fff0df;color:#a65d22;}
.tip {background:#f0f2eb;border-radius:11px;padding:15px 17px;color:#687466;font-size:12px;line-height:1.6;}
.stButton>button {background:#2e7547;color:white;border:0;border-radius:9px;font-weight:700;padding:.55rem 1rem;}
.stButton>button:hover {background:#235f39;color:white;border:0;}
/* Keep recipe preference text readable across Streamlit themes. */
.stTextArea textarea, textarea[data-testid] {background-color:#ffffff !important;color:#202b22 !important;-webkit-text-fill-color:#202b22 !important;border:1px solid #d9e1d5 !important;border-radius:10px !important;caret-color:#202b22 !important;}
.stTextArea textarea::placeholder {color:#788078 !important;-webkit-text-fill-color:#788078 !important;opacity:1 !important;}
.stTextArea label, .stTextArea label p {color:#202b22 !important;}
/* High-contrast safety notice: pale green background with readable dark text. */
div[data-testid="stAlert"] {background:#e8f4e8 !important;border:1px solid #b8d8bb !important;border-radius:12px !important;}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {color:#23432b !important;-webkit-text-fill-color:#23432b !important;opacity:1 !important;}
div[data-testid="stAlert"] svg {fill:#2e7547 !important;color:#2e7547 !important;}
div[data-testid="stForm"] {background:#fff;border:1px solid #e8ebe4;border-radius:14px;padding:18px;}
.recipe-box {background:#f0f5e9;border-radius:15px;padding:22px;}
footer {color:#8b9389;}
/* Popup, menu, tooltip and dialog contrast fixes: warm light surfaces + readable dark text. */
[data-baseweb="popover"], [data-baseweb="menu"], [data-testid="stPopover"],
[data-testid="stDialog"], [role="dialog"], [data-testid="stTooltipContent"],
[data-testid="stToast"], [data-testid="stNotification"] {
  background:#fffdf7 !important;
  color:#202b22 !important;
  border-color:#d8e3d4 !important;
}
[data-baseweb="popover"] *, [data-baseweb="menu"] *, [data-testid="stPopover"] *,
[data-testid="stDialog"] *, [role="dialog"] *, [data-testid="stTooltipContent"] *,
[data-testid="stToast"] *, [data-testid="stNotification"] * {
  color:#202b22 !important;
  -webkit-text-fill-color:#202b22 !important;
  opacity:1 !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
[role="option"][aria-selected="true"] {
  background:#e5f1e2 !important;
}
[data-testid="stDialog"] button, [role="dialog"] button {
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  background:#2e7547 !important;
  border-color:#2e7547 !important;
}
[data-testid="stTooltipContent"] {background:#fffdf7 !important; box-shadow:0 4px 18px #243b2b22 !important;}
[data-testid="stAlert"] a, [data-testid="stDialog"] a, [role="dialog"] a {color:#17683a !important; text-decoration:underline !important;}

/* FIX: Streamlit/BaseWeb calendar day numbers and month controls must remain visible. */
[data-baseweb="calendar"], [data-baseweb="datepicker"],
[data-baseweb="calendar"] *, [data-baseweb="datepicker"] * {
  color:#24352a !important;
  -webkit-text-fill-color:#24352a !important;
}
[data-baseweb="calendar"] button,
[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="button"],
[data-baseweb="calendar"] [role="grid"] button {
  color:#24352a !important;
  -webkit-text-fill-color:#24352a !important;
  background:#fffdf7 !important;
  opacity:1 !important;
  border-radius:7px !important;
}
[data-baseweb="calendar"] button:hover,
[data-baseweb="calendar"] [aria-selected="true"],
[data-baseweb="calendar"] button[aria-pressed="true"] {
  background:#dcefd8 !important;
  color:#173d25 !important;
  -webkit-text-fill-color:#173d25 !important;
  font-weight:800 !important;
}
[data-baseweb="calendar"] [aria-disabled="true"] {
  color:#9aa59a !important;
  -webkit-text-fill-color:#9aa59a !important;
}
/* Food/category popup menus: prevent clipped labels and force readable option contrast. */
[data-baseweb="popover"], [data-baseweb="menu"],
[data-baseweb="popover"] ul, [data-baseweb="menu"] ul,
ul[role="listbox"] {
  background:#fffdf7 !important;
  min-width:max-content !important;
  max-width:min(92vw,420px) !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"],
li[role="option"], [data-baseweb="select"] [role="option"] {
  color:#24352a !important;
  -webkit-text-fill-color:#24352a !important;
  background:#fffdf7 !important;
  opacity:1 !important;
  white-space:normal !important;
  overflow:visible !important;
  text-overflow:clip !important;
  line-height:1.45 !important;
  min-height:38px !important;
  padding-top:9px !important;
  padding-bottom:9px !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
[role="option"][aria-selected="true"] {
  background:#e4f1df !important;
  color:#173d25 !important;
  -webkit-text-fill-color:#173d25 !important;
}
/* Pantry inputs/select controls: enough width and contrast for complete option names. */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  min-height:44px !important;
  background:#fffdf7 !important;
  color:#24352a !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] *,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {
  color:#24352a !important;
  -webkit-text-fill-color:#24352a !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] input {
  min-width:3rem !important;
}
[data-testid="stSelectbox"] label, [data-testid="stDateInput"] label,
[data-testid="stNumberInput"] label, [data-testid="stTextInput"] label {
  color:#24352a !important;
  font-weight:600 !important;
}


/* Final Streamlit Cloud compatibility fix: BaseWeb menus are rendered in a portal
   near the end of the document, so style their actual popup and nested text nodes. */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="menu"],
[role="listbox"],
[role="listbox"] > div {
  background-color: #fffdf7 !important;
  color: #202b22 !important;
  opacity: 1 !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [role="option"] *,
[data-baseweb="menu"] [role="option"],
[data-baseweb="menu"] [role="option"] *,
[role="listbox"] [role="option"],
[role="listbox"] [role="option"] *,
li[role="option"], li[role="option"] * {
  background-color: transparent !important;
  color: #202b22 !important;
  -webkit-text-fill-color: #202b22 !important;
  opacity: 1 !important;
  visibility: visible !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
[role="listbox"] [role="option"]:hover,
[role="option"][aria-selected="true"] {
  background-color: #e4f1df !important;
  color: #173d25 !important;
  -webkit-text-fill-color: #173d25 !important;
}
/* Streamlit versions use different internal markup for the date picker. */
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] input *,
[data-testid="stDateInput"] [data-baseweb="input"] > div,
[data-testid="stDateInput"] [data-baseweb="input"] input {
  background-color: #fffdf7 !important;
  color: #202b22 !important;
  -webkit-text-fill-color: #202b22 !important;
  caret-color: #202b22 !important;
  opacity: 1 !important;
}
[data-baseweb="calendar"],
[data-baseweb="calendar"] > div,
[data-baseweb="datepicker"],
[data-baseweb="datepicker"] > div,
[data-baseweb="popover"] [data-baseweb="calendar"],
[data-baseweb="popover"] [data-baseweb="datepicker"],
[data-baseweb="popover"] [role="grid"],
[data-baseweb="popover"] [role="grid"] * {
  background-color: #fffdf7 !important;
  color: #202b22 !important;
  -webkit-text-fill-color: #202b22 !important;
  opacity: 1 !important;
}
[data-baseweb="calendar"] button,
[data-baseweb="calendar"] button *,
[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="gridcell"] *,
[data-baseweb="calendar"] [role="button"],
[data-baseweb="datepicker"] button,
[data-baseweb="datepicker"] button *,
[data-baseweb="datepicker"] [role="gridcell"],
[data-baseweb="datepicker"] [role="gridcell"] *,
[data-baseweb="popover"] [role="grid"] button,
[data-baseweb="popover"] [role="grid"] button * {
  color: #202b22 !important;
  -webkit-text-fill-color: #202b22 !important;
  opacity: 1 !important;
  visibility: visible !important;
}
[data-baseweb="calendar"] button:hover,
[data-baseweb="calendar"] [aria-selected="true"],
[data-baseweb="datepicker"] button:hover,
[data-baseweb="datepicker"] [aria-selected="true"],
[data-baseweb="popover"] [role="grid"] [aria-selected="true"] {
  background-color: #dcefd8 !important;
  color: #173d25 !important;
  -webkit-text-fill-color: #173d25 !important;
}
/* Pantry action labels: allow readable full labels and comfortable button height. */
[data-testid="stVerticalBlock"] [data-testid="stButton"] > button {
  width: 100% !important;
  min-height: 44px !important;
  height: auto !important;
  padding: 0.65rem 0.45rem !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
  line-height: 1.25 !important;
  word-break: normal !important;
  font-size: 0.92rem !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stButton"] p {
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

/* Some Streamlit builds use react-datepicker class names instead of BaseWeb. */
.react-datepicker,
.react-datepicker__month-container,
.react-datepicker__header,
.react-datepicker__month,
.react-datepicker__week,
.react-datepicker__day-names {
  background: #fffdf7 !important;
  color: #202b22 !important;
}
.react-datepicker *,
.react-datepicker__current-month,
.react-datepicker__day-name,
.react-datepicker__day,
.react-datepicker__navigation-icon::before {
  color: #202b22 !important;
  -webkit-text-fill-color: #202b22 !important;
  opacity: 1 !important;
}
.react-datepicker__day:hover,
.react-datepicker__day--selected,
.react-datepicker__day--keyboard-selected {
  background: #dcefd8 !important;
  color: #173d25 !important;
}

/* Sidebar menu labels: white, bold text with a deep-green button for contrast. */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 800 !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: #245d3a !important;
  border: 1px solid #245d3a !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #17492b !important;
  border-color: #17492b !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if not st.session_state.get("foodwise_splash_shown", False):
    st.session_state.foodwise_splash_shown = True
    st.markdown("""
    <div class="foodwise-splash">
      <div class="food-orbit"><span>🍅</span><span>🥕</span><span>🍎</span><span>🥑</span></div>
      <div class="food-orbit two"><span>🥛</span><span>🧀</span><span>🥚</span><span>🍞</span></div>
      <div class="food-orbit three"><span>🍚</span><span>🥦</span><span>🍌</span><span>🧅</span></div>
      <div class="loading-center">
        <div class="loading-logo">🥬</div>
        <div class="brand">FOODWISE AI</div>
        <div class="tagline">Fresh ideas. Less waste.</div>
        <div class="loading-dots"><i></i><i></i><i></i></div>
      </div>
      <div style="position:absolute;bottom:35px;color:#a9c8eb;font-size:11px;letter-spacing:1px">PREPARING YOUR KITCHEN</div>
    </div>
    """, unsafe_allow_html=True)

if "pantry" not in st.session_state:
    today = date.today()
    st.session_state.pantry = [
        {"id": 1, "name": "Spinach", "quantity": "1 bunch", "expiry": (today + timedelta(days=1)).isoformat(), "category": "Fruits & vegetables", "added_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")},
        {"id": 2, "name": "Tomatoes", "quantity": "4 pieces", "expiry": (today + timedelta(days=2)).isoformat(), "category": "Fruits & vegetables", "added_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")},
        {"id": 3, "name": "Cooked rice", "quantity": "2 cups", "expiry": today.isoformat(), "category": "Rice items", "added_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")},
        {"id": 4, "name": "Yogurt", "quantity": "1 cup", "expiry": (today + timedelta(days=3)).isoformat(), "category": "Dairy", "added_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")},
    ]
if "saved_log" not in st.session_state: st.session_state.saved_log = []
if "waste_log" not in st.session_state: st.session_state.waste_log = []
if "next_id" not in st.session_state: st.session_state.next_id = 5
if "page" not in st.session_state: st.session_state.page = "Overview"


def days_left(item):
    try: return (date.fromisoformat(item["expiry"]) - date.today()).days
    except Exception: return 999

# App warning thresholds are reminders, not guarantees that food is safe.
# Medicines are flagged as expired immediately; never apply a post-expiry grace period.
FOOD_WARNING_DAYS = {
    "Rice items": 1,
    "Dairy": 1,
    "Juices": 2,
    "Snacks": 2,
    "Fruits & vegetables": 1,
    "Other": 0,
}


def expiry_status(item):
    """Return a category-aware reminder; visual checks matter for fresh produce."""
    days = days_left(item)  # positive = days remaining; negative = days past label date
    category = item.get("category", "Other")
    if category == "Fruits & vegetables":
        # Produce freshness varies; use the date as a reminder, not a safety verdict.
        if days < 0:
            return ("🥦 Check freshness: if still fresh, use it soon; if rotten, moldy, slimy, or smells unusual, throw it away. Don't taste-test it.", "#a65d22")
        if days <= 1:
            return ("🥦 If it's fresh, use it soon; if it's rotten, moldy, slimy, or smells unusual, throw it away. Don't taste-test it.", "#a65d22")
        return (f"{days} day(s) until date · Check freshness before use; discard if rotten or moldy.", "#788078")
    if category == "Medicines":
        if days < 0:
            return ("⚠️ EXPIRED MEDICINE — DO NOT USE. Ask a pharmacist or healthcare professional how to dispose of it safely.", "#b42318")
        if days == 0:
            return ("⚠️ Medicine reaches its expiry date today. Follow the label and ask a pharmacist if unsure.", "#a65d22")
        return (f"Medicine expiry in {days} day(s). Follow the package instructions.", "#788078")

    allowed_days = FOOD_WARNING_DAYS.get(category, 0)
    past_days = -days if days < 0 else 0
    if days < 0 and past_days > allowed_days:
        return (f"⚠️ POSSIBLE SPOILAGE — DO NOT USE. This item is {past_days} day(s) past its date. It may be unsafe or harmful. Discard it if safety is uncertain; the date alone cannot confirm spoilage.", "#b42318")
    if days < 0:
        return (f"Date passed by {past_days} day(s). Check the label and storage guidance carefully; this is not a guarantee of safety.", "#a65d22")
    if days == 0:
        return ("Date is today — follow the label and storage guidance.", "#a65d22")
    return (f"{days} day(s) until date", "#788078")


def now_ist():
    """Use India Standard Time explicitly; Streamlit Cloud servers may use UTC."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))


def get_whatsapp_config():
    """Read WhatsApp Cloud API credentials from Streamlit secrets or environment."""
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    try:
        token = token or str(st.secrets.get("WHATSAPP_ACCESS_TOKEN", ""))
        phone_id = phone_id or str(st.secrets.get("WHATSAPP_PHONE_NUMBER_ID", ""))
    except Exception:
        pass
    return token.strip(), phone_id.strip()


def send_whatsapp_message(to_number, message):
    """Send a WhatsApp text via Meta WhatsApp Cloud API."""
    token, phone_id = get_whatsapp_config()
    if not token or not phone_id:
        return False, "WhatsApp API credentials are not configured yet. Add WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID to Streamlit Cloud → Settings → Secrets."
    digits = re.sub(r"\D", "", to_number or "")
    if not digits or len(digits) < 8 or len(digits) > 15:
        return False, "Enter a valid WhatsApp number with country code, e.g. 919876543210 (no + or spaces needed)."
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": digits,
        "type": "text",
        "text": {"preview_url": False, "body": message[:4000]},
    }
    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{phone_id}/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            if response.status in (200, 201) and result.get("messages"):
                return True, "WhatsApp message accepted by Meta for delivery."
            return False, "WhatsApp API did not confirm the message. Check your Meta WhatsApp setup."
    except Exception as exc:
        detail = str(exc)
        try:
            if getattr(exc, "read", None):
                detail = exc.read().decode("utf-8")[:500]
        except Exception:
            pass
        return False, f"Could not send WhatsApp message. Check the API credentials, recipient opt-in, and Meta error details: {detail}"


def format_added_at(value):
    """Format stored timestamps in IST; treat older naive timestamps as IST."""
    if not value:
        return "Date/time unavailable"
    try:
        stamp = datetime.fromisoformat(value)
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        else:
            stamp = stamp.astimezone(ZoneInfo("Asia/Kolkata"))
        return stamp.strftime("%d %b %Y · %I:%M:%S %p IST")
    except (TypeError, ValueError):
        return "Date/time unavailable"


def emoji_for(name, category=None):
    low = str(name).lower()
    cat = str(category or "").lower()
    # Check medicines before food keywords so medicine items never fall through to the tin emoji.
    medicine_words = ("medicine", "medication", "tablet", "capsule", "pill", "syrup", "antibiotic", "paracetamol", "crocin", "dolo", "vitamin")
    if cat == "medicines" or any(word in low for word in medicine_words):
        return "💊"
    pairs = {"spinach":"🥬","tomato":"🍅","rice":"🍚","yogurt":"🥣","carrot":"🥕","apple":"🍎","banana":"🍌","bread":"🍞","milk":"🥛","potato":"🥔","onion":"🧅","egg":"🥚","cheese":"🧀","lemon":"🍋","beans":"🫘","lettuce":"🥗"}
    for key, emoji in pairs.items():
        if key in low:
            return emoji
    return "🥫"

def money(value): return "₹" + format(float(value or 0), ",.2f").rstrip("0").rstrip(".")

def remove_item(item_id):
    st.session_state.pantry = [x for x in st.session_state.pantry if x["id"] != item_id]

def make_recipes(preferences):
    """Generate general recipes with Gemini without reading or sending pantry data."""

    # Read Gemini credentials from Streamlit Cloud Secrets, or environment variables locally.
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        model = st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash")
    except Exception:
        api_key = ""
        model = "gemini-3.8-flash"

    api_key = os.getenv("GEMINI_API_KEY", api_key) or api_key
    model = os.getenv("GEMINI_MODEL", model) or model
    api_key = str(api_key or "").strip().strip('"').strip("'")
    model = str(model or "gemini-3.8-flash").strip()

    if not api_key:
        return (
            "Live Gemini AI is not configured yet. Open your Streamlit Cloud app → Settings → Secrets and add:\n\n"
            'GEMINI_API_KEY = "your_gemini_api_key_here"\n'
            'GEMINI_MODEL = "gemini-3.8-flash"\n\n'
            "Create your key at https://aistudio.google.com/app/apikey, save the secrets, then reboot the app. "
            "Keep your API key private. This app will not show sample recipes as if they were AI-generated."
        ), "Gemini setup required"

    prompt = (
        "Create 3 general, practical recipes. Do not access, infer, mention, or use any pantry inventory. "
        "Base the recipes only on the dietary preferences and cooking requirements provided by the user. "
        "Dietary preferences and requirements: " + (preferences.strip() or "none specified") + ". "
        "Choose common, widely available ingredients and include approximate quantities, preparation/cooking time, "
        "and 3-6 numbered steps for each recipe. Use a professional, clear, formal tone. "
        "Do not claim that the recipes are based on the user's pantry or available ingredients. "
        "Do not recommend using food that may be spoiled or unsafe. Explain briefly that smell and appearance "
        "cannot guarantee food safety. Return readable Markdown."
    )

    # Google now recommends the Interactions API for new Gemini integrations.
    endpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"
    payload = {
        "model": model,
        "input": prompt,
        "system_instruction": (
            "You are FoodWise AI, a professional cooking assistant. Generate general recipes without accessing or "
            "using pantry inventory. Respect stated dietary preferences and never advise eating unsafe or spoiled food."
        ),
        "generation_config": {"thinking_level": "low"}
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        # Interactions API returns output_text in current responses; retain a
        # fallback parser for responses represented as an output item list.
        answer = str(data.get("output_text", "") or "").strip()
        if not answer:
            chunks = []
            for item in data.get("output", []) or []:
                if not isinstance(item, dict):
                    continue
                if item.get("text"):
                    chunks.append(str(item["text"]).strip())
                for part in item.get("content", []) or []:
                    if isinstance(part, dict) and part.get("text"):
                        chunks.append(str(part["text"]).strip())
            answer = "\n\n".join(chunk for chunk in chunks if chunk).strip()
        if not answer:
            return "Gemini returned an empty response. Please try again.", "Gemini response unavailable"
        return answer, "Live Gemini AI · " + model

    except urllib.error.HTTPError as exc:
        status = getattr(exc, "code", None)
        try:
            body = json.loads(exc.read().decode("utf-8", errors="replace"))
            err = body.get("error", {}) if isinstance(body, dict) else {}
            err_message = str(err.get("message", "") or "")
        except Exception:
            err_message = ""

        if status == 400:
            message = f"Gemini rejected the request (HTTP 400). Check GEMINI_MODEL and request settings. Details: {err_message[:350]}"
        elif status == 401:
            message = "Gemini rejected the API key (HTTP 401). Create a new key at https://aistudio.google.com/app/apikey and replace GEMINI_API_KEY in Streamlit Cloud → Settings → Secrets. Paste the Google AI Studio key only, then save and reboot."
        elif status == 403:
            message = f"Gemini access was denied (HTTP 403). Check that the Google Cloud project has Gemini API access enabled and the key is valid. Details: {err_message[:350]}"
        elif status == 404:
            message = f"Gemini model or endpoint not found (HTTP 404). Check GEMINI_MODEL in Streamlit Secrets; use gemini-3.8-flash if it is available to your project. Details: {err_message[:350]}"
        elif status == 429:
            message = "Gemini API quota or rate limit reached (HTTP 429). Check your Google AI Studio project quota/billing and try again later."
        elif status:
            message = f"Gemini returned HTTP {status}. Check your API key, model, and project settings. Details: {err_message[:350]}"
        else:
            message = "Gemini returned an API error. Check the Gemini API configuration and try again."
        return message, "Gemini connection error"

    except Exception:
        return "Could not reach Gemini. Check the app's internet connection and Gemini API configuration, then try again.", "Gemini connection error"

with st.sidebar:
    st.markdown("# ✳ foodwise<span style='color:#2e7547'>.ai</span>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>YOUR KITCHEN</div>", unsafe_allow_html=True)
    choices = ["Overview", "My Pantry", "AI Recipe Lab", "Your Impact", "Monthly Report", "WhatsApp Alerts"]
    for choice, icon in zip(choices, ["⌂", "▦", "♨", "↗", "▤", "☏"]):
        if st.button(f"{icon}  {choice}", key="nav_"+choice, use_container_width=True):
            st.session_state.page = choice
            st.rerun()
    st.markdown("<br><div class='tip'><b>✦ Small choices. Big impact.</b><br>Use what you have before buying more.</div><br><div style='color:#788078;font-size:12px'>◉ My Kitchen<br><small>Waste less, live better</small></div>", unsafe_allow_html=True)

pantry = sorted(st.session_state.pantry, key=lambda x: (days_left(x), x["name"].lower()))
urgent = sum(1 for x in pantry if 0 <= days_left(x) <= 1)
saved_count = len(st.session_state.saved_log)
saved_value = sum(float(x.get("cost", 0)) for x in st.session_state.saved_log)
waste_count = len(st.session_state.waste_log)
wasted_value = sum(float(x.get("cost", 30.0)) for x in st.session_state.waste_log)

if st.session_state.page == "Overview":
    st.markdown("<div class='hero'><div class='eyebrow'>YOUR KITCHEN DASHBOARD</div><h1>Good food deserves<br><span class='green'>a second chance.</span></h1><div class='sub'>A little planning goes a long way. Let's make every ingredient count.　🥬</div></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [("In your pantry", len(pantry), "ingredients tracked", False), ("Needs attention", urgent, "use today or tomorrow", True), ("Food rescued", saved_count, "items marked as saved", False), ("Money saved", money(saved_value), "your estimated savings", False)]
    for col, (label, value, foot, warn) in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='metric-card {'warn' if warn else ''}'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-foot'>{foot}</div></div>", unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.25, .9], gap="large")
    with left:
        st.markdown("### Save-it-first list")
        st.caption("Ingredients approaching their date")
        priority = [x for x in pantry if days_left(x) <= 2][:4]
        if not priority: st.success("Nothing urgent right now ✨ Your pantry is looking good.")
        for item in priority:
            d = days_left(item)
            due, due_color = expiry_status(item)
            st.markdown(f"<div class='food-row'>{emoji_for(item['name'], item.get('category'))}　<b>{item['name']}</b><br><span style='color:{due_color};font-size:12px;font-weight:{'700' if due.startswith('⚠️') else '400'}'>{item['quantity']} · {due}</span></div>", unsafe_allow_html=True)
        if st.button("View pantry ↗", key="overview_pantry"):
            st.session_state.page = "My Pantry"; st.rerun()
    with right:
        st.markdown("<div class='recipe-box'><div class='eyebrow'>MEET YOUR LEFTOVER CHEF</div><h2>What's in your fridge today?</h2><p>Turn what you already have into something delicious.</p></div>", unsafe_allow_html=True)
        if st.button("✦ Create my recipes →", key="overview_recipes"):
            st.session_state.page = "AI Recipe Lab"; st.rerun()
    st.markdown("<div class='tip'><b>✦ FoodWise principle</b><br>Best-before dates and safety expiry guidance differ by food. Follow local food-safety guidance—never taste food to test whether it's safe.</div>", unsafe_allow_html=True)

elif st.session_state.page == "My Pantry":
    st.markdown("<div class='eyebrow'>KNOW WHAT YOU HAVE</div><h1>My pantry<span class='green'>.</span></h1><p class='sub'>Keep track of your food and give every ingredient a plan.</p>", unsafe_allow_html=True)
    with st.expander("＋ Add an ingredient", expanded=False):
        with st.form("add_food_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Food name", placeholder="e.g. Carrots")
            quantity = c2.text_input("Quantity", placeholder="e.g. 3 pieces")
            expiry = c1.date_input("Date label / expiry date", value=date.today()+timedelta(days=3))
            category = c2.selectbox("Category", ["Rice items", "Dairy", "Medicines", "Juices", "Snacks", "Fruits & vegetables", "Other"], help="Expiry warnings are category-aware. They do not guarantee food is safe after its date.")
            estimated_value = st.number_input("Estimated value of this item (₹)", min_value=0.0, value=30.0, step=5.0, help="Used to estimate money saved or lost in your monthly report.")
            submitted = st.form_submit_button("Add to pantry")
            if submitted:
                if not name.strip(): st.error("Please enter a food name.")
                else:
                    st.session_state.pantry.append({"id":st.session_state.next_id,"name":name.strip(),"quantity":quantity.strip() or "1 item","expiry":expiry.isoformat(),"category":category,"cost":float(estimated_value),"added_at":now_ist().isoformat(timespec="seconds")})
                    st.session_state.next_id += 1
                    st.success(f"{name.strip()} added to your pantry.")
                    st.rerun()
    search = st.text_input("⌕ Search your ingredients", placeholder="Search your ingredients...")
    filtered = [x for x in pantry if search.lower() in x["name"].lower()]
    st.caption(f"{len(filtered)} items")
    if not filtered: st.info("No matching food found. Add an ingredient to get started.")
    for start in range(0, len(filtered), 3):
        cols = st.columns(3)
        for col, item in zip(cols, filtered[start:start+3]):
            d = days_left(item)
            date_text, date_color = expiry_status(item)
            with col:
                warning_style = "background:#fff0ef;border:1px solid #f2b8b5;border-radius:8px;padding:9px 10px;font-weight:700;" if date_text.startswith("⚠️") else ""
                added_at = item.get("added_at")
                try:
                    added_display = format_added_at(added_at)
                except (TypeError, ValueError):
                    added_display = "Date/time unavailable"
                st.markdown(f"<div class='panel'><div style='font-size:28px'>{emoji_for(item['name'], item.get('category'))}</div><h3>{item['name']}</h3><p class='sub'>{item['quantity']} · {item['category']}</p><p style='font-size:12px;color:#647568'>🕒 Added: {added_display}</p><p style='font-size:12px;color:{date_color};{warning_style}'>{date_text}</p></div>", unsafe_allow_html=True)
                # Give the two important actions half-width each so their labels are not clipped.
                action_left, action_right = st.columns(2, gap="small")
                if action_left.button("✓ I used it", key=f"used_{item['id']}", use_container_width=True):
                    st.session_state.saved_log.append({
                        "name": item["name"], "quantity": item["quantity"],
                        "category": item["category"], "cost": float(item.get("cost", 30.0)),
                        "date": date.today().isoformat(),
                    })
                    remove_item(item["id"])
                    st.session_state.foodwise_flash = f"{item['name']} logged under Used / rescued (estimated ₹30 saved)."
                    st.rerun()
                if action_right.button("✕ Wasted", key=f"wasted_{item['id']}", use_container_width=True):
                    st.session_state.waste_log.append({
                        "name": item["name"], "quantity": item["quantity"],
                        "category": item["category"], "cost": float(item.get("cost", 30.0)),
                        "date": date.today().isoformat(),
                        "reason": "Not used before being removed from the pantry",
                    })
                    remove_item(item["id"])
                    st.session_state.foodwise_flash = f"{item['name']} logged under Not used / wasted."
                    st.rerun()
                if st.button("Remove item", key=f"remove_{item['id']}", use_container_width=True, type="secondary"):
                    remove_item(item["id"])
                    st.rerun()
    if st.session_state.get("foodwise_flash"):
        st.success(st.session_state.foodwise_flash)
        del st.session_state.foodwise_flash
    if st.session_state.saved_log:
        st.markdown("### Recent food rescued")
        st.caption("Used / rescued items recorded in this session. Default estimated value: ₹30 per item.")
        for row in reversed(st.session_state.saved_log[-5:]):
            st.markdown(f"**{row['name']}** · {row.get('quantity', '1 item')} · {row['date']} — {money(row['cost'])}")
    if st.session_state.waste_log:
        st.markdown("### Recent not used / wasted")
        for row in reversed(st.session_state.waste_log[-5:]):
            st.markdown(f"**{row['name']}** · {row.get('quantity', '1 item')} · {row['date']}")

elif st.session_state.page == "AI Recipe Lab":
    st.markdown("<div class='eyebrow'>CREATIVE COOKING, LESS WASTE</div><h1>AI Recipe Lab<span class='green'>.</span></h1><p class='sub'>Explore practical recipe ideas tailored to your dietary preferences.</p>", unsafe_allow_html=True)
    left, right = st.columns([.8, 1.2], gap="large")
    with left:
        st.markdown("<div class='recipe-box'><div style='font-size:28px'>♨</div><h2>Recipe recommendations</h2><p>Generate general recipe ideas using common ingredients. Your pantry inventory is not accessed for this feature.</p></div>", unsafe_allow_html=True)
        preferences = st.text_area("Dietary preferences (optional)", placeholder="e.g. vegetarian, no peanuts, quick meals...")
        if st.button("✦ Generate recipes →", use_container_width=True):
            with st.spinner("Preparing recipe recommendations..."):
                result, mode = make_recipes(preferences)
            st.session_state.recipes_result = result
            st.session_state.recipes_mode = mode
    with right:
        st.markdown("### Your recipe ideas")
        st.caption(st.session_state.get("recipes_mode", "Ready when you are"))
        if st.session_state.get("recipes_result"):
            st.markdown(st.session_state.recipes_result)
        else:
            st.markdown("<div class='panel' style='text-align:center;padding:45px 15px'><div style='font-size:42px'>🍲</div><b>Your recipe ideas will appear here.</b><p class='sub'>Generate general recipes tailored to your stated preferences, without using pantry data.</p></div>", unsafe_allow_html=True)
    st.warning("Safety first: Do not use food that may be spoiled. Follow storage guidance, and discard food when safety is uncertain. Reheating does not make all improperly stored food safe.")

elif st.session_state.page == "Your Impact":
    st.markdown("<div class='eyebrow'>EVERY INGREDIENT COUNTS</div><h1>Your impact<span class='green'>.</span></h1><p class='sub'>See the food you used and the estimated savings you created.</p>", unsafe_allow_html=True)
    total_logged_items = saved_count + waste_count
    item_waste_rate = (waste_count / total_logged_items * 100) if total_logged_items else 0
    total_logged_value = saved_value + wasted_value
    value_waste_rate = (wasted_value / total_logged_value * 100) if total_logged_value else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Food items used / rescued</div><div class='metric-value'>{saved_count}</div><div class='metric-foot'>logged by you</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Food items wasted</div><div class='metric-value'>{waste_count}</div><div class='metric-foot'>{money(wasted_value)} estimated value lost</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Estimated money saved</div><div class='metric-value'>{money(saved_value)}</div><div class='metric-foot'>based on item values</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><div class='metric-label'>Waste percentage</div><div class='metric-value'>{item_waste_rate:.1f}%</div><div class='metric-foot'>{value_waste_rate:.1f}% of logged value wasted</div></div>", unsafe_allow_html=True)
    st.markdown("### Used / rescued list")
    if st.session_state.saved_log:
        for row in reversed(st.session_state.saved_log):
            st.markdown(f"**{row['name']}** · {row.get('quantity', '1 item')} · {row['date']} — saved estimate {money(row.get('cost', 0))}")
    else:
        st.info("No used / rescued items logged yet. In My Pantry, choose ‘I used it’ when you use an ingredient.")
    st.markdown("### Not used / wasted list")
    if st.session_state.waste_log:
        for row in reversed(st.session_state.waste_log):
            st.markdown(f"**{row['name']}** · {row.get('quantity', '1 item')} · {row['date']} — {row.get('reason', 'Marked as wasted')}")
    else:
        st.success("No wasted items logged yet. Great start — keep tracking honestly.")

elif st.session_state.page == "WhatsApp Alerts":
    st.markdown("<div class='eyebrow'>EXPIRY REMINDERS</div><h1>WhatsApp alerts<span class='green'>.</span></h1><p class='sub'>Get a WhatsApp reminder about pantry items that are approaching their labelled date.</p>", unsafe_allow_html=True)
    st.info("To send real WhatsApp messages, connect the official Meta WhatsApp Cloud API in Streamlit Cloud Secrets. A phone number alone cannot send messages.")
    saved_number = st.session_state.get("whatsapp_number", "")
    with st.form("whatsapp_settings_form"):
        phone_number = st.text_input("WhatsApp number (include country code)", value=saved_number, placeholder="e.g. 919876543210", help="Enter the recipient's number in international format, digits only. Get the recipient's permission first.")
        reminder_days = st.selectbox("Remind me when items are due within", [0, 1, 2, 3, 5, 7], index=2, format_func=lambda n: "On the date only" if n == 0 else f"{n} day(s) before the date")
        save_alert_settings = st.form_submit_button("Save alert preferences", use_container_width=True)
        if save_alert_settings:
            normalized = re.sub(r"\D", "", phone_number or "")
            if len(normalized) < 8 or len(normalized) > 15:
                st.error("Enter a valid number with country code, such as 919876543210.")
            else:
                st.session_state.whatsapp_number = normalized
                st.session_state.whatsapp_reminder_days = int(reminder_days)
                st.success("WhatsApp alert preferences saved for this app session.")
    st.markdown("### Items that need a reminder")
    selected_days = int(st.session_state.get("whatsapp_reminder_days", 2))
    alert_items = [item for item in pantry if 0 <= days_left(item) <= selected_days]
    if alert_items:
        for item in alert_items:
            remaining = days_left(item)
            when = "due today" if remaining == 0 else f"due in {remaining} day(s)"
            st.markdown(f"- **{item['name']}** ({item.get('quantity', '1 item')}) — {when}; date: {item['expiry']}")
    else:
        st.success(f"No pantry items are due within the next {selected_days} day(s).")
    saved_number = st.session_state.get("whatsapp_number", "")
    if saved_number:
        st.markdown("### Send a message")
        st.caption(f"Recipient: +{saved_number}")
        test_col, expiry_col = st.columns(2)
        if test_col.button("Send test WhatsApp", use_container_width=True):
            ok, message = send_whatsapp_message(saved_number, "🥬 FoodWise AI test message. Your WhatsApp alert connection is working if you received this.")
            (st.success if ok else st.error)(message)
        if expiry_col.button("Send expiry reminders now", use_container_width=True, disabled=not alert_items):
            lines = ["🥬 *FoodWise AI — Expiry reminder*", "Please check these pantry items:"]
            for item in alert_items:
                remaining = days_left(item)
                due_text = "due today" if remaining == 0 else f"due in {remaining} day(s)"
                lines.append(f"• {item['name']} ({item.get('quantity', '1 item')}) — {due_text}; date: {item['expiry']}")
            lines.append("Follow the package/storage guidance. This reminder is not a guarantee that food is safe.")
            ok, message = send_whatsapp_message(saved_number, "\n".join(lines))
            (st.success if ok else st.error)(message)
    else:
        st.caption("Save a WhatsApp number above to enable sending controls.")
    st.warning("Important: this version can send a test or expiry reminder when you press a button. Automatic messages at a future time need a scheduled service (such as GitHub Actions or a server cron job), persistent storage for your pantry and preferences, and approved WhatsApp API setup. Streamlit by itself does not run reliably as a background scheduler. Messages outside WhatsApp's customer-service window may require an approved message template.")

else:
    st.markdown("<div class='eyebrow'>MONTHLY FOOD MANAGEMENT</div><h1>Monthly report<span class='green'>.</span></h1><p class='sub'>Review what you used, what went to waste, and how to improve next month.</p>", unsafe_allow_html=True)
    month_choice = st.date_input("Choose a month", value=date.today().replace(day=1), help="Choose any date in the month you want to review.")
    month_start = month_choice.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    used_month = [x for x in st.session_state.saved_log if month_start.isoformat() <= x.get("date", "") <= month_end.isoformat()]
    wasted_month = [x for x in st.session_state.waste_log if month_start.isoformat() <= x.get("date", "") <= month_end.isoformat()]
    month_saved = sum(float(x.get("cost", 0)) for x in used_month)
    month_wasted_value = sum(float(x.get("cost", 30.0)) for x in wasted_month)
    total_logged = len(used_month) + len(wasted_month)
    waste_rate = (len(wasted_month) / total_logged * 100) if total_logged else 0
    total_month_value = month_saved + month_wasted_value
    value_waste_rate = (month_wasted_value / total_month_value * 100) if total_month_value else 0
    st.markdown(f"### {month_start.strftime('%B %Y')}")
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, foot in [
        (c1, "Used / rescued", len(used_month), "items marked used"),
        (c2, "Not used / wasted", len(wasted_month), "items marked wasted"),
        (c3, "Estimated savings", money(month_saved), "from rescued food"),
        (c4, "Waste share", f"{waste_rate:.1f}%", f"{value_waste_rate:.1f}% of value wasted"),
    ]:
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-foot'>{foot}</div></div>", unsafe_allow_html=True)
    st.markdown("### 1. Used / rescued this month")
    if used_month:
        for row in used_month:
            st.markdown(f"- **{row['name']}** — {row.get('quantity', '1 item')} · {row['date']} · saved estimate {money(row.get('cost', 0))}")
    else:
        st.info("No used / rescued items were recorded for this month.")
    st.markdown("### 2. Not used / wasted this month")
    if wasted_month:
        for row in wasted_month:
            st.markdown(f"- **{row['name']}** — {row.get('quantity', '1 item')} · {row['date']} · estimated value wasted {money(row.get('cost', 30.0))}")
    else:
        st.success("No wasted items were recorded for this month.")
    st.markdown("### 3. Suggestions for next month")
    if not total_logged:
        st.info("Start logging each pantry item as ‘I used it’ or ‘Wasted’ to build a useful monthly report. Logs currently last for this Streamlit session; refreshes or app restarts may clear them.")
    else:
        if wasted_month:
            waste_names = [x.get("name", "item") for x in wasted_month]
            common = max(set(waste_names), key=waste_names.count)
            st.markdown(f"- **Plan around waste:** You logged {len(wasted_month)} wasted item(s), worth an estimated **{money(month_wasted_value)}** ({value_waste_rate:.1f}% of the logged value). Review when they were bought and reduce the amount next time.")
            st.markdown(f"- **Buy smaller quantities:** {common} appears most often in your wasted list; consider buying less or planning a meal for it earlier.")
            st.markdown("- **Use a first-in, first-out shelf:** Put older items at the front and check your pantry twice a week.")
        else:
            st.markdown("- **Keep it up:** You have no items marked wasted this month. Continue planning meals around what is already in your pantry.")
        st.markdown("- **Make a weekly use-first plan:** Choose 2–3 meals that use ingredients nearing their labelled date before shopping again.")
        st.markdown("- **Store food correctly:** Refrigerate promptly when appropriate, keep raw and cooked foods separate, and follow package storage instructions.")
    st.caption("Waste value and percentages are estimates based on the item values entered (or ₹30 default for older/sample items). The item percentage is based on logged entries; the value percentage is based on estimated rupee value. This report counts item entries, not precise weight or environmental impact. Logs are currently held in Streamlit session state, so they may not survive refreshes, new sessions, or app restarts.")

st.markdown("<hr><div style='display:flex;justify-content:space-between;color:#8b9389;font-size:10px'><span>Made with care for people and the planet</span><b>✳ FOODWISE AI · HACKATHON PROTOTYPE</b></div>", unsafe_allow_html=True)
