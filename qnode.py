import pennylane as qml
from pennylane import numpy as np
import matplotlib.pyplot as plt

# Quantum device: 1 qubit, 1 shot per measurement
dev = qml.device("default.qubit", wires=1, shots=1)

def encode_qubit(bit, basis):
    """Encode a classical bit into a qubit in the given basis ('Z' or 'X')."""
    if basis == 'Z':
        # Z basis: |0> for bit=0, |1> for bit=1
        if bit == 1:
            qml.PauliX(wires=0)
    elif basis == 'X':
        # X basis: |+> for bit=0, |-> for bit=1
        if bit == 1:
            qml.PauliX(wires=0)
        qml.Hadamard(wires=0)


# QNode to encode and measure a qubit
@qml.qnode(dev)
def measure_qubit(bit, prep_basis, meas_basis):
    encode_qubit(bit, prep_basis)
    if meas_basis == 'X':
        qml.Hadamard(wires=0)  # Rotate back to computational basis
    return qml.sample(wires=0)  # Single-shot measurement

# Wrapper for BB84 simulation use
def measure_bit_with_pennylane(bit, prep_basis, meas_basis):
    result = measure_qubit(bit, prep_basis, meas_basis)
    return int(result)  # Convert to int for consistency