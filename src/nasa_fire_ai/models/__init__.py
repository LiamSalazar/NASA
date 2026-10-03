from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EvidenceReference(BaseModel):
    evidence_id: str
    source_id: str
    page: int | None = None
    section: str | None = None


class EvidenceBacked(BaseModel):
    evidence_refs: list[EvidenceReference] = Field(min_length=1)


class InvestigationRecord(EvidenceBacked):
    id: str
    title: str
    doi: str | None = None


class SampleRecord(EvidenceBacked):
    id: str
    material: str
    geometry: str | None = None


class ConditionRecord(EvidenceBacked):
    kind: str
    reported_value: float | str
    reported_unit: str | None = None
    canonical_value: float | None = None
    canonical_unit: str | None = None
    reported_lower_value: float | None = None
    reported_upper_value: float | None = None
    canonical_lower_value: float | None = None
    canonical_upper_value: float | None = None
    is_approximate: bool = False


class InterventionRecord(EvidenceBacked):
    id: str
    description: str


class MeasurementRecord(EvidenceBacked):
    id: str
    name: str
    reported_value: float | str
    reported_unit: str | None = None


class ObservationRecord(EvidenceBacked):
    id: str
    phenomenon: str
    text: str


class MeasurementObservationRecord(EvidenceBacked):
    """A numeric observation reported by a source, never an inferred value."""

    id: str
    measurement: str
    reported_value: float | str
    reported_unit: str | None = None


class ReportedExperimentalObservationRecord(EvidenceBacked):
    """A qualitative experimental observation explicitly reported by NASA."""

    id: str
    text: str
    phenomenon: str | None = None


class ExperimentalRunRecord(EvidenceBacked):
    id: str
    investigation_id: str
    sample_id: str
    condition_ids: list[str]


class NASAConclusionRecord(EvidenceBacked):
    id: str
    text: str
    concerns: str


class NormativeStatementRecord(EvidenceBacked):
    id: str
    statement_type: Literal["requirement", "guidance", "design_criterion", "test_criterion"]
    text: str


class OpenQuestionRecord(EvidenceBacked):
    id: str
    text: str


class SafetyStatementRecord(EvidenceBacked):
    statement_id: str
    statement_type: Literal[
        "nasa_conclusion",
        "safety_implication",
        "requirement",
        "guidance",
        "design_criterion",
        "test_criterion",
        "open_question",
    ]
    normalized_text: str
    source_document: str
    source_page: int | None = None
    source_section: str | None = None
    scope_applicability: str | None = None


class PublicationRecord(EvidenceBacked):
    id: str
    title: str
    nasa_id: str | None = None
    url: str | None = None


class NumericFilter(BaseModel):
    operator: Literal["<", "<=", "=", ">=", ">"] = "="
    value: float
    unit: str | None = None


class QueryIntent(BaseModel):
    query_mode: Literal[
        "general_search", "experiment_search", "safety_search", "combined_search", "compare"
    ] = "general_search"
    materials: list[str] = []
    investigations: list[str] = []
    gravity_conditions: list[str] = []
    oxygen: NumericFilter | None = None
    pressure: NumericFilter | None = None
    flow_velocity: NumericFilter | None = None
    flow_direction: str | None = None
    geometries: list[str] = []
    phenomena: list[str] = []
    safety_intents: list[
        Literal[
            "requirement", "guidance", "design_criterion", "safety_implication", "open_question"
        ]
    ] = []
    requested_information: list[
        Literal[
            "experiments", "observations", "measurements", "conclusions", "publications", "safety"
        ]
    ] = []


class Claim(BaseModel):
    claim_id: str
    claim_type: Literal[
        "observed_result",
        "tested_intervention",
        "nasa_conclusion",
        "safety_implication",
        "requirement",
        "guidance",
        "design_criterion",
        "open_question",
        "related_evidence_notice",
        "no_direct_evidence_notice",
    ]
    text: str
    evidence_ids: list[str] = []
    scope_conditions: list[str] = []

    @model_validator(mode="after")
    def scientific_claims_have_evidence(self):
        if self.claim_type not in {"no_direct_evidence_notice"} and not self.evidence_ids:
            raise ValueError("Scientific claims require evidence_ids")
        return self


class EvidenceBundle(BaseModel):
    query_intent: QueryIntent
    direct_evidence: list[dict] = []
    related_evidence: list[dict] = []
    experimental_observations: list[dict] = []
    interventions: list[dict] = []
    nasa_conclusions: list[dict] = []
    safety_implications: list[dict] = []
    requirements: list[dict] = []
    guidance: list[dict] = []
    design_test_criteria: list[dict] = []
    nasa_identified_open_questions: list[dict] = []
    publications: list[dict] = []
    evidence_passages: list[dict] = []
    no_direct_evidence: bool = False


class ExperimentComparison(BaseModel):
    run_ids: list[str]
    shared_conditions: dict[str, object] = {}
    different_conditions: dict[str, dict[str, object]] = {}
    unknown_or_unavailable_conditions: list[str] = []


class ScientificAnswer(BaseModel):
    query: str
    query_intent: QueryIntent
    direct_evidence_status: Literal["DIRECT_EVIDENCE", "RELATED_EVIDENCE", "NO_DIRECT_EVIDENCE"]
    direct_evidence: list[dict] = []
    related_evidence: list[dict] = []
    experimental_interventions: list[dict] = []
    observations: list[dict] = []
    measurements: list[dict] = []
    nasa_conclusions: list[dict] = []
    safety_implications: list[dict] = []
    requirements: list[dict] = []
    guidance: list[dict] = []
    design_test_criteria: list[dict] = []
    nasa_identified_open_questions: list[dict] = []
    publications: list[dict] = []
    sources: list[dict] = []
    coverage_notes: list[str] = []
    comparison: ExperimentComparison | None = None
