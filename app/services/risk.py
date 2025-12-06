from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class RiskFinding:
    label: str
    severity: str
    rationale: str


@dataclass
class RiskReport:
    vendor: str
    risk_score: int
    level: str
    findings: List[RiskFinding]
    recommendations: List[str]


def compute_risk_score(vendor_profile: Dict) -> RiskReport:
    """Compute a transparent, deterministic vendor risk score.

    The scoring favors privacy-by-design (DPA, encryption), data sovereignty,
    and operational maturity that are critical for EU buyers.
    """

    score = 0
    findings: List[RiskFinding] = []
    recommendations: List[str] = []

    # Data residency and transfers
    residency = vendor_profile.get("data_residency", "").lower()
    transfer = vendor_profile.get("data_transfer_mechanism", "").lower()
    if "eu" in residency or "eea" in residency:
        score += 25
    else:
        findings.append(
            RiskFinding(
                label="Data residency",
                severity="high",
                rationale="Data stored outside the EU/EEA increases Schrems II exposure.",
            )
        )
        recommendations.append("Offer an EU/EEA data-hosting option and document sub-processors.")

    if transfer in {"sccs", "standard contractual clauses"}:
        score += 15
    else:
        findings.append(
            RiskFinding(
                label="Data transfers",
                severity="medium",
                rationale="No clear lawful transfer mechanism (e.g., SCCs) defined.",
            )
        )
        recommendations.append("Clarify transfer mechanism (SCCs) and add a Transfer Impact Assessment.")

    # Security posture
    if vendor_profile.get("certifications"):
        score += min(20, 5 * len(vendor_profile["certifications"]))
    else:
        findings.append(
            RiskFinding(
                label="Certifications",
                severity="medium",
                rationale="Missing attestations like ISO27001/SOC2 lowers trust for procurement.",
            )
        )
        recommendations.append("Provide ISO 27001 or SOC 2 evidence and a recent pentest summary.")

    if vendor_profile.get("encryption_at_rest", False):
        score += 10
    else:
        findings.append(
            RiskFinding(
                label="Encryption at rest",
                severity="medium",
                rationale="Datastores should be encrypted at rest to meet GDPR Article 32 expectations.",
            )
        )
        recommendations.append("Enable encryption at rest on primary datastores and backups.")

    if vendor_profile.get("uses_ai", False):
        if vendor_profile.get("ai_guardrails", False):
            score += 15
        else:
            findings.append(
                RiskFinding(
                    label="AI guardrails",
                    severity="medium",
                    rationale="AI features without documented safeguards risk hallucinations and data leaks.",
                )
            )
            recommendations.append("Publish AI usage policy, monitoring, and red-teaming results.")

    # Breach history
    if vendor_profile.get("breach_history", 0) == 0:
        score += 10
    else:
        findings.append(
            RiskFinding(
                label="Breach history",
                severity="high",
                rationale="Past breaches require evidence of remediation and improved controls.",
            )
        )
        recommendations.append("Share root-cause analysis and compensating controls post-incident.")

    # SLAs
    if vendor_profile.get("sla_hours", 0) <= 4:
        score += 5
    else:
        findings.append(
            RiskFinding(
                label="Support SLA",
                severity="low",
                rationale="Long response times reduce suitability for regulated customers.",
            )
        )
        recommendations.append("Offer EU business-hours support with <4h first response.")

    score = min(score, 100)
    if score >= 80:
        level = "low"
    elif score >= 60:
        level = "medium"
    else:
        level = "high"

    if not recommendations:
        recommendations.append("Maintain current controls and provide quarterly security reports.")

    return RiskReport(
        vendor=vendor_profile.get("name", "Unknown"),
        risk_score=score,
        level=level,
        findings=findings,
        recommendations=recommendations,
    )
