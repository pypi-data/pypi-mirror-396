"""
Three-Qubit Majority Vote BB84 Protocol Implementation.

Enhanced BB84 variant with:
- Three-qubit repetition encoding per logical bit
- Majority vote decoding for error correction
- Significantly reduced QBER at high noise levels

This protocol enables secure key distribution at noise levels
that would be insecure for standard BB84 (up to ~18-20% vs ~11%).

Reference: Balakrishnan et al., "Enhancing BB84 QKD under Depolarizing Noise"
"""

import numpy as np
from typing import List, Optional, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .base import BaseProtocol, ProtocolResult


class MajorityVoteBB84(BaseProtocol):
    """
    Three-Qubit Majority Vote BB84 quantum key distribution protocol.

    Key features:
    1. Each logical bit is encoded across THREE identical qubits
    2. Bob measures all three qubits individually
    3. Majority vote decoding: logical bit = majority of 3 measurements
    4. Synchronized bases for high sifting rate

    Error suppression mechanism:
    - Even if one qubit is corrupted by noise, the other two can
      "outvote" it to recover the correct bit
    - Effective QBER ≈ (3/2)p² for small p (vs p for standard BB84)
    - Enables key distribution at ~2x the noise threshold

    Attributes:
        protocol_name: "Three-Qubit Majority Vote BB84"
        qubits_per_bit: 3
    """

    protocol_name = "Three-Qubit Majority Vote BB84"
    qubits_per_bit = 3

    def __init__(
        self,
        seed: Optional[int] = None,
        base_match_prob: float = 0.9
    ):
        """
        Initialize Three-Qubit Majority Vote BB84 protocol.

        Args:
            seed: Random seed for reproducibility
            base_match_prob: Probability of basis match in synchronized mode
        """
        super().__init__(seed)
        self._simulator = AerSimulator()
        self.base_match_prob = base_match_prob

    def prepare_qubits(
        self,
        bits: np.ndarray,
        bases: np.ndarray
    ) -> List[QuantumCircuit]:
        """
        Prepare three-qubit blocks for each logical bit.

        Each logical bit is encoded in THREE identical qubits
        prepared in the same basis.

        Args:
            bits: Array of logical bits to encode
            bases: Array of bases for each bit

        Returns:
            List of QuantumCircuits (3 per bit, flattened)
        """
        circuits = []

        for bit, basis in zip(bits, bases):
            # Create three identical qubits for each logical bit
            for _ in range(3):
                qc = QuantumCircuit(1, 1)

                if bit == 1:
                    qc.x(0)

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
        Measure qubit triples with noise.

        Args:
            circuits: List of quantum circuits (3 per logical bit)
            bases: Array of measurement bases (1 per logical bit)
            noise_prob: Depolarizing noise probability

        Returns:
            Array of measurement results (3 per logical bit, flattened)
        """
        results = []

        noise_model = None
        if noise_prob > 0:
            noise_model = NoiseModel()
            error = depolarizing_error(noise_prob, 1)
            noise_model.add_all_qubit_quantum_error(error, ['x', 'h', 'measure'])

        simulator = AerSimulator(noise_model=noise_model) if noise_model else self._simulator

        for i, circuit in enumerate(circuits):
            basis = bases[i // 3]  # Same basis for all 3 qubits of a triple

            qc = circuit.copy()
            if basis == 'X':
                qc.h(0)
            qc.measure(0, 0)

            transpiled = transpile(qc, simulator)
            job = simulator.run(transpiled, shots=1)
            counts = job.result().get_counts()
            bit = int(list(counts.keys())[0])
            results.append(bit)

        return np.array(results)

    @staticmethod
    def majority_vote(bits: np.ndarray) -> int:
        """
        Apply majority vote decoding to a triple of bits.

        Args:
            bits: Array of 3 bits

        Returns:
            Majority bit value (0 or 1)
        """
        return 1 if np.sum(bits) >= 2 else 0

    def sift_key(
        self,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        alice_bits: np.ndarray,
        bob_results: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform sifting with majority vote decoding.

        For each logical bit:
        1. Check if bases match
        2. Apply majority vote to Bob's three measurements

        Args:
            alice_bases: Alice's basis choices (1 per logical bit)
            bob_bases: Bob's basis choices (1 per logical bit)
            alice_bits: Alice's original bits
            bob_results: Bob's measurement results (3 per logical bit)

        Returns:
            Tuple of (sifted_alice, sifted_bob, sifted_indices)
        """
        n_bits = len(alice_bits)
        sifted_alice = []
        sifted_bob = []
        sifted_indices = []

        for i in range(n_bits):
            # Check basis match
            if alice_bases[i] != bob_bases[i]:
                continue

            # Get Bob's triple measurements
            triple = bob_results[3*i : 3*i + 3]

            # Apply majority vote decoding
            decoded_bit = self.majority_vote(triple)

            sifted_alice.append(alice_bits[i])
            sifted_bob.append(decoded_bit)
            sifted_indices.append(i)

        return (
            np.array(sifted_alice),
            np.array(sifted_bob),
            np.array(sifted_indices)
        )

    def run(
        self,
        n_bits: int = 1000,
        noise_prob: float = 0.0,
        eavesdropper: bool = False,
        eve_interception_rate: float = 1.0,
        base_match_prob: Optional[float] = None,
        **kwargs
    ) -> ProtocolResult:
        """
        Run Three-Qubit Majority Vote BB84 protocol.

        Args:
            n_bits: Number of logical bits to transmit
            noise_prob: Depolarizing noise probability
            eavesdropper: Whether to simulate Eve
            eve_interception_rate: Fraction of qubits Eve intercepts
            base_match_prob: Override default basis match probability

        Returns:
            ProtocolResult with simulation data
        """
        from ..metrics import compute_qber, compute_kgr, theoretical_qber_majority_vote

        if base_match_prob is None:
            base_match_prob = self.base_match_prob

        # Generate Alice's random bits
        alice_bits = self.rng.integers(0, 2, size=n_bits)

        # Generate synchronized bases
        alice_bases, bob_bases = self._generate_bases(
            n_bits,
            synchronized=True,
            match_prob=base_match_prob
        )

        # Prepare triple qubits
        circuits = self.prepare_qubits(alice_bits, alice_bases)

        # Simulate eavesdropping if enabled
        eve_info = None
        if eavesdropper:
            circuits, eve_info = self._simulate_eavesdropping(
                circuits, np.repeat(alice_bases, 3), eve_interception_rate
            )

        # Bob measures qubits (3 per logical bit)
        bob_results = self.measure_qubits(circuits, bob_bases, noise_prob)

        # Sift key with majority vote decoding
        sifted_alice, sifted_bob, sifted_indices = self.sift_key(
            alice_bases, bob_bases, alice_bits, bob_results
        )

        # Calculate metrics
        qber = compute_qber(sifted_alice, sifted_bob)
        n_qubits_sent = n_bits * self.qubits_per_bit
        sifting_rate = len(sifted_alice) / n_bits if n_bits > 0 else 0.0
        kgr = compute_kgr(qber, sifting_rate, n_qubits_sent)

        # Calculate theoretical QBER for comparison
        theoretical_qber = theoretical_qber_majority_vote(noise_prob) if noise_prob > 0 else 0.0

        return ProtocolResult(
            protocol_name=self.protocol_name,
            n_bits=n_bits,
            n_qubits_sent=n_qubits_sent,
            raw_key_alice=alice_bits,
            raw_key_bob=bob_results,
            sifted_key_alice=sifted_alice,
            sifted_key_bob=sifted_bob,
            sifted_indices=sifted_indices,
            qber=qber,
            sifting_rate=sifting_rate,
            kgr=kgr,
            eavesdropper_present=eavesdropper,
            eve_information=eve_info,
            noise_prob=noise_prob,
            metadata={
                'base_match_prob': base_match_prob,
                'theoretical_qber': theoretical_qber,
                'qber_suppression_factor': noise_prob / qber if qber > 0 else float('inf')
            }
        )

    def analyze_triple_errors(
        self,
        alice_bits: np.ndarray,
        bob_results: np.ndarray,
        sifted_indices: np.ndarray
    ) -> dict:
        """
        Analyze error patterns within qubit triples.

        Useful for understanding how majority voting corrects errors.

        Args:
            alice_bits: Alice's original bits
            bob_results: Bob's raw measurements (3 per bit)
            sifted_indices: Indices of sifted bits

        Returns:
            Dict with error analysis statistics
        """
        error_counts = {0: 0, 1: 0, 2: 0, 3: 0}  # Number of errors per triple
        corrected_count = 0
        uncorrected_count = 0

        for idx in sifted_indices:
            alice_bit = alice_bits[idx]
            triple = bob_results[3*idx : 3*idx + 3]

            # Count raw errors in triple
            n_errors = np.sum(triple != alice_bit)
            error_counts[n_errors] += 1

            # Check if majority vote corrected the error
            decoded = self.majority_vote(triple)
            if n_errors > 0 and decoded == alice_bit:
                corrected_count += 1
            elif decoded != alice_bit:
                uncorrected_count += 1

        total = len(sifted_indices)
        return {
            'error_distribution': error_counts,
            'corrected_errors': corrected_count,
            'uncorrected_errors': uncorrected_count,
            'correction_rate': corrected_count / (corrected_count + uncorrected_count)
                              if (corrected_count + uncorrected_count) > 0 else 1.0,
            'total_triples': total
        }
