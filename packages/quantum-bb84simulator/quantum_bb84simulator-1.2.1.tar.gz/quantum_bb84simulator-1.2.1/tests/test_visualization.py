import unittest
import matplotlib.pyplot as plt
from bb84.visualization import visualize_protocol_workflow, visualize_noise_impact, visualize_key_sifting


class TestVisualization(unittest.TestCase):
    def test_visualize_protocol_workflow(self):
        """
        Test the visualization of the BB84 protocol workflow.
        """
        sender_bases = ['X', 'Z', 'X', 'Z', 'X']
        receiver_bases = ['X', 'X', 'Z', 'Z', 'X']
        sender_bits = [1, 0, 1, 0, 1]
        receiver_results = [1, 1, 0, 0, 1]

        # Ensure visualization does not raise exceptions
        try:
            visualize_protocol_workflow(sender_bases, receiver_bases, sender_bits, receiver_results)
        except Exception as e:
            self.fail(f"visualize_protocol_workflow raised an exception: {e}")

    def test_visualize_noise_impact(self):
        """
        Test the visualization of noise impact on keys.
        """
        original_key = "1101010101"
        noisy_key = "1101110100"

        # Ensure visualization does not raise exceptions
        try:
            visualize_noise_impact(original_key, noisy_key)
        except Exception as e:
            self.fail(f"visualize_noise_impact raised an exception: {e}")

    def test_visualize_key_sifting(self):
        """
        Test the visualization of key sifting.
        """
        sender_bases = ['X', 'Z', 'X', 'Z', 'X']
        receiver_bases = ['X', 'X', 'Z', 'Z', 'X']
        sifted_indices = [0, 4]

        # Ensure visualization does not raise exceptions
        try:
            visualize_key_sifting(sender_bases, receiver_bases, sifted_indices)
        except Exception as e:
            self.fail(f"visualize_key_sifting raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
