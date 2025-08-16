# Quantum Key Distribution (QKD) Simulator

Quantum Key Distribution (QKD) is a secure communication method that uses quantum mechanics to enable two parties (commonly called Alice and Bob) to produce a shared, random secret key. This key can then be used to encrypt and decrypt messages with guaranteed security against an eavesdropper (Eve).

This repository provides an implementation and simulation of QKD protocols (currently BB84) in Python, along with interactive GUI tools, Bloch sphere visualizations, and performance analysis plots.

---

## Features

- **BB84 Protocol Simulation** with configurable parameters (qubits, Eve probability, test fraction)
- **Interactive Tkinter GUI** with real-time logs and results
- **Bloch Sphere Visualization** for Alice and Bob’s qubit states
- **Eve Probability Sweep Mode** to analyze error rates against eavesdropping
- **Batch Mode** for statistical evaluation over multiple runs
- **Export Results as CSV** for further analysis
- **Integration with PennyLane** for quantum circuit-based measurements

---

## Project Structure

```
Quantum-Key-Distribution/
│── main.py              # Entry point (launches GUI)
│── gui.py               # Tkinter GUI (plots, Bloch spheres, logs)
│── BB84.py              # BB84 protocol simulation (Alice, Bob, Eve logic)
│── runner.py            # Batch mode execution & result aggregation
│── qnode.py             # PennyLane-based qubit encoding & measurement
│── requirements.txt     # Python dependencies
│── README.md            # Documentation
```

---

## Background

The BB84 protocol (Bennett & Brassard, 1984) is the first and most widely studied QKD protocol.

**Workflow:**

- Alice generates random bits and chooses random bases (Z/X)
- Bob measures using his own random bases
- They publicly compare bases and keep only matching ones (sifted key)
- A subset is tested for error rates
- If errors exceed a threshold → Eve is detected. Otherwise → secure key established

This project provides both educational visualization and experimental analysis tools for BB84.

---

## Installation

Clone the repository:
```bash
git clone https://github.com/namanshetty25/Quantum-Key-Distribution.git
```

Change directory:
```bash
cd Quantum-Key-Distribution
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Run GUI

Launch the interactive simulator:
```bash
python main.py
```
This opens a Tkinter-based GUI where you can:
- Set number of qubits, Eve probability, test fraction
- Run a single trial or a batch of trials
- Sweep across multiple Eve probabilities
- Visualize Bloch spheres (Alice & Bob’s qubits)
- View plots of error rate vs Eve probability

### 2. Run Simulation Script

For a simple command-line run:
```bash
python bb84_simulation.py
```

---

---

## License

This project is licensed under the MIT License.

---

## Contributors

- [namanshetty25](https://github.com/namanshetty25)
- [VanshikaGupta001](https://github.com/VanshikaGupta001)
- [SiddhaNema](https://github.com/SiddhaNema)

---

For questions or support, please contact [namanshetty25](https://github.com/namanshetty25).
