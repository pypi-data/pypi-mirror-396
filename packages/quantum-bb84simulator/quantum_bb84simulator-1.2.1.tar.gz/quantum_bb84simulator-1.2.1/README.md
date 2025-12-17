# BB84 Quantum Key Distribution Simulator

[![PyPI version](https://badge.fury.io/py/quantum-bb84simulator.svg)](https://pypi.org/project/quantum-bb84simulator/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A research-grade Python library for simulating BB84 quantum key distribution protocols, featuring **three protocol variants** with configurable noise models, eavesdropping simulation, and statistical analysis tools.

**Based on peer-reviewed research** on enhancing BB84 quantum key distribution under depolarizing noise using bitwise and three-qubit majority vote protocols.

---

## Key Features

### Three Protocol Variants

| Protocol | Description | Best For |
|----------|-------------|----------|
| **Standard BB84** | Original Bennett-Brassard 1984 protocol | Baseline comparison |
| **Bitwise BB84** | Synchronized bases + duplicate qubit filtering | High key rate at low noise |
| **Three-Qubit Majority Vote** | Repetition coding with majority decoding | High noise tolerance (up to ~18%) |

### Research-Grade Metrics

- **QBER** (Quantum Bit Error Rate) - Error rate after basis sifting
- **KGR** (Key Generation Rate) - Secure bits per qubit using asymptotic formula: `KGR = s[1 - H₂(QBER)] - s_test`
- **EDP** (Eavesdropping Detection Probability) - Detection rate under intercept-resend attacks
- **Statistical significance testing** - Two-sample t-tests with effect sizes

### Comprehensive Simulation Framework

- Depolarizing noise models (p = 0.01 to 0.20)
- Intercept-resend eavesdropping attacks
- Parameter sweeps with parallel execution
- Paper-replication experiment suite

---

## Installation

```bash
pip install quantum-bb84simulator
```

**Requirements:** Python 3.8+, Qiskit, NumPy, SciPy, Pandas, Matplotlib

---

## Quick Start

### One-Line Simulation

```python
import bb84

# Simulate Three-Qubit Majority Vote protocol at 10% noise
result = bb84.simulate(
    protocol='majority_vote',
    n_bits=1000,
    noise_prob=0.10,
    seed=42
)

print(result.summary())
```

**Output:**
```
=== Three-Qubit Majority Vote BB84 Results ===
Bits transmitted: 1000
Qubits sent: 3000
Sifted key length: 894
Sifting rate: 89.40%
QBER: 1.12%
Key Generation Rate: 0.8234 bits/qubit
Eavesdropper: NOT PRESENT
Noise probability: 10.00%
```

### Compare All Protocols

```python
import bb84

# Quick comparison at 10% noise
results = bb84.compare(n_bits=1000, noise_prob=0.10)

for name, r in results.items():
    print(f"{name:20} | QBER: {r.qber:6.2%} | KGR: {r.kgr:.4f} | Sifting: {r.sifting_rate:.0%}")
```

**Output:**
```
standard             | QBER: 10.23% | KGR: 0.1845 | Sifting: 51%
bitwise              | QBER:  5.12% | KGR: 0.6521 | Sifting: 82%
majority_vote        | QBER:  1.12% | KGR: 0.8234 | Sifting: 89%
```

---

## Protocol Details

### Standard BB84

The original protocol where Alice and Bob independently choose random bases (Z or X), resulting in ~50% sifting loss.

```python
from bb84.protocols import StandardBB84

protocol = StandardBB84(seed=42)
result = protocol.run(n_bits=1000, noise_prob=0.05)
```

### Bitwise BB84

Enhanced protocol with:
- **Synchronized basis selection** (~90% match rate vs 50%)
- **Duplicate qubit encoding** - each bit sent twice
- **Error detection** - discards pairs with mismatched measurements

```python
from bb84.protocols import BitwiseBB84

protocol = BitwiseBB84(seed=42, base_match_prob=0.9)
result = protocol.run(n_bits=1000, noise_prob=0.05)
```

### Three-Qubit Majority Vote

Error-correcting protocol with:
- **Triple redundancy** - each bit encoded in 3 qubits
- **Majority vote decoding** - corrects single-qubit errors
- **Extended noise tolerance** - operates up to ~18% QBER

```python
from bb84.protocols import MajorityVoteBB84

protocol = MajorityVoteBB84(seed=42)
result = protocol.run(n_bits=1000, noise_prob=0.15)

# Analyze error correction performance
analysis = protocol.analyze_triple_errors(
    result.raw_key_alice,
    result.raw_key_bob,
    result.sifted_indices
)
print(f"Errors corrected: {analysis['corrected_errors']}")
```

---

## Eavesdropping Simulation

Simulate intercept-resend attacks where Eve measures qubits in random bases:

```python
import bb84

# Simulate with eavesdropper present
result = bb84.simulate(
    protocol='standard',
    n_bits=1000,
    noise_prob=0.05,
    eavesdropper=True,
    eve_interception_rate=1.0  # Eve intercepts all qubits
)

# Check if attack is detected (QBER > 11% threshold)
detected = result.qber > 0.11
print(f"QBER: {result.qber:.2%} | Eve detected: {detected}")
```

---

## Research Experiments

### Noise Sweep (Replicate Paper Results)

Run comprehensive experiments across noise levels with statistical analysis:

```python
from bb84.experiments import run_noise_sweep

# Paper parameters: 100 trials, 10000 bits, noise 1-20%
results = run_noise_sweep(
    protocols=['standard', 'bitwise', 'majority_vote'],
    noise_probs=[i/100 for i in range(1, 21)],
    n_trials=100,
    n_bits=10000,
    seed=42,
    parallel=True  # Use all CPU cores
)

# Plot KGR comparison (Figure 3 from paper)
results.plot_comparison('kgr')

# Statistical comparison with t-tests
comparison = results.compare_protocols('standard', 'majority_vote', metric='kgr')
print(comparison[['noise_prob', 'p_value', 'significant', 'effect_size']])

# Export for further analysis
results.to_csv('experiment_results.csv')
```

### Eavesdropping Detection Experiment

```python
from bb84.experiments import run_eavesdropping_experiment

edp_results = run_eavesdropping_experiment(
    protocols=['standard', 'bitwise', 'majority_vote'],
    n_trials=100,
    detection_threshold=0.11
)

print(edp_results[['protocol', 'noise_prob', 'edp', 'mean_qber']])
```

### Win Count Analysis

```python
# Count which protocol "wins" across noise levels
wins = results.get_win_counts('kgr')
print(wins)  # {'standard': 0, 'bitwise': 5, 'majority_vote': 15}

# Visualize win counts
results.plot_win_counts()
```

---

## Metrics API

```python
from bb84.metrics import (
    compute_qber,          # Quantum Bit Error Rate
    compute_kgr,           # Key Generation Rate
    compute_edp,           # Eavesdropping Detection Probability
    binary_entropy,        # H₂(x) function
    two_sample_ttest,      # Statistical comparison
    theoretical_qber_majority_vote  # Theoretical QBER for majority vote
)

# Example: Compute theoretical vs observed QBER
p = 0.10  # 10% noise
theoretical = theoretical_qber_majority_vote(p)  # ≈ 0.028
print(f"Theoretical QBER at p={p}: {theoretical:.2%}")
```

---

## Key Formulas

### Key Generation Rate (Asymptotic)
```
KGR = s × [1 - H₂(QBER)] - s_test
```
Where:
- `s` = sifting rate (fraction of bits retained)
- `H₂(x) = -x·log₂(x) - (1-x)·log₂(1-x)` (binary entropy)
- `s_test ≈ 0.01` (bits sacrificed for parameter estimation)

### Majority Vote QBER (Theoretical)
```
QBER_logical = 3p²(1-p) + p³ ≈ (3/2)p²
```
Where `p` is the physical depolarizing noise probability.

---

## Project Structure

```
quantum_bb84simulator/
├── bb84/
│   ├── __init__.py          # High-level API: simulate(), compare()
│   ├── protocols/
│   │   ├── standard.py      # Standard BB84
│   │   ├── bitwise.py       # Bitwise BB84
│   │   └── majority_vote.py # Three-Qubit Majority Vote
│   ├── metrics.py           # QBER, KGR, EDP, statistical tests
│   ├── experiments.py       # Parameter sweeps, batch runs
│   └── attacks/
│       └── intercept_resend.py
├── notebooks/
│   └── 01_paper_replication.ipynb
├── examples/
│   └── run_bb84.py
└── tests/
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Author

**Syon Balakrishnan**
Email: balakrishnansyon@gmail.com

---

## Acknowledgments

- IBM Qiskit team for the quantum computing framework
- University of Florida Feng ECE Lab for research support
