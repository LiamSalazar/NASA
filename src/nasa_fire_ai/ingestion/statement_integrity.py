"""Whole-statement integrity checks read from the original page text.

These checks never repair or reinterpret a statement. They mark, for review,
statements that are not one whole source proposition (cut at an abbreviation or
at a page break), observations whose own source prints a conflicting count, and
one source span accepted with incompatible epistemic roles.
"""

import re

ABBREVIATION_END = re.compile(
    r"(?:\b(?:i\.\s?e|e\.\s?g|vs|cf|approx|ca|Figs?|Eqs?|No|Refs?)\.|\bet\s+al\.)\s*$",
    re.IGNORECASE,
)
TERMINAL = re.compile(r"[.!?:;\"”’)\]]\s*$")
CONTINUING_TAIL = re.compile(
    r"(?:[,(–—-]|\b(?:of|the|a|an|and|or|nor|to|in|for|with|by|from|as|at|on|that|which|than"
    r"|whose|its|their|be|been|being|was|were|is|are|has|have|had|not|will|would|could"
    r"|should|may|might|can)\b)\s*$",
    re.IGNORECASE,
)
OBSERVATION_CUE = re.compile(
    r"\b(?:test\w*|react\w*|pass(?:ed|es)?|fail\w*|impact\w*|ignit\w*|burn\w*|flam\w*|extinguish\w*"
    r"|measur\w*|observ\w*|shown|show(?:s|ed|ing)?|result\w*|data|record\w*|detect\w*|seen"
    r"|pictur\w*|photo\w*|imag\w*|produc\w*|perform\w*|exhibit\w*|found|reach\w*|increas\w*"
    r"|decreas\w*|rose|fell|remain\w*|became|occur\w*|spread\w*|grew|shrank|reduc\w*)\b",
    re.IGNORECASE,
)
PURPOSE = re.compile(r"\b(?:in\s+order\s+to|so\s+as\s+to)\b", re.IGNORECASE)
POINTER = re.compile(
    r"\b(?:are|is|were|was)\s+(?:shown|presented|listed|given|summarized|tabulated|plotted"
    r"|depicted)\s+in\s+(?:Table|Figure|Fig\.?|Appendix)\b",
    re.IGNORECASE,
)
RULE_OR_CAVEAT = re.compile(
    r"\b(?:(?:cannot|can\s+only)(?!\s+be\s+(?:seen|observed|detected|distinguished|resolved|identified|measured)\b)|must|shall|should|ought\s+to|(?:is|are)\s+only\s+valid"
    r"|(?:is|are)\s+(?:not\s+)?(?:required|necessary|permitted|allowed))\b",
    re.IGNORECASE,
)
VALIDITY_CAVEAT = re.compile(
    r"\b(?:is|are|was|were)\s+(?:only\s+)?(?:valid|applicable)(?:\s+only)?\s+(?:for|when|if"
    r"|within|below|above|under|between|up\s+to)\b",
    re.IGNORECASE,
)
APPLIED_STEP = re.compile(
    r"\b(?:was|were)\s+(?:impacted|struck|tested|exposed|subjected|heated|pressurized|loaded"
    r"|placed|positioned|submerged|immersed|purged|sealed|prepared|cooled|dropped|mounted)\b",
    re.IGNORECASE,
)
OUTCOME_CUE = re.compile(
    r"\b(?:react\w*|pass(?:ed|es)?|fail\w*|ignit\w*|burn\w*|flam\w*|extinguish\w*|observ\w*"
    r"|shown|show(?:s|ed|ing)?|result\w*|detect\w*|seen|found|produc\w*|perform\w*|exhibit\w*"
    r"|increas\w*|decreas\w*|rose|fell|remain\w*|became|occur\w*|spread\w*|grew|shrank|reduc\w*"
    r"|no\s+(?:reaction|ignition|flash|change)s?|zero)\b",
    re.IGNORECASE,
)
FRONT_MATTER = re.compile(
    r"(?:Available\s+online|Paper\s+ID|Published\s+[A-Z0-9]|doi:|©|Vol\.?\s*[\w]+,\s*No\.)",
    re.IGNORECASE,
)
CAPTION_LINE = re.compile(
    r"^\s*(?:Figure|Fig\.?|Table)\s*[-–—]?\s*\d+\s*[-–—:.]\s*[^\n]*\n\s*\S", re.IGNORECASE
)
CRITERION = re.compile(
    r"\b(?:is|are)\s+said\s+to\b|\bpass/fail\b|\bcriteri(?:on|a)\b"
    r"|\bif\b[^.;]*\b(?:then|is\s+recorded|are\s+recorded|must|shall)\b"
    # "The indication of autogenous ignition was the rapid increase of ...":
    # what counts as the event, not an event seen.
    r"|^\s*the\s+indications?\s+of\b[^.;]*?\b(?:was|were|is|are)\s+(?:the|a|an)\b",
    re.IGNORECASE,
)
EXAMINATION_STEP = re.compile(
    r"\b(?:was|were)\s+(?:analy[sz]ed|examined|inspected|checked|evaluated|conducted|performed)"
    r"\s+(?:for|to|by|using|with|at|in|under)\b",
    re.IGNORECASE,
)
INTERPRETIVE_CUE = re.compile(
    r"\b(?:suggest\w*|indicat\w*|conclu\w*|appear\w*|likely|probabl\w*|due\s+to|because"
    r"|therefore|thus|hence|demonstrat\w*|superior|outperform\w*|better|worse|compatib\w*"
    r"|sensitiv\w*|reactiv\w*|perform\w*|safe\w*|recommend\w*|attribut\w*|explain\w*)\b",
    re.IGNORECASE,
)
WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
EVENT = r"(?:react\w*|ignit\w*|fail\w*|burn\w*)"
NEGATED_COUNT = re.compile(
    rf"\b(?:no|zero|none|neither|not\s+any|without\s+any)\b[^.;]*?\b{EVENT}[^.;]*?"
    r"\b(?:out\s+of|of)\s+(?:the\s+)?(?:[a-z]+\s+){0,2}?(\d[\d,]*)\b",
    re.IGNORECASE,
)
POSITIVE_COUNT = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:of|out\s+of)\s+(?:the\s+)?"
    rf"(?:[a-z]+\s+){{0,3}}?(\d[\d,]*)\b[^.;]*?\b{EVENT}",
    re.IGNORECASE,
)
ROLE_FAMILY = {
    "measured_observation": "OBSERVATION",
    "derived_quantity": "DERIVATION",
    "experimental_configuration": "CONFIGURATION",
    "author_reported_conclusion": "INTERPRETATION",
    "tentative_interpretation": "INTERPRETATION",
    "hypothesis": "INTERPRETATION",
    "normative_requirement": "NORM",
    "guidance": "NORM",
    "open_question": "QUESTION",
    "documentary_context": "DOCUMENTARY",
    "reported_quantity": "OBSERVATION",
}


def _body_bounds(text):
    """Page text without a leading or trailing page-number line."""
    begin = re.match(r"\s*\d{1,4}\s*\n", text)
    end = re.search(r"\n\s*\d{1,4}\s*$", text)
    return (begin.end() if begin else 0), (end.start() if end else len(text.rstrip()))


def fragment_context(text, location, evidence):
    """Why a statement is not one whole source sentence, or None.

    ``location`` is the statement's exact original span: evidence_id, start, end.
    """
    if ABBREVIATION_END.search(text.strip()):
        return {"basis": "STATEMENT_ENDS_AT_ABBREVIATION", "quote": text.strip()[-12:]}
    if CAPTION_LINE.match(text):
        # A figure or table caption line glued to the sentence that follows it.
        return {"basis": "STATEMENT_INCLUDES_A_CAPTION_LINE", "quote": text.strip()[:60]}
    if text.count("\n") >= 3 and FRONT_MATTER.search(text):
        # Journal front matter (byline, placeholders, URL) is not one proposition.
        return {"basis": "STATEMENT_IS_FRONT_MATTER", "quote": text.strip()[:60]}
    page = evidence[location["evidence_id"]]
    begin, end = _body_bounds(page["text"])
    stripped = text.lstrip()
    if stripped[:1].islower() and not re.match(r"(?:pH\b|[a-z][-\d])", stripped):
        # A lower-case start after text that did not end a sentence is the tail
        # of the previous sentence ("temperature  This sought to ...").
        before = page["text"][: location["start"]].rstrip()
        if before and not TERMINAL.search(before) and not re.search(r"\n\s*\d{1,4}\s*$", before):
            return {
                "basis": "STATEMENT_STARTS_MID_SENTENCE",
                "quote": before[-40:] + " | " + stripped[:40],
            }
    pages = [
        p
        for p in evidence.values()
        if p["source_id"] == page["source_id"] and p.get("page") is not None
    ]
    after = [p for p in pages if p.get("page") == (page.get("page") or 0) + 1]
    # A slide bullet may end a page without punctuation; only a word that needs
    # its continuation ("of", "the", a comma), or a next page that resumes in
    # lower case, shows the sentence goes on.
    if after and not TERMINAL.search(text) and not page["text"][location["end"] : end].strip():
        following = after[0]["text"]
        resumed = following[_body_bounds(following)[0] :].lstrip()[:1].islower()
        if CONTINUING_TAIL.search(text) or resumed:
            return {"basis": "SENTENCE_CONTINUES_ON_NEXT_PDF_PAGE", "quote": text.strip()[-60:]}
    before = [p for p in pages if p.get("page") == (page.get("page") or 0) - 1]
    if before and not page["text"][begin : location["start"]].strip():
        previous = before[0]["text"]
        tail = previous[: _body_bounds(previous)[1]].rstrip()
        if CONTINUING_TAIL.search(tail):
            return {"basis": "SENTENCE_STARTS_ON_PREVIOUS_PDF_PAGE", "quote": tail[-60:]}
    return None


def _count(value):
    value = value.lower().replace(",", "")
    return WORD_NUMBERS.get(value, int(value) if value.isdigit() else None)


def count_conflict(location, evidence, window=600):
    """A nearby source sentence giving a non-zero count of the same total.

    "Neither ... showed any reactions out of the 80 impacts" next to "Four of
    the additional 80 LOX samples reacted" is a conflict printed by the source;
    both statements stay for review instead of one being accepted.
    """
    text = evidence[location["evidence_id"]]["text"]
    own = text[location["start"] : location["end"]]
    nearby = text[max(0, location["start"] - window) : location["end"] + window]
    for negated in NEGATED_COUNT.finditer(own):
        total = _count(negated.group(1))
        for positive in POSITIVE_COUNT.finditer(nearby):
            if _count(positive.group(2)) == total and (_count(positive.group(1)) or 0) > 0:
                return {"basis": "SOURCE_PRINTS_CONFLICTING_COUNTS", "quote": positive.group()}
    for positive in POSITIVE_COUNT.finditer(own):
        if not (_count(positive.group(1)) or 0) > 0:
            continue
        total = _count(positive.group(2))
        for negated in NEGATED_COUNT.finditer(nearby):
            if _count(negated.group(1)) == total:
                return {"basis": "SOURCE_PRINTS_CONFLICTING_COUNTS", "quote": negated.group()}
    return None


def observation_cue(text):
    """Whether a passage reports testing or an observed result, not a procedure.

    A purpose clause ("a picture was taken in order to show ...") describes
    what was done, not what was observed.
    """
    return bool(OBSERVATION_CUE.search(text or "")) and not PURPOSE.search(text or "")


def stated_criterion(text):
    """Whether a passage states an acceptance or recording rule."""
    return bool(CRITERION.search(text or ""))


def documentary_pointer(text):
    """Whether a passage only points at where results are printed."""
    return bool(POINTER.search(text or ""))


def rule_or_caveat(text):
    """Whether a passage states a rule, requirement or validity caveat."""
    return bool(RULE_OR_CAVEAT.search(text or ""))


def validity_caveat(text):
    """Whether a passage states the conditions under which a value or comparison holds."""
    return bool(VALIDITY_CAVEAT.search(text or ""))


def procedure_without_outcome(text):
    """Whether a passage only says what was done to the specimens, with no outcome.

    "Each was impacted with 98 J at 10,000 psia" is a test step; it becomes an
    observation only when the passage also reports what happened.
    """
    return bool(APPLIED_STEP.search(text or "")) and not OUTCOME_CUE.search(text or "")


DETECTION_METHOD = re.compile(
    r"^\s*the\s+detection\s+of\b[^.;]*?\b(?:was|were|is|are)\s+(?:indicated|determined|made|signall?ed)\s+by\b",
    re.IGNORECASE,
)
DATA_PROVENANCE = re.compile(
    r"\b(?:data|results?|values?)\b[^.;]*?\b(?:were|was|are|is)\s+(?:obtained|taken|collected"
    r"|gathered|compiled|drawn|acquired|sourced)\b",
    re.IGNORECASE,
)


DOCUMENTED_OBSERVATION = re.compile(
    r"\b(?:shows?|showed|reveals?|revealed)\s+that\b"
    r"|\bcan(?:not)?\s+be\s+seen\b(?!\s+in\s+(?:Table|Figure|Fig\.?)\b)",
    re.IGNORECASE,
)


def documented_observation(text):
    """Whether a passage reports what a picture or record shows, not where it is."""
    text = text or ""
    return bool(
        DOCUMENTED_OBSERVATION.search(text)
        and re.search(
            r"\b(?:pictures?|photo\w*|images?|micrographs?|figures?|can(?:not)?\s+be\s+seen)\b",
            text,
            re.IGNORECASE,
        )
        and not POINTER.search(text)
    )


def reported_outcome(text):
    """Whether a passage reports what happened, not only what was done, used or sourced.

    "The detection of a reaction was indicated by a photodiode" says how an
    outcome is detected, and "The data ... were obtained by ..." where data came
    from; neither reports an outcome.
    """
    text = text or ""
    return bool(
        OUTCOME_CUE.search(text)
        and not DETECTION_METHOD.search(text)
        and not DATA_PROVENANCE.search(text)
    )


def procedure_without_interpretation(text):
    """Whether a passage only says what was done to or with the specimens.

    "After several series of tests were conducted ..., the samples were
    analyzed for signs of combustion" is a step of the method; it interprets
    nothing.
    """
    text = text or ""
    return bool(
        (APPLIED_STEP.search(text) or EXAMINATION_STEP.search(text))
        and not INTERPRETIVE_CUE.search(text)
    )


def conflicting_roles(records):
    """Accepted statements or quantity values on one source span with incompatible roles.

    Returns the ids of the records to hold for review.
    """
    groups = {}
    for record in records:
        if record["status"] != "SOURCE_SUPPORTED":
            continue
        if record["kind"] == "quantities" and record.get("quantity_value_spans"):
            # One printed value read both as a set-up input and as a result.
            key = (
                "quantities",
                record.get("subject"),
                tuple(
                    (v["evidence_id"], v["start"], v["end"]) for v in record["quantity_value_spans"]
                ),
            )
            groups.setdefault(key, []).append(record)
            continue
        if record["kind"] != "statements":
            continue
        located = record.get("statement_location")
        if not located:
            continue
        key = (located["evidence_id"], located["start"], located["end"])
        groups.setdefault(key, []).append(record)
    held = set()
    for members in groups.values():
        families = {
            ROLE_FAMILY.get(r["proposal"]["epistemic"], r["proposal"]["epistemic"]) for r in members
        }
        if len(families) > 1:
            held.update(r["id"] for r in members)
    return held
