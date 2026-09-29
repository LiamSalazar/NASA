from pathlib import Path

import fitz


def extract_pdf(path: Path):
    doc = fitz.open(path)
    return [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
