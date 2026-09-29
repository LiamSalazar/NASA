import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nasa_fire_ai.config import Settings
from nasa_fire_ai.evidence import EvidenceRegistry
from nasa_fire_ai.query import parse_query
from nasa_fire_ai.services import build_bundle, render

st.set_page_config(page_title="NASA Fire Safety Evidence", layout="wide")
st.title("NASA spacecraft fire-safety evidence assistant")
st.caption(
    "Evidence assistant only — scientists make scientific interpretation and applicability judgments."
)
q = st.text_input(
    "Natural-language query", placeholder="Find microgravity PMMA evidence below 18% O2"
)
if q:
    registry = EvidenceRegistry(Settings().registry_path)
    intent = parse_query(q)
    bundle = build_bundle(intent, q, Path(__file__).resolve().parents[1], registry)
    with st.expander("Parsed QueryIntent", expanded=True):
        st.json(intent.model_dump())
    if bundle.no_direct_evidence:
        st.warning(
            "No direct matching evidence was found in the indexed corpus. This is not a NASA-identified knowledge gap."
        )
    for label, items in [
        ("Direct Evidence", bundle.direct_evidence),
        ("Related Evidence", bundle.related_evidence),
        (
            "Safety Knowledge",
            bundle.nasa_conclusions
            + bundle.safety_implications
            + bundle.requirements
            + bundle.guidance
            + bundle.design_test_criteria,
        ),
        ("NASA-Identified Open Questions", bundle.nasa_identified_open_questions),
    ]:
        if items:
            st.subheader(label)
            st.write(items)
    st.subheader("Sources")
    for p in bundle.evidence_passages:
        with st.expander(f"{p['evidence_id']} · page {p['page']}"):
            st.write(p["text"])
    st.text_area("Extractive answer", render(bundle), height=360)
    if not Settings().api_key:
        st.info(
            "LLM synthesis is disabled (no OPENAI_API_KEY). Retrieval and comparisons remain available."
        )
