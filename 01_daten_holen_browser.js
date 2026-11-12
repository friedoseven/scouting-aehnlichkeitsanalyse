// Alternative zu 01_daten_holen.py: auf fotmob.com in der Konsole (F12) ausführen
(async () => {
  const LIGEN = {54: "Bundesliga (GER)", 38: "Bundesliga (AUT)", 57: "Eredivisie (NED)",
                 40: "Pro League (BEL)", 46: "Superliga (DEN)", 146: "2. Bundesliga (GER)"};
  const RB_ID = 178475, RB_LIGA = 54;
  const STATS = {goals: "sum", expected_goals: "sum", total_scoring_att: "p90", goal_assist: "sum",
    expected_assists: "sum", big_chance_created: "sum", total_att_assist: "sum", accurate_pass: "p90",
    accurate_long_balls: "p90", won_contest: "p90", total_tackle: "p90", interception: "p90", ball_recovery: "p90",
    poss_won_att_3rd: "p90", effective_clearance: "p90", defensive_contributions: "p90"};

  const posGruppe = d => {
    const p = (d || "").split(",")[0].trim();
    if (p === "CB") return "Innenverteidiger";
    if (["LB", "RB", "LWB", "RWB"].includes(p)) return "Außenverteidiger";
    if (["DM", "CDM", "CM"].includes(p)) return "Zentrales Mittelfeld";
    if (["AM", "CAM", "LM", "RM", "LW", "RW"].includes(p)) return "Flügel/Offensiv";
    if (["ST", "CF"].includes(p)) return "Stürmer";
    return null;
  };
  const get = u => fetch(u).then(r => r.json());

  const rows = [];
  for (const [id, name] of Object.entries(LIGEN)) {
    const lid = Number(id);
    const L = await get("/api/data/leagues?id=" + lid);
    const base = L.stats.players.find(x => x.fetchAllUrl).fetchAllUrl.replace(/[^/]+\.json$/, "");
    const P = {};
    for (const x of (await get(base + "mins_played.json")).TopLists[0].StatList)
      P[x.ParticiantId] = {id: x.ParticiantId, player: x.ParticipantName, team: x.TeamName, teamId: x.TeamId,
                           minutes: x.MinutesPlayed, matches: x.MatchesPlayed};
    for (const [stat, art] of Object.entries(STATS)) {
      let liste;
      try { liste = (await get(base + stat + ".json")).TopLists[0].StatList; } catch (e) { continue; }
      for (const x of liste) {
        const p = P[x.ParticiantId];
        if (!p) continue;
        p[stat] = art === "sum" ? (x.MinutesPlayed ? x.StatValue / x.MinutesPlayed * 90 : 0) : x.StatValue;
        if (stat === "accurate_pass") p.pass_pct = x.SubStatValue;
      }
    }
    const teams = [...new Set(Object.values(P).filter(p => lid !== RB_LIGA || p.teamId === RB_ID).map(p => p.teamId))];
    const info = {};
    for (const t of teams) {
      const T = await get("/api/data/teams?id=" + t);
      for (const g of T.squad.squad) for (const m of g.members) info[m.id] = {age: m.age, pos: m.positionIdsDesc};
    }
    for (const p of Object.values(P)) {
      const i = info[p.id];
      if (!i || (lid === RB_LIGA && p.teamId !== RB_ID)) continue;
      const g = posGruppe(i.pos);
      if (g) rows.push({...p, league: name, age: i.age, position_group: g, pos_detail: i.pos});
    }
    console.log(name, rows.length);
  }

  const cols = ["player", "team", "teamId", "league", "age", "position_group", "pos_detail", "minutes", "matches",
                ...Object.keys(STATS), "pass_pct"];
  const fmt = v => {
    if (v == null) return "";
    if (typeof v === "number") return String(Math.round(v * 1000) / 1000);
    return /[",]/.test(v) ? '"' + String(v).replace(/"/g, '""') + '"' : v;
  };
  const csv = [cols.join(","), ...rows.map(r => cols.map(c => fmt(r[c])).join(","))].join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], {type: "text/csv"}));
  a.download = "spielerdaten.csv";
  a.click();
})();
