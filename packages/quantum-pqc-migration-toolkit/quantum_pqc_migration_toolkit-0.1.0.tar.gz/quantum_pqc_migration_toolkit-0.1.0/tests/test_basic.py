"""Basic tests for quantum_pqc_migration_toolkit."""

import pytest
from quantum_pqc_migration_toolkit.models import System, Scenario, CryptoStatus
from quantum_pqc_migration_toolkit.risk import compute_pq_risk, compute_inventory_risk
from quantum_pqc_migration_toolkit.planner import recommend_migration, plan_inventory_migration
from quantum_pqc_migration_toolkit.io import parse_inventory_data, create_sample_inventory


class TestModels:
    """Test data model classes."""

    def test_system_creation(self):
        """Test System dataclass creation and defaults."""
        system = System(name="test_system")
        assert system.name == "test_system"
        assert system.sector == "default"
        assert system.data_sensitivity == "medium"
        assert not system.internet_exposed

    def test_system_crypto_status_classical(self):
        """Test crypto status detection for classical algorithms."""
        system = System(
            name="classical_system",
            current_algos=["RSA-2048", "ECDSA-P256"]
        )
        assert system.crypto_status == CryptoStatus.CLASSICAL
        assert not system.is_pq_ready

    def test_system_crypto_status_pqc(self):
        """Test crypto status detection for PQC algorithms."""
        system = System(
            name="pqc_system",
            current_algos=["ML-KEM-768", "ML-DSA-65"]
        )
        assert system.crypto_status == CryptoStatus.PQC
        assert system.is_pq_ready

    def test_system_crypto_status_hybrid(self):
        """Test crypto status detection for hybrid setups."""
        system = System(
            name="hybrid_system",
            current_algos=["RSA-2048", "ML-KEM-768"]
        )
        assert system.crypto_status == CryptoStatus.HYBRID
        assert system.is_pq_ready

    def test_scenario_baseline(self):
        """Test baseline scenario creation."""
        scenario = Scenario.baseline()
        assert scenario.quantum_arrival_min == 2030
        assert scenario.quantum_arrival_max == 2035
        assert scenario.adoption_strategy == "baseline"

    def test_scenario_validation(self):
        """Test scenario parameter validation."""
        with pytest.raises(ValueError):
            Scenario(quantum_arrival_min=2035, quantum_arrival_max=2030)


class TestRiskAssessment:
    """Test risk assessment functions."""

    def test_compute_pq_risk_basic(self):
        """Test basic risk computation."""
        system = System(
            name="test",
            current_algos=["RSA-2048"],
            data_lifetime_years=10,
            data_sensitivity="medium",
        )
        assessment = compute_pq_risk(system)

        assert 0 <= assessment.pq_risk_score <= 1
        assert 0 <= assessment.priority_score <= 100
        assert assessment.system_name == "test"

    def test_high_sensitivity_higher_risk(self):
        """Test that high sensitivity systems have higher risk."""
        low_sens = System(
            name="low",
            current_algos=["RSA-2048"],
            data_sensitivity="low",
            data_lifetime_years=15,  # Long enough to overlap with quantum window
        )
        high_sens = System(
            name="high",
            current_algos=["RSA-2048"],
            data_sensitivity="high",
            data_lifetime_years=15,  # Long enough to overlap with quantum window
        )

        low_assessment = compute_pq_risk(low_sens)
        high_assessment = compute_pq_risk(high_sens)

        assert high_assessment.pq_risk_score > low_assessment.pq_risk_score

    def test_pqc_systems_lower_risk(self):
        """Test that PQC-ready systems have lower risk."""
        classical = System(
            name="classical",
            current_algos=["RSA-2048"],
            data_sensitivity="high",
        )
        pqc = System(
            name="pqc",
            current_algos=["ML-KEM-768", "ML-DSA-65"],
            data_sensitivity="high",
        )

        classical_assessment = compute_pq_risk(classical)
        pqc_assessment = compute_pq_risk(pqc)

        assert pqc_assessment.pq_risk_score < classical_assessment.pq_risk_score

    def test_internet_exposed_higher_risk(self):
        """Test that internet-exposed systems have higher risk."""
        internal = System(
            name="internal",
            current_algos=["RSA-2048"],
            internet_exposed=False,
        )
        exposed = System(
            name="exposed",
            current_algos=["RSA-2048"],
            internet_exposed=True,
        )

        internal_assessment = compute_pq_risk(internal)
        exposed_assessment = compute_pq_risk(exposed)

        assert exposed_assessment.pq_risk_score > internal_assessment.pq_risk_score

    def test_inventory_risk_sorted(self):
        """Test that inventory risk returns sorted results."""
        systems = [
            System(name="low", data_sensitivity="low"),
            System(name="high", data_sensitivity="critical"),
            System(name="medium", data_sensitivity="medium"),
        ]

        assessments = compute_inventory_risk(systems)

        # Should be sorted by priority descending
        priorities = [a.priority_score for a in assessments]
        assert priorities == sorted(priorities, reverse=True)


class TestMigrationPlanning:
    """Test migration planning functions."""

    def test_recommend_migration_basic(self):
        """Test basic migration recommendation."""
        system = System(
            name="test",
            current_algos=["RSA-2048"],
            data_sensitivity="high",
        )

        rec = recommend_migration(system)

        assert rec.system_name == "test"
        assert "ML-KEM" in rec.target_kem
        assert "ML-DSA" in rec.target_sig or "SLH-DSA" in rec.target_sig
        assert rec.mode in ("pure_pq", "hybrid")
        assert 2026 <= rec.migrate_by_year <= 2040

    def test_critical_systems_earlier_deadline(self):
        """Test that critical systems get earlier deadlines."""
        low = System(name="low", data_sensitivity="low", data_lifetime_years=5)
        critical = System(name="critical", data_sensitivity="critical", data_lifetime_years=30)

        low_rec = recommend_migration(low)
        critical_rec = recommend_migration(critical)

        assert critical_rec.migrate_by_year < low_rec.migrate_by_year

    def test_pki_systems_get_conservative_algorithms(self):
        """Test that PKI systems get SLH-DSA for critical cases."""
        pki_system = System(
            name="root_ca",
            system_role="pki",
            data_sensitivity="critical",
            data_lifetime_years=30,
        )

        rec = recommend_migration(pki_system)

        # Should recommend SLH-DSA for signature due to conservative security
        assert "SLH-DSA" in rec.target_sig


class TestIO:
    """Test I/O functions."""

    def test_parse_inventory_data(self):
        """Test inventory data parsing."""
        data = {
            "systems": [
                {
                    "name": "system1",
                    "sector": "healthcare",
                    "current_algos": ["RSA-2048"],
                },
                {
                    "name": "system2",
                    "sector": "financial",
                },
            ]
        }

        systems = parse_inventory_data(data)

        assert len(systems) == 2
        assert systems[0].name == "system1"
        assert systems[0].sector == "healthcare"
        assert systems[1].name == "system2"
        assert systems[1].sector == "financial"

    def test_create_sample_inventory(self):
        """Test sample inventory generation."""
        sample = create_sample_inventory()

        assert isinstance(sample, str)
        assert "systems:" in sample
        assert "name:" in sample

    def test_parse_inventory_missing_name_raises(self):
        """Test that missing name field raises error."""
        data = {
            "systems": [
                {"sector": "healthcare"}  # Missing name
            ]
        }

        with pytest.raises(ValueError):
            parse_inventory_data(data)
