import unittest
from qiskit import QuantumCircuit
from bb84.noise_simulation import (
    create_custom_noise_model,
    simulate_noisy_circuit,
    simulate_eavesdropping,
    simulate_lossy_channel
)


class TestNoiseSimulation(unittest.TestCase):
    def setUp(self):
        """
        Set up a basic QuantumCircuit and noise parameters for tests.
        """
        self.qc = QuantumCircuit(1, 1)
        self.qc.h(0)
        self.qc.measure(0, 0)
        self.noise_params = {
            "depolarizing_prob": 0.1,
            "amplitude_damping_prob": 0.05,
            "phase_damping_prob": 0.03,
            "include_readout_error": True,
            "readout_error_prob": 0.02,
        }

    def test_create_custom_noise_model(self):
        """
        Test that a noise model is created with the specified parameters.
        """
        noise_model = create_custom_noise_model(**self.noise_params)
        self.assertIsNotNone(noise_model, "Noise model should be created.")
        self.assertTrue(len(noise_model.quantum_errors) > 0, "Noise model should include quantum errors.")
        self.assertTrue(len(noise_model.readout_errors) > 0, "Noise model should include readout errors.")

    def test_simulate_noisy_circuit(self):
        """
        Test that a noisy circuit simulation returns valid results.
        """
        counts = simulate_noisy_circuit(self.qc, **self.noise_params, shots=100)
        self.assertIsInstance(counts, dict, "Simulation results should be a dictionary.")
        self.assertGreater(len(counts), 0, "Simulation results should not be empty.")

    def test_simulate_eavesdropping(self):
        """
        Test the eavesdropping simulation with random bases.
        """
        sender_bases = ['X', 'Z', 'X', 'Z', 'X']
        qubits = [QuantumCircuit(1, 1).h(0) for _ in range(len(sender_bases))]  # Prepare sample qubits
        eavesdropper_results = simulate_eavesdropping(sender_bases, qubits)
        self.assertEqual(len(eavesdropper_results), len(sender_bases), 
                         "Eavesdropper results should match the number of sender bases.")
        self.assertTrue(all(result in [0, 1] for result in eavesdropper_results), 
                        "Eavesdropper results should only contain 0 or 1.")

    def test_simulate_lossy_channel(self):
        """
        Test the simulation of a lossy channel where qubits can be dropped.
        """
        qubits = [QuantumCircuit(1, 1) for _ in range(10)]  # Create 10 qubits
        loss_prob = 0.3
        remaining_qubits = simulate_lossy_channel(qubits, loss_prob=loss_prob)
        self.assertLessEqual(len(remaining_qubits), len(qubits), 
                             "Number of remaining qubits should be less than or equal to the original number.")
        self.assertGreater(len(remaining_qubits), 0, 
                           "Some qubits should remain after loss simulation with moderate loss probability.")


if __name__ == "__main__":
    unittest.main()
