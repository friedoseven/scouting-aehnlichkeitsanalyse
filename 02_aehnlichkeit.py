# Ähnlichkeit RB-Spieler vs. U23-Kandidaten (z-Scores je Position, Kosinus)
import argparse
import os

import numpy as np
import pandas as pd

KENNZAHLEN = [
    "goals", "expected_goals", "total_scoring_att", "goal_assist", "expected_assists",
    "big_chance_created", "total_att_assist", "accurate_pass", "pass_pct", "accurate_long_balls",
    "won_contest", "total_tackle", "interception", "ball_recovery", "poss_won_att_3rd",
    "effective_clearance", "defensive_contributions",
]

parser = argparse.ArgumentParser()
parser.add_argument("--datei", default="spielerdaten.csv")
parser.add_argument("--team", default="RB Leipzig")
parser.add_argument("--max-alter", type=int, default=23)
parser.add_argument("--min-minuten", type=int, default=450)
parser.add_argument("--min-minuten-ref", type=int, default=290)
parser.add_argument("--top", type=int, default=5)
args = parser.parse_args()

df = pd.read_csv(args.datei)
df["ref"] = df["team"] == args.team
df = df[(df["ref"] & (df["minutes"] >= args.min_minuten_ref)) |
        (~df["ref"] & (df["minutes"] >= args.min_minuten) & (df["age"] <= args.max_alter))].copy()
print(df["ref"].sum(), "RB-Spieler,", (~df["ref"]).sum(), "Kandidaten")

# nicht in der FotMob-Liste = 0, fehlende Passquote = Median der Position
for k in KENNZAHLEN:
    if k == "pass_pct":
        df[k] = df[k].fillna(df.groupby("position_group")[k].transform("median"))
    else:
        df[k] = df[k].fillna(0)


def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


ergebnis, profile = [], []
for pos, g in df.groupby("position_group"):
    z = (g[KENNZAHLEN] - g[KENNZAHLEN].mean()) / g[KENNZAHLEN].std(ddof=0).replace(0, 1)
    pct = g[KENNZAHLEN].apply(lambda s: s.apply(lambda v: (s < v).sum() / (len(s) - 1) * 100))

    for i in g.index:
        profile.append({"player": g.at[i, "player"], "team": g.at[i, "team"], "position_group": pos,
                        **{f"z_{k}": round(z.at[i, k], 3) for k in KENNZAHLEN},
                        **{f"pct_{k}": round(pct.at[i, k]) for k in KENNZAHLEN}})

    kand = g[~g["ref"]]
    for r in g[g["ref"]].index:
        sims = sorted(((c, cosine(z.loc[r].values, z.loc[c].values)) for c in kand.index),
                      key=lambda t: t[1], reverse=True)
        for rang, (c, s) in enumerate(sims[:args.top], 1):
            ergebnis.append({
                "referenzspieler": g.at[r, "player"], "position": pos, "minuten_ref": g.at[r, "minutes"],
                "rang": rang, "kandidat": g.at[c, "player"], "verein": g.at[c, "team"],
                "liga": g.at[c, "league"], "alter": g.at[c, "age"], "minuten": g.at[c, "minutes"],
                "aehnlichkeit_pct": round(s * 100, 1), "von_kandidaten": len(kand),
            })

os.makedirs("ergebnis", exist_ok=True)
res = pd.DataFrame(ergebnis)
res.to_csv("ergebnis/aehnlichkeit_top5.csv", index=False)
pd.DataFrame(profile).to_csv("ergebnis/profile.csv", index=False)

for r in res[res["rang"] == 1].sort_values("aehnlichkeit_pct", ascending=False).itertuples():
    print(f"{r.referenzspieler:<24} -> {r.kandidat:<26} {r.verein:<24} {r.aehnlichkeit_pct:5.1f} %")
