"""
Base protocol class defining the common interface for all BB84 variants.

All protocol implementations inherit from BaseProtocol and implement
the same interface for consistency and easy comparison.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class ProtocolResult:
    """
    Container for protocol simulation results.

    Attributes:
        protocol_name: Name of the protocol used
        n_bits: Number of logical bits transmitted
        n_qubits_sent: Total physical qubits sent
        raw_key_alice: Alice's raw key bits before sifting
        raw_key_bob: Bob's raw key bits before sifting
        sifted_key_alice: Alice's key after basis sifting
        sifted_key_bob: Bob's key after basis sifting
        sifted_indices: Indices of bits retained after sifting
        qber: Quantum Bit Error Rate (fraction)
        sifting_rate: Fraction of bits retained after sifting
        kgr: Key Generation Rate (bits per qubit sent)
        edp: Eavesdropping Detection Probability (if attack simulated)
        eavesdropper_present: Whether Eve was simulated
        eve_information: Information gained by Eve (if applicable)
        noise_prob: Depolarizing noise probability used
        metadata: Additional protocol-specific data
    """
    protocol_name: str
    n_bits: int
    n_qubits_sent: int

    raw_key_alice: np.ndarray
    raw_key_bob: np.ndarray
    sifted_key_alice: np.ndarray
    sifted_key_bob: np.ndarray
    sifted_indices: np.ndarray

    qber: float
    sifting_rate: float
    kgr: float

    edp: Optional[float] = None
    eavesdropper_present: bool = False
    eve_information: Optional[np.ndarray] = None
    noise_prob: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a formatted summary of the results."""
        lines = [
            f"=== {self.protocol_name} Results ===",
            f"Bits transmitted: {self.n_bits}",
            f"Qubits sent: {self.n_qubits_sent}",
            f"Sifted key length: {len(self.sifted_key_alice)}",
            f"Sifting rate: {self.sifting_rate:.2%}",
            f"QBER: {self.qber:.4%}",
            f"Key Generation Rate: {self.kgr:.4f} bits/qubit",
        ]
        if self.eavesdropper_present:
            lines.append(f"Eavesdropper: PRESENT")
            if self.edp is not None:
                lines.append(f"Detection threshold exceeded: {self.qber > 0.11}")
        else:
            lines.append(f"Eavesdropper: NOT PRESENT")

        if self.noise_prob > 0:
            lines.append(f"Noise probability: {self.noise_prob:.2%}")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"ProtocolResult(protocol={self.protocol_name}, "
                f"qber={self.qber:.4f}, kgr={self.kgr:.4f}, "
                f"sifting_rate={self.sifting_rate:.2%})")


class BaseProtocol(ABC):
    """
    Abstract base class for BB84 protocol variants.

    All protocol implementations must inherit from this class and
    implement the required abstract methods.
    """

    # Class-level protocol identifier
    protocol_name: str = "BaseProtocol"

    # Qubits per logical bit (1 for standard, 2 for bitwise, 3 for majority vote)
    qubits_per_bit: int = 1

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the protocol.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def prepare_qubits(
        self,
        bits: np.ndarray,
        bases: np.ndarray
    ) -> List[Any]:
        """
        Prepare quantum circuits for Alice's bits in given bases.

        Args:
            bits: Array of bits (0 or 1) to encode
            bases: Array of bases ('Z' or 'X') for each bit

        Returns:
            List of prepared quantum circuits
        """
        pass

    @abstractmethod
    def measure_qubits(
        self,
        circuits: List[Any],
        bases: np.ndarray,
        noise_prob: float = 0.0
    ) -> np.ndarray:
        """
        Measure qubits in given bases with optional noise.

        Args:
            circuits: List of quantum circuits to measure
            bases: Array of measurement bases
            noise_prob: Depolarizing noise probability

        Returns:
            Array of measurement results
        """
        pass

    @abstractmethod
    def sift_key(
        self,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        alice_bits: np.ndarray,
        bob_results: np.ndarray
    ) -> tuple:
        """
        Perform basis sifting to extract matching bits.

        Args:
            alice_bases: Alice's basis choices
            bob_bases: Bob's basis choices
            alice_bits: Alice's original bits
            bob_results: Bob's measurement results

        Returns:
            Tuple of (sifted_alice, sifted_bob, sifted_indices)
        """
        pass

    def run(
        self,
        n_bits: int = 1000,
        noise_prob: float = 0.0,
        eavesdropper: bool = False,
        eve_interception_rate: float = 1.0,
        synchronized_bases: bool = None,
        base_match_prob: float = 0.9
    ) -> ProtocolResult:
        """
        Run the complete protocol simulation.

        Args:
            n_bits: Number of logical bits to transmit
            noise_prob: Depolarizing noise probability (0.0 to 1.0)
            eavesdropper: Whether to simulate intercept-resend attack
            eve_interception_rate: Fraction of qubits Eve intercepts
            synchronized_bases: Whether Alice/Bob use synchronized bases
                               (default depends on protocol)
            base_match_prob: Probability of basis match for synchronized mode

        Returns:
            ProtocolResult containing all simulation data
        """
        from ..metrics import compute_qber, compute_kgr

        # Generate Alice's random bits
        alice_bits = self.rng.integers(0, 2, size=n_bits)

        # Generate bases (protocol-specific logic may override)
        alice_bases, bob_bases = self._generate_bases(
            n_bits, synchronized_bases, base_match_prob
        )

        # Prepare qubits
        circuits = self.prepare_qubits(alice_bits, alice_bases)

        # Simulate eavesdropping if enabled
        eve_info = None
        if eavesdropper:
            circuits, eve_info = self._simulate_eavesdropping(
                circuits, alice_bases, eve_interception_rate
            )

        # Bob measures qubits
        bob_results = self.measure_qubits(circuits, bob_bases, noise_prob)

        # Sift key
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
            noise_prob=noise_prob
        )

    def _generate_bases(
        self,
        n_bits: int,
        synchronized: Optional[bool],
        match_prob: float
    ) -> tuple:
        """
        Generate basis choices for Alice and Bob.

        Args:
            n_bits: Number of bits
            synchronized: Whether to use synchronized bases
            match_prob: Probability of matching bases in synchronized mode

        Returns:
            Tuple of (alice_bases, bob_bases) as numpy arrays of 'Z'/'X'
        """
        # Default: unsynchronized (random independent choices)
        if synchronized is None:
            synchronized = False

        alice_bases = self.rng.choice(['Z', 'X'], size=n_bits)

        if synchronized:
            # Bob matches Alice with high probability
            matches = self.rng.random(n_bits) < match_prob
            bob_bases = np.where(
                matches,
                alice_bases,
                np.where(alice_bases == 'Z', 'X', 'Z')
            )
        else:
            # Independent random choice
            bob_bases = self.rng.choice(['Z', 'X'], size=n_bits)

        return alice_bases, bob_bases

    def _simulate_eavesdropping(
        self,
        circuits: List[Any],
        alice_bases: np.ndarray,
        interception_rate: float
    ) -> tuple:
        """
        Simulate intercept-resend eavesdropping attack.

        Eve intercepts qubits, measures in random basis, and resends.

        Args:
            circuits: Quantum circuits representing qubits
            alice_bases: Alice's basis choices (Eve doesn't know these)
            interception_rate: Fraction of qubits Eve intercepts

        Returns:
            Tuple of (modified_circuits, eve_measurements)
        """
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator

        n_qubits = len(circuits)
        eve_results = np.full(n_qubits, -1)  # -1 means not intercepted
        eve_bases = self.rng.choice(['Z', 'X'], size=n_qubits)
        intercept_mask = self.rng.random(n_qubits) < interception_rate

        simulator = AerSimulator()
        modified_circuits = []

        for i, (circuit, intercept) in enumerate(zip(circuits, intercept_mask)):
            if intercept:
                # Eve measures the qubit
                eve_circuit = circuit.copy()
                if eve_bases[i] == 'X':
                    eve_circuit.h(0)
                eve_circuit.measure(0, 0)

                transpiled = transpile(eve_circuit, simulator)
                result = simulator.run(transpiled, shots=1).result()
                eve_bit = int(list(result.get_counts().keys())[0])
                eve_results[i] = eve_bit

                # Eve prepares new qubit based on her measurement
                new_circuit = QuantumCircuit(1, 1)
                if eve_bit == 1:
                    new_circuit.x(0)
                if eve_bases[i] == 'X':
                    new_circuit.h(0)
                modified_circuits.append(new_circuit)
            else:
                modified_circuits.append(circuit)

        return modified_circuits, eve_results
