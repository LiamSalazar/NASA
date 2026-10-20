#!/bin/sh
# Replay the eight PTFE runs and the exposed sources at the working tree.
T=${NFA_TMP:-/tmp/nfa6}
OUT=$1
rm -rf "$T/$OUT"
for r in 1 2 4 5 6 7 8 9; do
  in=$(python -c "import json;print(json.load(open('artifacts/phase1_generalizable_ingestion/v6/milestone4/rescored_c314286/ptfe_run$r/replay.json',encoding='utf-8'))['input'])")
  uv run python scripts/phase1_offline_replay.py "$in" --output "$T/$OUT/run$r" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
done
for s in $(ls ${NFA_TMP:-/tmp/nfa6}/exposed); do
  in=$(python -c "import json;print(json.load(open('$T/exposed/$s/replay.json',encoding='utf-8'))['input'])")
  uv run python scripts/phase1_offline_replay.py "$in" --output "$T/$OUT/exposed/$s" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
done
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone5/ptfe_live_fe4f1bb/prepared.json.gz --output "$T/$OUT/run10" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone5/ptfe_live_160d73f/prepared.json.gz --output "$T/$OUT/run11" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone5/ptfe_live_134b543/prepared.json.gz --output "$T/$OUT/run12" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone5/ptfe_live_160a931/prepared.json.gz --output "$T/$OUT/run13" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
for n in ignition regulator textiles; do
  uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone7/${n}_live_1dffc83/prepared.json.gz --output "$T/$OUT/dev_$n" > /dev/null 2> "$T/$OUT.err" || tail -3 "$T/$OUT.err"
done
