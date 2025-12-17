# Changelog

All notable changes to this project will be documented in this file.

## [1.2.1] - 2025-12-14
### Changed
- Updated documentation and README

---

## [1.2.0] - 2025-12-13
### Added
- **Three Protocol Variants**:
  - `StandardBB84`: Original BB84 protocol with random basis selection
  - `BitwiseBB84`: Synchronized bases + duplicate qubit filtering (~90% sifting rate)
  - `MajorityVoteBB84`: Three-qubit repetition encoding with majority vote decoding
- **High-Level API**: Simple `bb84.simulate()` function for quick simulations
- **Metrics Module** (`bb84/metrics.py`):
  - `compute_qber()`: Quantum Bit Error Rate calculation
  - `compute_kgr()`: Key Generation Rate with binary entropy formula
  - `compute_edp()`: Eavesdropping Detection Probability
  - `binary_entropy()`: H_2(x) function
  - `two_sample_ttest()`, `paired_ttest()`: Statistical significance testing
  - `theoretical_qber_majority_vote()`: Theoretical QBER for majority vote protocol
- **Experiments Framework** (`bb84/experiments.py`):
  - `run_noise_sweep()`: Parameter sweep across noise levels with parallel execution
  - `run_eavesdropping_experiment()`: EDP analysis under intercept-resend attacks
  - `ExperimentResults` class with plotting and statistical comparison methods
- **Attacks Module** (`bb84/attacks/`):
  - `InterceptResendAttack`: Full intercept-resend eavesdropping simulation
- **Paper Replication Notebook**: `notebooks/01_paper_replication.ipynb`
- New dependencies: `scipy`, `pandas`, `tqdm`, `qiskit-aer`

### Changed
- Restructured codebase with `bb84/protocols/` submodule
- Enhanced noise modeling with protocol-specific implementations
- Updated `__init__.py` with comprehensive API documentation

---

## [1.1.0] - 2025-01-15
### Added
- AI-based eavesdropper detection using Isolation Forest algorithm (`ai_detect_eavesdropper` function).
- IBM Qiskit integration for running BB84 on quantum simulators (`run_bb84_on_ibm` function).
- New `add_quantum_noise` function for applying quantum noise to bit sequences.
- Real-time QBER visualization with `plot_qber_variation` function.
- Added `scikit-learn` as a new dependency for machine learning-based detection.

### Changed
- Enhanced noise simulation module with additional noise application methods.
- Improved visualization tools with QBER tracking capabilities.

### Fixed
- N/A

---

## [1.0.0] - 2024-12-22
### Added
- Quantum key generation process using Qiskit.
- Noise simulation for quantum channels with configurable noise intensity and types.
- Error detection and correction mechanisms using parity checks and hashing.
- Classical communication module for basis reconciliation and error correction.
- Full BB84 protocol implementation, including basis reconciliation and key sifting.
- Visualization tools for qubit states, measurement results, and noise impact.
- Customizable parameters for key length, noise, and error correction.

### Changed
- Initial release with full BB84 protocol implementation and supportive tools.

### Fixed
- N/A (Initial release)

---