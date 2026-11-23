from bs4 import BeautifulSoup
import requests
import time
import os
import pandas as pd

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

all_rows = []

for year in range(1990, 2027):          # 2027 so that 2026 is included
    if year == 2005:                    # lockout, no season
        continue

    # --- Layer 1: download the page once and save it ---
    path = f"data/raw/voting-{year}.html"
    if not os.path.exists(path):
        url = f"https://www.hockey-reference.com/awards/voting-{year}.html"
        response = requests.get(url)
        print(year, response.status_code)
        with open(path, "w", encoding="utf-8") as f:
            f.write(response.text)
        time.sleep(3)

    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # --- Find the Hart table ---
    table = soup.find("table", id="hart_stats")
    if table is None:
        print(f"{year}: Hart table not found, skipping")
        continue

    # --- Turn each row into a dictionary ---
    for tr in table.find("tbody").find_all("tr"):
        row = {}
        for cell in tr.find_all(["th", "td"]):
            row[cell["data-stat"]] = cell.get_text(strip=True)

        row["player_id"] = tr.find("td", {"data-stat": "player"})["data-append-csv"]
        row["season"] = year
        all_rows.append(row)

# --- Layer 2: one combined CSV ---
df = pd.DataFrame(all_rows)
df.to_csv("data/raw/hart_voting.csv", index=False)
print(df.shape)
print(df.head())

