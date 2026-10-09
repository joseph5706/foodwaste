import streamlit as st
from datetime import date, timedelta
import os, json, urllib.request

st.set_page_config(page_title="FoodWise AI — Save Food. Save Money.", page_icon="🥬", layout="wide")

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#f7f8f3;color:#202b22;}
[data-testid="stSidebar"] {background:#fff;border-right:1px solid #e8ebe4;}
[data-testid="stSidebar"] h1 {font-family:Manrope,sans-serif;font-weight:800;letter-spacing:-1px;color:#202b22;}
.block-container {padding-top:1.6rem;padding-bottom:2rem;max-width:1500px;}
h1,h2,h3 {font-family:Manrope,sans-serif!important;letter-spacing:-.7px!important;color:#202b22;}
.eyebrow {font-size:10px;font-weight:800;letter-spacing:1.5px;color:#8b9589;text-transform:uppercase;margin-bottom:8px;}
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
div[data-testid="stForm"] {background:#fff;border:1px solid #e8ebe4;border-radius:14px;padding:18px;}
.recipe-box {background:#f0f5e9;border-radius:15px;padding:22px;}
footer {color:#8b9389;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if "pantry" not in st.session_state:
    today = date.today()
    st.session_state.pantry = [
        {"id": 1, "name": "Spinach", "quantity": "1 bunch", "expiry": (today + timedelta(days=1)).isoformat(), "category": "Vegetables"},
        {"id": 2, "name": "Tomatoes", "quantity": "4 pieces", "expiry": (today + timedelta(days=2)).isoformat(), "category": "Vegetables"},
        {"id": 3, "name": "Cooked rice", "quantity": "2 cups", "expiry": today.isoformat(), "category": "Cooked food"},
        {"id": 4, "name": "Yogurt", "quantity": "1 cup", "expiry": (today + timedelta(days=3)).isoformat(), "category": "Dairy"},
    ]
if "saved_log" not in st.session_state: st.session_state.saved_log = []
if "next_id" not in st.session_state: st.session_state.next_id = 5
if "page" not in st.session_state: st.session_state.page = "Overview"


def days_left(item):
    try: return (date.fromisoformat(item["expiry"]) - date.today()).days
    except Exception: return 999

def emoji_for(name):
    pairs = {"spinach":"🥬","tomato":"🍅","rice":"🍚","yogurt":"🥣","carrot":"🥕","apple":"🍎","banana":"🍌","bread":"🍞","milk":"🥛","potato":"🥔","onion":"🧅","egg":"🥚","cheese":"🧀","lemon":"🍋","beans":"🫘","lettuce":"🥗"}
    low = name.lower()
    for key, emoji in pairs.items():
        if key in low: return emoji
    return "🥫"

def money(value): return "₹" + format(float(value or 0), ",.2f").rstrip("0").rstrip(".")

def remove_item(item_id):
    st.session_state.pantry = [x for x in st.session_state.pantry if x["id"] != item_id]

def make_recipes(preferences):
    items = sorted(st.session_state.pantry, key=days_left)
    ingredients = [x["name"] for x in items if days_left(x) >= 0]
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        endpoint = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = ("Create 3 practical recipes using these ingredients first: " + ", ".join(ingredients) +
                  ". Dietary preferences: " + preferences +
                  ". For each recipe include title, ingredients, 3-5 steps, time, and which pantry items it helps use. "
                  "Do not advise eating potentially unsafe food. Return readable plain text.")
        payload = {"model": model, "messages": [
            {"role":"system","content":"You are FoodWise, a practical food-waste reduction assistant. Never advise eating food that may be unsafe. Smell and appearance cannot guarantee safety."},
            {"role":"user","content":prompt}], "temperature":0.5}
        try:
            req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json", "Authorization":"Bearer " + api_key})
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode())["choices"][0]["message"]["content"], "AI-powered"
        except Exception:
            pass
    items_text = ", ".join(ingredients) if ingredients else "your available pantry ingredients"
    return (f"1. Pantry Vegetable Rice Bowl (15–20 min)\nUse first: {items_text}\nSteps: Check that every ingredient has been stored safely. Cook vegetables thoroughly, add freshly prepared or safely stored rice, heat through until steaming hot, then season to taste.\n\n"
            f"2. Quick Vegetable Sauté (10–15 min)\nUse first: vegetables from your pantry\nSteps: Wash fresh vegetables, chop them, sauté until cooked through, season, and serve with a suitable grain.\n\n"
            f"3. Simple Yogurt Bowl or Raita (5–8 min)\nUse first: fresh, properly refrigerated yogurt and suitable vegetables\nSteps: Wash and chop vegetables, mix with fresh yogurt, add seasoning, and keep chilled until serving.\n\n"
            "These are general starter ideas. Adjust ingredients to your dietary needs and follow food-safety guidance. " + ("Preferences noted: " + preferences if preferences else ""), "Smart demo mode")

with st.sidebar:
    st.markdown("# ✳ foodwise<span style='color:#2e7547'>.ai</span>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>YOUR KITCHEN</div>", unsafe_allow_html=True)
    choices = ["Overview", "My Pantry", "AI Recipe Lab", "Your Impact"]
    for choice, icon in zip(choices, ["⌂", "▦", "♨", "↗"]):
        if st.button(f"{icon}  {choice}", key="nav_"+choice, use_container_width=True):
            st.session_state.page = choice
            st.rerun()
    st.markdown("<br><div class='tip'><b>✦ Small choices. Big impact.</b><br>Use what you have before buying more.</div><br><div style='color:#788078;font-size:12px'>◉ My Kitchen<br><small>Waste less, live better</small></div>", unsafe_allow_html=True)

pantry = sorted(st.session_state.pantry, key=lambda x: (days_left(x), x["name"].lower()))
urgent = sum(1 for x in pantry if 0 <= days_left(x) <= 1)
saved_count = len(st.session_state.saved_log)
saved_value = sum(x["cost"] for x in st.session_state.saved_log)

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
            due = "Date passed — check safety" if d < 0 else "Date is today" if d == 0 else f"{d} day(s) left"
            st.markdown(f"<div class='food-row'>{emoji_for(item['name'])}　<b>{item['name']}</b><br><span style='color:#788078;font-size:12px'>{item['quantity']} · {due}</span></div>", unsafe_allow_html=True)
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
            category = c2.selectbox("Category", ["Vegetables", "Fruit", "Dairy", "Cooked food", "Grains", "Other"])
            submitted = st.form_submit_button("Add to pantry")
            if submitted:
                if not name.strip(): st.error("Please enter a food name.")
                else:
                    st.session_state.pantry.append({"id":st.session_state.next_id,"name":name.strip(),"quantity":quantity.strip() or "1 item","expiry":expiry.isoformat(),"category":category})
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
            date_text = "Date passed — check safety" if d < 0 else "Date is today" if d == 0 else f"{d} day(s) until date"
            with col:
                st.markdown(f"<div class='panel'><div style='font-size:28px'>{emoji_for(item['name'])}</div><h3>{item['name']}</h3><p class='sub'>{item['quantity']} · {item['category']}</p><p style='font-size:12px;color:#a65d22'>{date_text}</p></div>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                if b1.button("✓ I used it", key=f"used_{item['id']}", use_container_width=True):
                    # Log the rescue immediately so the click updates both dashboard and impact page.
                    # ₹30 is the default estimate; users can see the recorded value in Your Impact.
                    st.session_state.saved_log.append({
                        "name": item["name"],
                        "cost": 30.0,
                        "date": date.today().isoformat(),
                    })
                    remove_item(item["id"])
                    st.session_state.foodwise_flash = f"Nice! {item['name']} was logged as rescued (estimated ₹30 saved)."
                    st.rerun()
                if b2.button("Remove", key=f"remove_{item['id']}", use_container_width=True):
                    remove_item(item["id"]); st.rerun()
    if st.session_state.get("foodwise_flash"):
        st.success(st.session_state.foodwise_flash)
        del st.session_state.foodwise_flash
    if st.session_state.saved_log:
        st.markdown("### Recent food rescued")
        st.caption("Each ‘I used it’ click logs an item with a default estimated value of ₹30.")
        for row in reversed(st.session_state.saved_log[-5:]):
            st.markdown(f"**{row['name']}** · {row['date']} — {money(row['cost'])}")

elif st.session_state.page == "AI Recipe Lab":
    st.markdown("<div class='eyebrow'>CREATIVE COOKING, LESS WASTE</div><h1>AI Recipe Lab<span class='green'>.</span></h1><p class='sub'>Recipes start with what you already own—not another shopping trip.</p>", unsafe_allow_html=True)
    left, right = st.columns([.8, 1.2], gap="large")
    with left:
        st.markdown("<div class='recipe-box'><div style='font-size:28px'>♨</div><h2>Let's make something good.</h2><p>We'll look at your pantry and prioritize ingredients that need to be used soon.</p></div>", unsafe_allow_html=True)
        preferences = st.text_area("Dietary preferences (optional)", placeholder="e.g. vegetarian, no peanuts, quick meals...")
        if st.button("✦ Generate recipes →", use_container_width=True):
            with st.spinner("Checking your pantry and preparing ideas..."):
                result, mode = make_recipes(preferences)
            st.session_state.recipes_result = result
            st.session_state.recipes_mode = mode
    with right:
        st.markdown("### Your recipe ideas")
        st.caption(st.session_state.get("recipes_mode", "Ready when you are"))
        if st.session_state.get("recipes_result"):
            st.markdown(st.session_state.recipes_result)
        else:
            st.markdown("<div class='panel' style='text-align:center;padding:45px 15px'><div style='font-size:42px'>🍲</div><b>Your next meal is waiting.</b><p class='sub'>Generate recipes to see ideas based on your current ingredients.</p></div>", unsafe_allow_html=True)
    st.warning("Safety first: Do not use food that may be spoiled. Follow storage guidance, and discard food when safety is uncertain. Reheating does not make all improperly stored food safe.")

else:
    st.markdown("<div class='eyebrow'>EVERY INGREDIENT COUNTS</div><h1>Your impact<span class='green'>.</span></h1><p class='sub'>Celebrate food you intentionally use instead of throwing away.</p>", unsafe_allow_html=True)
    st.markdown("<div class='recipe-box'><div class='eyebrow'>YOUR FOODWISE JOURNEY</div><h2>Progress starts with one ingredient.</h2><p>Mark food as rescued when you use it instead of discarding it.</p>🌍</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Food items rescued</div><div class='metric-value'>{saved_count}</div><div class='metric-foot'>logged by you</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Estimated money saved</div><div class='metric-value'>{money(saved_value)}</div><div class='metric-foot'>based on your entries</div></div>", unsafe_allow_html=True)
    st.markdown("### How we measure impact")
    st.caption("Food rescued is self-reported. Savings are based on the values you enter. We do not claim precise carbon reduction without reliable ingredient-specific data.")
    if not st.session_state.saved_log: st.info("Your impact log is empty. In My Pantry, choose ‘I used it’ to record food you rescued.")
    else:
        for row in reversed(st.session_state.saved_log):
            st.markdown(f"**{row['name']}** · {row['date']}　—　{money(row['cost'])}")

st.markdown("<hr><div style='display:flex;justify-content:space-between;color:#8b9389;font-size:10px'><span>Made with care for people and the planet</span><b>✳ FOODWISE AI · HACKATHON PROTOTYPE</b></div>", unsafe_allow_html=True)
