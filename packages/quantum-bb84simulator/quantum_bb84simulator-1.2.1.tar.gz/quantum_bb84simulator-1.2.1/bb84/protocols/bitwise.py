"""
Bitwise BB84 Protocol Implementation.

Enhanced BB84 variant with:
- Synchronized basis selection (~90% match rate)
- Duplicate qubit encoding for error detection
- Discards mismatched duplicate pairs

Reference: Balakrishnan et al., "Enhancing BB84 QKD under Depolarizing Noise"
"""

import numpy as np
from typing import List, Optional, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .base import BaseProtocol, ProtocolResult


class BitwiseBB84(BaseProtocol):
    """
    Bitwise BB84 quantum key distribution protocol.

    Enhancements over standard BB84:
    1. Synchronized basis selection: Alice and Bob use a pre-shared
       pseudo-random basis sequence, achieving ~90% basis match rate
    2. Duplicate qubit encoding: Each bit is encoded in two identical
       qubits sent consecutively
    3. Error detection: Bob compares duplicate measurements and discards
       pairs with discrepancies

    This improves key generation rate at low noise but uses 2x qubits.

    Attributes:
        protocol_name: "Bitwise BB84"
        qubits_per_bit: 2
        base_match_prob: Probability of synchronized basis match (default 0.9)
    """

    protocol_name = "Bitwise BB84"
    qubits_per_bit = 2

    def __init__(
        self,
        seed: Optional[int] = None,
        base_match_prob: float = 0.9
    ):
        """
        Initialize Bitwise BB84 protocol.

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
        Prepare duplicate qubit pairs for each bit.

        Each logical bit is encoded in TWO identical qubits
        prepared in the same basis.

        Args:
            bits: Array of bits to encode
            bases: Array of bases for each bit

        Returns:
            List of QuantumCircuits (2 per bit, flattened)
        """
        circuits = []

        for bit, basis in zip(bits, bases):
            # Create two identical qubits for each bit
            for _ in range(2):
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
        Measure qubit pairs with noise.

        Args:
            circuits: List of quantum circuits (2 per logical bit)
            bases: Array of measurement bases (1 per logical bit)
            noise_prob: Depolarizing noise probability

        Returns:
            Array of measurement results (2 per logical bit, flattened)
        """
        results = []

        noise_model = None
        if noise_prob > 0:
            noise_model = NoiseModel()
            error = depolarizing_error(noise_prob, 1)
            noise_model.add_all_qubit_quantum_error(error, ['x', 'h', 'measure'])

        simulator = AerSimulator(noise_model=noise_model) if noise_model else self._simulator

        # Each logical bit has 2 qubits, bases has 1 entry per logical bit
        for i, circuit in enumerate(circuits):
            basis = bases[i // 2]  # Same basis for both qubits of a pair

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

    def sift_key(
        self,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        alice_bits: np.ndarray,
        bob_results: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform bitwise sifting with duplicate filtering.

        Two-stage sifting:
        1. Keep only bits where bases match
        2. Among matched bits, discard pairs where the two
           duplicate measurements disagree

        Args:
            alice_bases: Alice's basis choices (1 per logical bit)
            bob_bases: Bob's basis choices (1 per logical bit)
            alice_bits: Alice's original bits
            bob_results: Bob's measurement results (2 per logical bit)

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

            # Get Bob's duplicate measurements
            bob_bit1 = bob_results[2 * i]
            bob_bit2 = bob_results[2 * i + 1]

            # Check if duplicates agree (error detection)
            if bob_bit1 != bob_bit2:
                # Discrepancy detected - discard this bit
                continue

            # Both checks passed - keep this bit
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bit1)  # Use first (both are same)
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
        Run Bitwise BB84 protocol.

        Args:
            n_bits: Number of logical bits to transmit
            noise_prob: Depolarizing noise probability
            eavesdropper: Whether to simulate Eve
            eve_interception_rate: Fraction of qubits Eve intercepts
            base_match_prob: Override default basis match probability

        Returns:
            ProtocolResult with simulation data
        """
        from ..metrics import compute_qber, compute_kgr

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

        # Prepare duplicate qubits
        circuits = self.prepare_qubits(alice_bits, alice_bases)

        # Simulate eavesdropping if enabled
        eve_info = None
        if eavesdropper:
            circuits, eve_info = self._simulate_eavesdropping(
                circuits, np.repeat(alice_bases, 2), eve_interception_rate
            )

        # Bob measures qubits (2 per logical bit)
        bob_results = self.measure_qubits(circuits, bob_bases, noise_prob)

        # Sift key with duplicate filtering
        sifted_alice, sifted_bob, sifted_indices = self.sift_key(
            alice_bases, bob_bases, alice_bits, bob_results
        )

        # Calculate metrics
        qber = compute_qber(sifted_alice, sifted_bob)
        n_qubits_sent = n_bits * self.qubits_per_bit
        sifting_rate = len(sifted_alice) / n_bits if n_bits > 0 else 0.0
        kgr = compute_kgr(qber, sifting_rate, n_qubits_sent)

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
                'duplicates_discarded': n_bits - len(sifted_alice)
            }
        )
