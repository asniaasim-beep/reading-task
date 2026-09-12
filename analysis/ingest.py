#!/usr/bin/env python3
"""DataPipe CSVs -> one SQLite database, with the schema's guarantees enforced.

DataPipe drops one CSV per participant into the OSF component, each carrying
its own header. This walks that directory, checks every file against the exact
column list reading_study_engine.html emits, refuses anything that disagrees,
de-duplicates repeat submissions by pid, and builds the analysis views.

  python3 ingest.py --csv-dir ./datapipe_export --db study.db
  python3 ingest.py --demo 1000 --db demo.db     # synthetic data, for testing the pipeline
"""
import argparse, csv, hashlib, io, json, pathlib, sqlite3, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"

# Exactly the keys of the `wide` object in wideRow(), in order. If the engine
# ever changes, this check fails loudly instead of silently misaligning columns.
EXPECTED_COLS = ["trial_type", "pid", "rung", "frame",
                 "pos1_role", "pos2_role", "pos3_role", "pos4_role",
                 "cause_position", "selfblame_position", "picked_position",
                 "picked_role", "picked_is_cause", "why_text",
                 "attn_response", "attn_pass", "age", "gender",
                 "rt_pick_ms", "rt_why_ms", "total_ms", "completed",
                 "jspsych_version"]


def read_one(path: pathlib.Path):
    rows = list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"))))
    if not rows:
        return [], f"{path.name}: empty"
    got = list(rows[0].keys())
    if got != EXPECTED_COLS:
        missing, extra = set(EXPECTED_COLS) - set(got), set(got) - set(EXPECTED_COLS)
        return [], f"{path.name}: column mismatch (missing={sorted(missing)} extra={sorted(extra)})"
    return rows, None


def load_stimuli(con):
    stim = json.loads((ANALYSIS / "stimuli.json").read_text(encoding="utf-8"))
    codes = json.loads((ANALYSIS / "grammar_codes.json").read_text(encoding="utf-8"))
    dims = codes["dims"]
    out = []
    for rec in stim["long"]:
        # grammar codes describe the self-blame ladder; the three fixed
        # sentences get NULL, because they do not move with rung.
        vals = ([codes["codes"][str(rec["rung"])][d]["score"] for d in dims]
                if rec["role"] == "B" else [None] * len(dims))
        out.append((rec["frame"], rec["rung"], rec["role"], rec["role_name"], rec["text"],
                    len(rec["text"].split()), *vals))
    con.executemany(
        "INSERT INTO stimuli (frame,rung,role,role_name,text,n_words,"
        "sigma_predication,tau_temporal,epsilon_commitment,delta_domain,"
        "alpha_agency,kappa_free) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", out)
    return len(out)


def synth(n, seed=7):
    """Synthetic DataPipe rows under the hinge truth, for pipeline testing only."""
    rng = np.random.default_rng(seed)
    rolenames = ["C", "B", "S", "N"]
    pB = {"plain": {1: .20, 2: .22, 3: .38, 4: .42, 5: .45},
          "setaside": {1: .10, 2: .11, 3: .28, 4: .33, 5: .37}}
    rows = []
    for i in range(n):
        frame = "plain" if i % 2 == 0 else "setaside"
        rung = (i // 2) % 5 + 1
        rest = 1 + np.exp(-1.6) + np.exp(-1.8)
        aB = np.log(pB[frame][rung] * rest / (1 - pB[frame][rung]))
        util = np.array([0.0, aB, -1.6, -1.8])
        order = rng.permutation(4)
        v = util[order] + np.array([0, -.15, -.25, -.30])
        p = np.exp(v - v.max()); p /= p.sum()
        k = int(rng.choice(4, p=p))
        roles = [rolenames[j] for j in order]
        rows.append({
            "trial_type": "reading_task", "pid": f"P{i:05d}", "rung": str(rung), "frame": frame,
            "pos1_role": roles[0], "pos2_role": roles[1], "pos3_role": roles[2], "pos4_role": roles[3],
            "cause_position": str(roles.index("C") + 1), "selfblame_position": str(roles.index("B") + 1),
            "picked_position": str(k + 1), "picked_role": roles[k],
            "picked_is_cause": "true" if roles[k] == "C" else "false",
            "why_text": "it explains what happened" if roles[k] == "C" else "it felt like the heart of it",
            "attn_response": "rough" if rng.random() > .06 else "calm",
            "attn_pass": "true" if rng.random() > .06 else "false",
            "age": "25 to 34", "gender": "Woman",
            "rt_pick_ms": f"{rng.normal(14000, 5000):.0f}", "rt_why_ms": f"{rng.normal(22000, 8000):.0f}",
            "total_ms": f"{rng.normal(150000, 30000):.0f}", "completed": "true",
            "jspsych_version": "8.2.3"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-dir"); ap.add_argument("--demo", type=int)
    ap.add_argument("--db", default=str(ANALYSIS / "study.db"))
    a = ap.parse_args()
    if not a.csv_dir and not a.demo:
        sys.exit("need --csv-dir or --demo N")

    if a.demo:
        rows = [(f"synthetic_{i:05d}.csv", r) for i, r in enumerate(synth(a.demo))]
        problems = []
    else:
        rows, problems = [], []
        for p in sorted(pathlib.Path(a.csv_dir).glob("*.csv")):
            rs, err = read_one(p)
            if err:
                problems.append(err)
            rows.extend((p.name, r) for r in rs)

    # de-duplicate repeat submissions: keep the FIRST row seen per pid
    seen, deduped, dups = set(), [], 0
    for src, r in rows:
        if r["pid"] in seen:
            dups += 1
            continue
        seen.add(r["pid"]); deduped.append((src, r))

    db = pathlib.Path(a.db)
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.executescript((ANALYSIS / "schema.sql").read_text(encoding="utf-8"))
    con.executemany(
        f"INSERT INTO raw (source_file,{','.join(EXPECTED_COLS)}) "
        f"VALUES ({','.join('?' * (len(EXPECTED_COLS) + 1))})",
        [(src, *[r[c] for c in EXPECTED_COLS]) for src, r in deduped])
    n_stim = load_stimuli(con)
    # participant_map: the only place pid <-> participant_id is kept
    con.executemany("INSERT INTO participant_map (pid, participant_id) VALUES (?,?)",
                    [(pid, "sub-" + hashlib.sha256(("reading-task:" + pid).encode()).hexdigest()[:12])
                     for pid in sorted(seen)])
    con.commit()

    q = lambda s: con.execute(s).fetchall()
    print(f"loaded {len(deduped)} rows ({dups} duplicate pid dropped, {len(problems)} bad files)")
    for e in problems[:10]:
        print("  ! " + e)
    print(f"stimuli rows: {n_stim}")
    print(f"raw={q('SELECT COUNT(*) FROM raw')[0][0]}  "
          f"clean={q('SELECT COUNT(*) FROM v_clean')[0][0]}  "
          f"public={q('SELECT COUNT(*) FROM v_public')[0][0]}  "
          f"choice_set rows={q('SELECT COUNT(*) FROM v_choice_set')[0][0]}")
    # the guarantee the schema exists to make
    bad = q("SELECT COUNT(*) FROM v_choice_set WHERE text IS NULL")[0][0]
    assert bad == 0, f"{bad} option rows failed to join a stimulus sentence"
    per = q("SELECT COUNT(*) FROM (SELECT pid FROM v_choice_set GROUP BY pid HAVING COUNT(*)<>4)")[0][0]
    assert per == 0, "some choice sets do not have exactly 4 options"
    one = q("SELECT COUNT(*) FROM (SELECT pid FROM v_choice_set GROUP BY pid HAVING SUM(chosen)<>1)")[0][0]
    assert one == 0, "some choice sets do not have exactly 1 chosen option"
    print("integrity: every option row joins a sentence; 4 options and exactly 1 pick per participant  OK")
    con.close()
    print(f"wrote {db}")


if __name__ == "__main__":
    main()
