"""
Parse 13th Age magic items from the docx file into items.json.
Run once: python parse_items.py
"""
import json
import re
from pathlib import Path
from docx import Document

DOCX_PATH = Path(__file__).parent / "13th-Age-Archmage-Engine-v4.0_MagicItems.docx"
OUTPUT_PATH = Path(__file__).parent / "items.json"

CATEGORY_MAP = {
    "Arrow, Crossbow Bolt, Slingstone": "ammunition",
    "Armor, Robe, Shirt, Tunic": "armor",
    "Belt, Swordbelt, Kilt, Skirt, Girdle, Sash": "belts",
    "Book, Scroll, Tome, Grimoire": "books",
    "Boots, Shoes, Sandals, Slippers": "boots",
    "Bracers": None,
    "Cloak, Mantle, Cape": "cloaks",
    "Gloves, Gauntlets": "gloves",
    "Helmet, Crown, Diadem, Circlet": "helmets",
    "Necklace, Pendant": "necklaces",
    "Rings": "rings",
    "Shield": "shields",
    "Staff": "staffs",
    "Symbol, Holy Symbol, Relic, Sacred Branch": "symbols",
    "Wand": "wands",
    "Weapons": "weapons",
    "Wondrous Items": "wondrous",
    "Chuul Symbiote Magic Items": "chuul",
    "Cursed Magic Items": "cursed",
}

TIER_HEADINGS = {"Adventurer", "Champion", "Epic"}
SKIP_H4 = {"Default Bonus", "Optional Default Bonus", "General"}
# Categories where items appear at Heading 4 (not Heading 5)
H4_ITEM_CATEGORIES = {"wondrous", "chuul"}


def normalize_text(text: str) -> str:
    # Fix smart quotes and dashes that come out garbled from docx
    replacements = {
        "’": "'", "‘": "'",
        "“": '"', "”": '"',
        "–": "-", "—": "-",
        "…": "...",
        "�": "'",  # replacement character often stands in for apostrophe
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.strip()


def finalize_item(item: dict | None, items: list) -> None:
    if item is None:
        return
    item["description"] = normalize_text(item["description"])
    item["quirk"] = normalize_text(item["quirk"])
    item["name"] = normalize_text(item["name"])
    if item["name"] and item["category"]:
        items.append(item)


def new_item(name: str, category: str | None, tier: str | None) -> dict | None:
    if category is None:
        return None
    return {
        "name": normalize_text(name),
        "category": category,
        "tier": tier or "adventurer",
        "description": "",
        "quirk": "",
    }


def append_text(item: dict, text: str) -> None:
    """Append text to description, handling the Quirk: split."""
    if "Quirk:" in text:
        parts = text.split("Quirk:", 1)
        pre = parts[0].strip()
        quirk = parts[1].strip()
        if pre:
            item["description"] = (item["description"] + " " + pre).strip()
        if not item["quirk"]:
            item["quirk"] = quirk
    else:
        item["description"] = (item["description"] + " " + text).strip()


def parse(docx_path: Path) -> list[dict]:
    doc = Document(str(docx_path))
    items: list[dict] = []

    in_descriptions = False
    current_category: str | None = None
    current_tier: str | None = None
    current_item: dict | None = None

    for para in doc.paragraphs:
        style = para.style.name
        text = para.text.strip()

        if not text:
            continue

        # Enter item descriptions section
        if style == "Heading 2" and text == "Magic Item Descriptions":
            in_descriptions = True
            continue

        if not in_descriptions:
            continue

        if style == "Heading 3":
            finalize_item(current_item, items)
            current_item = None
            current_tier = None
            current_category = CATEGORY_MAP.get(text)  # None = skip (Bracers)
            continue

        if current_category is None:
            continue

        if style == "Heading 4":
            if text in TIER_HEADINGS:
                finalize_item(current_item, items)
                current_item = None
                current_tier = text.lower()
            elif text in SKIP_H4:
                finalize_item(current_item, items)
                current_item = None
            elif current_category in H4_ITEM_CATEGORIES:
                # Wondrous / Chuul: item name is at Heading 4
                finalize_item(current_item, items)
                current_item = new_item(text, current_category, current_tier)
            continue

        if style == "Heading 5":
            finalize_item(current_item, items)
            current_item = new_item(text, current_category, current_tier)
            continue

        if style in ("Normal", "List Paragraph") and current_item is not None:
            append_text(current_item, text)

    finalize_item(current_item, items)
    return items


def main():
    print(f"Parsing {DOCX_PATH} ...")
    items = parse(DOCX_PATH)
    print(f"Extracted {len(items)} items")

    # Summary by category and tier
    from collections import Counter
    by_cat = Counter(i["category"] for i in items)
    by_tier = Counter(i["tier"] for i in items)
    print("\nBy category:")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat:12s}  {n}")
    print("\nBy tier:")
    for tier, n in sorted(by_tier.items()):
        print(f"  {tier:12s}  {n}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
