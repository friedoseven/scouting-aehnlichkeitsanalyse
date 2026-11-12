# Grafiken für ein Spielerpaar, z.B.:
# python 03_grafiken.py --ref "Antonio Nusa" --kand "Carlos Forbs" --x total_att_assist --y won_contest
import argparse
import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROT, BLAU, GRAU = "#DD0741", "#0C2043", "#C7CBD1"
KENNZAHLEN = ["goals", "expected_goals", "total_scoring_att", "goal_assist", "expected_assists",
              "big_chance_created", "total_att_assist", "accurate_pass", "pass_pct", "accurate_long_balls",
              "won_contest", "total_tackle", "interception", "ball_recovery", "poss_won_att_3rd",
              "effective_clearance", "defensive_contributions"]
NAMEN = ["Tore", "xG", "Schüsse", "Vorlagen", "xA", "Große Chancen kreiert", "Chancen kreiert", "Angek. Pässe",
         "Passquote", "Lange Bälle", "Dribblings", "Tacklings", "Interceptions", "Ballgewinne",
         "Ballgew. letztes Drittel", "Klärungen", "Defensivaktionen"]
NAME = dict(zip(KENNZAHLEN, NAMEN))

parser = argparse.ArgumentParser()
parser.add_argument("--ref", required=True)
parser.add_argument("--kand", required=True)
parser.add_argument("--x", default="total_att_assist")
parser.add_argument("--y", default="won_contest")
parser.add_argument("--datei", default="spielerdaten.csv")
args = parser.parse_args()

plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("grafiken", exist_ok=True)
prof = pd.read_csv("ergebnis/profile.csv")
res = pd.read_csv("ergebnis/aehnlichkeit_top5.csv")
daten = pd.read_csv(args.datei)

ref = prof[prof["player"] == args.ref].iloc[0]
kand = prof[prof["player"] == args.kand].iloc[0]
pos = ref["position_group"]
name = args.kand.split()[-1]

# z-Score-Profil
fig, ax = plt.subplots(figsize=(4.2, 4.6))
y = np.arange(len(KENNZAHLEN))[::-1]
ax.barh(y + 0.19, [ref[f"z_{k}"] for k in KENNZAHLEN], 0.38, color=ROT, label=args.ref)
ax.barh(y - 0.19, [kand[f"z_{k}"] for k in KENNZAHLEN], 0.38, color=BLAU, label=args.kand)
ax.axvline(0, color="#374151", lw=0.8)
ax.set_yticks(y)
ax.set_yticklabels(NAMEN, fontsize=7)
ax.set_xlabel("z-Score")
ax.legend(frameon=False, fontsize=7, loc="lower right")
ax.set_title("Profilvergleich (z-Scores)", loc="left", fontweight="bold", color=BLAU)
fig.tight_layout()
fig.savefig(f"grafiken/z_{name}.png", dpi=200)
plt.close(fig)

# Streudiagramm
pool = daten.merge(prof[["player", "team"]], on=["player", "team"])
pool = pool[pool["position_group"] == pos]
fig, ax = plt.subplots(figsize=(4, 3.4))
ax.scatter(pool[args.x], pool[args.y], s=14, color=GRAU, edgecolor="white", lw=0.4)
ax.axvline(pool[args.x].mean(), color="#9CA3AF", ls="--", lw=0.7)
ax.axhline(pool[args.y].mean(), color="#9CA3AF", ls="--", lw=0.7)
for spieler, farbe, dy in [(args.ref, ROT, -12), (args.kand, BLAU, 7)]:
    p = pool[pool["player"] == spieler].iloc[0]
    ax.scatter(p[args.x], p[args.y], s=55, color=farbe, zorder=3)
    ax.annotate(spieler, (p[args.x], p[args.y]), xytext=(6, dy), textcoords="offset points",
                color=farbe, fontweight="bold")
ax.set_xlabel(NAME.get(args.x, args.x) + " pro 90")
ax.set_ylabel(NAME.get(args.y, args.y) + " pro 90")
ax.set_title(f"{pos} (n={len(pool)})", loc="left", fontweight="bold", color=BLAU)
fig.tight_layout()
fig.savefig(f"grafiken/streu_{name}.png", dpi=200)
plt.close(fig)

# Top 5
t = res[res["referenzspieler"] == args.ref].sort_values("rang", ascending=False)
fig, ax = plt.subplots(figsize=(4, 2))
ax.barh(range(len(t)), t["aehnlichkeit_pct"], color=[BLAU if k == args.kand else GRAU for k in t["kandidat"]])
ax.set_yticks(range(len(t)))
ax.set_yticklabels([f"{k} ({a})" for k, a in zip(t["kandidat"], t["alter"])], fontsize=7)
for i, v in enumerate(t["aehnlichkeit_pct"]):
    ax.text(v + 1, i, f"{v:.0f} %", va="center", fontsize=7)
ax.set_xlim(0, 100)
ax.set_title(f"Top 5 zu {args.ref}", loc="left", fontweight="bold", color=BLAU)
fig.tight_layout()
fig.savefig(f"grafiken/top5_{name}.png", dpi=200)
plt.close(fig)

# bester Treffer je RB-Spieler
b = res[res["rang"] == 1].sort_values("aehnlichkeit_pct")
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.barh(range(len(b)), b["aehnlichkeit_pct"], color=GRAU)
ax.set_yticks(range(len(b)))
ax.set_yticklabels([f"{r} > {k}" for r, k in zip(b["referenzspieler"], b["kandidat"])], fontsize=7)
ax.axvline(60, color="#9CA3AF", ls="--", lw=0.8)
ax.set_xlim(0, 100)
ax.set_xlabel("Ähnlichkeit (%)")
fig.tight_layout()
fig.savefig("grafiken/bester_treffer.png", dpi=200)
plt.close(fig)
