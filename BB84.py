import numpy as np
import hashlib
from typing import Optional, Dict, List
from qnode import measure_qubit  # expects measure_qubit(bit, prep_basis, meas_basis) -> 0/1

def _privacy_amplify(bitstring: List[int], output_len_bits: int) -> List[int]:
    if len(bitstring) == 0 or output_len_bits == 0:
        return []
    b = bytes(int(''.join(str(bi) for bi in bitstring), 2).to_bytes((len(bitstring)+7)//8, 'big'))
    digest = hashlib.sha256(b).digest()
    bits = []
    for byte in digest:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
            if len(bits) >= output_len_bits:
                return bits
    return bits[:output_len_bits]

def _simple_error_correction_length(sifted_len: int, qber: float, efficiency: float = 1.15) -> int:
    if sifted_len == 0:
        return 0
    q = min(max(qber, 1e-12), 1-1e-12)
    Hq = -q*np.log2(q) - (1-q)*np.log2(1-q)
    leaked = int(np.ceil(efficiency * Hq * sifted_len))
    return min(leaked, sifted_len)

def simulate_bb84_stream(
    n_qubits: int = 500,
    eve_prob: float = 0.0,
    eve_strategy: str = "intercept_random",
    channel_error_rate: float = 0.0,
    test_fraction: float = 0.2,
    ec_efficiency: float = 1.15,
    privacy_amp_ratio: float = 0.5,
    rng: Optional[np.random.Generator] = None
):
    if rng is None:
        rng = np.random.default_rng()

    alice_bits = rng.integers(0, 2, size=n_qubits)
    alice_bases = rng.choice(['Z', 'X'], size=n_qubits)
    bob_bases = rng.choice(['Z', 'X'], size=n_qubits)
    bob_results = np.zeros(n_qubits, dtype=int)

    eve_memory = {'Z': 0, 'X': 0, 'total': 0}

    # Will collect sifted bits after loop to finalize
    for i in range(n_qubits):
        a_bit = int(alice_bits[i])
        a_basis = alice_bases[i]
        b_basis = bob_bases[i]
        intercepted = False

        if rng.random() < eve_prob:
            # Eve chooses basis and measures
            e_basis = rng.choice(['Z', 'X'])  # or adaptive
            eve_meas = int(measure_qubit(a_bit, a_basis, e_basis))
            send_bit = eve_meas
            send_basis = e_basis
            intercepted = True
        else:
            send_bit = a_bit
            send_basis = a_basis

        bob_results[i] = int(measure_qubit(send_bit, send_basis, b_basis))
        
        # Yield current qubit info so caller can update Bloch sphere etc.
        yield {
            "index": i,
            "alice_bit": a_bit,
            "alice_basis": a_basis,
            "bob_basis": b_basis,
            "bob_bit": bob_results[i],
            "eve_intercepted": intercepted
        }

    # After processing all qubits, sift
    same_basis_mask = (alice_bases == bob_bases)
    sifted_alice = alice_bits[same_basis_mask]
    sifted_bob = bob_results[same_basis_mask]
    sift_len = len(sifted_alice)
    sift_rate = sift_len / n_qubits if n_qubits > 0 else 0.0

    if sift_len == 0:
        observed_error_rate = None
        test_size = 0
        test_errors = 0
    else:
        test_size = max(1, int(np.ceil(test_fraction * sift_len)))
        test_indices = rng.choice(sift_len, size=test_size, replace=False)
        test_errors = int(np.sum(sifted_alice[test_indices] != sifted_bob[test_indices]))
        observed_error_rate = test_errors / test_size

    abort_threshold = 0.15
    aborted = False
    if observed_error_rate is not None and observed_error_rate > abort_threshold:
        aborted = True

    final_key = []
    leaked_bits = 0
    after_ec_len = 0

    if not aborted and sift_len > 0:
        remaining_mask = np.ones(sift_len, dtype=bool)
        if test_size > 0:
            remaining_mask[test_indices] = False
        remain_A = sifted_alice[remaining_mask]
        remain_B = sifted_bob[remaining_mask]
        remain_len = len(remain_A)

        qber_est = observed_error_rate if observed_error_rate is not None else 0.0

        leaked_bits = _simple_error_correction_length(remain_len, qber_est, efficiency=ec_efficiency)
        after_ec_len = max(0, remain_len - leaked_bits)

        keep_len = int(np.floor(after_ec_len * privacy_amp_ratio))
        final_key = _privacy_amplify(list(remain_A), keep_len)
    else:
        final_key = []

    stats = {
        "n_qubits": n_qubits,
        "sift_len": sift_len,
        "sift_rate": sift_rate,
        "test_size": test_size,
        "test_errors": test_errors,
        "observed_error_rate": observed_error_rate,
        "aborted": aborted,
        "leaked_bits_ec": leaked_bits,
        "after_ec_len": after_ec_len,
        "final_key_len": len(final_key),
        "eve_strategy": eve_strategy,
        "channel_error_rate": channel_error_rate
    }

    # Yield final summary at the end (optional)
    yield {
        "final": True,
        "observed_error_rate": observed_error_rate,
        "sift_rate": sift_rate,
        "sifted_A": sifted_alice.tolist(),
        "sifted_B": sifted_bob.tolist(),
        "final_key": final_key,
        "stats": stats
    }
