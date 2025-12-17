import unittest
import numpy as np
from bb84.error_correction import ldpc_error_correction, privacy_amplification, generate_toeplitz_matrix


class TestErrorCorrection(unittest.TestCase):
    def setUp(self):
        """
        Set up a sifted key and test matrices for error correction and privacy amplification.
        """
        self.sifted_key = "1101010101"
        self.parity_check_matrix = np.array([
            [1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 0, 1, 0, 0, 1, 0, 0]
        ])
        self.hash_matrix = generate_toeplitz_matrix(10, 5)

    def test_ldpc_error_correction(self):
        """
        Test LDPC error correction using a parity-check matrix.
        """
        corrected_key = ldpc_error_correction(self.sifted_key, self.parity_check_matrix)
        self.assertEqual(len(corrected_key), self.parity_check_matrix.shape[0], 
                         "Corrected key length should match the number of rows in the parity-check matrix.")
        self.assertIsInstance(corrected_key, str, "Corrected key should be a string.")

    def test_privacy_amplification(self):
        """
        Test privacy amplification using a Toeplitz hash matrix.
        """
        final_key = privacy_amplification(self.sifted_key, self.hash_matrix)
        self.assertEqual(len(final_key), self.hash_matrix.shape[0], 
                         "Final key length should match the number of rows in the hash matrix.")
        self.assertIsInstance(final_key, str, "Final key should be a string.")

    def test_generate_toeplitz_matrix(self):
        """
        Test the generation of a Toeplitz matrix.
        """
        rows, cols = 5, 10
        toeplitz_matrix = generate_toeplitz_matrix(cols, rows)
        self.assertEqual(toeplitz_matrix.shape, (rows, cols), 
                         "Toeplitz matrix dimensions should match the specified rows and columns.")
        self.assertTrue((toeplitz_matrix == 0).sum() + (toeplitz_matrix == 1).sum() == rows * cols, 
                        "Toeplitz matrix should only contain binary values (0 or 1).")


if __name__ == "__main__":
    unittest.main()
