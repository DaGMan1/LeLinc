from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class Confidence(str, Enum):
    CONFIRMED = "CONFIRMED"
    HIGH = "HIGH"
    POSSIBLE = "POSSIBLE"
    FALSE = "FALSE"


# Each claim type's 3 independent checks - see ARCHITECTURE.md section 6.
RULES: dict[str, list[str]] = {
    "instagram": [
        "username_resolves",
        "email_breach_linked_to_handle",
        "domain_in_bio_or_posts",
    ],
    "linkedin": [
        "name_company_match",
        "domain_in_company_description",
        "email_format_matches_domain",
    ],
    "facebook": [
        "username_resolves",
        "name_location_match",
        "domain_in_bio_or_posts",
    ],
    "tiktok": [
        "username_resolves",
        "email_breach_linked_to_handle",
        "domain_in_bio_or_posts",
    ],
    "financial_distress": [
        "distress_signal_found",
        "actively_trading",
        "decision_maker_identified",
    ],
    "business_viability": [
        "distress_signal_found",
        "actively_trading",
        "decision_maker_identified",
    ],
}

_SCORE_TO_CONFIDENCE = {
    3: Confidence.CONFIRMED,
    2: Confidence.HIGH,
    1: Confidence.POSSIBLE,
    0: Confidence.FALSE,
}


class QCCheckRequest(BaseModel):
    claim_type: str
    sources: list[str]


class QCCheckResponse(BaseModel):
    claim_type: str
    matched_sources: list[str]
    confidence: Confidence
    show_to_client: bool


router = APIRouter()


@router.post("/qc/check", response_model=QCCheckResponse)
def check_claim(req: QCCheckRequest) -> QCCheckResponse:
    rule_set = RULES.get(req.claim_type.lower())
    if rule_set is None:
        raise HTTPException(status_code=400, detail=f"Unknown claim_type: {req.claim_type}")
    matched = [s for s in req.sources if s in rule_set]
    confidence = _SCORE_TO_CONFIDENCE[len(matched)]
    return QCCheckResponse(
        claim_type=req.claim_type,
        matched_sources=matched,
        confidence=confidence,
        # Anything below HIGH (2/3) is never shown to the client - flagged internally only.
        show_to_client=confidence in (Confidence.CONFIRMED, Confidence.HIGH),
    )
