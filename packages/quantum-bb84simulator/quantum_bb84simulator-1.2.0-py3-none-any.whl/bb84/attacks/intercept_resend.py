"""
Intercept-Resend Attack Implementation.

In this attack, Eve:
1. Intercepts qubits in transit
2. Measures in a random basis (Z or X)
3. Prepares new qubits based on measurement results
4. Sends the new qubits to Bob

This introduces ~25% error rate on intercepted qubits when Eve
chooses the wrong basis, enabling detection.

Reference: Balakrishnan et al., "Enhancing BB84 QKD under Depolarizing Noise"
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


@dataclass
class AttackResult:
    """Container for attack simulation results."""
    intercepted_indices: np.ndarray
    eve_bases: np.ndarray
    eve_measurements: np.ndarray
    n_intercepted: int
    interception_rate: float

    def eve_information_gain(self, alice_bits: np.ndarray, alice_bases: np.ndarray) -> float:
        """
        Calculate Eve's information gain.

        Eve gains full information when her basis matches Alice's.
        """
        if self.n_intercepted == 0:
            return 0.0

        correct_basis = self.eve_bases[self.intercepted_indices] == alice_bases[self.intercepted_indices]
        return np.sum(correct_basis) / self.n_intercepted


class InterceptResendAttack:
    """
    Intercept-Resend eavesdropping attack on BB84.

    Eve intercepts qubits, measures them, and resends based on her results.
    This is the canonical BB84 attack that the protocol is designed to detect.
    """

    def __init__(self, interception_rate: float = 1.0, seed: Optional[int] = None):
        """
        Initialize attack.

        Args:
            interception_rate: Fraction of qubits Eve intercepts (0.0 to 1.0)
            seed: Random seed for reproducibility
        """
        self.interception_rate = interception_rate
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._simulator = AerSimulator()

    def attack(
        self,
        circuits: List[QuantumCircuit],
        alice_bases: Optional[np.ndarray] = None
    ) -> Tuple[List[QuantumCircuit], AttackResult]:
        """
        Execute intercept-resend attack on quantum circuits.

        Args:
            circuits: List of quantum circuits representing transmitted qubits
            alice_bases: Alice's bases (Eve doesn't know these, used for analysis)

        Returns:
            Tuple of (modified_circuits, AttackResult)
        """
        n_qubits = len(circuits)

        # Determine which qubits to intercept
        intercept_mask = self.rng.random(n_qubits) < self.interception_rate
        intercepted_indices = np.where(intercept_mask)[0]

        # Eve chooses random bases (she doesn't know Alice's bases)
        eve_bases = self.rng.choice(['Z', 'X'], size=n_qubits)

        # Initialize results
        eve_measurements = np.full(n_qubits, -1)  # -1 = not intercepted

        modified_circuits = []

        for i, circuit in enumerate(circuits):
            if not intercept_mask[i]:
                # Not intercepted - pass through unchanged
                modified_circuits.append(circuit)
                continue

            # Eve intercepts and measures
            eve_circuit = circuit.copy()
            if eve_bases[i] == 'X':
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)

            # Execute measurement
            transpiled = transpile(eve_circuit, self._simulator)
            result = self._simulator.run(transpiled, shots=1).result()
            eve_bit = int(list(result.get_counts().keys())[0])
            eve_measurements[i] = eve_bit

            # Eve prepares replacement qubit
            new_circuit = QuantumCircuit(1, 1)
            if eve_bit == 1:
                new_circuit.x(0)
            if eve_bases[i] == 'X':
                new_circuit.h(0)

            modified_circuits.append(new_circuit)

        attack_result = AttackResult(
            intercepted_indices=intercepted_indices,
            eve_bases=eve_bases,
            eve_measurements=eve_measurements,
            n_intercepted=len(intercepted_indices),
            interception_rate=len(intercepted_indices) / n_qubits if n_qubits > 0 else 0.0
        )

        return modified_circuits, attack_result


def apply_intercept_resend(
    circuits: List[QuantumCircuit],
    interception_rate: float = 1.0,
    seed: Optional[int] = None
) -> Tuple[List[QuantumCircuit], AttackResult]:
    """
    Convenience function to apply intercept-resend attack.

    Args:
        circuits: Quantum circuits to attack
        interception_rate: Fraction to intercept
        seed: Random seed

    Returns:
        Tuple of (modified_circuits, AttackResult)
    """
    attack = InterceptResendAttack(interception_rate=interception_rate, seed=seed)
    return attack.attack(circuits)


def theoretical_error_rate_with_eve(
    noise_prob: float,
    interception_rate: float = 1.0
) -> float:
    """
    Calculate theoretical QBER with Eve present.

    When Eve intercepts and measures in wrong basis (50% of time),
    she introduces 25% error on those qubits.

    Args:
        noise_prob: Channel depolarizing noise probability
        interception_rate: Fraction Eve intercepts

    Returns:
        Expected QBER
    """
    # Error from noise (on all qubits)
    noise_error = noise_prob

    # Error from Eve (25% on intercepted qubits due to wrong basis 50% of time)
    eve_error = interception_rate * 0.25

    # Combined (simplified - assumes independent)
    # More accurate would account for overlap
    total_error = noise_error + eve_error - noise_error * eve_error

    return min(total_error, 0.5)
