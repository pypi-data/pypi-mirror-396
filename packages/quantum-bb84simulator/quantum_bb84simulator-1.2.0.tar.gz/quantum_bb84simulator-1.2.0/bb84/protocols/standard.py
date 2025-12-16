"""
Standard BB84 Protocol Implementation.

The original BB84 protocol as proposed by Bennett and Brassard (1984).
- Single qubit per bit encoding
- Random independent basis choices (Z or X)
- ~50% sifting loss due to basis mismatches
"""

import numpy as np
from typing import List, Optional, Any
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .base import BaseProtocol


class StandardBB84(BaseProtocol):
    """
    Standard BB84 quantum key distribution protocol.

    In this protocol:
    - Alice encodes each bit in a randomly chosen basis (Z or X)
    - Bob measures each qubit in a randomly chosen basis
    - After transmission, they publicly compare bases and keep only
      matching measurements (~50% retention)

    Attributes:
        protocol_name: "Standard BB84"
        qubits_per_bit: 1
    """

    protocol_name = "Standard BB84"
    qubits_per_bit = 1

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize Standard BB84 protocol.

        Args:
            seed: Random seed for reproducibility
        """
        super().__init__(seed)
        self._simulator = AerSimulator()

    def prepare_qubits(
        self,
        bits: np.ndarray,
        bases: np.ndarray
    ) -> List[QuantumCircuit]:
        """
        Prepare single-qubit states for each bit.

        Encoding:
        - Z basis: |0⟩ for bit 0, |1⟩ for bit 1
        - X basis: |+⟩ for bit 0, |-⟩ for bit 1

        Args:
            bits: Array of bits (0 or 1) to encode
            bases: Array of bases ('Z' or 'X') for each bit

        Returns:
            List of prepared QuantumCircuits
        """
        circuits = []
        for bit, basis in zip(bits, bases):
            qc = QuantumCircuit(1, 1)

            # Encode bit value
            if bit == 1:
                qc.x(0)

            # Apply basis transformation
            if basis == 'X':
                qc.h(0)

            circuits.append(qc)

        return circuits

    def measure_qubits(
        self,
        circuits: List[QuantumCircuit],
        bases: np.ndarray,
        noise_prob: float = 0.0
    ) -> np.ndarray:
        """
        Measure qubits in given bases with optional depolarizing noise.

        Args:
            circuits: List of quantum circuits to measure
            bases: Array of measurement bases ('Z' or 'X')
            noise_prob: Depolarizing noise probability (0.0 to 1.0)

        Returns:
            Array of measurement results (0 or 1)
        """
        results = []

        # Create noise model if needed
        noise_model = None
        if noise_prob > 0:
            noise_model = NoiseModel()
            error = depolarizing_error(noise_prob, 1)
            noise_model.add_all_qubit_quantum_error(error, ['x', 'h', 'measure'])

        simulator = AerSimulator(noise_model=noise_model) if noise_model else self._simulator

        for circuit, basis in zip(circuits, bases):
            # Copy circuit to avoid modifying original
            qc = circuit.copy()

            # Apply basis transformation for measurement
            if basis == 'X':
                qc.h(0)

            qc.measure(0, 0)

            # Execute and get result
            transpiled = transpile(qc, simulator)
            job = simulator.run(transpiled, shots=1)
            counts = job.result().get_counts()
            bit = int(list(counts.keys())[0])
            results.append(bit)

        return np.array(results)

    def sift_key(
        self,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        alice_bits: np.ndarray,
        bob_results: np.ndarray
    ) -> tuple:
        """
        Perform standard basis sifting.

        Keep only bits where Alice and Bob used the same basis.

        Args:
            alice_bases: Alice's basis choices
            bob_bases: Bob's basis choices
            alice_bits: Alice's original bits
            bob_results: Bob's measurement results

        Returns:
            Tuple of (sifted_alice, sifted_bob, sifted_indices)
        """
        # Find matching bases
        matching = alice_bases == bob_bases
        sifted_indices = np.where(matching)[0]

        sifted_alice = alice_bits[matching]
        sifted_bob = bob_results[matching]

        return sifted_alice, sifted_bob, sifted_indices

    def run(
        self,
        n_bits: int = 1000,
        noise_prob: float = 0.0,
        eavesdropper: bool = False,
        eve_interception_rate: float = 1.0,
        **kwargs
    ):
        """
        Run Standard BB84 protocol.

        Args:
            n_bits: Number of bits to transmit
            noise_prob: Depolarizing noise probability
            eavesdropper: Whether to simulate Eve
            eve_interception_rate: Fraction of qubits Eve intercepts
            **kwargs: Additional arguments (ignored for standard BB84)

        Returns:
            ProtocolResult with simulation data
        """
        # Standard BB84 uses random independent bases
        return super().run(
            n_bits=n_bits,
            noise_prob=noise_prob,
            eavesdropper=eavesdropper,
            eve_interception_rate=eve_interception_rate,
            synchronized_bases=False,  # Always random for standard BB84
            base_match_prob=0.5
        )
