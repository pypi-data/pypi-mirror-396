print("Package myqcc Loaded. Run qc.help() for list of functions.")

def linear_algebra_ops():
    print(r'''
# 2. Linear algebra, Vector Operations, Vector Multiplication, Tensor Product

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from qiskit.circuit.library import XGate
import numpy as np

# Define |0> and |1> as numpy arrays
zero = np.array([1, 0])
one = np.array([0, 1])

print("Zero state:", zero)
print("One state:", one)

# Vector addition
v_add = zero + one

# Scalar multiplication
v_scale = 2 * zero

# Inner (dot) product
inner_product = np.dot(zero, one)

print("Addition:", v_add)
print("Scalar * Vector:", v_scale)
print("Inner product <0|1>:", inner_product)

# Operator evolution
X_op = Operator(XGate())
state = Statevector(zero)
new_state = state.evolve(X_op)

print("Using Qiskit Operator:", new_state)

# Tensor product
sv1 = Statevector(zero)
sv2 = Statevector(one)
combined = sv1.tensor(sv2)

print("Tensor product using Qiskit:", combined)

tensor_state = combined
norm = np.linalg.norm(tensor_state)
print("Norm =", norm)
''')


def identity_matrix():
    print(r'''
# 3. Implementation of Identity Matrix 1Qubit, 2 Qubits, 3 Qubits

from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit
import numpy as np

# 1-qubit identity operator
I1 = Operator(np.eye(2))
print("1-qubit Identity:\n", I1.data)

# Create 2-qubit identity by tensoring two 1-qubit identities
I2 = I1.tensor(I1)
print("2-qubit Identity using Qiskit tensor:\n", I2.data)

# Create 3-qubit identity by tensoring three 1-qubit identities
I3 = I1.tensor(I1.tensor(I1))
print("3-qubit Identity using Qiskit tensor:\n", I3.data)
''')


def pauli_gates():
    print(r'''
# 4. Implementation of Pauli Gates

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# --- Pauli X ---
qc_x = QuantumCircuit(1, 1)
qc_x.x(0)
# Display circuit
print("Circuit X:")
print(qc_x.draw())

sv = Statevector.from_label('0')
result = sv.evolve(qc_x)
print("Result X:", result)

# --- Pauli Y ---
qc_y = QuantumCircuit(1, 1)
qc_y.y(0)
# Display circuit
print("Circuit Y:")
print(qc_y.draw())

sv = Statevector.from_label('0')
result = sv.evolve(qc_y)
print("Result Y:", result)

# --- Pauli Z ---
qc_z = QuantumCircuit(1, 1)
qc_z.z(0)
# Display circuit
print("Circuit Z:")
print(qc_z.draw())

sv = Statevector.from_label('0')
result = sv.evolve(qc_z)
print("Result Z:", result)
''')


def hadamard_gate():
    print(r'''
# 5. Implementation of Hadamard Gates

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Create a circuit
qc_h = QuantumCircuit(1, 1)
qc_h.h(0)

# Display circuit
print(qc_h.draw())

# Create |0> state
sv = Statevector.from_label('0')

# Apply Hadamard gate
result = sv.evolve(qc_h)

# Print the resulting statevector
print(result)
''')


def two_qubit_gates():
    print(r'''
# 6. Implementation of Two Qubit Gates

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# --- CNOT Gate ---
# Create a 2-qubit circuit
qc_cx = QuantumCircuit(2, 2)

# Apply CNOT (control = qubit 0, target = qubit 1)
qc_cx.cx(0, 1)

# Display circuit
print("CNOT Circuit:")
print(qc_cx.draw())

# Initial state |00>
sv = Statevector.from_label('00')

# Evolve under CNOT
result = sv.evolve(qc_cx)
print(result)

# --- SWAP Gate ---
# Create a 2-qubit circuit
qc_swap = QuantumCircuit(2)
qc_swap.swap(0, 1)

# Display circuit
print("SWAP Circuit:")
print(qc_swap.draw())

sv = Statevector.from_label('10') # qubit 0=1, qubit 1=0
result = sv.evolve(qc_swap)
print(result)
''')


def three_qubit_gates():
    print(r'''
# 7. Implementation of Three Qubit Gates

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# --- Toffoli Gate Implementation ---

# Create a 3-qubit circuit
qc_toffoli = QuantumCircuit(3)

# Apply Toffoli gate: controls (0,1), target (2)
qc_toffoli.ccx(0, 1, 2)

# Display circuit
print("Toffoli Circuit:")
print(qc_toffoli.draw())

# Create initial state |110> (controls = 1,1; target = 0)
sv = Statevector.from_label('110')

# Evolve state under Toffoli gate
result = sv.evolve(qc_toffoli)
print(result)

# --- Fredkin Gate Implementation ---

# Create a 3-qubit circuit
qc_fredkin = QuantumCircuit(3)

# Apply Fredkin gate: control (0), swap between (1, 2)
qc_fredkin.cswap(0, 1, 2)

# Display circuit
print("Fredkin Circuit:")
print(qc_fredkin.draw())

# Create initial state |101> (control = 1; swap targets = 0 and 1)
sv = Statevector.from_label('101')

# Evolve state under Fredkin gate
result = sv.evolve(qc_fredkin)
print(result)
''')


def circuit_formation_1():
    print(r'''
# 8. Implementation of Circuit Formation-1

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# -- Step 1: Create a circuit with 3 qubits and 3 classical bits
qc = QuantumCircuit(3, 3)

# -- Step 2: Apply some basic gates
qc.x(0)      # Apply Pauli-X (NOT) on qubit 0
qc.h(1)      # Apply Hadamard on qubit 1
qc.cx(1, 2)  # CNOT with control qubit 1 target qubit 2

# --- Step 3: Measure all qubits
qc.measure([0, 1, 2], [0, 1, 2])

# --- Step 4: Draw the circuit
print(qc.draw())

# Initialize simulator
sim = AerSimulator()

# Transpile for simulator
compiled_circuit = transpile(qc, sim)

# Run the simulation
result = sim.run(compiled_circuit, shots=1024).result()

# Get counts
counts = result.get_counts()
print(counts)

# Note: plot_histogram(counts) requires a display environment.
''')


def circuit_formation_2():
    print(r'''
# 9. Implementation of Circuit Formation-2

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# --- Step 1: Create a 3-qubit, 3-classical-bit circuit
qc = QuantumCircuit(3, 3)

# --- Step 2: Apply gates
qc.h(0)          # Put qubit 0 into superposition
qc.cx(0, 1)      # CNOT: control=0, target=1 (entangle qubit 1)
qc.ccx(0, 1, 2)  # Toffoli gate: controls=0,1 target=2 (3-qubit interaction)

# --- Step 3: Measure all qubits
qc.measure([0, 1, 2], [0, 1, 2])

# --- Step 4: Draw the circuit
print(qc.draw())

# Initialize simulator
sim = AerSimulator()

# Transpile the circuit for the simulator
compiled_circuit = transpile(qc, sim)

# Run the simulation
result = sim.run(compiled_circuit, shots=1024).result()

# Get measurement counts
counts = result.get_counts()
print(counts)

# Note: plot_histogram(counts) requires a display environment.
''')


def all():
    print("="*50)
    print(" PRINTING ALL QISKIT CODES ")
    print("="*50)
    print("\n--- LINEAR_ALGEBRA_OPS ---\n")
    linear_algebra_ops()
    print("-" * 50)
    print("\n--- IDENTITY_MATRIX ---\n")
    identity_matrix()
    print("-" * 50)
    print("\n--- PAULI_GATES ---\n")
    pauli_gates()
    print("-" * 50)
    print("\n--- HADAMARD_GATE ---\n")
    hadamard_gate()
    print("-" * 50)
    print("\n--- TWO_QUBIT_GATES ---\n")
    two_qubit_gates()
    print("-" * 50)
    print("\n--- THREE_QUBIT_GATES ---\n")
    three_qubit_gates()
    print("-" * 50)
    print("\n--- CIRCUIT_FORMATION_1 ---\n")
    circuit_formation_1()
    print("-" * 50)
    print("\n--- CIRCUIT_FORMATION_2 ---\n")
    circuit_formation_2()
    print("-" * 50)


def help():
    print("\nAvailable Commands:")
    print("-------------------")
    methods = [
        'linear_algebra_ops',
        'identity_matrix',
        'pauli_gates',
        'hadamard_gate',
        'two_qubit_gates',
        'three_qubit_gates',
        'circuit_formation_1',
        'circuit_formation_2',
    ]
    for m in methods:
        print(f"qc.{m}()")
    print("\nSpecial:")
    print("qc.all()")
    print("qc.help()")
