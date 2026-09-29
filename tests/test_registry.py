from nasa_fire_ai.evidence import EvidenceRegistry


def test_fts_and_resolution_without_api_key(tmp_path):
    r = EvidenceRegistry(tmp_path / "x.sqlite")
    r.add_passage(
        {
            "evidence_id": "E1",
            "document_id": "D",
            "page": 1,
            "section": None,
            "text": "microgravity flame spread evidence",
            "start_offset": 0,
            "end_offset": 36,
            "raw_file": "x.pdf",
            "checksum": "a",
        }
    )
    assert r.search("microgravity")[0]["evidence_id"] == "E1"
    assert r.resolve("E1")["page"] == 1
