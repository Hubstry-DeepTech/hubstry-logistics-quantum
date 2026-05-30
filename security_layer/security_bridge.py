"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Security Bridge — Integrates PQC with the logistics data pipeline.

Ensures that all route plans, IoT telemetry, and sustainability
reports are cryptographically protected before transmission
to the fleet management dashboard.

Integrates with: Hubstry Security framework + IoT Protocol Hubstry.
"""

import json
import time
from typing import Any, Dict, List

from security_layer.pqc_wrapper import PQCWrapper


class SecurityBridge:
    """
    Bridges the PQC layer with the logistics pipeline.

    Responsibilities:
      - Encrypt route plans before fleet dispatch
      - Sign sustainability reports for audit trail
      - Protect IoT telemetry in transit
      - Maintain encryption session state
    """

    def __init__(self, seed: int = 42):
        self._pqc = PQCWrapper(seed=seed)
        self._session_id = f"SES-{int(time.time())}"
        self._encrypt_count = 0
        self._sign_count = 0
        self._audit_log: List[Dict] = []

    # ------------------------------------------------------------------
    # Route plan encryption
    # ------------------------------------------------------------------

    def encrypt_route_plan(self, routes: List[List[int]],
                          metadata: Dict = None) -> Dict:
        """
        Encrypt an optimized route plan for secure fleet dispatch.

        Args:
            routes: List of route lists (node indices).
            metadata: Optional extra context (vehicle IDs, timestamps).

        Returns:
            Dict with encrypted payload and verification info.
        """
        payload = {
            "routes": routes,
            "metadata": metadata or {},
            "session": self._session_id,
        }
        plaintext = json.dumps(payload, separators=(",", ":"))

        enc_result = self._pqc.encrypt(plaintext)
        sign_result = self._pqc.sign(plaintext)

        self._encrypt_count += 1
        self._log_audit("ENCRYPT_ROUTE", len(plaintext))

        return {
            "encrypted": enc_result,
            "signature": sign_result,
            "session_id": self._session_id,
            "timestamp": time.time(),
        }

    def decrypt_route_plan(self, encrypted_data: Dict) -> List[List[int]]:
        """
        Decrypt a previously encrypted route plan.

        Args:
            encrypted_data: Output from encrypt_route_plan().

        Returns:
            Original routes list.
        """
        enc = encrypted_data["encrypted"]
        plaintext = self._pqc.decrypt(
            enc["ciphertext_hex"], enc["nonce_hex"]
        )
        payload = json.loads(plaintext)
        return payload["routes"]

    # ------------------------------------------------------------------
    # Report signing
    # ------------------------------------------------------------------

    def sign_sustainability_report(self, report: Dict) -> Dict:
        """
        Sign a sustainability report for GDPR / EU ETS compliance.

        Args:
            report: KPI dictionary from SustainabilityCalculator.

        Returns:
            Report with attached signature.
        """
        report_json = json.dumps(report, sort_keys=True)
        sig = self._pqc.sign(report_json)

        self._sign_count += 1
        self._log_audit("SIGN_REPORT", len(report_json))

        signed = dict(report)
        signed["_signature"] = sig
        signed["_signed_at"] = time.time()
        signed["_session_id"] = self._session_id
        return signed

    def verify_report(self, signed_report: Dict, original_report: Dict) -> bool:
        """
        Verify a signed sustainability report.

        Args:
            signed_report: Report with _signature field.
            original_report: Original unsigned report.

        Returns:
            True if signature is valid.
        """
        if "_signature" not in signed_report:
            return False
        report_json = json.dumps(original_report, sort_keys=True)
        return self._pqc.verify(report_json, signed_report["_signature"]["signature_hex"])

    # ------------------------------------------------------------------
    # Audit & status
    # ------------------------------------------------------------------

    def _log_audit(self, action: str, size: int) -> None:
        self._audit_log.append({
            "action": action,
            "timestamp": time.time(),
            "session": self._session_id,
            "data_size": size,
        })

    def status(self) -> Dict:
        """Full security-layer status overview."""
        return {
            "session_id": self._session_id,
            "pqc": self._pqc.status(),
            "encrypt_operations": self._encrypt_count,
            "sign_operations": self._sign_count,
            "audit_entries": len(self._audit_log),
        }
