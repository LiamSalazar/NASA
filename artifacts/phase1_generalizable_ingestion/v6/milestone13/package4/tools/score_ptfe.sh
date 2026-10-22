#!/bin/sh
# score_ptfe.sh ROUND  (repo root) -> review/ptfe_rN_{judgments,review,metrics}.json
set -e
R=$1; C=${PKG_COMMIT:-dc6f342}; B=../nasa-live/pkg4-$C; RUN=$B/r$R/ptfe_sonnet_${C}_r$R; T=../nasa-live/pkg4-dc6f342/tools
python $T/carry.py ptfe $RUN/prepared.json.gz $B/review/ptfe_r${R}_carry.json
python - "$B/review/ptfe_r${R}_carry.json" "$B/review/ptfe_manual.json" "$B/review/ptfe_r${R}_judgments.json" <<'PY'
import json, sys
carry = json.load(open(sys.argv[1], encoding="utf-8"))
manual = json.load(open(sys.argv[2], encoding="utf-8"))
out = {k: [v[0], v[2] + " | " + v[1]] for k, v in carry["carried"].items()}
missing = [t["id"] for t in carry["to_judge"] if t["id"] not in manual]
if missing:
    raise SystemExit("judgment needed: " + " ".join(missing))
out.update({t["id"]: manual[t["id"]] for t in carry["to_judge"]})
json.dump(out, open(sys.argv[3], "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
PY
rm -f $B/review/ptfe_r${R}_review.json $B/review/ptfe_r${R}_metrics.json $B/review/ptfe_r${R}_prepared.json
python artifacts/phase1_generalizable_ingestion/v6/review_tools/build_review_generic.py $RUN/prepared.json.gz "Package 4 round $R (fresh Sonnet run at $C); judgments carried for identical records, new records judged against the printed source" $B/review/ptfe_r${R}_review.json $B/review/ptfe_r${R}_judgments.json
python -c "import gzip,json,sys;json.dump(json.load(gzip.open(sys.argv[1],'rt',encoding='utf-8')),open(sys.argv[2],'w',encoding='utf-8'))" $RUN/prepared.json.gz $B/review/ptfe_r${R}_prepared.json
python scripts/score_scientific_review.py $B/review/ptfe_r${R}_prepared.json $B/review/ptfe_r${R}_review.json --output $B/review/ptfe_r${R}_metrics.json > /dev/null
python -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));print('recall',d['semantic_recall'],'precision',d['reviewed_proposal_precision'],'critical',d['incorrect_critical_assignments_in_sample'],d['outcomes'])" $B/review/ptfe_r${R}_metrics.json
