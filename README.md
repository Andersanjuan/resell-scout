# resell-scout
# AI Resell Scout (Learning Project)

Resell Scout is a learning project written in Python.  
Its goal is to explore how AI and programmatic tools could help identify potentially profitable resale items by:

- Representing online listings as structured data (`Listing` dataclass).
- Simulating listing sources with mock data.
- Analyzing basic metrics (total cost, naive profit).
- Ranking listings by estimated profit.

At this stage, the project uses **mock data only**.  
It does **not** scrape real websites or call marketplace APIs yet.

---

## Features (Current)

- `Listing` dataclass to model item data.
- Mock fetcher that returns example listings.
- Analyzer that:
  - Computes total cost (bid + shipping).
  - Computes a naive profit estimate.
  - Sorts listings by profit.

---

## Requirements

- Python 3.10+ (or your version)
- Packages listed in `requirements.txt`

---

## Installation

```bash
git clone https://github.com/<your-username>/ai-resell-scout.git
cd ai-resell-scout
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
