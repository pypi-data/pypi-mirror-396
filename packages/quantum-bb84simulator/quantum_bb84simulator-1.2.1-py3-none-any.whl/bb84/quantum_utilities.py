from qiskit import QuantumCircuit


def prepare_qubit(bit, basis):
    """
    Prepare a single qubit in the specified basis.

    :param bit: 0 or 1 for the qubit state.
    :param basis: 'X' or 'Z' for the basis.
    :return: Prepared QuantumCircuit.
    """
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == 'X':
        qc.h(0)
    return qc


def measure_qubit(circuit, basis):
    """
    Measure a single qubit in the specified basis.

    :param circuit: QuantumCircuit containing the qubit.
    :param basis: 'X' or 'Z' for the measurement basis.
    :return: QuantumCircuit with measurement added.
    """
    if basis == 'X':
        circuit.h(0)  # Transform to X basis before measurement
    circuit.measure(0, 0)
    return circuit


def copy_circuit(circuit):
    """
    Create a deep copy of a QuantumCircuit for use in simulations.

    :param circuit: QuantumCircuit to copy.
    :return: Copied QuantumCircuit.
    """
    return circuit.copy()


def add_noise_to_circuit(circuit, noise_model):
    """
    Apply a noise model to a given QuantumCircuit.

    :param circuit: QuantumCircuit to which noise will be applied.
    :param noise_model: NoiseModel object defining the noise.
    :return: Circuit with noise applied (if supported by the simulator).
    """
    # This is a placeholder function that can be enhanced as needed.
    # In practice, noise is simulated during execution rather than directly on the circuit.
    return circuit
