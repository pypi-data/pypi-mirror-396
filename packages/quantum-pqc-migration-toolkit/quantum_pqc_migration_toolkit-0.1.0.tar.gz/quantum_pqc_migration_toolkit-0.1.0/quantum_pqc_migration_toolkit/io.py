"""
I/O Functions for PQC Migration Toolkit

Functions for loading inventory files and writing assessment reports.
Supports YAML and JSON formats.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import yaml

from quantum_pqc_migration_toolkit.models import System, RiskAssessment, MigrationRecommendation


def load_inventory(path: Union[str, Path]) -> List[System]:
    """
    Load a cryptographic inventory from a YAML or JSON file.

    Args:
        path: Path to the inventory file

    Returns:
        List of System objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {path}")

    content = path.read_text()

    # Parse based on file extension
    if path.suffix.lower() in (".yaml", ".yml"):
        data = yaml.safe_load(content)
    elif path.suffix.lower() == ".json":
        data = json.loads(content)
    else:
        # Try YAML first, then JSON
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            data = json.loads(content)

    return parse_inventory_data(data)


def parse_inventory_data(data: Dict[str, Any]) -> List[System]:
    """
    Parse inventory data dictionary into System objects.

    Args:
        data: Dictionary with 'systems' key containing list of system dicts

    Returns:
        List of System objects
    """
    if not isinstance(data, dict):
        raise ValueError("Inventory data must be a dictionary with 'systems' key")

    systems_data = data.get("systems", data.get("inventory", []))

    if not isinstance(systems_data, list):
        raise ValueError("Systems must be a list")

    systems = []
    for i, sys_data in enumerate(systems_data):
        try:
            system = _parse_system(sys_data)
            systems.append(system)
        except Exception as e:
            raise ValueError(f"Error parsing system at index {i}: {e}")

    return systems


def _parse_system(data: Dict[str, Any]) -> System:
    """Parse a single system dictionary into a System object."""
    if not isinstance(data, dict):
        raise ValueError("System data must be a dictionary")

    if "name" not in data:
        raise ValueError("System must have a 'name' field")

    return System(
        name=data["name"],
        sector=data.get("sector", "default"),
        current_algos=data.get("current_algos", data.get("algorithms", ["RSA-2048"])),
        tls_versions=data.get("tls_versions", data.get("tls", ["TLS1.2"])),
        data_lifetime_years=data.get("data_lifetime_years", data.get("data_lifetime", 10)),
        data_sensitivity=data.get("data_sensitivity", data.get("sensitivity", "medium")),
        internet_exposed=data.get("internet_exposed", data.get("exposed", False)),
        vendor_type=data.get("vendor_type", data.get("vendor", "first_party")),
        system_role=data.get("system_role", data.get("role", "default")),
        has_qkd=data.get("has_qkd", False),
        description=data.get("description", ""),
        tags=data.get("tags", []),
    )


def write_report(
    systems: List[System],
    assessments: List[RiskAssessment],
    recommendations: List[MigrationRecommendation],
    path_json: Optional[Union[str, Path]] = None,
    path_csv: Optional[Union[str, Path]] = None,
    simulation_results: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Write assessment report to JSON and/or CSV files.

    Args:
        systems: List of assessed systems
        assessments: Risk assessment results
        recommendations: Migration recommendations
        path_json: Optional path for JSON output
        path_csv: Optional path for CSV output
        simulation_results: Optional simulation results to include

    Returns:
        The report data dictionary
    """
    # Build report structure
    report = {
        "metadata": {
            "version": "0.1.0",
            "generated_at": _get_timestamp(),
            "total_systems": len(systems),
        },
        "summary": _compute_summary(assessments),
        "systems": [s.to_dict() for s in systems],
        "assessments": [a.to_dict() for a in assessments],
        "recommendations": [r.to_dict() for r in recommendations],
    }

    if simulation_results:
        report["simulation"] = simulation_results

    # Write JSON
    if path_json:
        path_json = Path(path_json)
        path_json.write_text(json.dumps(report, indent=2))

    # Write CSV
    if path_csv:
        _write_csv_report(assessments, recommendations, path_csv)

    return report


def _compute_summary(assessments: List[RiskAssessment]) -> Dict[str, Any]:
    """Compute summary statistics from assessments."""
    if not assessments:
        return {"total_systems": 0}

    scores = [a.pq_risk_score for a in assessments]
    priorities = [a.priority_score for a in assessments]

    # Count by crypto status
    status_counts: Dict[str, int] = {}
    for a in assessments:
        status = a.crypto_status
        status_counts[status] = status_counts.get(status, 0) + 1

    # Count by priority tier
    high_priority = sum(1 for p in priorities if p >= 70)
    medium_priority = sum(1 for p in priorities if 40 <= p < 70)
    low_priority = sum(1 for p in priorities if p < 40)

    return {
        "total_systems": len(assessments),
        "mean_risk_score": round(sum(scores) / len(scores), 4),
        "max_risk_score": round(max(scores), 4),
        "min_risk_score": round(min(scores), 4),
        "high_priority_count": high_priority,
        "medium_priority_count": medium_priority,
        "low_priority_count": low_priority,
        "crypto_status_distribution": status_counts,
    }


def _write_csv_report(
    assessments: List[RiskAssessment],
    recommendations: List[MigrationRecommendation],
    path: Union[str, Path],
) -> None:
    """Write CSV report combining assessments and recommendations."""
    import csv

    path = Path(path)

    # Create lookup for recommendations
    rec_lookup = {r.system_name: r for r in recommendations}

    rows = []
    for assessment in assessments:
        rec = rec_lookup.get(assessment.system_name)
        row = {
            "system_name": assessment.system_name,
            "pq_risk_score": round(assessment.pq_risk_score, 4),
            "priority_score": assessment.priority_score,
            "crypto_status": assessment.crypto_status,
            "vulnerability_window_years": round(assessment.window_of_vulnerability_years, 2),
            "target_kem": rec.target_kem if rec else "",
            "target_sig": rec.target_sig if rec else "",
            "mode": rec.mode if rec else "",
            "migrate_by": rec.migrate_by_year if rec else "",
        }
        rows.append(row)

    # Sort by priority (descending)
    rows.sort(key=lambda x: x["priority_score"], reverse=True)

    # Write CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def _get_timestamp() -> str:
    """Get ISO format timestamp."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def create_sample_inventory() -> str:
    """
    Generate a sample inventory YAML for demonstration.

    Returns:
        YAML string with sample systems
    """
    sample = {
        "systems": [
            {
                "name": "ehr_database",
                "sector": "healthcare",
                "current_algos": ["RSA-2048", "ECDSA-P256"],
                "tls_versions": ["TLS1.2", "TLS1.3"],
                "data_lifetime_years": 20,
                "data_sensitivity": "high",
                "internet_exposed": False,
                "vendor_type": "first_party",
                "system_role": "database",
                "has_qkd": False,
                "description": "Electronic Health Records database",
            },
            {
                "name": "patient_portal",
                "sector": "healthcare",
                "current_algos": ["RSA-2048"],
                "tls_versions": ["TLS1.2"],
                "data_lifetime_years": 10,
                "data_sensitivity": "medium",
                "internet_exposed": True,
                "vendor_type": "third_party",
                "system_role": "web_server",
                "has_qkd": False,
                "description": "Patient-facing web portal",
            },
            {
                "name": "pki_root_ca",
                "sector": "healthcare",
                "current_algos": ["RSA-4096"],
                "tls_versions": [],
                "data_lifetime_years": 30,
                "data_sensitivity": "critical",
                "internet_exposed": False,
                "vendor_type": "first_party",
                "system_role": "pki",
                "has_qkd": False,
                "description": "Root Certificate Authority",
            },
            {
                "name": "payment_gateway",
                "sector": "financial",
                "current_algos": ["ECDSA-P256", "RSA-2048"],
                "tls_versions": ["TLS1.2", "TLS1.3"],
                "data_lifetime_years": 7,
                "data_sensitivity": "high",
                "internet_exposed": True,
                "vendor_type": "tier1_vendor",
                "system_role": "api_gateway",
                "has_qkd": False,
                "description": "Payment processing integration",
            },
            {
                "name": "internal_auth",
                "sector": "technology",
                "current_algos": ["RSA-2048", "Ed25519"],
                "tls_versions": ["TLS1.3"],
                "data_lifetime_years": 5,
                "data_sensitivity": "high",
                "internet_exposed": False,
                "vendor_type": "first_party",
                "system_role": "authentication",
                "has_qkd": False,
                "description": "Internal authentication service",
            },
            {
                "name": "backup_storage",
                "sector": "technology",
                "current_algos": ["RSA-2048"],
                "tls_versions": ["TLS1.2"],
                "data_lifetime_years": 15,
                "data_sensitivity": "medium",
                "internet_exposed": False,
                "vendor_type": "saas",
                "system_role": "internal",
                "has_qkd": False,
                "description": "Cloud backup service",
            },
            {
                "name": "code_signing",
                "sector": "technology",
                "current_algos": ["RSA-4096"],
                "tls_versions": [],
                "data_lifetime_years": 25,
                "data_sensitivity": "critical",
                "internet_exposed": False,
                "vendor_type": "first_party",
                "system_role": "code_signing",
                "has_qkd": False,
                "description": "Software code signing infrastructure",
            },
            {
                "name": "vpn_gateway",
                "sector": "technology",
                "current_algos": ["ECDH-P256", "ECDSA-P256"],
                "tls_versions": ["TLS1.3"],
                "data_lifetime_years": 5,
                "data_sensitivity": "medium",
                "internet_exposed": True,
                "vendor_type": "first_party",
                "system_role": "vpn",
                "has_qkd": False,
                "description": "Corporate VPN gateway",
            },
        ]
    }

    return yaml.dump(sample, default_flow_style=False, sort_keys=False)
