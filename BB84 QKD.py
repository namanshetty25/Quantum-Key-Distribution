import pennylane as qml
import numpy as np

# Number of qubits to simulate
n_qubits = 100

# Quantum device initialization with 1 qubit and 1 shot per measurement
dev = qml.device("default.qubit", wires=1, shots=1)

# Function to encode a qubit in the specified basis (Z or X)
def encode_qubit(bit, basis):
    if basis == 'Z':
        if bit == 1:
            qml.PauliX(wires=0)
    elif basis == 'X':
        if bit == 0:
            qml.Hadamard(wires=0)
        else:
            qml.PauliX(wires=0)
            qml.Hadamard(wires=0)

# Define the quantum node that encodes and measures the qubit in the given basis
@qml.qnode(dev)
def measure_qubit(bit, alice_basis, bob_basis):
    encode_qubit(bit, alice_basis)
    if bob_basis == 'X':
        qml.Hadamard(wires=0)
    return qml.sample(wires=0)

# Function to simulate Alice and Bob's process (without eavesdropper)
def simulate_no_eavesdropper():
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []

    for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
        result = measure_qubit(bit, alice_basis, bob_basis)
        bob_results.append(int(result))

    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if matching_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    print("-------- Without Eavesdropper --------")
    print("Error rate:", error_rate)
    print("Shared key length:", len(shared_key))

    if error_rate > 0.15:  # Lowered threshold for demonstration
        print("Warning: High error rate detected! Eavesdropper might be present.")
    else:
        print("No significant eavesdropping detected.")
    print()

# Function to simulate Alice, Bob, and Eve's process (with eavesdropper)
def simulate_with_eavesdropper():
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    eve_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []
    eve_results = []

    for bit, alice_basis, bob_basis, eve_basis in zip(alice_bits, alice_bases, bob_bases, eve_bases):
        eve_result = measure_qubit(bit, alice_basis, eve_basis)
        eve_results.append(int(eve_result))
        bob_result = measure_qubit(int(eve_result), eve_basis, bob_basis)
        bob_results.append(int(bob_result))

    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if matching_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    print("-------- With Eavesdropper --------")
    print("Error rate:", error_rate)
    print("Shared key length:", len(shared_key))

    if error_rate > 0.15:
        print("Warning: High error rate detected! Eavesdropper is likely present.")
    else:
        print("No significant eavesdropping detected.")
    print()

# Run simulations
simulate_no_eavesdropper()
simulate_with_eavesdropper()
'''
Output:
-------- Without Eavesdropper --------
Error rate: 0.0
Shared key length: 45
No significant eavesdropping detected.

-------- With Eavesdropper --------
Error rate: 0.21153846153846154
Shared key length: 52
Warning: High error rate detected! Eavesdropper is likely present.
'''
