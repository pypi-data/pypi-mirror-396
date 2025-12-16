import numpy as np
from sklearn.ensemble import IsolationForest
from .key_distribution import BB84Simulation
from .noise_simulation import simulate_eavesdropping
from .error_correction import ldpc_error_correction, privacy_amplification


class Communication:
    def __init__(self, key_length=10, noise_params=None, loss_prob=0.0):
        """
        Initialize the communication process between Alice and Bob.

        :param key_length: Number of bits to generate for the key.
        :param noise_params: Parameters for noise simulation.
        :param loss_prob: Probability of qubit loss during transmission.
        """
        self.simulation = BB84Simulation(key_length=key_length)
        self.noise_params = noise_params or {}
        self.loss_prob = loss_prob
        self.eavesdropper_results = None
        self.sifted_key = None
        self.key_length = key_length  # Ensure key_length is defined

    def run_communication(self, eavesdropper=None):
        """
        Simulate the communication process between Alice and Bob.

        :param eavesdropper: Callable function for eavesdropping simulation (default=None).
        :return: Sifted key as a string.
        """
        # Step 1: Alice prepares the qubits
        self.simulation.prepare_qubits()

        # Step 2: Eavesdropper intercepts (if enabled)
        if eavesdropper:
            self.eavesdropper_results = eavesdropper(
                self.simulation.sender_bases, self.simulation.qubits
            )

        # Step 3: Bob measures the qubits
        self.simulation.measure_qubits_with_advanced_noise(**self.noise_params)

        # Step 4: Alice and Bob sift the key
        self.simulation.sift_key()
        self.sifted_key = self.simulation.sifted_key
        return ''.join(map(str, self.sifted_key))

    def detect_eavesdropper(self):
        """
        Detect the presence of an eavesdropper based on key discrepancies.

        :return: Boolean indicating whether eavesdropping is detected.
        """
        if self.eavesdropper_results is None:
            print("No eavesdropper was simulated.")
            return False

        mismatches = sum(
            1 for a, b in zip(self.simulation.sender_bits, self.eavesdropper_results) if a != b
        )
        error_rate = mismatches / len(self.simulation.sender_bits)
        print(f"Eavesdropper Error Rate: {error_rate:.2f}")
        return error_rate > 0.2  # Threshold for detecting eavesdropping

    def apply_error_correction(self, error_matrix):
        """
        Apply LDPC error correction to the sifted key.

        :param error_matrix: Pre-defined parity-check matrix.
        :return: Error-corrected key.
        """
        if self.sifted_key is None:
            raise ValueError("No sifted key available. Run the communication first.")
        return ldpc_error_correction(self.sifted_key, error_matrix)

    def apply_privacy_amplification(self, hash_matrix):
        """
        Apply privacy amplification to the sifted key.

        :param hash_matrix: Toeplitz matrix for hashing.
        :return: Privacy-amplified key.
        """
        if self.sifted_key is None:
            raise ValueError("No sifted key available. Run the communication first.")
        return privacy_amplification(self.sifted_key, hash_matrix)


def ai_detect_eavesdropper(alice_key, bob_key):
    """
    Detects an eavesdropper using an Isolation Forest anomaly detection algorithm.

    :param alice_key: Alice's sifted key bits
    :param bob_key: Bob's sifted key bits
    :return: Boolean indicating whether anomalies (potential eavesdropping) detected
    """
    key_diffs = np.array([int(a != b) for a, b in zip(alice_key, bob_key)]).reshape(-1, 1)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(key_diffs)

    anomalies = model.predict(key_diffs)
    return np.any(anomalies == -1)
