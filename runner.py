from BB84 import simulate_bb84_stream
import numpy as np

def batch_run_bb84(n_qubits, eve_prob, test_fraction, trials):
    results = []
    for _ in range(trials):
        gen = simulate_bb84_stream(n_qubits, eve_prob, test_fraction)
        res = None
        for data in gen:
            if data.get("final"):
                res = data
        if res is not None:
            results.append(res)

    # Now aggregate results (means, stddev, etc.)
    if not results:
        return {
            "mean_error": None,
            "std_error": None,
            "mean_sift": None
        }
    
    observed_errors = [r["observed_error_rate"] for r in results if r["observed_error_rate"] is not None]
    sift_rates = [r["sift_rate"] for r in results if r["sift_rate"] is not None]

    mean_error = float(np.mean(observed_errors)) if observed_errors else None
    std_error = float(np.std(observed_errors)) if observed_errors else None
    mean_sift = float(np.mean(sift_rates)) if sift_rates else None

    return {
        "mean_error": mean_error,
        "std_error": std_error,
        "mean_sift": mean_sift
    }
