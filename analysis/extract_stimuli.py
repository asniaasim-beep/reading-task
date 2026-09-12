#!/usr/bin/env python3
"""Pull the sealed STIMULI/COPY objects out of the live engine HTML into JSON.

The stimuli currently live only inside reading_study_engine.html. Every
downstream analysis must read them from there so that what we analyse is
byte-identical to what participants saw.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENGINE = ROOT / "reading_study_engine.html"


def grab(html: str, name: str) -> dict:
    m = re.search(rf"^const {name}\s*=\s*", html, re.M)
    if not m:
        sys.exit(f"could not find const {name}")
    obj, _ = json.JSONDecoder().raw_decode(html, m.end())
    return obj


def main() -> None:
    html = ENGINE.read_text(encoding="utf-8")
    stim, copy = grab(html, "STIMULI"), grab(html, "COPY")

    rows = []
    for frame, rungs in stim.items():
        for rung, cell in rungs.items():
            for role_key, role in (("cause", "C"), ("selfblame", "B"),
                                   ("scene", "S"), ("neutral", "N")):
                rows.append({"frame": frame, "rung": int(rung), "role": role,
                             "role_name": role_key, "text": cell[role_key]})

    out = {"stimuli": stim, "copy": copy, "long": rows}
    (ROOT / "analysis" / "stimuli.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # structural audit: what actually varies across the 10 cells?
    print(f"cells: {sum(len(v) for v in stim.values())}  sentences: {len(rows)}")
    for role_key in ("cause", "scene", "neutral", "question", "selfblame"):
        vals = {stim[f][r][role_key] for f in stim for r in stim[f]}
        print(f"  {role_key:<10} distinct across all 10 cells: {len(vals)}")
    for frame in stim:
        qs = {stim[frame][r]["question"] for r in stim[frame]}
        print(f"  question[{frame}] distinct across rungs: {len(qs)}")


if __name__ == "__main__":
    main()
