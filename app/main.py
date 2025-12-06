from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.risk import compute_risk_score, RiskReport, RiskFinding


class VendorProfile(BaseModel):
    name: str = Field(..., description="Vendor display name")
    data_residency: str = Field(..., description="Primary data residency (EU/EEA/US)")
    data_transfer_mechanism: Optional[str] = Field(
        None, description="Mechanism such as SCCs, BCRs, or none"
    )
    certifications: List[str] = Field(default_factory=list)
    encryption_at_rest: bool = False
    uses_ai: bool = False
    ai_guardrails: bool = False
    breach_history: int = 0
    sla_hours: int = 4


class RiskFindingResponse(BaseModel):
    label: str
    severity: str
    rationale: str


class RiskReportResponse(BaseModel):
    vendor: str
    risk_score: int
    level: str
    findings: List[RiskFindingResponse]
    recommendations: List[str]


class DataSovereigntyRequest(BaseModel):
    country: str
    stores_personal_data: bool = True
    sub_processors: List[str] = Field(default_factory=list)


class DataSovereigntyResponse(BaseModel):
    allowed: bool
    rationale: str


app = FastAPI(
    title="AI Vendor Trust Pilot",
    description=(
        "MVP for automated vendor risk scoring tailored to EU/Spain buyers. "
        "Use it in sales calls to produce transparent, exportable reports."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vendors: List[VendorProfile] = []


def serialize_report(report: RiskReport) -> RiskReportResponse:
    return RiskReportResponse(
        vendor=report.vendor,
        risk_score=report.risk_score,
        level=report.level,
        findings=[
            RiskFindingResponse(
                label=f.label, severity=f.severity, rationale=f.rationale
            )
            for f in report.findings
        ],
        recommendations=report.recommendations,
    )


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/vendors", response_model=VendorProfile)
def register_vendor(vendor: VendorProfile):
    vendors.append(vendor)
    return vendor


@app.post("/vendors/{vendor_name}/risk", response_model=RiskReportResponse)
def assess_vendor(vendor_name: str):
    vendor = next((v for v in vendors if v.name.lower() == vendor_name.lower()), None)
    if not vendor:
        dummy_vendor = VendorProfile(
            name=vendor_name,
            data_residency="US",
            data_transfer_mechanism="unknown",
            certifications=[],
            encryption_at_rest=False,
            uses_ai=True,
            ai_guardrails=False,
            breach_history=1,
            sla_hours=12,
        )
        report = compute_risk_score(dummy_vendor.model_dump())
        return serialize_report(report)

    report = compute_risk_score(vendor.model_dump())
    return serialize_report(report)


@app.post("/data-sovereignty", response_model=DataSovereigntyResponse)
def data_sovereignty_check(payload: DataSovereigntyRequest):
    eu_countries = {"spain", "germany", "france", "italy", "netherlands", "sweden"}
    if payload.country.lower() in eu_countries and payload.stores_personal_data:
        rationale = "Data stays in the EU/EEA; align with GDPR and local residency expectations."
        return DataSovereigntyResponse(allowed=True, rationale=rationale)

    if payload.sub_processors:
        rationale = (
            "Data leaves the EU; require SCCs, a TIA, and sub-processor transparency."
        )
    else:
        rationale = "Data location unclear; request data-flow map and DPA addendum."

    return DataSovereigntyResponse(allowed=False, rationale=rationale)


@app.get("/demo", response_model=RiskReportResponse)
def demo():
    sample_vendor = VendorProfile(
        name="IberiaCloud AI",
        data_residency="EU (Madrid)",
        data_transfer_mechanism="SCCs",
        certifications=["ISO 27001", "SOC 2"],
        encryption_at_rest=True,
        uses_ai=True,
        ai_guardrails=True,
        breach_history=0,
        sla_hours=2,
    )
    report = compute_risk_score(sample_vendor.model_dump())
    return serialize_report(report)
