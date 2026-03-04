import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import html
import json
import time
from difflib import SequenceMatcher

def fetch_understat_data():
    """Fetch xG and xA for Premier League players from Understat."""
    url = "https://understat.com/league/EPL"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            match = re.search(
                r"playersData\s*=\s*JSON\.parse\('(.+?)'\)",
                response.text,
                re.DOTALL
            )
            if not match:
                match = re.search(
                    r"var\s+playersData\s*=\s*(\[.+?\]);",
                    response.text,
                    re.DOTALL
                )
                if not match:
                    raise ValueError("playersData not found in page HTML")
                raw = match.group(1)
                data = json.loads(raw)
            else:
                raw = match.group(1)
                decoded = html.unescape(
                    bytes(raw, "utf-8").decode("unicode_escape")
                )
                data = json.loads(decoded)

            df = pd.DataFrame(data)
            if df.empty:
                raise ValueError("Parsed DataFrame is empty")

            df = df[["player_name", "xG", "xA", "games"]]
            df["xG"] = pd.to_numeric(df["xG"], errors="coerce")
            df["xA"] = pd.to_numeric(df["xA"], errors="coerce")
            df["games"] = pd.to_numeric(df["games"], errors="coerce")
            return df
            
        except Exception as e:
            print(f"[understat] Attempt {attempt}/3 failed: {e}")
            if attempt < 3:
                time.sleep(5)

    print("[understat] WARNING: Returning empty DataFrame. XG data skipped.")
    return pd.DataFrame()

def match_understat_to_fpl(understat_df, fpl_players_df):
    matches = []
    for _, under_row in understat_df.iterrows():
        under_name = under_row["player_name"]
        best_match = None
        best_score = 0.6
        for _, fpl_row in fpl_players_df.iterrows():
            fpl_name = fpl_row["name"]
            score = SequenceMatcher(None, under_name.lower(), fpl_name.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = fpl_row["id"]
        if best_match:
            matches.append({
                "player_id": best_match,
                "xG": under_row["xG"],
                "xA": under_row["xA"],
                "games_understat": under_row["games"]
            })
    return pd.DataFrame(matches)