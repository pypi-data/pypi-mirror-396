import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error, phase_damping_error, ReadoutError


def simulate_eavesdropping(sender_bases, qubits, eavesdropper_bases=None):
    """
    Simulate an eavesdropper measuring qubits in random or specified bases.

    :param sender_bases: List of bases used by the sender ('X' or 'Z').
    :param qubits: List of QuantumCircuit objects representing the qubits.
    :param eavesdropper_bases: Optional list of bases used by the eavesdropper. If None, random bases are chosen.
    :return: List of eavesdropper's measurement results.
    """
    if eavesdropper_bases is None:
        eavesdropper_bases = np.random.choice(['X', 'Z'], len(sender_bases))

    eavesdrop_results = []
    simulator = AerSimulator()

    print("Eavesdropping in progress...")
    for i, (basis, qubit) in enumerate(zip(eavesdropper_bases, qubits)):
        qc = qubit.copy()
        if basis == 'X':
            qc.h(0)  # Transform to X basis
        qc.measure(0, 0)
        transpiled_qc = transpile(qc, simulator)
        result = simulator.run(transpiled_qc, shots=1).result()
        counts = result.get_counts()
        eavesdrop_results.append(int(list(counts.keys())[0]))
        print(f"Qubit {i}: Measured basis={basis}, Result={eavesdrop_results[-1]}")

    return eavesdrop_results


# Cache for created noise models
_cached_noise_models = {}


def create_custom_noise_model(
    depolarizing_prob=0.1,
    amplitude_damping_prob=0.05,
    phase_damping_prob=0.03,
    include_readout_error=False,
    readout_error_prob=0.02
):
    """
    Create a customizable noise model with multiple noise effects.
    Uses caching to prevent duplicate warnings and improve efficiency.

    :param depolarizing_prob: Probability of depolarizing error (default=0.1).
    :param amplitude_damping_prob: Probability of amplitude damping error (default=0.05).
    :param phase_damping_prob: Probability of phase damping error (default=0.03).
    :param include_readout_error: Boolean flag to include readout errors (default=False).
    :param readout_error_prob: Probability of readout error if enabled (default=0.02).
    :return: Configured NoiseModel.
    """
    cache_key = (
        depolarizing_prob,
        amplitude_damping_prob,
        phase_damping_prob,
        include_readout_error,
        readout_error_prob
    )

    if cache_key in _cached_noise_models:
        return _cached_noise_models[cache_key]

    noise_model = NoiseModel()

    # Add depolarizing error
    if depolarizing_prob > 0:
        dep_error = depolarizing_error(depolarizing_prob, 1)
        noise_model.add_all_qubit_quantum_error(dep_error, ['x', 'h', 'measure'])

    # Add amplitude damping error
    if amplitude_damping_prob > 0:
        amp_damp_error = amplitude_damping_error(amplitude_damping_prob)
        noise_model.add_all_qubit_quantum_error(amp_damp_error, ['x', 'h', 'measure'])

    # Add phase damping error
    if phase_damping_prob > 0:
        phase_damp_error = phase_damping_error(phase_damping_prob)
        noise_model.add_all_qubit_quantum_error(phase_damp_error, ['x', 'h', 'measure'])

    # Add readout error
    if include_readout_error and readout_error_prob > 0:
        readout_error = ReadoutError([
            [1 - readout_error_prob, readout_error_prob],
            [readout_error_prob, 1 - readout_error_prob]
        ])
        noise_model.add_all_qubit_readout_error(readout_error)

    _cached_noise_models[cache_key] = noise_model
    return noise_model


def simulate_noisy_circuit(
    circuit,
    depolarizing_prob=0.1,
    amplitude_damping_prob=0.05,
    phase_damping_prob=0.03,
    include_readout_error=False,
    readout_error_prob=0.02,
    shots=1024
):
    """
    Simulate a quantum circuit under a configurable noise model.

    :param circuit: QuantumCircuit to simulate.
    :param depolarizing_prob: Probability of depolarizing error.
    :param amplitude_damping_prob: Probability of amplitude damping error.
    :param phase_damping_prob: Probability of phase damping error.
    :param include_readout_error: Boolean flag to include readout errors.
    :param readout_error_prob: Probability of readout error if enabled.
    :param shots: Number of simulation shots (default=1024).
    :return: Simulation result counts.
    """
    noise_model = create_custom_noise_model(
        depolarizing_prob,
        amplitude_damping_prob,
        phase_damping_prob,
        include_readout_error,
        readout_error_prob
    )

    simulator = AerSimulator(noise_model=noise_model)
    transpiled_circuit = transpile(circuit, simulator)
    result = simulator.run(transpiled_circuit, shots=shots).result()
    return result.get_counts()


def simulate_lossy_channel(qubits, loss_prob=0.1):
    """
    Simulate a lossy channel where qubits can be randomly dropped.

    :param qubits: List of QuantumCircuit objects representing the qubits.
    :param loss_prob: Probability of a qubit being lost in transmission.
    :return: List of qubits after simulating loss.
    """
    return [qubit for qubit in qubits if np.random.random() > loss_prob]


def add_quantum_noise(bits, noise_type="depolarizing", probability=0.05):
    """
    Applies quantum noise to a bit sequence.
    """
    noisy_bits = bits.copy()
    noise_indices = np.random.rand(len(bits)) < probability

    if noise_type == "depolarizing":
        noisy_bits[noise_indices] = np.random.randint(0, 2, size=noise_indices.sum())
    elif noise_type == "amplitude_damping":
        noisy_bits[noise_indices] = 0  # Simulates energy loss
    elif noise_type == "phase_damping":
        noisy_bits[noise_indices] = bits[noise_indices]  # No bit flip, just decoherence

    return noisy_bits
