"""
Testes de fumaca / Smoke tests — Hubstry Quantum Logistics MVP.

Rodam apenas com stdlib + pytest. Nao exigem D-Wave, OR-Tools ou Streamlit.
Run with stdlib + pytest only. No D-Wave, OR-Tools or Streamlit required.
"""

import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config.settings import VEHICLE_CAPACITY  # noqa: E402
from core_layer.quantum_optimizer import QuboVRPOptimizer  # noqa: E402
from security_layer.pqc_wrapper import PQCWrapper  # noqa: E402


# ----------------------------------------------------------------------
# Camada de seguranca (simulacao) / Security layer (simulation)
# ----------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    pqc = PQCWrapper(seed=1)
    payload = "rota-01|lat=41.15|lon=-8.61"
    envelope = pqc.encrypt(payload)
    assert pqc.decrypt(envelope["ciphertext_hex"], envelope["nonce_hex"]) == payload


def test_sign_verify_positivo():
    pqc = PQCWrapper(seed=1)
    sig = pqc.sign("relatorio-frota")
    assert pqc.verify("relatorio-frota", sig["signature_hex"]) is True


def test_sign_verify_negativo_mensagem_adulterada():
    pqc = PQCWrapper(seed=1)
    sig = pqc.sign("relatorio-frota")
    assert pqc.verify("relatorio-ADULTERADO", sig["signature_hex"]) is False


def test_verify_rejeita_assinatura_malformada():
    pqc = PQCWrapper(seed=1)
    assert pqc.verify("qualquer", "nao-e-hex") is False


# ----------------------------------------------------------------------
# Solver QUBO / QUBO solver
# ----------------------------------------------------------------------

def _instancia_pequena():
    coords = [(0, 0), (0, 2), (2, 0), (2, 2), (0, 4)]
    n = len(coords)
    dist = [
        [abs(coords[i][0] - coords[j][0]) + abs(coords[i][1] - coords[j][1])
         for j in range(n)]
        for i in range(n)
    ]
    demands = [0, 1, 1, 1, 1]
    return dist, demands


def test_solver_visita_cada_no_exatamente_uma_vez():
    dist, demands = _instancia_pequena()
    rotas = QuboVRPOptimizer(dist, demands, seed=42).solve()["routes"]
    visitados = [no for rota in rotas for no in rota]
    assert sorted(visitados) == list(range(1, len(demands)))


def test_solver_respeita_capacidade():
    dist, demands = _instancia_pequena()
    rotas = QuboVRPOptimizer(dist, demands, seed=42).solve()["routes"]
    for rota in rotas:
        assert sum(demands[no] for no in rota) <= VEHICLE_CAPACITY


# ----------------------------------------------------------------------
# Pipeline ponta a ponta / End-to-end pipeline
# ----------------------------------------------------------------------


def test_pipeline_executa_sem_excecao():
    resultado = subprocess.run(
        [sys.executable, "run_mvp.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert resultado.returncode == 0, resultado.stderr
