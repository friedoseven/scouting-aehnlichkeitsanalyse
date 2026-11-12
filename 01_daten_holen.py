# Holt Saisonstatistiken von FotMob -> spielerdaten.csv
import csv
import time

import requests

LIGEN = {
    54: "Bundesliga (GER)",
    38: "Bundesliga (AUT)",
    57: "Eredivisie (NED)",
    40: "Pro League (BEL)",
    46: "Superliga (DEN)",
    146: "2. Bundesliga (GER)",
}
RB_ID = 178475
RB_LIGA = 54

# "sum" = Saisonwert, wird auf 90 min umgerechnet / "p90" = schon pro 90
STATS = {
    "goals": "sum", "expected_goals": "sum", "total_scoring_att": "p90",
    "goal_assist": "sum", "expected_assists": "sum", "big_chance_created": "sum",
    "total_att_assist": "sum", "accurate_pass": "p90", "accurate_long_balls": "p90",
    "won_contest": "p90", "total_tackle": "p90", "interception": "p90",
    "ball_recovery": "p90", "poss_won_att_3rd": "p90", "effective_clearance": "p90",
    "defensive_contributions": "p90",
}

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"


def get(url):
    r = session.get(url, timeout=20)
    r.raise_for_status()
    time.sleep(0.4)
    return r.json()


def pos_gruppe(pos):
    p = (pos or "").split(",")[0].strip()
    if p == "CB":
        return "Innenverteidiger"
    if p in ("LB", "RB", "LWB", "RWB"):
        return "Außenverteidiger"
    if p in ("DM", "CDM", "CM"):
        return "Zentrales Mittelfeld"
    if p in ("AM", "CAM", "LM", "RM", "LW", "RW"):
        return "Flügel/Offensiv"
    if p in ("ST", "CF"):
        return "Stürmer"
    return None  # GK


def hole_liga(liga_id, liga_name):
    liga = get(f"https://www.fotmob.com/api/data/leagues?id={liga_id}")
    url = next(x["fetchAllUrl"] for x in liga["stats"]["players"] if x.get("fetchAllUrl"))
    base = url.rsplit("/", 1)[0] + "/"

    spieler = {}
    for x in get(base + "mins_played.json")["TopLists"][0]["StatList"]:
        spieler[x["ParticiantId"]] = {
            "id": x["ParticiantId"], "player": x["ParticipantName"], "team": x["TeamName"],
            "teamId": x["TeamId"], "minutes": x["MinutesPlayed"], "matches": x["MatchesPlayed"],
        }

    for stat, art in STATS.items():
        try:
            liste = get(base + stat + ".json")["TopLists"][0]["StatList"]
        except Exception as e:
            print(stat, "fehlt:", e)
            continue
        for x in liste:
            p = spieler.get(x["ParticiantId"])
            if p is None:
                continue
            if art == "sum":
                p[stat] = x["StatValue"] / x["MinutesPlayed"] * 90 if x["MinutesPlayed"] else 0
            else:
                p[stat] = x["StatValue"]
            if stat == "accurate_pass":
                p["pass_pct"] = x["SubStatValue"]

    # Alter + Position aus den Kadern
    info = {}
    for team_id in {p["teamId"] for p in spieler.values()}:
        if liga_id == RB_LIGA and team_id != RB_ID:
            continue
        team = get(f"https://www.fotmob.com/api/data/teams?id={team_id}")
        for gruppe in team["squad"]["squad"]:
            for m in gruppe["members"]:
                info[m["id"]] = (m.get("age"), m.get("positionIdsDesc"))

    rows = []
    for p in spieler.values():
        if p["id"] not in info:
            continue
        if liga_id == RB_LIGA and p["teamId"] != RB_ID:
            continue
        alter, pos = info[p["id"]]
        gruppe = pos_gruppe(pos)
        if gruppe:
            rows.append({**p, "league": liga_name, "age": alter, "position_group": gruppe, "pos_detail": pos})
    print(liga_name, len(rows))
    return rows


if __name__ == "__main__":
    daten = []
    for lid, name in LIGEN.items():
        daten += hole_liga(lid, name)

    spalten = ["player", "team", "teamId", "league", "age", "position_group", "pos_detail",
               "minutes", "matches"] + list(STATS) + ["pass_pct"]
    with open("spielerdaten.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=spalten, extrasaction="ignore")
        w.writeheader()
        for row in daten:
            w.writerow({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()})
    print("gespeichert:", len(daten), "Spieler")
