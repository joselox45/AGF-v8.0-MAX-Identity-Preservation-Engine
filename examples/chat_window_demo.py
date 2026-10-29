"""Ejemplo pegable en ventana de chat — AGF v9.0"""
import sys, json
sys.path.insert(0, "src")
from face_embedding import OnnxFaceEmbedder, VectorComparator, EmbeddingResult, EmbeddingStatus
from evidence_signing import EvidenceChain, HMACFallbackSigner
from agent_identity import enroll_agent, verify_agent

# 1. Embedding (fail-closed sin pesos en la ventana de chat)
arc = OnnxFaceEmbedder("arcface").embed(None)
print("[T21]", arc.to_json())

# 2. Comparación (anti-replay incluido)
ref = EmbeddingResult(EmbeddingStatus.PASS, "demo", vector=[0.6, 0.8])
cand = EmbeddingResult(EmbeddingStatus.PASS, "demo", vector=[0.59, 0.81])
print("[T23/T24]", json.dumps(VectorComparator(0.65).verify(ref, cand)))

# 3. Cadena de evidencia firmada
ch = EvidenceChain(HMACFallbackSigner(b"chat-secret"))
ch.append({"etapa": "captura", "hash": "abc..."})
print("[T25/T26]", json.dumps(ch.verify()))

# 4. Identidad de agente SPIFFE/DID
idn = enroll_agent("akadi.local", "agent-001")
print("[T27]", idn.to_json())
print("[T28]", json.dumps(verify_agent(idn)))
