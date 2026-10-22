#!/bin/sh
# replay_set.sh CHECKOUT OUTDIR : replays the package 4 Sonnet runs and round B NVIDIA packages
C=$1; OUT=$2
M=/c/Users/legom/Documents/proyects/nasa/artifacts/phase1_generalizable_ingestion/v6/milestone13
mkdir -p $OUT
for s in ptfe ignition regulator textiles; do
  for r in 1 2; do
    (cd $C && PYTHONUTF8=1 uv run python scripts/phase1_offline_replay.py $M/package4/${s}_sonnet_a6d967b_r$r/prepared.json.gz --output $OUT/${s}_sonnet_r$r > /dev/null 2>> $OUT/errors.txt) &
  done
  (cd $C && PYTHONUTF8=1 uv run python scripts/phase1_offline_replay.py $M/${s}_live_b4be17d_r1/prepared.json.gz --output $OUT/${s}_nvidia_b > /dev/null 2>> $OUT/errors.txt) &
  wait
done
ls $OUT
