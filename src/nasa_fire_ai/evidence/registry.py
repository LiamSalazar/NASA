import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class EvidenceRegistry:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.init()

    def init(self):
        self.db.executescript("""CREATE TABLE IF NOT EXISTS sources(source_id TEXT PRIMARY KEY, source_type TEXT, nasa_id TEXT, title TEXT, doi TEXT, url TEXT, retrieved_at TEXT, filename TEXT, sha256 TEXT, mime_type TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS documents(document_id TEXT PRIMARY KEY, source_id TEXT, title TEXT);
        CREATE TABLE IF NOT EXISTS passages(evidence_id TEXT PRIMARY KEY, document_id TEXT, page INTEGER, section TEXT, text TEXT, start_offset INTEGER, end_offset INTEGER, raw_file TEXT, checksum TEXT);
        CREATE TABLE IF NOT EXISTS evidence_refs(evidence_id TEXT PRIMARY KEY, source_id TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(evidence_id UNINDEXED, text);""")
        # Operational ingestion state intentionally stays outside the RDF domain graph.
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS ingestion_batches(batch_id TEXT PRIMARY KEY, source_id TEXT, created_at TEXT, status TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS source_artifacts(artifact_id TEXT PRIMARY KEY, batch_id TEXT, source_id TEXT, investigation_id TEXT, document_id TEXT, source_type TEXT, canonical_url TEXT, doi TEXT, retrieval_timestamp TEXT, source_version TEXT, filename TEXT, mime_type TEXT, file_size INTEGER, sha256 TEXT, retrieval_status TEXT);
        CREATE TABLE IF NOT EXISTS candidate_records(candidate_id TEXT PRIMARY KEY, batch_id TEXT, candidate_type TEXT, payload_json TEXT, evidence_id TEXT, status TEXT, validation_error TEXT, fingerprint TEXT UNIQUE);
        CREATE TABLE IF NOT EXISTS review_queue(review_id TEXT PRIMARY KEY, batch_id TEXT, candidate_id TEXT, reason TEXT, status TEXT, detail_json TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS extraction_cache(cache_key TEXT PRIMARY KEY, response_json TEXT, status TEXT, created_at TEXT);
        """)
        self.db.commit()

    def add_source(self, row: dict):
        cols = ", ".join(row)
        self.db.execute(
            f"INSERT OR REPLACE INTO sources ({cols}) VALUES ({', '.join('?' for _ in row)})",
            tuple(row.values()),
        )
        self.db.commit()

    def add_document(self, document_id: str, source_id: str, title: str):
        self.db.execute(
            "INSERT OR REPLACE INTO documents(document_id, source_id, title) VALUES (?,?,?)",
            (document_id, source_id, title),
        )
        self.db.commit()

    def add_passage(self, row: dict):
        self.db.execute(
            "INSERT OR REPLACE INTO passages VALUES (:evidence_id,:document_id,:page,:section,:text,:start_offset,:end_offset,:raw_file,:checksum)",
            row,
        )
        # FTS5 has no primary-key semantics: delete first so re-ingestion cannot
        # leave stale duplicate searchable rows for the same evidence ID.
        self.db.execute("DELETE FROM passages_fts WHERE evidence_id=?", (row["evidence_id"],))
        self.db.execute(
            "INSERT INTO passages_fts(evidence_id,text) VALUES (?,?)",
            (row["evidence_id"], row["text"]),
        )
        self.db.commit()

    def search(self, query: str, eligible_ids: list[str] | None = None, limit=8):
        # FTS query syntax is not user query syntax. Quote lexical tokens so
        # punctuation such as BASS-II cannot become an FTS operator.
        terms = re.findall(r"[A-Za-z0-9]+", query)
        fts_query = " OR ".join(f'"{term}"' for term in terms) or '""'
        rows = self.db.execute(
            "SELECT p.*, bm25(passages_fts) score FROM passages_fts JOIN passages p USING(evidence_id) WHERE passages_fts MATCH ? ORDER BY score LIMIT ?",
            (fts_query, limit * 4),
        ).fetchall()
        if eligible_ids is not None:
            rows = [r for r in rows if r["evidence_id"] in eligible_ids]
        return [dict(r) for r in rows[:limit]]

    def resolve(self, evidence_id: str):
        row = self.db.execute(
            "SELECT * FROM passages WHERE evidence_id=?", (evidence_id,)
        ).fetchone()
        return dict(row) if row else None

    def rebuild_fts(self):
        self.db.execute("DELETE FROM passages_fts")
        self.db.execute(
            "INSERT INTO passages_fts(evidence_id,text) SELECT evidence_id,text FROM passages"
        )
        self.db.commit()

    def begin_batch(self, batch_id: str, source_id: str, notes: str = ""):
        self.db.execute(
            "INSERT OR IGNORE INTO ingestion_batches VALUES (?,?,?,?,?)",
            (batch_id, source_id, datetime.now(UTC).isoformat(), "INGESTED", notes),
        )
        self.db.commit()

    def add_artifact(self, row: dict):
        columns = ", ".join(row)
        self.db.execute(
            f"INSERT OR IGNORE INTO source_artifacts ({columns}) VALUES ({','.join('?' for _ in row)})",
            tuple(row.values()),
        )
        self.db.commit()

    def add_candidate(self, row: dict):
        columns = ", ".join(row)
        self.db.execute(
            f"INSERT OR REPLACE INTO candidate_records ({columns}) VALUES ({','.join('?' for _ in row)})",
            tuple(row.values()),
        )
        self.db.commit()

    def review(
        self, review_id: str, batch_id: str, candidate_id: str, reason: str, detail_json: str
    ):
        self.db.execute(
            "INSERT OR IGNORE INTO review_queue VALUES (?,?,?,?,?,?,?)",
            (
                review_id,
                batch_id,
                candidate_id,
                reason,
                "PENDING",
                detail_json,
                datetime.now(UTC).isoformat(),
            ),
        )
        self.db.commit()
