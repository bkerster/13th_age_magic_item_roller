# 13th Age Magic Item Roller

A Streamlit web app for randomly selecting magic items from the 13th Age RPG (1st edition). Filter by tier, item category, and character class, then roll to get a random item from the matching pool.

## Features

- **Tier filter** — narrow results to Adventurer, Champion, and/or Epic tier items
- **Category filter** — toggle individual item slots (Armor, Boots, Weapons, Wands, etc.)
- **Class filter** — selecting a class automatically checks the categories relevant to that class based on the official *Useful Magic Items by Class* table
- **189 items** parsed from the official 13th Age Archmage Engine SRD, including standard items, Chuul Symbiotes, and Cursed Items

## Setup

**Requirements:** Python (via Anaconda or standard install), with `streamlit` and `python-docx`.

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## Regenerating Item Data

`items.json` is pre-generated and included in the repo. If you update the source `.docx` file, regenerate it with:

```bash
python parse_items.py
```

## File Overview

| File | Description |
|------|-------------|
| `app.py` | Streamlit app — UI, filters, and random roll logic |
| `parse_items.py` | One-time parser: reads the `.docx` and writes `items.json` |
| `items.json` | 189 magic items extracted from the SRD |
| `13th-Age-Archmage-Engine-v4.0_MagicItems.docx` | Source data |
| `requirements.txt` | Python dependencies |

## Legal

This tool uses trademarks and/or copyrights owned by Fire Opal Media Inc., which are used under the Fire Opal Media Inc., 13th Age Community Use Policy. We are expressly prohibited from charging you to use or access this content. This tool is not published, endorsed, or specifically approved by Fire Opal Media.
