import concurrent.futures
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))
from nasa_fire_ai.config import Settings
from nasa_fire_ai.ingestion.document_extraction import stage_prompt
from nasa_fire_ai.llm.interfaces import NvidiaStructuredClient
from nasa_fire_ai.llm.scientific_provider import ScientificTransportError, complete_scientific

root = Path("artifacts/phase1_generalizable_ingestion")
out = root / "v4/comparison_contract_reasoning"
out.mkdir(exist_ok=True)
c = sqlite3.connect(root / "v3/luci_live_07/workspace/data/index/evidence.sqlite")
tasks = {}
for (s,) in c.execute(
    "SELECT payload_json FROM phase3_cache WHERE cache_kind='scientific_document_attempt'"
):
    a = json.loads(s)
    r = a.get("request", {})
    pages = {m["page"] for m in r.get("segments", [])}
    for p in [29, 37]:
        if (
            p in pages
            and r.get("stage") == "propositions"
            and r.get("focus") is None
            and p not in tasks
        ):
            tasks[p] = a
settings = Settings()


def run(t):
    model, p = t
    a = tasks[p]
    f = out / (model.split("/")[-1] + "_" + str(p) + ".json")
    if f.exists():
        return
    receipt = {"model": model, "task": a["request"], "system": stage_prompt("propositions")}
    try:
        r = complete_scientific(
            NvidiaStructuredClient(settings.nvidia_api_key, settings.nvidia_base_url, model),
            model=model,
            system=receipt["system"],
            payload=json.dumps(a["request"], ensure_ascii=False),
            max_tokens=8192,
            timeout=120,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "scientific_propositions",
                    "strict": True,
                    "schema": a["request"]["schema"],
                },
            },
            reasoning_budget=2048,
        )
        receipt.update(
            state="COMPLETED",
            content=r.content,
            usage=r.usage,
            finish_reason=r.finish_reason,
            transport=r.metadata,
        )
    except ScientificTransportError as e:
        receipt.update(state="FAILED", error=e.kind, content=e.content, transport=e.metadata)
    f.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(model, p, receipt["state"], flush=True)


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(
        pool.map(
            run,
            [
                (m, p)
                for p in tasks
                for m in [
                    "nvidia/nemotron-3-super-120b-a12b",
                    "nvidia/nemotron-3.5-super-vl-120b-a12b",
                ]
            ],
        )
    )
