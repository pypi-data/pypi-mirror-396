"""
Data Models for PQC Migration Assessment

Core data structures for representing systems, scenarios, and migration
recommendations in the post-quantum cryptography migration workflow.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class CryptoStatus(Enum):
    """Classification of a system's cryptographic posture."""
    CLASSICAL = "classical"        # Only quantum-vulnerable algorithms
    HYBRID = "hybrid"              # Mix of classical and PQC
    PQC = "pqc"                    # Fully post-quantum
    UNKNOWN = "unknown"            # Cannot determine


class DataSensitivity(Enum):
    """Data sensitivity classification levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AdoptionStrategy(Enum):
    """PQC adoption timing strategies."""
    EARLY = "early"       # Aggressive early adoption
    BASELINE = "baseline" # Standard NSM-10 aligned timeline
    LATE = "late"         # Delayed adoption


@dataclass
class System:
    """
    Represents a system or service in the cryptographic inventory.

    Attributes:
        name: Unique identifier for the system
        sector: Industry sector (e.g., healthcare, financial)
        current_algos: List of cryptographic algorithms in use
        tls_versions: TLS versions supported
        data_lifetime_years: How long data must remain confidential
        data_sensitivity: Classification of data sensitivity
        internet_exposed: Whether system is internet-facing
        vendor_type: Position in supply chain (first_party, third_party, etc.)
        system_role: Functional role (pki, authentication, etc.)
        has_qkd: Whether quantum key distribution is available
        description: Optional description of the system
        tags: Optional metadata tags
    """
    name: str
    sector: str = "default"
    current_algos: List[str] = field(default_factory=lambda: ["RSA-2048"])
    tls_versions: List[str] = field(default_factory=lambda: ["TLS1.2"])
    data_lifetime_years: int = 10
    data_sensitivity: str = "medium"
    internet_exposed: bool = False
    vendor_type: str = "first_party"
    system_role: str = "default"
    has_qkd: bool = False
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and normalize inputs."""
        # Normalize string inputs to lowercase
        self.sector = self.sector.lower()
        self.data_sensitivity = self.data_sensitivity.lower()
        self.vendor_type = self.vendor_type.lower()
        self.system_role = self.system_role.lower()

        # Ensure current_algos is a list
        if isinstance(self.current_algos, str):
            self.current_algos = [self.current_algos]

        # Ensure tls_versions is a list
        if isinstance(self.tls_versions, str):
            self.tls_versions = [self.tls_versions]

    @property
    def crypto_status(self) -> CryptoStatus:
        """Determine the cryptographic status of this system."""
        from quantum_pqc_migration_toolkit.risk_params import (
            QUANTUM_VULNERABLE_ALGORITHMS,
            PQC_ALGORITHMS,
            HYBRID_ALGORITHMS,
        )

        algos_upper = {a.upper() for a in self.current_algos}

        has_classical = bool(algos_upper & {a.upper() for a in QUANTUM_VULNERABLE_ALGORITHMS})
        has_pqc = bool(algos_upper & {a.upper() for a in PQC_ALGORITHMS})
        has_hybrid = bool(algos_upper & {a.upper() for a in HYBRID_ALGORITHMS})

        if has_hybrid or (has_classical and has_pqc):
            return CryptoStatus.HYBRID
        elif has_pqc and not has_classical:
            return CryptoStatus.PQC
        elif has_classical:
            return CryptoStatus.CLASSICAL
        else:
            return CryptoStatus.UNKNOWN

    @property
    def is_pq_ready(self) -> bool:
        """Check if system is already quantum-resistant."""
        return self.crypto_status in (CryptoStatus.PQC, CryptoStatus.HYBRID)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "sector": self.sector,
            "current_algos": self.current_algos,
            "tls_versions": self.tls_versions,
            "data_lifetime_years": self.data_lifetime_years,
            "data_sensitivity": self.data_sensitivity,
            "internet_exposed": self.internet_exposed,
            "vendor_type": self.vendor_type,
            "system_role": self.system_role,
            "has_qkd": self.has_qkd,
            "description": self.description,
            "tags": self.tags,
            "crypto_status": self.crypto_status.value,
            "is_pq_ready": self.is_pq_ready,
        }


@dataclass
class Scenario:
    """
    Represents a simulation scenario for risk assessment.

    Attributes:
        quantum_arrival_min: Earliest year CRQC might arrive
        quantum_arrival_max: Latest year for CRQC arrival window
        quantum_arrival_mode: Most likely year for CRQC arrival
        adoption_strategy: PQC adoption timing strategy
        n_runs: Number of Monte Carlo simulation runs
        name: Optional scenario name
    """
    quantum_arrival_min: int = 2030
    quantum_arrival_max: int = 2035
    quantum_arrival_mode: int = 2032
    adoption_strategy: str = "baseline"
    n_runs: int = 1000
    name: str = "default"

    def __post_init__(self):
        """Validate scenario parameters."""
        if self.quantum_arrival_min > self.quantum_arrival_max:
            raise ValueError("quantum_arrival_min must be <= quantum_arrival_max")
        if not (self.quantum_arrival_min <= self.quantum_arrival_mode <= self.quantum_arrival_max):
            raise ValueError("quantum_arrival_mode must be within arrival range")
        if self.n_runs < 1:
            raise ValueError("n_runs must be positive")
        self.adoption_strategy = self.adoption_strategy.lower()

    @classmethod
    def optimistic(cls) -> "Scenario":
        """Create an optimistic (early quantum) scenario."""
        return cls(
            quantum_arrival_min=2028,
            quantum_arrival_max=2030,
            quantum_arrival_mode=2029,
            adoption_strategy="early",
            name="optimistic",
        )

    @classmethod
    def baseline(cls) -> "Scenario":
        """Create a baseline scenario aligned with NSM-10."""
        return cls(
            quantum_arrival_min=2030,
            quantum_arrival_max=2035,
            quantum_arrival_mode=2032,
            adoption_strategy="baseline",
            name="baseline",
        )

    @classmethod
    def conservative(cls) -> "Scenario":
        """Create a conservative (later quantum) scenario."""
        return cls(
            quantum_arrival_min=2035,
            quantum_arrival_max=2040,
            quantum_arrival_mode=2037,
            adoption_strategy="baseline",
            name="conservative",
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "quantum_arrival_min": self.quantum_arrival_min,
            "quantum_arrival_max": self.quantum_arrival_max,
            "quantum_arrival_mode": self.quantum_arrival_mode,
            "adoption_strategy": self.adoption_strategy,
            "n_runs": self.n_runs,
            "name": self.name,
        }


@dataclass
class MigrationRecommendation:
    """
    Migration recommendation for a specific system.

    Attributes:
        system_name: Name of the system
        target_kem: Recommended key encapsulation mechanism
        target_sig: Recommended signature algorithm
        mode: Migration mode (pure_pq or hybrid)
        migrate_by_year: Recommended migration deadline
        priority_score: Priority score (0-100)
        rationale: Explanation for the recommendation
    """
    system_name: str
    target_kem: str
    target_sig: str
    mode: str  # "pure_pq" or "hybrid"
    migrate_by_year: int
    priority_score: int
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "system_name": self.system_name,
            "target_kem": self.target_kem,
            "target_sig": self.target_sig,
            "mode": self.mode,
            "migrate_by_year": self.migrate_by_year,
            "priority_score": self.priority_score,
            "rationale": self.rationale,
        }


@dataclass
class RiskAssessment:
    """
    Risk assessment results for a system.

    Attributes:
        system_name: Name of the assessed system
        pq_risk_score: Quantum-vulnerability risk score (0-1)
        priority_score: Migration priority score (0-100)
        window_of_vulnerability_years: Years of potential exposure
        crypto_status: Current cryptographic posture
        factors: Breakdown of contributing risk factors
    """
    system_name: str
    pq_risk_score: float
    priority_score: int
    window_of_vulnerability_years: float
    crypto_status: str
    factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "system_name": self.system_name,
            "pq_risk_score": round(self.pq_risk_score, 4),
            "priority_score": self.priority_score,
            "window_of_vulnerability_years": round(self.window_of_vulnerability_years, 2),
            "crypto_status": self.crypto_status,
            "factors": {k: round(v, 4) for k, v in self.factors.items()},
        }


@dataclass
class SimulationResult:
    """
    Results from Monte Carlo simulation.

    Attributes:
        strategy: Adoption strategy simulated
        n_runs: Number of simulation runs
        mean_risk: Mean aggregate risk score
        percentiles: Risk percentile values
        per_system_stats: Per-system statistics
    """
    strategy: str
    n_runs: int
    mean_risk: float
    std_risk: float
    percentiles: Dict[int, float]
    per_system_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "strategy": self.strategy,
            "n_runs": self.n_runs,
            "mean_risk": round(self.mean_risk, 4),
            "std_risk": round(self.std_risk, 4),
            "percentiles": {str(k): round(v, 4) for k, v in self.percentiles.items()},
            "per_system_stats": self.per_system_stats,
        }
