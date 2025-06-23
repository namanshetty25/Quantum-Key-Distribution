import pennylane as qml
import numpy as np

# Step 1: Initialize parameters
n_qubits = 10  # Number of qubits (can be increased)
dev = qml.device("default.qubit", wires=1, shots=1)  # Enable sampling mode

# Step 2: Define the encoding and measurement functions
def encode_qubit(bit, basis):
    """Prepare a qubit in the given basis."""
    if basis == 'Z':
        if bit == 1:
            qml.PauliX(wires=0)
    elif basis == 'X':
        if bit == 0:
            qml.Hadamard(wires=0)
        else:
            qml.Hadamard(wires=0)
            qml.PauliX(wires=0)

@qml.qnode(dev)
def measure_qubit(bit, basis):
    """Encode the qubit and measure in the given basis."""
    encode_qubit(bit, basis)
    if basis == 'X':
        qml.Hadamard(wires=0)
    return qml.sample(wires=0)  # Sample measurement

# Step 3: Simulate the BB84 protocol
# Alice's preparation
alice_bits = np.random.randint(0, 2, n_qubits)  # Random 0s and 1s
alice_bases = np.random.choice(['Z', 'X'], n_qubits)  # Random bases

# Bob's measurement
bob_bases = np.random.choice(['Z', 'X'], n_qubits)  # Random bases
bob_results = []

for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
    result = measure_qubit(bit, bob_basis)  # Measure the qubit
    bob_results.append(int(result))
  # Append the scalar result directly

# Step 4: Public discussion
matching_bases = alice_bases == bob_bases
shared_key = alice_bits[matching_bases]

# Step 5: Output results
print("Alice's bits:    ", alice_bits)
print("Alice's bases:   ", alice_bases)
print("Bob's bases:     ", bob_bases)
print("Bob's results:   ", bob_results)
print("Matching bases:  ", matching_bases)
print("Shared key:      ", shared_key)

'''
Expected Output:
Alice's bits:     [1 1 1 0 0 0 1 1 0 0]
Alice's bases:    ['Z' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'X']
Bob's bases:      ['X' 'X' 'X' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'Z']
Bob's results:    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
Matching bases:   [False  True  True False  True  True False False False False]
Shared key:       [1 1 0 0]
'''

