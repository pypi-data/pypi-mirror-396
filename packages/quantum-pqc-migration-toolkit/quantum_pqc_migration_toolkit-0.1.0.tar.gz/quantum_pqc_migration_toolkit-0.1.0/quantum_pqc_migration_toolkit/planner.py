"""
Migration Planning Engine for PQC Migration

Provides algorithm recommendations and migration timelines based on
system characteristics and organizational strategy. Recommendations
are informed by:

- NIST FIPS 203-205 algorithm specifications
- Performance characteristics (computational overhead, key/signature sizes)
- NSM-10 implementation timelines
- System criticality and data sensitivity
"""

from typing import List, Dict, Any, Optional, Tuple

from quantum_pqc_migration_toolkit.models import (
    System,
    Scenario,
    MigrationRecommendation,
    RiskAssessment,
)
from quantum_pqc_migration_toolkit.risk_params import (
    CURRENT_YEAR,
    MIGRATION_DEADLINES,
    PQC_COMPUTATIONAL_OVERHEAD,
    PQC_SIZE_FACTORS,
    DATA_LIFETIME_THRESHOLDS,
)


def recommend_migration(
    system: System,
    scenario: Optional[Scenario] = None,
    risk_assessment: Optional[RiskAssessment] = None,
) -> MigrationRecommendation:
    """
    Generate a migration recommendation for a system.

    Recommends target PQC algorithms and migration timeline based on
    system characteristics, data sensitivity, and organizational strategy.

    Args:
        system: The system to plan migration for
        scenario: Optional scenario parameters
        risk_assessment: Optional pre-computed risk assessment

    Returns:
        MigrationRecommendation with algorithm targets and timeline
    """
    if scenario is None:
        scenario = Scenario.baseline()

    # Determine migration mode and algorithm selections
    target_kem, target_sig, mode = _select_algorithms(system)

    # Determine migration deadline
    migrate_by_year = _compute_migration_deadline(system, scenario)

    # Get priority score from assessment or compute basic score
    if risk_assessment:
        priority_score = risk_assessment.priority_score
    else:
        priority_score = _compute_basic_priority(system)

    # Generate rationale
    rationale = _generate_rationale(system, target_kem, target_sig, mode, migrate_by_year)

    return MigrationRecommendation(
        system_name=system.name,
        target_kem=target_kem,
        target_sig=target_sig,
        mode=mode,
        migrate_by_year=migrate_by_year,
        priority_score=priority_score,
        rationale=rationale,
    )


def plan_inventory_migration(
    systems: List[System],
    assessments: Optional[List[RiskAssessment]] = None,
    scenario: Optional[Scenario] = None,
) -> List[MigrationRecommendation]:
    """
    Generate migration recommendations for all systems in an inventory.

    Args:
        systems: List of systems to plan for
        assessments: Optional pre-computed risk assessments
        scenario: Optional scenario parameters

    Returns:
        List of MigrationRecommendations, sorted by priority
    """
    # Create lookup for assessments if provided
    assessment_lookup: Dict[str, RiskAssessment] = {}
    if assessments:
        assessment_lookup = {a.system_name: a for a in assessments}

    recommendations = []
    for system in systems:
        assessment = assessment_lookup.get(system.name)
        rec = recommend_migration(system, scenario, assessment)
        recommendations.append(rec)

    # Sort by priority descending, then by migrate_by_year ascending
    recommendations.sort(
        key=lambda r: (-r.priority_score, r.migrate_by_year)
    )

    return recommendations


def _select_algorithms(system: System) -> Tuple[str, str, str]:
    """
    Select appropriate PQC algorithms based on system characteristics.

    Returns:
        Tuple of (target_kem, target_sig, mode)
    """
    sensitivity = system.data_sensitivity.lower()
    lifetime = system.data_lifetime_years
    role = system.system_role.lower()

    # Determine mode: pure PQC vs hybrid
    # Hybrid is recommended for systems that need backward compatibility
    # or have lower sensitivity
    use_hybrid = sensitivity in ("low", "medium") and lifetime < 10

    # Select KEM based on sensitivity
    if sensitivity == "critical" or lifetime >= 20:
        target_kem = "ML-KEM-1024"
    elif sensitivity == "high" or lifetime >= 15:
        target_kem = "ML-KEM-768"
    else:
        target_kem = "ML-KEM-768"  # ML-KEM-512 could be used but 768 is safer default

    # If hybrid mode, prepend with classical algorithm
    if use_hybrid:
        target_kem = f"X25519+{target_kem}"

    # Select signature algorithm
    if role in ("pki", "code_signing", "key_management"):
        # For long-term trust anchors, consider SLH-DSA for conservative security
        # despite overhead, especially for root CAs and code signing
        if sensitivity == "critical" and lifetime >= 25:
            target_sig = "SLH-DSA-256s"
        elif sensitivity == "critical":
            target_sig = "SLH-DSA-192s"
        else:
            target_sig = "ML-DSA-87"
    elif sensitivity == "critical":
        target_sig = "ML-DSA-87"
    elif sensitivity == "high" or lifetime >= 10:
        target_sig = "ML-DSA-65"
    else:
        target_sig = "ML-DSA-44"

    # If hybrid mode for signatures
    if use_hybrid and not target_sig.startswith("SLH"):
        target_sig = f"ECDSA-P256+{target_sig}"

    mode = "hybrid" if use_hybrid else "pure_pq"

    return target_kem, target_sig, mode


def _compute_migration_deadline(
    system: System,
    scenario: Scenario,
) -> int:
    """
    Compute recommended migration deadline year.

    Based on:
    - Data sensitivity and lifetime
    - System role criticality
    - Adoption strategy
    - Quantum arrival timeline
    """
    sensitivity = system.data_sensitivity.lower()
    lifetime = system.data_lifetime_years
    role = system.system_role.lower()
    strategy = scenario.adoption_strategy.lower()

    # Base deadline from strategy
    base_deadline = MIGRATION_DEADLINES.get(strategy, 2032)

    # Adjust based on criticality
    adjustment = 0

    # Critical systems and long-lived data need earlier migration
    if sensitivity == "critical":
        adjustment -= 3
    elif sensitivity == "high":
        adjustment -= 1

    if lifetime >= 20:
        adjustment -= 2
    elif lifetime >= 15:
        adjustment -= 1

    # High-priority roles need earlier migration
    if role in ("pki", "code_signing", "key_management"):
        adjustment -= 2
    elif role in ("authentication", "vpn"):
        adjustment -= 1

    # Compute final deadline
    deadline = base_deadline + adjustment

    # Clamp to reasonable range
    min_deadline = CURRENT_YEAR + 1
    max_deadline = scenario.quantum_arrival_max

    return max(min_deadline, min(deadline, max_deadline))


def _compute_basic_priority(system: System) -> int:
    """
    Compute a basic priority score without full risk assessment.

    Used when risk_assessment is not provided.
    """
    score = 50  # Base score

    # Adjust for sensitivity
    sensitivity = system.data_sensitivity.lower()
    if sensitivity == "critical":
        score += 25
    elif sensitivity == "high":
        score += 15
    elif sensitivity == "low":
        score -= 15

    # Adjust for data lifetime
    if system.data_lifetime_years >= 20:
        score += 15
    elif system.data_lifetime_years >= 10:
        score += 5

    # Adjust for exposure
    if system.internet_exposed:
        score += 10

    # Adjust for role
    role = system.system_role.lower()
    if role in ("pki", "code_signing", "key_management"):
        score += 15
    elif role in ("authentication", "vpn", "api_gateway"):
        score += 10

    # Already PQ-ready reduces priority
    if system.is_pq_ready:
        score -= 40

    return max(0, min(100, score))


def _generate_rationale(
    system: System,
    target_kem: str,
    target_sig: str,
    mode: str,
    migrate_by: int,
) -> str:
    """Generate human-readable rationale for the recommendation."""
    parts = []

    sensitivity = system.data_sensitivity.lower()
    lifetime = system.data_lifetime_years
    role = system.system_role.lower()

    # Algorithm selection rationale
    if "SLH-DSA" in target_sig:
        parts.append(
            f"SLH-DSA recommended for {role} role due to conservative security "
            "assumptions and long-term trust requirements."
        )
    elif "1024" in target_kem or "87" in target_sig:
        parts.append(
            "Higher security levels selected due to critical sensitivity "
            f"and {lifetime}-year data retention requirement."
        )

    # Mode rationale
    if mode == "hybrid":
        parts.append(
            "Hybrid mode recommended for backward compatibility "
            "with legacy systems during transition."
        )
    else:
        parts.append(
            "Pure post-quantum mode recommended for maximum "
            "long-term security."
        )

    # Timeline rationale
    if migrate_by <= 2028:
        parts.append(
            f"Early migration by {migrate_by} recommended due to "
            "high criticality and harvest-now-decrypt-later risk."
        )
    elif migrate_by <= 2030:
        parts.append(
            f"Migration by {migrate_by} aligns with NSM-10 deadlines "
            "for high-sensitivity systems."
        )
    else:
        parts.append(
            f"Migration by {migrate_by} provides adequate protection "
            "within baseline quantum arrival timeline."
        )

    return " ".join(parts)


def get_algorithm_info(algorithm: str) -> Dict[str, Any]:
    """
    Get performance and sizing information for a PQC algorithm.

    Args:
        algorithm: Algorithm name (e.g., 'ML-KEM-768')

    Returns:
        Dictionary with algorithm characteristics
    """
    # Strip hybrid prefix if present
    base_algo = algorithm.split("+")[-1] if "+" in algorithm else algorithm

    info: Dict[str, Any] = {
        "name": algorithm,
        "base_algorithm": base_algo,
        "is_hybrid": "+" in algorithm,
    }

    # Add overhead info if available
    if base_algo in PQC_COMPUTATIONAL_OVERHEAD:
        info["computational_overhead"] = PQC_COMPUTATIONAL_OVERHEAD[base_algo]

    if base_algo in PQC_SIZE_FACTORS:
        info["size_factors"] = PQC_SIZE_FACTORS[base_algo]

    # Add algorithm family info
    if "ML-KEM" in base_algo:
        info["family"] = "ML-KEM (FIPS 203)"
        info["type"] = "Key Encapsulation Mechanism"
    elif "ML-DSA" in base_algo:
        info["family"] = "ML-DSA (FIPS 204)"
        info["type"] = "Digital Signature"
    elif "SLH-DSA" in base_algo:
        info["family"] = "SLH-DSA (FIPS 205)"
        info["type"] = "Digital Signature (stateless hash-based)"
        info["note"] = "Conservative security assumptions; larger signatures but minimal cryptographic assumptions"

    return info


def estimate_migration_effort(
    recommendations: List[MigrationRecommendation],
) -> Dict[str, Any]:
    """
    Estimate aggregate migration effort from recommendations.

    Args:
        recommendations: List of migration recommendations

    Returns:
        Effort estimation summary
    """
    total_systems = len(recommendations)
    if total_systems == 0:
        return {"total_systems": 0}

    # Count by mode
    hybrid_count = sum(1 for r in recommendations if r.mode == "hybrid")
    pure_pq_count = total_systems - hybrid_count

    # Count by deadline year
    by_year: Dict[int, int] = {}
    for r in recommendations:
        by_year[r.migrate_by_year] = by_year.get(r.migrate_by_year, 0) + 1

    # Count by priority tier
    high_priority = sum(1 for r in recommendations if r.priority_score >= 70)
    medium_priority = sum(1 for r in recommendations if 40 <= r.priority_score < 70)
    low_priority = sum(1 for r in recommendations if r.priority_score < 40)

    return {
        "total_systems": total_systems,
        "hybrid_migrations": hybrid_count,
        "pure_pq_migrations": pure_pq_count,
        "by_deadline_year": dict(sorted(by_year.items())),
        "priority_distribution": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        },
    }
