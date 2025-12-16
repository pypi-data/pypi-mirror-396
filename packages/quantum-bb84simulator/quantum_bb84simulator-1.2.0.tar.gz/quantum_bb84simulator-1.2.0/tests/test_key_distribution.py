import unittest
from bb84.key_distribution import BB84Simulation


class TestKeyDistribution(unittest.TestCase):
    def setUp(self):
        """
        Set up a default BB84Simulation object for tests.
        """
        self.simulation = BB84Simulation(key_length=10)

    def test_initialization(self):
        """
        Test the initialization of BB84Simulation.
        """
        self.assertEqual(len(self.simulation.sender_bases), 10, "Sender bases length should match key length.")
        self.assertEqual(len(self.simulation.sender_bits), 10, "Sender bits length should match key length.")
        self.assertEqual(len(self.simulation.receiver_bases), 10, "Receiver bases length should match key length.")

    def test_prepare_qubits(self):
        """
        Test the preparation of qubits based on sender bits and bases.
        """
        self.simulation.prepare_qubits()
        self.assertEqual(len(self.simulation.qubits), 10, "Number of prepared qubits should match key length.")
        for qubit in self.simulation.qubits:
            self.assertIsNotNone(qubit, "Each qubit should be initialized as a QuantumCircuit.")

    def test_measure_qubits_with_advanced_noise(self):
        """
        Test the measurement of qubits with noise applied.
        """
        self.simulation.prepare_qubits()
        self.simulation.measure_qubits_with_advanced_noise()
        self.assertEqual(len(self.simulation.receiver_results), 10, "Receiver results should match key length.")

    def test_sift_key(self):
        """
        Test the sifting process to retain bits where sender and receiver bases match.
        """
        self.simulation.prepare_qubits()
        self.simulation.measure_qubits_with_advanced_noise()
        self.simulation.sift_key()
        self.assertIsInstance(self.simulation.sifted_key, list, "Sifted key should be a list.")
        self.assertLessEqual(len(self.simulation.sifted_key), 10, 
                             "Sifted key length should be less than or equal to key length.")

    def test_run_protocol(self):
        """
        Test the full BB84 protocol to generate a sifted key.
        """
        sifted_key = self.simulation.run_protocol()
        self.assertIsInstance(sifted_key, str, "Sifted key should be returned as a string.")
        self.assertGreater(len(sifted_key), 0, "Sifted key should not be empty.")
        self.assertLessEqual(len(sifted_key), 10, "Sifted key length should be less than or equal to key length.")


if __name__ == "__main__":
    unittest.main()
