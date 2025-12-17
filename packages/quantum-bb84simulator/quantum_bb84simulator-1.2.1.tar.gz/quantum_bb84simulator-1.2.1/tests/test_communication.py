import unittest
import numpy as np
from bb84 import Communication, simulate_eavesdropping, generate_toeplitz_matrix


class TestCommunication(unittest.TestCase):
    def setUp(self):
        self.comm = Communication(
            key_length=10, noise_params={"depolarizing_prob": 0.1}, loss_prob=0.1
        )

    def test_run_communication(self):
        sifted_key = self.comm.run_communication()
        self.assertIsNotNone(sifted_key)
        self.assertTrue(len(sifted_key) <= self.comm.simulation.key_length)

    def test_run_communication_with_eavesdropper(self):
        sifted_key = self.comm.run_communication(eavesdropper=simulate_eavesdropping)
        self.assertIsNotNone(sifted_key)
        self.assertTrue(len(sifted_key) <= self.comm.simulation.key_length)

    def test_detect_eavesdropper(self):
        self.comm.run_communication(eavesdropper=simulate_eavesdropping)
        eavesdropper_detected = self.comm.detect_eavesdropper()
        self.assertIsInstance(eavesdropper_detected, bool)

    def test_error_correction(self):
        self.comm.run_communication()
        error_matrix = np.eye(
            len(self.comm.sifted_key), dtype=int
        )  # Identity matrix for simple parity check
        corrected_key = self.comm.apply_error_correction(error_matrix)
        self.assertIsNotNone(corrected_key)
        self.assertEqual(len(corrected_key), len(self.comm.sifted_key))

    def test_privacy_amplification(self):
        self.comm.run_communication()
        hash_matrix = generate_toeplitz_matrix(
            len(self.comm.sifted_key), len(self.comm.sifted_key) // 2
        )
        final_key = self.comm.apply_privacy_amplification(hash_matrix)
        self.assertIsNotNone(final_key)
        self.assertLess(len(final_key), len(self.comm.sifted_key))


if __name__ == "__main__":
    unittest.main()
