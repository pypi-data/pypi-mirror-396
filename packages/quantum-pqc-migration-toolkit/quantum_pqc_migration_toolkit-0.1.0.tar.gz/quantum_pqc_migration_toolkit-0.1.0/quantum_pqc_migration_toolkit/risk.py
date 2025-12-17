"""
Risk Assessment Engine for PQC Migration

Implements the core risk scoring algorithm for assessing quantum-vulnerability
of cryptographic systems. The scoring formula incorporates:

- Algorithm vulnerability classification
- Data lifetime and quantum arrival timeline overlap
- Sector baseline breach rates
- Supply chain position and exposure factors
- Adoption strategy timing multipliers

The parameters are derived from empirical research including NIST FIPS 203-205
specifications, DBIR sector statistics, and NSM-10 implementation timelines.
"""

from typing import List, Dict, Any, Optional

from quantum_pqc_migration_toolkit.models import (
    System,
    Scenario,
    RiskAssessment,
    CryptoStatus,
)
from quantum_pqc_migration_toolkit.risk_params import (
    CURRENT_YEAR,
    SECTOR_BASELINES,
    SUPPLY_CHAIN_MULTIPLIERS,
    SYSTEM_ROLE_MULTIPLIERS,
    ADOPTION_STRATEGY_MULTIPLIERS,
    DATA_SENSITIVITY_WEIGHTS,
    INTERNET_EXPOSURE_MULTIPLIER,
    QKD_RESILIENCE_FACTOR,
    QUANTUM_VULNERABLE_ALGORITHMS,
    PQC_ALGORITHMS,
)


def compute_pq_risk(
    system: System,
    scenario: Optional[Scenario] = None,
) -> RiskAssessment:
    """
    Compute the post-quantum risk score for a system.

    The risk score reflects the probability of a quantum-enabled breach
    based on the system's cryptographic posture, data characteristics,
    and exposure factors.

    Args:
        system: The system to assess
        scenario: Optional scenario parameters (uses baseline if not provided)

    Returns:
        RiskAssessment with scores and contributing factors
    """
    if scenario is None:
        scenario = Scenario.baseline()

    # Initialize factors dictionary for transparency
    factors: Dict[str, float] = {}

    # Step 1: Determine crypto status and base vulnerability
    crypto_status = system.crypto_status
    factors["crypto_status_factor"] = _get_crypto_status_factor(crypto_status)

    # Step 2: Compute window of vulnerability
    vulnerability_window = _compute_vulnerability_window(
        system.data_lifetime_years,
        scenario.quantum_arrival_min,
        scenario.quantum_arrival_max,
    )
    factors["vulnerability_window"] = vulnerability_window

    # Normalize to overlap factor (0-1)
    window_span = scenario.quantum_arrival_max - scenario.quantum_arrival_min + 5
    overlap_factor = min(1.0, max(0.0, vulnerability_window / window_span))
    factors["overlap_factor"] = overlap_factor

    # Step 3: Get sector baseline
    sector_base = SECTOR_BASELINES.get(system.sector, SECTOR_BASELINES["default"])
    factors["sector_baseline"] = sector_base

    # Step 4: Compute exposure multiplier
    exposure_mult = 1.0
    if system.internet_exposed:
        exposure_mult *= INTERNET_EXPOSURE_MULTIPLIER
    factors["exposure_multiplier"] = exposure_mult

    # Step 5: Get supply chain multiplier
    supply_chain_mult = SUPPLY_CHAIN_MULTIPLIERS.get(
        system.vendor_type, SUPPLY_CHAIN_MULTIPLIERS["default"]
    )
    factors["supply_chain_multiplier"] = supply_chain_mult

    # Step 6: Get system role multiplier
    role_mult = SYSTEM_ROLE_MULTIPLIERS.get(
        system.system_role, SYSTEM_ROLE_MULTIPLIERS["default"]
    )
    factors["role_multiplier"] = role_mult

    # Step 7: Get data sensitivity weight
    sensitivity_weight = DATA_SENSITIVITY_WEIGHTS.get(
        system.data_sensitivity, DATA_SENSITIVITY_WEIGHTS["medium"]
    )
    factors["sensitivity_weight"] = sensitivity_weight

    # Step 8: Get adoption strategy multiplier
    strategy_mult = ADOPTION_STRATEGY_MULTIPLIERS.get(
        scenario.adoption_strategy, ADOPTION_STRATEGY_MULTIPLIERS["baseline"]
    )
    factors["strategy_multiplier"] = strategy_mult

    # Step 9: Apply QKD resilience if available
    qkd_factor = QKD_RESILIENCE_FACTOR if system.has_qkd else 1.0
    factors["qkd_factor"] = qkd_factor

    # Step 10: Combine factors into base risk probability
    base_probability = (
        sector_base
        * overlap_factor
        * exposure_mult
        * supply_chain_mult
        * role_mult
        * sensitivity_weight
    )

    # Apply crypto status reduction (PQC/hybrid systems have lower risk)
    crypto_adjusted = base_probability * factors["crypto_status_factor"]

    # Apply adoption timing multiplier
    strategy_adjusted = crypto_adjusted * strategy_mult

    # Apply QKD resilience
    final_probability = strategy_adjusted * qkd_factor

    # Clamp to [0, 1]
    pq_risk_score = min(1.0, max(0.0, final_probability))

    # Convert to priority score (0-100)
    priority_score = int(round(100 * pq_risk_score))

    return RiskAssessment(
        system_name=system.name,
        pq_risk_score=pq_risk_score,
        priority_score=priority_score,
        window_of_vulnerability_years=vulnerability_window,
        crypto_status=crypto_status.value,
        factors=factors,
    )


def compute_inventory_risk(
    systems: List[System],
    scenario: Optional[Scenario] = None,
) -> List[RiskAssessment]:
    """
    Compute risk assessments for all systems in an inventory.

    Args:
        systems: List of systems to assess
        scenario: Optional scenario parameters

    Returns:
        List of RiskAssessment objects, sorted by priority (descending)
    """
    assessments = [compute_pq_risk(system, scenario) for system in systems]

    # Sort by priority score descending
    assessments.sort(key=lambda a: a.priority_score, reverse=True)

    return assessments


def compute_aggregate_risk(
    assessments: List[RiskAssessment],
    method: str = "weighted_mean",
) -> float:
    """
    Compute aggregate risk score across multiple assessments.

    Args:
        assessments: List of risk assessments
        method: Aggregation method ('mean', 'max', 'weighted_mean')

    Returns:
        Aggregate risk score (0-1)
    """
    if not assessments:
        return 0.0

    scores = [a.pq_risk_score for a in assessments]
    priorities = [a.priority_score for a in assessments]

    if method == "max":
        return max(scores)
    elif method == "weighted_mean":
        # Weight by priority score
        total_weight = sum(priorities)
        if total_weight == 0:
            return sum(scores) / len(scores)
        return sum(s * p for s, p in zip(scores, priorities)) / total_weight
    else:  # mean
        return sum(scores) / len(scores)


def _get_crypto_status_factor(status: CryptoStatus) -> float:
    """
    Get risk reduction factor based on cryptographic status.

    Returns:
        Multiplier (1.0 for classical, reduced for PQC/hybrid)
    """
    if status == CryptoStatus.PQC:
        return 0.1  # 90% risk reduction for fully PQC systems
    elif status == CryptoStatus.HYBRID:
        return 0.5  # 50% risk reduction for hybrid systems
    else:
        return 1.0  # Full risk for classical/unknown


def _compute_vulnerability_window(
    data_lifetime_years: int,
    quantum_arrival_min: int,
    quantum_arrival_max: int,
) -> float:
    """
    Compute the window of vulnerability in years.

    This represents the overlap between when data needs protection
    and when quantum computers might be available to break it.

    Args:
        data_lifetime_years: How long data must remain confidential
        quantum_arrival_min: Earliest quantum threat year
        quantum_arrival_max: Latest quantum threat year

    Returns:
        Years of potential vulnerability exposure
    """
    # Data needs protection until this year
    data_expiry_year = CURRENT_YEAR + data_lifetime_years

    # If data expires before quantum arrives, minimal risk
    if data_expiry_year <= quantum_arrival_min:
        return 0.0

    # Compute overlap with quantum window
    # Consider "harvest now, decrypt later" attacks
    overlap_start = max(CURRENT_YEAR, quantum_arrival_min)
    overlap_end = data_expiry_year

    # The vulnerability window is how long data is exposed during quantum era
    vulnerability_years = max(0.0, overlap_end - overlap_start)

    return vulnerability_years


def classify_priority_tier(priority_score: int) -> str:
    """
    Classify a priority score into migration urgency tier.

    Args:
        priority_score: Score from 0-100

    Returns:
        Tier classification string
    """
    if priority_score >= 80:
        return "critical"
    elif priority_score >= 60:
        return "high"
    elif priority_score >= 40:
        return "medium"
    elif priority_score >= 20:
        return "low"
    else:
        return "minimal"


def get_risk_summary(assessments: List[RiskAssessment]) -> Dict[str, Any]:
    """
    Generate a summary of risk assessments.

    Args:
        assessments: List of risk assessments

    Returns:
        Summary statistics dictionary
    """
    if not assessments:
        return {"total_systems": 0}

    scores = [a.pq_risk_score for a in assessments]
    priorities = [a.priority_score for a in assessments]

    # Tier distribution
    tier_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "minimal": 0,
    }
    for p in priorities:
        tier = classify_priority_tier(p)
        tier_counts[tier] += 1

    # Crypto status distribution
    status_counts: Dict[str, int] = {}
    for a in assessments:
        status_counts[a.crypto_status] = status_counts.get(a.crypto_status, 0) + 1

    return {
        "total_systems": len(assessments),
        "mean_risk": sum(scores) / len(scores),
        "max_risk": max(scores),
        "min_risk": min(scores),
        "mean_priority": sum(priorities) / len(priorities),
        "tier_distribution": tier_counts,
        "crypto_status_distribution": status_counts,
    }
