"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Post-Quantum Cryptography Wrapper — NIST PQC simulation layer.

Integrates with: Hubstry Security framework.

Simulates NIST-approved post-quantum algorithms (Kyber768 for key
encapsulation, Dilithium3 for digital signatures) with a classical
a didactic SHA3-256 keystream fallback (XOR, non-AEAD) for current hardware.

In production, swap the fallback functions with liboqs / pqclean bindings.
"""

import hashlib
import hmac
import os
import struct
import time
from typing import Dict, Tuple, Optional

from config.settings import (
    PQC_ALGORITHM_KEM,
    PQC_ALGORITHM_SIG,
    PQC_FALLBACK_CIPHER,
    PQC_FALLBACK_HASH,
    HSM_SIMULATED,
    KEY_ROTATION_HOURS,
    TLS_MIN_VERSION,
    DATA_CLASSIFICATION,
)


class PQCWrapper:
    """
    Post-Quantum Cryptography wrapper with classical fallback.

    Provides:
      - Key generation (KEM + signature)
      - Encryption / Decryption
      - Signing / Verification
      - Key rotation management
    """

    def __init__(self, seed: int = None):
        self._seed = seed
        self._key_ts = time.time()
        self._key_id = 0
        self._public_key: Optional[bytes] = None
        self._private_key: Optional[bytes] = None
        self._generate_keypair()

    # ------------------------------------------------------------------
    # Key management
    # ------------------------------------------------------------------

    def _generate_keypair(self) -> None:
        """
        Generate a simulated PQC keypair.

        In production, this calls Kyber768.KeyGen() via liboqs.
        MVP uses deterministic SHA3-256 based derivation.
        """
        rng_seed = f"{self._seed or os.urandom(16).hex()}-key-{self._key_id}".encode()
        self._private_key = hashlib.sha3_256(rng_seed).digest()
        self._public_key = hashlib.sha3_256(self._private_key + b"-pub").digest()
        self._key_ts = time.time()

    def rotate_key(self) -> Dict:
        """
        Force a key rotation event.

        Returns:
            Dict with new key metadata.
        """
        self._key_id += 1
        self._generate_keypair()
        return {
            "key_id": self._key_id,
            "algorithm": PQC_ALGORITHM_KEM,
            "timestamp": time.time(),
            "public_key_hex": self._public_key.hex()[:32] + "...",
        }

    def needs_rotation(self) -> bool:
        """Check if key rotation is overdue."""
        age_hours = (time.time() - self._key_ts) / 3600
        return age_hours >= KEY_ROTATION_HOURS

    # ------------------------------------------------------------------
    # Encryption / Decryption (KEM simulation)
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> Dict:
        """
        Encrypt a plaintext string using the PQC KEM + SHA3-256 keystream fallback (XOR, non-AEAD).

        Args:
            plaintext: Message to encrypt.

        Returns:
            Dict with ciphertext, nonce, and metadata.
        """
        nonce = os.urandom(12)

        # Derive keystream seed from shared secret + public key
        shared_secret = hashlib.sha3_256(
            self._public_key + nonce + struct.pack(">I", self._key_id)
        ).digest()

        # XOR-based stream cipher simulation (MVP only)
        plain_bytes = plaintext.encode("utf-8")
        key_stream = hashlib.sha3_256(shared_secret + nonce).digest()
        # Expand key stream to match plaintext length
        expanded = b""
        block_size = 32
        for i in range(0, len(plain_bytes), block_size):
            block_key = hashlib.sha3_256(
                shared_secret + struct.pack(">I", i // block_size)
            ).digest()
            expanded += block_key

        cipher_bytes = bytes(a ^ b for a, b in zip(plain_bytes, expanded))
        cipher_hex = cipher_bytes.hex()

        return {
            "ciphertext_hex": cipher_hex,
            "nonce_hex": nonce.hex(),
            "algorithm": f"{PQC_ALGORITHM_KEM}+{PQC_FALLBACK_CIPHER}",
            "key_id": self._key_id,
            "plaintext_len": len(plaintext),
        }

    def decrypt(self, ciphertext_hex: str, nonce_hex: str) -> str:
        """
        Decrypt a message encrypted by encrypt().

        Args:
            ciphertext_hex: Hex-encoded ciphertext.
            nonce_hex: Hex-encoded nonce.

        Returns:
            Decrypted plaintext string.
        """
        nonce = bytes.fromhex(nonce_hex)
        cipher_bytes = bytes.fromhex(ciphertext_hex)

        shared_secret = hashlib.sha3_256(
            self._public_key + nonce + struct.pack(">I", self._key_id)
        ).digest()

        expanded = b""
        block_size = 32
        for i in range(0, len(cipher_bytes), block_size):
            block_key = hashlib.sha3_256(
                shared_secret + struct.pack(">I", i // block_size)
            ).digest()
            expanded += block_key

        plain_bytes = bytes(a ^ b for a, b in zip(cipher_bytes, expanded))
        return plain_bytes.decode("utf-8")

    # ------------------------------------------------------------------
    # Digital Signature (Dilithium3 simulation)
    # ------------------------------------------------------------------

    def sign(self, message: str) -> Dict:
        """
        Create a digital signature over a message.

        Args:
            message: Message to sign.

        Returns:
            Dict with signature hex and metadata.

        NOTA DE SIMULACAO / SIMULATION NOTE:
        Simulacao didatica. Nao e assinatura digital assimetrica: a chave
        publica deriva da privada (sha3_256(priv + "-pub")), logo nao ha par
        de chaves real. Nao usar para fins de seguranca.

        Didactic simulation. Not an asymmetric digital signature: the public
        key is derived from the private one, so there is no real key pair.
        Do not use for security purposes.
        """
        msg_bytes = message.encode("utf-8")
        sig_input = self._private_key + msg_bytes
        signature = hashlib.sha3_512(sig_input).digest()

        return {
            "signature_hex": signature.hex(),
            "algorithm": PQC_ALGORITHM_SIG,
            "key_id": self._key_id,
        }

    def verify(self, message: str, signature_hex: str) -> bool:
        """
        Verify a digital signature.

        Args:
            message: Original message.
            signature_hex: Hex-encoded signature.

        Returns:
            True if signature is valid.

        NOTA DE SIMULACAO / SIMULATION NOTE:
        Esta verificacao recomputa o mesmo valor que sign() produz, usando a
        chave privada. Portanto trata-se de um MAC com chave, NAO de uma
        assinatura digital assimetrica: nao e possivel verificar sem o
        segredo. Em producao, substituir por Dilithium3 via liboqs/PQClean.

        This check recomputes the same value sign() produces, using the
        private key. It is therefore a keyed MAC, NOT an asymmetric digital
        signature: verification without the secret is not possible. In
        production, replace with Dilithium3 via liboqs/PQClean.
        """
        try:
            sig_bytes = bytes.fromhex(signature_hex)
        except ValueError:
            return False
        msg_bytes = message.encode("utf-8")
        expected = hashlib.sha3_512(self._private_key + msg_bytes).digest()
        return hmac.compare_digest(expected, sig_bytes)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict:
        """Return the current PQC module status."""
        return {
            "kem_algorithm": PQC_ALGORITHM_KEM,
            "sig_algorithm": PQC_ALGORITHM_SIG,
            "fallback_cipher": PQC_FALLBACK_CIPHER,
            "fallback_hash": PQC_FALLBACK_HASH,
            "hsm_simulated": HSM_SIMULATED,
            "key_id": self._key_id,
            "key_age_hours": round((time.time() - self._key_ts) / 3600, 2),
            "needs_rotation": self.needs_rotation(),
            "tls_min_version": TLS_MIN_VERSION,
            "data_classification": DATA_CLASSIFICATION,
        }
