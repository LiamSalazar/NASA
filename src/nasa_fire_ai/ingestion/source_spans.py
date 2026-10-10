"""Recover literal source offsets after reversible whitespace/NFC normalization."""

import re
import unicodedata


def normalized_with_offsets(text):
    output, offsets = [], []
    for match in re.finditer(r"\s+|[^\s][\u0300-\u036f]*", text):
        token = match.group()
        normalized = " " if token.isspace() else unicodedata.normalize("NFC", token)
        output.extend(normalized)
        offsets.extend([(match.start(), match.end())] * len(normalized))
    return "".join(output), offsets


def recover_span(source, proposal, start_offset=None):
    if not proposal:
        raise ValueError("empty supporting span")
    exact = [m.start() for m in re.finditer(re.escape(proposal), source)]
    if start_offset is not None and start_offset in exact:
        exact = [start_offset]
    if len(exact) == 1:
        start = exact[0]
        return {"span": proposal, "start": start, "end": start + len(proposal), "method": "EXACT"}
    normalized, offsets = normalized_with_offsets(source)
    needle = normalized_with_offsets(proposal)[0].strip()
    if not needle:
        raise ValueError("empty supporting span")
    positions = [m.start() for m in re.finditer(re.escape(needle), normalized)]
    if start_offset is not None:
        positions = [p for p in positions if offsets[p][0] == start_offset]
    if len(positions) != 1:
        raise ValueError("span missing or ambiguous; explicit source offset required")
    start = offsets[positions[0]][0]
    end = offsets[positions[0] + len(needle) - 1][1]
    return {"span": source[start:end], "start": start, "end": end, "method": "WHITESPACE_NFC"}
