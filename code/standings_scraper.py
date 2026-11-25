from bs4 import BeautifulSoup
import requests
import time
import os
import pandas as pd

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

all_rows = []

for year in range(1990, 2027):          # same seasons as the voting data
    if year == 2005:                    # lockout, no season
        continue

    # --- Layer 1: download the page once and save it ---
    path = f"data/raw/standings-{year}.html"
    if not os.path.exists(path):
        url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"
        response = requests.get(url)
        response.encoding = "utf-8"
        print(year, response.status_code)
        with open(path, "w", encoding="utf-8") as f:
            f.write(response.text)
        time.sleep(3)

    with open(path, encoding="utf-8") as f:
        html = f.read()

    # Hockey-Reference hides some tables inside HTML comments <!-- -->.
    # Removing the comment markers makes those tables visible to BeautifulSoup.
    html = html.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "html.parser")

    # --- Find the Team Statistics table (one row per team) ---
    table = soup.find("table", id="stats")
    if table is None:
        print(f"{year}: team stats table not found, skipping")
        continue

    # --- Turn each team row into a dictionary ---
    for tr in table.find("tbody").find_all("tr"):
        link = tr.find("a")
        if link is None:                # skips "League Average" and header rows
            continue

        name = tr.find("td", {"data-stat": "team_name"}).get_text(strip=True)

        row = {}
        row["season"] = year
        row["team_id"] = link["href"].split("/")[2]     # "/teams/DAL/2026.html" -> "DAL"
        row["team_name"] = name.replace("*", "")
        row["made_playoffs"] = 1 if "*" in name else 0  # * means made the playoffs
        row["games"] = tr.find("td", {"data-stat": "games"}).get_text(strip=True)
        row["points"] = tr.find("td", {"data-stat": "points"}).get_text(strip=True)
        row["points_pct"] = tr.find("td", {"data-stat": "points_pct"}).get_text(strip=True)
        all_rows.append(row)

# --- Layer 2: one combined CSV ---
df = pd.DataFrame(all_rows)
df["points_pct"] = df["points_pct"].astype(float)

# League rank by points % within each season (1 = best team that year)
df["team_rank"] = df.groupby("season")["points_pct"].rank(ascending=False, method="min").astype(int)

df.to_csv("data/processed/team_standings.csv", index=False)
print(df.shape)
print(df.head())