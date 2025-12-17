"""
BB84 Quantum Key Distribution Simulation Library
================================================

A comprehensive Python library for simulating BB84 quantum key distribution
protocols, including enhanced variants for improved noise tolerance.

This library implements three protocol variants:
- Standard BB84: The original Bennett-Brassard 1984 protocol
- Bitwise BB84: Enhanced with synchronized bases and duplicate qubits
- Three-Qubit Majority Vote: Error-correcting variant for high-noise environments

Quick Start
-----------
>>> import bb84
>>> result = bb84.simulate(protocol='majority_vote', n_bits=1000, noise_prob=0.10)
>>> print(result.summary())

For paper replication:
>>> from bb84.experiments import run_noise_sweep
>>> results = run_noise_sweep(n_trials=100, n_bits=10000)
>>> results.plot_comparison('kgr')
"""

__version__ = "1.2.1"
__author__ = "Syon Balakrishnan"
__email__ = "balakrishnansyon@gmail.com"

# =============================================================================
# High-Level API (New in v1.2.0)
# =============================================================================

from typing import Optional, Union, Dict, Any
from .protocols import (
    StandardBB84,
    BitwiseBB84,
    MajorityVoteBB84,
    ProtocolResult,
    BaseProtocol
)
from .metrics import (
    compute_qber,
    compute_kgr,
    compute_edp,
    binary_entropy,
    two_sample_ttest,
    paired_ttest,
    summary_statistics,
    theoretical_qber_majority_vote
)
from .experiments import (
    run_noise_sweep,
    run_eavesdropping_experiment,
    quick_comparison,
    ExperimentConfig,
    ExperimentResults
)
from .attacks import InterceptResendAttack, apply_intercept_resend


# Protocol mapping for high-level API
_PROTOCOLS = {
    'standard': StandardBB84,
    'bitwise': BitwiseBB84,
    'majority_vote': MajorityVoteBB84,
}


def simulate(
    protocol: str = 'standard',
    n_bits: int = 1000,
    noise_prob: float = 0.0,
    eavesdropper: bool = False,
    eve_interception_rate: float = 1.0,
    seed: Optional[int] = None,
    **kwargs
) -> ProtocolResult:
    """
    Run a BB84 protocol simulation with a single function call.

    This is the recommended entry point for quick simulations.

    Args:
        protocol: Protocol variant to use:
            - 'standard': Original BB84 protocol
            - 'bitwise': Bitwise BB84 with synchronized bases
            - 'majority_vote': Three-qubit majority vote protocol
        n_bits: Number of logical bits to transmit (default 1000)
        noise_prob: Depolarizing noise probability 0.0-1.0 (default 0.0)
        eavesdropper: Whether to simulate intercept-resend attack (default False)
        eve_interception_rate: Fraction of qubits Eve intercepts (default 1.0)
        seed: Random seed for reproducibility
        **kwargs: Additional protocol-specific parameters

    Returns:
        ProtocolResult with all simulation data and metrics

    Examples:
        Basic simulation:
        >>> result = bb84.simulate(n_bits=1000, noise_prob=0.05)
        >>> print(f"QBER: {result.qber:.2%}, KGR: {result.kgr:.4f}")

        Compare protocols at high noise:
        >>> for proto in ['standard', 'bitwise', 'majority_vote']:
        ...     r = bb84.simulate(protocol=proto, noise_prob=0.15)
        ...     print(f"{proto}: QBER={r.qber:.2%}")

        With eavesdropper:
        >>> result = bb84.simulate(eavesdropper=True, noise_prob=0.05)
        >>> print(f"Eve detected: {result.qber > 0.11}")
    """
    if protocol not in _PROTOCOLS:
        raise ValueError(f"Unknown protocol '{protocol}'. "
                        f"Choose from: {list(_PROTOCOLS.keys())}")

    protocol_class = _PROTOCOLS[protocol]
    proto = protocol_class(seed=seed)

    return proto.run(
        n_bits=n_bits,
        noise_prob=noise_prob,
        eavesdropper=eavesdropper,
        eve_interception_rate=eve_interception_rate,
        **kwargs
    )


def compare(
    n_bits: int = 1000,
    noise_prob: float = 0.10,
    seed: Optional[int] = None
) -> Dict[str, ProtocolResult]:
    """
    Quick comparison of all three protocols.

    Args:
        n_bits: Bits per protocol
        noise_prob: Noise level
        seed: Random seed

    Returns:
        Dict mapping protocol names to results

    Example:
        >>> results = bb84.compare(noise_prob=0.10)
        >>> for name, r in results.items():
        ...     print(f"{name}: QBER={r.qber:.2%}, KGR={r.kgr:.4f}")
    """
    return quick_comparison(n_bits=n_bits, noise_prob=noise_prob, seed=seed)


# =============================================================================
# Legacy API (v1.0.0 - v1.1.0 compatibility)
# =============================================================================

# Import core BB84 protocol implementation (legacy)
from .key_distribution import BB84Simulation

# Import visualization tools
from .visualization import (
    visualize_protocol_workflow,
    visualize_noise_impact,
    visualize_key_sifting,
    plot_qber_variation
)

# Import quantum utilities for circuit preparation
from .quantum_utilities import prepare_qubit

# Import noise simulation tools
from .noise_simulation import (
    create_custom_noise_model,
    simulate_noisy_circuit,
    simulate_eavesdropping,
    simulate_lossy_channel,
    add_quantum_noise
)

# Import error correction and privacy amplification utilities
from .error_correction import (
    ldpc_error_correction,
    privacy_amplification,
    generate_toeplitz_matrix
)

# Import communication module
from .communication import Communication, ai_detect_eavesdropper


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Version info
    "__version__",
    "__author__",

    # High-level API (v1.2.0)
    "simulate",
    "compare",
    "run_noise_sweep",
    "run_eavesdropping_experiment",
    "quick_comparison",

    # Protocol classes
    "StandardBB84",
    "BitwiseBB84",
    "MajorityVoteBB84",
    "BaseProtocol",
    "ProtocolResult",

    # Experiment framework
    "ExperimentConfig",
    "ExperimentResults",

    # Metrics
    "compute_qber",
    "compute_kgr",
    "compute_edp",
    "binary_entropy",
    "two_sample_ttest",
    "paired_ttest",
    "summary_statistics",
    "theoretical_qber_majority_vote",

    # Attacks
    "InterceptResendAttack",
    "apply_intercept_resend",

    # Legacy API (v1.0.0 - v1.1.0)
    "BB84Simulation",
    "visualize_protocol_workflow",
    "visualize_noise_impact",
    "visualize_key_sifting",
    "plot_qber_variation",
    "prepare_qubit",
    "create_custom_noise_model",
    "simulate_noisy_circuit",
    "simulate_eavesdropping",
    "simulate_lossy_channel",
    "add_quantum_noise",
    "ldpc_error_correction",
    "privacy_amplification",
    "generate_toeplitz_matrix",
    "Communication",
    "ai_detect_eavesdropper"
]
