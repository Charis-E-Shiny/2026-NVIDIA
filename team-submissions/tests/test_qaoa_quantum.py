import random
import numpy as np
import cudaq

# -----------------------------
# Core: LABS energy + reverse symmetry
# -----------------------------
def energy(bits):
    """
    LABS energy:
      E(s) = sum_{k=1..N-1} C_k^2
      C_k = sum_{i=0..N-k-1} sigma_i*sigma_{i+k}
      sigma_i = 2*bit-1 in {-1,+1}
    """
    sigma = [2 * b - 1 for b in bits]
    N = len(bits)
    E = 0
    for k in range(1, N):
        Ck = 0
        for i in range(N - k):
            Ck += sigma[i] * sigma[i + k]
        E += Ck * Ck
    return E

def reverse_bits(bits):
    """Reverse symmetry (the 'inverse' requested)."""
    return bits[::-1]

# -----------------------------
# Interactions (0-based)
# -----------------------------
def get_interactions(N: int):
    G2, G4 = [], []

    # G2: [i, i+2k]
    for i in range(0, N - 2):
        max_k = (N - 1 - i) // 2
        for k in range(1, max_k + 1):
            G2.append([i, i + 2 * k])

    # G4: [i, i+t, i+k, i+k+t]
    for i in range(0, N - 3):
        max_t = (N - 2 - i) // 2
        for t in range(1, max_t + 1):
            for k in range(t + 1, N - i - t):
                G4.append([i, i + t, i + k, i + k + t])

    return G2, G4

# -----------------------------
# CUDA-Q kernel: QAOA p=1 (no pi, no rzz)
# -----------------------------
@cudaq.kernel
def qaoa_p1_labs(
    N: int,
    G2: list[list[int]],
    G4: list[list[int]],
    gamma: float,
    beta: float,
    cost_scale: float
):
    q = cudaq.qvector(N)
    h(q)

    cost_ang = cost_scale * gamma

    # ZZ terms: CNOT-RZ-CNOT
    for pair in G2:
        i, j = pair[0], pair[1]
        x.ctrl(q[i], q[j])
        rz(cost_ang, q[j])
        x.ctrl(q[i], q[j])

    # ZZZZ terms: parity ladder
    for quad in G4:
        a, b, c, d = quad[0], quad[1], quad[2], quad[3]
        x.ctrl(q[a], q[d])
        x.ctrl(q[b], q[d])
        x.ctrl(q[c], q[d])
        rz(cost_ang, q[d])
        x.ctrl(q[c], q[d])
        x.ctrl(q[b], q[d])
        x.ctrl(q[a], q[d])

    # Mixer: RX(2*beta)
    mix_ang = 2.0 * beta
    for i in range(N):
        rx(mix_ang, q[i])

# -----------------------------
# Helpers
# -----------------------------
def _best_from_sample(sample_result):
    best_bits, best_E = None, None
    for bitstr in sample_result:
        bits = [int(c) for c in bitstr]
        E = energy(bits)
        if best_E is None or E < best_E:
            best_E, best_bits = E, bits
    return best_bits, best_E

# -----------------------------
# Public API: all knobs passed in (notebook owns profiles/config)
# -----------------------------
def qaoa_best_bitstring(
    N: int,
    *,
    gammas,
    betas,
    shots_score: int,
    shots_final: int,
    top_k: int,
    cost_scale: float = 2.0,
    seed: int = 123,
    target: str | None = None,
    G2=None,
    G4=None,
):
    """
    QAOA p=1 seeder:
      - gammas: iterable of floats
      - betas:  iterable of floats
      - shots_score: shots for scoring each (gamma,beta)
      - shots_final: shots for resampling top_k params
      - top_k: number of top params to resample
      - cost_scale: rotation scaling factor (convention knob)
      - seed: reproducibility for any classical randomness (and numpy)
      - target: optional cudaq target (None for qBraid CPU, "nvidia" for Brev GPU)
      - G2/G4: optional precomputed interactions (otherwise computed)

    Returns:
      dict with best_bits, best_energy, best_params, and meta info.
    """
    if target:
        cudaq.set_target(target)

    random.seed(seed)
    np.random.seed(seed)

    if G2 is None or G4 is None:
        G2, G4 = get_interactions(N)

    # Stage 1: cheap scoring over grid
    scored = []
    for g in gammas:
        for b in betas:
            res = cudaq.sample(
                qaoa_p1_labs,
                N, G2, G4, float(g), float(b), float(cost_scale),
                shots_count=int(shots_score)
            )
            bits, E = _best_from_sample(res)
            scored.append((E, float(g), float(b)))

    scored.sort(key=lambda x: x[0])
    best_params = scored[:int(top_k)]

    # Stage 2: resample top params and return best overall
    best_bits, best_E = None, None
    for _, g, b in best_params:
        res = cudaq.sample(
            qaoa_p1_labs,
            N, G2, G4, float(g), float(b), float(cost_scale),
            shots_count=int(shots_final)
        )
        bits, E = _best_from_sample(res)
        if best_E is None or E < best_E:
            best_bits, best_E = bits, E

    return {
        "N": N,
        "best_bits": best_bits,
        "best_energy": best_E,
        "best_params": best_params,
        "lens": {"G2": len(G2), "G4": len(G4)},
        "meta": {
            "shots_score": int(shots_score),
            "shots_final": int(shots_final),
            "top_k": int(top_k),
            "cost_scale": float(cost_scale),
            "seed": int(seed),
            "target": target,
            "n_gammas": len(list(gammas)) if not isinstance(gammas, np.ndarray) else int(gammas.size),
            "n_betas": len(list(betas)) if not isinstance(betas, np.ndarray) else int(betas.size),
        },
    }
