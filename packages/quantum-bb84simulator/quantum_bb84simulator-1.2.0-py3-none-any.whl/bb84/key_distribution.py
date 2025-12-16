import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from .noise_simulation import simulate_noisy_circuit


class BB84Simulation:
    def __init__(self, key_length=10):
        """
        Initialize the BB84 simulation parameters.

        :param key_length: Number of bits to generate for the key.
        """
        self.key_length = key_length
        self.sender_bases = np.random.choice(['X', 'Z'], size=key_length)
        self.sender_bits = np.random.choice([0, 1], size=key_length)
        self.receiver_bases = np.random.choice(['X', 'Z'], size=key_length)
        self.receiver_results = []
        self.sifted_key = []
        self.qubits = None

    def prepare_qubits(self):
        """
        Prepare qubits based on sender's random bits and bases.
        """
        print("Preparing qubits...")
        self.qubits = []
        for bit, basis in zip(self.sender_bits, self.sender_bases):
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.x(0)  # Apply X gate for a 1
            if basis == 'X':
                qc.h(0)  # Apply H gate for the X basis
            self.qubits.append(qc)
        print("Qubits prepared.")

    def measure_qubits_with_advanced_noise(
        self,
        depolarizing_prob=0.1,
        amplitude_damping_prob=0.05,
        phase_damping_prob=0.03,
        include_readout_error=False,
        readout_error_prob=0.02
    ):
        """
        Measure qubits under a configurable noise model.

        :param depolarizing_prob: Probability of depolarizing error.
        :param amplitude_damping_prob: Probability of amplitude damping error.
        :param phase_damping_prob: Probability of phase damping error.
        :param include_readout_error: Boolean to include readout errors.
        :param readout_error_prob: Probability of readout error.
        """
        if self.qubits is None:
            raise ValueError("Qubits have not been prepared. Call prepare_qubits() first.")

        print("Measuring qubits with noise...")
        self.receiver_results = []
        for qubit, basis in zip(self.qubits, self.receiver_bases):
            if basis == 'X':
                qubit.h(0)  # Transform to X basis
            qubit.measure(0, 0)
            counts = simulate_noisy_circuit(
                qubit,
                depolarizing_prob=depolarizing_prob,
                amplitude_damping_prob=amplitude_damping_prob,
                phase_damping_prob=phase_damping_prob,
                include_readout_error=include_readout_error,
                readout_error_prob=readout_error_prob,
                shots=1
            )
            self.receiver_results.append(int(list(counts.keys())[0]))
        print("Qubits measured.")

    def sift_key(self):
        """
        Sift the key by comparing sender's and receiver's bases.
        Only keep bits where the bases match.
        """
        if not self.receiver_results:
            raise ValueError("Receiver results are not available. Measure qubits first.")

        print("Sifting key...")
        self.sifted_key = [
            sr for sb, rb, sr in zip(self.sender_bases, self.receiver_bases, self.receiver_results) if sb == rb
        ]
        print("Sifted key:", ''.join(map(str, self.sifted_key)))
        return self.sifted_key


    def run_protocol(self, noise_params=None):
        """
        Run the complete BB84 protocol and return the sifted key.

        :param noise_params: Dictionary of noise parameters.
        :return: Sifted key as a string.
        """
        print("Running BB84 protocol...")
        self.prepare_qubits()
        self.measure_qubits_with_advanced_noise(**(noise_params or {}))
        self.sift_key()
        return ''.join(map(str, self.sifted_key))

    def simulate_communication(self, eavesdropper=None):
        """
        Simulate the full BB84 communication process between Alice and Bob.

        :param eavesdropper: Callable function representing Eve's behavior (default=None).
                            Example: simulate_eavesdropping(sender_bases, qubits).
        :return: Sifted key as a string.
        """
        print("Simulating communication...")
        self.prepare_qubits()

        # Step 2: Eavesdropper intercepts qubits (if present)
        if eavesdropper:
            print("Eavesdropping in progress...")
            intercepted_qubits = eavesdropper(self.sender_bases, self.qubits)
            print("Eavesdropper Results:", intercepted_qubits)

        # Step 3: Bob measures the (potentially intercepted) qubits
        self.measure_qubits_with_advanced_noise()

        # Step 4: Sift the key
        self.sift_key()
        return ''.join(map(str, self.sifted_key))

    def run_bb84_on_ibm():
        """
        Runs a BB84 quantum circuit on IBM Qiskit simulator.
        """
        simulator = AerSimulator()

        circuit = QuantumCircuit(1, 1)
        circuit.h(0)
        circuit.measure(0, 0)

        transpiled = transpile(circuit, simulator)
        job = simulator.run(transpiled, shots=1024)
        results = job.result().get_counts()

        return results
