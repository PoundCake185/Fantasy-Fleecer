import requests
import json
import csv
import inflect
from rapidfuzz import process

# 🎯 Your Sleeper League ID
LEAGUE_ID = "1182134435053940736"

# 📆 Draft settings
CURRENT_SEASON = 2025
FUTURE_SEASONS = [2026, 2027, 2028]
ROUNDS = 4

# 🧠 KTC + ordinal setup
p = inflect.engine()

def ordinal(n):
    return p.ordinal(n)

def get_rosters(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters").json()

def get_users(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users").json()

def get_traded_picks(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}/traded_picks").json()

def get_player_mapping():
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

def format_pick(pick, roster_id_to_teamname):
    season = pick["season"]
    rnd = pick["round"]
    orig_owner = pick["original_owner"]
    orig_team = roster_id_to_teamname.get(orig_owner, f"Unknown_{orig_owner}")
    rnd_str = ordinal(rnd)
    return f"{season} {rnd_str} Round (via {orig_team})"

def build_full_draft_picks(rosters, traded_picks):
    full_picks = {roster["roster_id"]: [] for roster in rosters}

    for roster in rosters:
        roster_id = roster["roster_id"]
        for season in FUTURE_SEASONS:
            for round_num in range(1, ROUNDS + 1):
                full_picks[roster_id].append({
                    "season": str(season),
                    "round": round_num,
                    "original_owner": roster_id
                })

    allowed_seasons = [str(y) for y in FUTURE_SEASONS]

    for pick in traded_picks:
        season = pick["season"]
        if season not in allowed_seasons:
            continue

        round_num = pick["round"]
        orig = pick["roster_id"]
        new_owner = pick["owner_id"]

        # Remove from original owner
        full_picks[orig] = [
            p for p in full_picks[orig]
            if not (p["season"] == season and p["round"] == round_num and p["original_owner"] == orig)
        ]

        # Add to new owner
        full_picks[new_owner].append({
            "season": season,
            "round": round_num,
            "original_owner": orig
        })

    return full_picks

def load_ktc_values(csv_path="ktc_latest.csv"):
    ktc = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row_num, row in enumerate(reader, start=2):
            if len(row) < 6:
                print(f"⚠️ Skipping malformed row {row_num}: {row}")
                continue
            name = row[0].strip().lower()
            try:
                value = float(row[4])
                age = float(row[5])
            except ValueError as e:
                print(f"⚠️ Error parsing row {row_num} ({name}): {e}")
                value = 0.0
                age = None
            ktc[name] = {
                "ktc_value": value,
                "age": age
            }
    return ktc

def fuzzy_match_player(name, ktc_values, threshold=90):
    matches = process.extractOne(name, ktc_values.keys(), score_cutoff=threshold)
    if matches:
        matched_name, score = matches[0], matches[1]
        print(f"🔍 Fuzzy matched '{name}' → '{matched_name}' (score: {score})")
        return ktc_values[matched_name]
    return {}

def build_team_data(league_id):
    rosters = get_rosters(league_id)
    users = get_users(league_id)
    traded_picks = get_traded_picks(league_id)
    player_map = get_player_mapping()
    ktc_values = load_ktc_values()

    roster_id_to_teamname = {}
    for roster in rosters:
        owner_id = roster.get("owner_id")
        user = next((u for u in users if u["user_id"] == owner_id), None)
        team_name = (
            user.get("metadata", {}).get("team_name") or
            user.get("display_name") if user else
            f"Unknown_{roster['roster_id']}"
        )
        roster_id_to_teamname[roster["roster_id"]] = team_name

    full_draft_picks = build_full_draft_picks(rosters, traded_picks)

    league_data = {}

    for roster in rosters:
        owner_id = roster.get("owner_id")

        user = next((u for u in users if u["user_id"] == owner_id), None)
        team_name = (
            user.get("metadata", {}).get("team_name") or
            user.get("display_name") if user else
            f"Unknown_{roster['roster_id']}"
        )

        player_ids = roster.get("players", [])
        players = []

        for pid in player_ids:
            player = player_map.get(pid, {})
            name = player.get("full_name") or f"{player.get('first_name', '')} {player.get('last_name', '')}"
            pos = player.get("position", "")
            team = player.get("team", "")

            key = name.strip().lower()
            ktc = ktc_values.get(key)

            if not ktc:
                ktc = fuzzy_match_player(key, ktc_values)

            players.append({
                "id": pid,
                "name": name.strip(),
                "position": pos,
                "team": team,
                "ktc_value": ktc.get("ktc_value", 0.0),
                "age": ktc.get("age", None)
            })

        picks_raw = full_draft_picks[roster["roster_id"]]
        picks_formatted = [format_pick(p, roster_id_to_teamname) for p in picks_raw]

        league_data[team_name] = {
            "roster_id": roster["roster_id"],
            "players": players,
            "draft_picks": picks_formatted
        }

    return league_data

if __name__ == "__main__":
    data = build_team_data(LEAGUE_ID)

    output_file = "sleeper_league_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Data saved to {output_file}")
