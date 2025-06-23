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
            qml.PauliX(wires=0)  # Apply Pauli-X gate to flip the qubit
    elif basis == 'X':
        if bit == 0:
            qml.Hadamard(wires=0)  # Apply Hadamard gate to create superposition
        else:
            qml.Hadamard(wires=0)  # Create superposition
            qml.PauliX(wires=0)  # Flip the qubit if the bit is 1

# Define the quantum node that encodes and measures the qubit in the given basis
@qml.qnode(dev)
def measure_qubit(bit, basis):
    encode_qubit(bit, basis)
    if basis == 'X':
        qml.Hadamard(wires=0)  # Apply Hadamard for X-basis measurement
    return qml.sample(wires=0)  # Sample the measurement result

# Function to simulate Alice and Bob's process (without eavesdropper)
def simulate_no_eavesdropper():
    # Alice generates random bits and chooses bases
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)

    # Bob chooses random bases for his measurements
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []

    # Simulate the transmission process (without Eve)
    for i, (bit, alice_basis, bob_basis) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
        result = measure_qubit(bit, bob_basis)  # Bob measures the qubit directly
        bob_results.append(int(result))  # Record Bob's result

    # Compare the bases between Alice and Bob to extract the shared key
    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    # Calculate error rate by comparing Alice's and Bob's results in matching bases
    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    # Output the results
    print("-------- Without Eavesdropper --------")
    print("Alice's bits:    ", alice_bits)
    print("Alice's bases:   ", alice_bases)
    print("Bob's bases:     ", bob_bases)
    print("Bob's results:   ", bob_results)
    print("Matching bases:  ", matching_bases)
    print("Shared key:      ", shared_key)
    print("Error rate:      ", error_rate)

    # Check for eavesdropping (without Eve)
    if error_rate > 0.25:
        print("Warning: High error rate detected! Eavesdropper is likely present.")
    else:
        print("No significant eavesdropping detected.")
    print("\n")

# Function to simulate Alice, Bob, and Eve's process (with eavesdropper)
def simulate_with_eavesdropper():
    # Alice generates random bits and chooses bases
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)

    # Bob chooses random bases for his measurements
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []

    # Eve chooses random bases to intercept and measure qubits
    eve_bases = np.random.choice(['Z', 'X'], n_qubits)
    eve_interference = []  # Store Eve's interference results

    # Simulate the transmission process (with Eve's interference)
    for i, (bit, alice_basis, bob_basis) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
        # Eve intercepts and measures the qubit in her chosen basis
        eve_result = measure_qubit(bit, eve_bases[i])
        eve_interference.append(int(eve_result))  # Record Eve's measurement result

        # Eve re-encodes the qubit for Bob to measure, potentially introducing errors
        result = measure_qubit(int(eve_result), bob_basis)
        bob_results.append(int(result))  # Record Bob's result

    # Compare the bases between Alice and Bob to extract the shared key
    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    # Calculate error rate by comparing Alice's and Bob's results in matching bases
    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    # Output the results
    print("-------- With Eavesdropper --------")
    print("Alice's bits:    ", alice_bits)
    print("Alice's bases:   ", alice_bases)
    print("Eve's bases:     ", eve_bases)
    print("Eve's results:   ", eve_interference)
    print("Bob's bases:     ", bob_bases)
    print("Bob's results:   ", bob_results)
    print("Matching bases:  ", matching_bases)
    print("Shared key:      ", shared_key)
    print("Error rate:      ", error_rate)

    # Check for eavesdropping (with Eve)
    if error_rate > 0.25:
        print("Warning: High error rate detected! Eavesdropper is likely present.")
    else:
        print("No significant eavesdropping detected.")
    print("\n")

# Run simulations
simulate_no_eavesdropper()
simulate_with_eavesdropper()

'''
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
            qml.PauliX(wires=0)  # Apply Pauli-X gate to flip the qubit
    elif basis == 'X':
        if bit == 0:
            qml.Hadamard(wires=0)  # Apply Hadamard gate to create superposition
        else:
            qml.Hadamard(wires=0)  # Create superposition
            qml.PauliX(wires=0)  # Flip the qubit if the bit is 1

# Define the quantum node that encodes and measures the qubit in the given basis
@qml.qnode(dev)
def measure_qubit(bit, basis):
    encode_qubit(bit, basis)
    if basis == 'X':
        qml.Hadamard(wires=0)  # Apply Hadamard for X-basis measurement
    return qml.sample(wires=0)  # Sample the measurement result

# Function to simulate Alice and Bob's process (without eavesdropper)
def simulate_no_eavesdropper():
    # Alice generates random bits and chooses bases
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)

    # Bob chooses random bases for his measurements
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []

    # Simulate the transmission process (without Eve)
    for i, (bit, alice_basis, bob_basis) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
        result = measure_qubit(bit, bob_basis)  # Bob measures the qubit directly
        bob_results.append(int(result))  # Record Bob's result

    # Compare the bases between Alice and Bob to extract the shared key
    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    # Calculate error rate by comparing Alice's and Bob's results in matching bases
    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    # Output the results
    print("-------- Without Eavesdropper --------")
    print("Alice's bits:    ", alice_bits)
    print("Alice's bases:   ", alice_bases)
    print("Bob's bases:     ", bob_bases)
    print("Bob's results:   ", bob_results)
    print("Matching bases:  ", matching_bases)
    print("Shared key:      ", shared_key)
    print("Error rate:      ", error_rate)

    # Check for eavesdropping (without Eve)
    if error_rate > 0.25:
        print("Warning: High error rate detected! Eavesdropper is likely present.")
    else:
        print("No significant eavesdropping detected.")
    print("\n")

# Function to simulate Alice, Bob, and Eve's process (with eavesdropper)
def simulate_with_eavesdropper():
    # Alice generates random bits and chooses bases
    alice_bits = np.random.randint(0, 2, n_qubits)
    alice_bases = np.random.choice(['Z', 'X'], n_qubits)

    # Bob chooses random bases for his measurements
    bob_bases = np.random.choice(['Z', 'X'], n_qubits)
    bob_results = []

    # Eve chooses random bases to intercept and measure qubits
    eve_bases = np.random.choice(['Z', 'X'], n_qubits)
    eve_interference = []  # Store Eve's interference results

    # Simulate the transmission process (with Eve's interference)
    for i, (bit, alice_basis, bob_basis) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
        # Eve intercepts and measures the qubit in her chosen basis
        eve_result = measure_qubit(bit, eve_bases[i])
        eve_interference.append(int(eve_result))  # Record Eve's measurement result

        # Eve re-encodes the qubit for Bob to measure, potentially introducing errors
        result = measure_qubit(int(eve_result), bob_basis)
        bob_results.append(int(result))  # Record Bob's result

    # Compare the bases between Alice and Bob to extract the shared key
    matching_bases = alice_bases == bob_bases
    shared_key = alice_bits[matching_bases]

    # Calculate error rate by comparing Alice's and Bob's results in matching bases
    error_count = sum([alice_bits[i] != bob_results[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]])
    error_rate = error_count / np.sum(matching_bases) if np.sum(matching_bases) > 0 else 0

    # Output the results
    print("-------- With Eavesdropper --------")
    print("Alice's bits:    ", alice_bits)
    print("Alice's bases:   ", alice_bases)
    print("Eve's bases:     ", eve_bases)
    print("Eve's results:   ", eve_interference)
    print("Bob's bases:     ", bob_bases)
    print("Bob's results:   ", bob_results)
    print("Matching bases:  ", matching_bases)
    print("Shared key:      ", shared_key)
    print("Error rate:      ", error_rate)

    # Check for eavesdropping (with Eve)
    if error_rate > 0.25:
        print("Warning: High error rate detected! Eavesdropper is likely present.")
    else:
        print("No significant eavesdropping detected.")
    print("\n")

# Run simulations
simulate_no_eavesdropper()
simulate_with_eavesdropper()


'''

Sample Output:

-------- Without Eavesdropper --------
Alice's bits:     [1 0 1 0 1 1 1 0 1 0 0 0 0 1 1 1 0 0 0 1 0 0 1 1 1 0 0 0 0 0 0 1 0 1 0 0 0
 1 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 0 0 1 1 0 0 1 0 1 0 0 0 1 1 1 0 1 1 1 1 1
 0 0 1 0 0 0 0 0 1 0 1 1 1 1 0 1 1 1 1 1 0 1 1 1 1 0]
Alice's bases:    ['X' 'X' 'X' 'X' 'X' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'X' 'Z' 'X' 'Z' 'Z'
 'X' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'X' 'Z'
 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'X' 'X' 'X'
 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z'
 'X' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'Z'
 'X' 'X' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X']
Bob's bases:      ['X' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'X' 'X' 'Z' 'Z' 'X' 'X' 'Z' 'Z' 'Z'
 'X' 'Z' 'X' 'X' 'X' 'X' 'X' 'X' 'X' 'X' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'Z'
 'X' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'Z' 'X' 'Z' 'X' 'X' 'X' 'X' 'Z' 'X' 'Z' 'Z'
 'X' 'Z' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'X' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'Z' 'X' 'X'
 'Z' 'X' 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'X' 'Z'
 'X' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'X' 'Z' 'Z']
Bob's results:    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0]
Matching bases:   [ True False  True False False False  True  True  True False  True False
  True  True False False  True  True  True False  True False  True False
 False False False  True False False False  True  True False False  True
 False  True False False  True False  True False False  True False  True
 False  True False  True False False False False False  True False  True
 False  True False False False  True  True  True  True  True False False
 False  True  True False False False False  True False  True  True False
 False  True  True  True False  True  True False  True False  True False
  True False  True False]
Shared key:       [1 1 1 0 1 0 0 1 0 0 0 0 1 0 1 0 0 1 0 0 0 0 0 1 0 1 1 1 1 1 0 1 1 0 0 0 1
 1 1 1 1 1 1 0 1 1]
Error rate:       0.2391304347826087
No significant eavesdropping detected.


-------- With Eavesdropper --------
Alice's bits:     [0 0 0 1 0 1 1 0 1 0 1 1 1 1 1 0 0 0 0 1 1 0 0 0 0 1 0 1 0 0 0 1 1 0 1 1 1
 1 1 1 1 0 0 1 0 1 1 1 1 1 0 1 1 1 1 0 1 0 1 1 1 0 0 0 0 0 1 1 0 1 1 0 1 1
 1 1 0 0 1 1 1 1 1 1 0 1 0 0 0 1 0 0 1 1 0 1 1 1 1 0]
Alice's bases:    ['X' 'X' 'X' 'Z' 'Z' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'X' 'X'
 'Z' 'Z' 'X' 'Z' 'X' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'X' 'X' 'Z'
 'X' 'Z' 'X' 'X' 'X' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'X' 'Z' 'X' 'X' 'Z'
 'X' 'X' 'X' 'X' 'X' 'X' 'Z' 'X' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'X' 'X'
 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'X' 'X' 'Z' 'X' 'Z'
 'Z' 'X' 'X' 'Z' 'Z' 'X' 'X' 'X' 'X' 'X']
Eve's bases:      ['Z' 'X' 'X' 'X' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'X'
 'Z' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z'
 'X' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'X' 'X' 'Z' 'X' 'X' 'X' 'X' 'X'
 'Z' 'X' 'X' 'X' 'X' 'Z' 'Z' 'X' 'X' 'Z' 'Z' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'Z'
 'X' 'Z' 'X' 'Z' 'X' 'X' 'X' 'Z' 'X' 'Z' 'X' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'X'
 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'Z']
Eve's results:    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0]
Bob's bases:      ['X' 'Z' 'Z' 'X' 'X' 'Z' 'X' 'X' 'Z' 'X' 'Z' 'Z' 'X' 'X' 'X' 'X' 'Z' 'X'
 'X' 'X' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z'
 'X' 'X' 'X' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'X' 'X' 'X' 'X'
 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'Z' 'Z' 'Z' 'X' 'Z' 'Z' 'Z' 'X' 'X' 'Z' 'X' 'Z'
 'Z' 'X' 'Z' 'X' 'Z' 'X' 'Z' 'Z' 'Z' 'X' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'Z'
 'X' 'Z' 'X' 'X' 'Z' 'Z' 'Z' 'Z' 'Z' 'Z']
Bob's results:    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0]
Matching bases:   [ True False False False False False  True  True  True False  True  True
  True False False False False  True False False  True  True False False
 False False False  True  True  True  True  True False  True False  True
  True False  True False False  True  True False  True False  True False
  True False False  True  True False  True False False False False False
  True False False False  True False  True  True  True  True  True False
 False False  True  True  True  True False  True  True  True  True  True
  True False False  True False  True False False  True False  True False
 False False False False]
Shared key:       [0 1 0 1 1 1 1 0 1 0 1 0 0 0 1 0 1 1 1 0 0 0 1 1 1 1 1 1 0 1 1 0 1 1 1 1 0
 0 1 1 1 1 1 0 0 1 1 0]
Error rate:       0.5
Warning: High error rate detected! Eavesdropper is likely present.
'''
