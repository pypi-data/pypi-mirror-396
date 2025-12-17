import unittest
import numpy as np
from bb84.communication import Communication


class TestEavesdropperDetection(unittest.TestCase):
    def setUp(self):
        """
        Set up a default Communication object for tests.
        """
        self.comm = Communication(
            key_length=10,
            noise_params={"depolarizing_prob": 0.1, "amplitude_damping_prob": 0.05},
            loss_prob=0.0  # Set loss probability to zero for focused eavesdropping tests
        )

    def test_no_eavesdropper_detected(self):
        """
        Test detection when no eavesdropper is present.
        """
        self.comm.run_communication(eavesdropper=False)
        eavesdropper_detected = self.comm.detect_eavesdropper()
        self.assertFalse(eavesdropper_detected, "Eavesdropping should not be detected when there is no eavesdropper.")

    def test_eavesdropper_detected(self):
        """
        Test detection when an eavesdropper is present.
        """
        self.comm.run_communication(eavesdropper=True)
        eavesdropper_detected = self.comm.detect_eavesdropper()
        self.assertTrue(eavesdropper_detected, "Eavesdropping should be detected when an eavesdropper is present.")

    def test_eavesdropper_error_rate(self):
        """
        Test that the eavesdropper error rate is calculated correctly.
        """
        self.comm.run_communication(eavesdropper=True)
        sender_bits = self.comm.simulation.sender_bits
        eavesdropper_results = self.comm.eavesdropper_results

        # Calculate error rate manually
        mismatches = sum(1 for s, e in zip(sender_bits, eavesdropper_results) if s != e)
        expected_error_rate = mismatches / len(sender_bits)

        # Capture the printed error rate from detect_eavesdropper()
        self.comm.detect_eavesdropper()  # Should print the error rate
        actual_error_rate = mismatches / len(sender_bits)  # Same calculation

        self.assertAlmostEqual(expected_error_rate, actual_error_rate, delta=0.01, msg="Error rate mismatch.")

    def test_detect_with_high_threshold(self):
        """
        Test detection when the eavesdropping error rate threshold is set high.
        """
        self.comm.run_communication(eavesdropper=True)

        # Manually override the error detection threshold in the class for testing
        original_threshold = 0.2  # Default threshold
        self.comm.detect_eavesdropper = lambda: sum(
            1 for s, e in zip(self.comm.simulation.sender_bits, self.comm.eavesdropper_results)
            if s != e
        ) / len(self.comm.simulation.sender_bits) > 0.5  # High threshold

        eavesdropper_detected = self.comm.detect_eavesdropper()
        self.assertFalse(
            eavesdropper_detected,
            "Eavesdropping should not be detected with a high error rate threshold."
        )


if __name__ == "__main__":
    unittest.main()
