"""
Quantum PQC Migration Toolkit

A toolkit for assessing and planning organizational migration from classical
public-key cryptography to post-quantum cryptographic algorithms.

This library implements a simplified, parameterized version of Monte Carlo
supply-chain risk models for practitioners, using parameters aligned with
NIST PQC FIPS profiles (FIPS 203-205) and empirical breach data.
"""

from quantum_pqc_migration_toolkit.models import System, Scenario, MigrationRecommendation
from quantum_pqc_migration_toolkit.risk import compute_pq_risk, compute_inventory_risk
from quantum_pqc_migration_toolkit.planner import recommend_migration, plan_inventory_migration
from quantum_pqc_migration_toolkit.simulate import run_monte_carlo, compare_strategies
from quantum_pqc_migration_toolkit.io import load_inventory, write_report

__version__ = "0.1.0"
__all__ = [
    "System",
    "Scenario",
    "MigrationRecommendation",
    "compute_pq_risk",
    "compute_inventory_risk",
    "recommend_migration",
    "plan_inventory_migration",
    "run_monte_carlo",
    "compare_strategies",
    "load_inventory",
    "write_report",
]
