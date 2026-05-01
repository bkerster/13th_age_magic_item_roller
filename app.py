import json
import random
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

ITEMS_PATH = Path(__file__).parent / "items.json"

CATEGORY_LABELS = {
    "ammunition": "Ammunition",
    "armor": "Armor",
    "belts": "Belts",
    "books": "Books",
    "boots": "Boots",
    "chuul": "Chuul Symbiotes",
    "cloaks": "Cloaks",
    "cursed": "Cursed Items",
    "gloves": "Gloves",
    "helmets": "Helmets",
    "necklaces": "Necklaces",
    "rings": "Rings",
    "shields": "Shields",
    "staffs": "Staffs",
    "symbols": "Symbols",
    "wands": "Wands",
    "weapons-any": "Weapons (Any)",
    "weapons-melee": "Weapons (Melee)",
    "weapons-1h": "Weapons (One-Handed)",
    "weapons-2h": "Weapons (Two-Handed)",
    "weapons-ranged": "Weapons (Ranged)",
    "wondrous": "Wondrous Items",
}

UNIVERSAL = [
    "boots", "cloaks", "rings", "necklaces", "helmets",
    "gloves", "belts", "books", "wondrous",
]

WEAPON_ANY  = ["weapons-any", "weapons-melee"]
WEAPON_1H   = WEAPON_ANY + ["weapons-1h"]
WEAPON_2H   = WEAPON_ANY + ["weapons-2h"]
WEAPON_ALL  = WEAPON_ANY + ["weapons-1h", "weapons-2h", "weapons-ranged"]

CLASS_CATEGORIES = {
    "Barbarian": WEAPON_2H + ["armor"] + UNIVERSAL,
    "Bard":      WEAPON_1H + ["weapons-ranged", "armor", "wands", "staffs"] + UNIVERSAL,
    "Cleric":    WEAPON_1H + ["symbols", "staffs", "armor", "shields"] + UNIVERSAL,
    "Fighter":   WEAPON_1H + ["armor", "shields"] + UNIVERSAL,
    "Paladin":   WEAPON_1H + ["armor", "shields"] + UNIVERSAL,
    "Ranger":    WEAPON_ALL + ["ammunition", "armor"] + UNIVERSAL,
    "Rogue":     WEAPON_1H + ["weapons-ranged", "armor"] + UNIVERSAL,
    "Sorcerer":  ["wands", "staffs", "armor"] + UNIVERSAL,
    "Wizard":    ["wands", "staffs", "armor", "books"] + UNIVERSAL,
}

TIER_ORDER = ["adventurer", "champion", "epic"]
TIER_COLORS = {
    "adventurer": "#4a9e6b",
    "champion":   "#b87333",
    "epic":       "#7b4fa6",
}


@st.cache_data
def load_items() -> list[dict]:
    with open(ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f)["items"]


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="13th Age Magic Item Roller",
    page_icon="🎲",
    layout="wide",
)

st.title("🎲 13th Age Magic Item Roller")

items = load_items()
all_categories = sorted(CATEGORY_LABELS.keys())

# Initialize category checkbox state once (session state is the single source of truth)
for _cat in all_categories:
    if f"cat_{_cat}" not in st.session_state:
        st.session_state[f"cat_{_cat}"] = _cat not in ("ammunition", "chuul", "cursed")

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

def apply_class_to_categories():
    selected = st.session_state.class_selector
    for cat in all_categories:
        if selected == "All Classes":
            st.session_state[f"cat_{cat}"] = cat not in ("ammunition", "chuul", "cursed")
        else:
            st.session_state[f"cat_{cat}"] = cat in CLASS_CATEGORIES[selected]

def select_all_categories():
    for cat in all_categories:
        st.session_state[f"cat_{cat}"] = True

def select_no_categories():
    for cat in all_categories:
        st.session_state[f"cat_{cat}"] = False

with st.sidebar:
    st.header("Filters")

    st.subheader("Tier")
    selected_tiers = []
    for tier in TIER_ORDER:
        if st.checkbox(tier.capitalize(), value=True, key=f"tier_{tier}"):
            selected_tiers.append(tier)

    st.subheader("Class")
    st.selectbox(
        "Class",
        options=["All Classes"] + sorted(CLASS_CATEGORIES.keys()),
        key="class_selector",
        on_change=apply_class_to_categories,
        label_visibility="collapsed",
    )

    st.subheader("Category")
    btn_col1, btn_col2 = st.columns(2)
    btn_col1.button("Select All", on_click=select_all_categories, use_container_width=True)
    btn_col2.button("Select None", on_click=select_no_categories, use_container_width=True)
    selected_categories = []
    for cat in all_categories:
        if st.checkbox(CATEGORY_LABELS[cat], key=f"cat_{cat}"):
            selected_categories.append(cat)

    st.divider()
    roll_button = st.button("🎲 Roll!", use_container_width=True, type="primary")

# ---------------------------------------------------------------------------
# Filter logic
# ---------------------------------------------------------------------------

filtered = items

if selected_tiers:
    filtered = [i for i in filtered if i["tier"] in selected_tiers]

if selected_categories:
    filtered = [i for i in filtered if i["category"] in selected_categories]

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

col_main, col_info = st.columns([3, 1])

with col_info:
    st.metric("Matching items", len(filtered))

with col_main:
    if not filtered:
        st.warning("No items match your current filters.")
    elif roll_button or "current_item" not in st.session_state:
        if filtered:
            st.session_state.current_item = random.choice(filtered)

    if "current_item" in st.session_state and filtered:
        item = st.session_state.current_item
        # Re-check item is still in filtered pool (filters may have changed)
        if item not in filtered:
            st.session_state.current_item = random.choice(filtered)
            item = st.session_state.current_item

        tier = item["tier"]
        color = TIER_COLORS.get(tier, "#888")
        cat_label = CATEGORY_LABELS.get(item["category"], item["category"].title())

        st.markdown(f"## {item['name']}")
        st.markdown(
            f'<span style="background:{color};color:white;padding:3px 10px;'
            f'border-radius:4px;font-size:0.85em;margin-right:8px">'
            f'{tier.capitalize()}</span>'
            f'<span style="background:#555;color:white;padding:3px 10px;'
            f'border-radius:4px;font-size:0.85em">'
            f'{cat_label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        if item["description"]:
            st.markdown(item["description"])

        if item["quirk"]:
            st.markdown(f"*Quirk: {item['quirk']}*")

st.divider()
st.caption(
    "This tool uses trademarks and/or copyrights owned by Fire Opal Media Inc., which are used "
    "under the Fire Opal Media Inc., 13th Age Community Use Policy. We are expressly prohibited "
    "from charging you to use or access this content. This tool is not published, endorsed, or "
    "specifically approved by Fire Opal Media."
)
