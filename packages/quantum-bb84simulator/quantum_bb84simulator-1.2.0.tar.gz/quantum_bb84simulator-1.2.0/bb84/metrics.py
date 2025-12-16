"""
Metrics computation module for BB84 protocol analysis.

Implements the key performance metrics from:
"Enhancing BB84 Quantum Key Distribution under Depolarizing Noise:
Bitwise vs Three-Qubit Majority Vote Protocols" - Balakrishnan et al.

Metrics:
- QBER: Quantum Bit Error Rate
- KGR: Key Generation Rate (asymptotic formula)
- EDP: Eavesdropping Detection Probability
- Statistical significance testing (t-tests)
"""

import numpy as np
from typing import Tuple, List, Optional, Union
from scipy import stats
from dataclasses import dataclass


# Default detection threshold (11% as per standard BB84 security analysis)
DEFAULT_QBER_THRESHOLD = 0.11

# Fraction of bits sacrificed for parameter estimation
S_TEST = 0.01


def binary_entropy(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Compute binary entropy function H_2(x).

    H_2(x) = -x * log_2(x) - (1-x) * log_2(1-x)

    Args:
        x: Probability value(s) in range [0, 1]

    Returns:
        Binary entropy value(s)
    """
    x = np.asarray(x)
    result = np.zeros_like(x, dtype=float)

    # Handle edge cases where x is 0 or 1
    valid = (x > 0) & (x < 1)
    if np.any(valid):
        xv = x[valid] if x.ndim > 0 else x
        result_valid = -xv * np.log2(xv) - (1 - xv) * np.log2(1 - xv)
        if x.ndim > 0:
            result[valid] = result_valid
        else:
            result = result_valid

    return float(result) if result.ndim == 0 else result


def compute_qber(
    alice_key: np.ndarray,
    bob_key: np.ndarray
) -> float:
    """
    Compute Quantum Bit Error Rate between Alice's and Bob's sifted keys.

    QBER = (number of mismatched bits) / (total sifted bits)

    Args:
        alice_key: Alice's sifted key bits
        bob_key: Bob's sifted key bits

    Returns:
        QBER as a fraction (0.0 to 1.0)
    """
    alice_key = np.asarray(alice_key)
    bob_key = np.asarray(bob_key)

    if len(alice_key) == 0 or len(bob_key) == 0:
        return 0.0

    if len(alice_key) != len(bob_key):
        raise ValueError("Alice and Bob keys must have same length")

    mismatches = np.sum(alice_key != bob_key)
    return float(mismatches) / len(alice_key)


def compute_kgr(
    qber: float,
    sifting_rate: float,
    n_qubits_sent: int,
    s_test: float = S_TEST
) -> float:
    """
    Compute Key Generation Rate using asymptotic Shannon limit formula.

    KGR = s * [1 - H_2(QBER)] - s_test

    Where:
    - s = sifting_rate (fraction of qubits retained after sifting)
    - H_2 = binary entropy function
    - s_test = fraction of bits sacrificed for parameter estimation

    Args:
        qber: Quantum Bit Error Rate
        sifting_rate: Fraction of bits retained after sifting
        n_qubits_sent: Total qubits sent (for normalization)
        s_test: Fraction sacrificed for testing (default 0.01)

    Returns:
        Key generation rate in bits per qubit sent
    """
    if qber >= 0.5:
        # No secure key possible above 50% QBER
        return 0.0

    if qber >= 0.25:
        # Beyond typical BB84 threshold, likely no key
        # But allow calculation for enhanced protocols
        pass

    # Asymptotic key rate formula
    h2_qber = binary_entropy(qber)
    key_rate = sifting_rate * (1 - h2_qber) - s_test

    return max(0.0, key_rate)


def compute_kgr_finite(
    qber: float,
    sifting_rate: float,
    n_bits: int,
    epsilon_sec: float = 1e-10,
    s_test: float = S_TEST
) -> float:
    """
    Compute finite-key secure key rate with statistical fluctuations.

    Adds finite-size corrections to the asymptotic formula.

    Args:
        qber: Quantum Bit Error Rate
        sifting_rate: Fraction of bits retained after sifting
        n_bits: Number of sifted bits
        epsilon_sec: Security parameter (default 10^-10)
        s_test: Fraction sacrificed for testing

    Returns:
        Finite-key generation rate
    """
    if n_bits == 0 or qber >= 0.5:
        return 0.0

    # Asymptotic part
    h2_qber = binary_entropy(qber)
    asymptotic_rate = sifting_rate * (1 - h2_qber) - s_test

    # Finite-size correction (simplified)
    # In practice, uses more sophisticated bounds
    delta = np.sqrt(np.log(1 / epsilon_sec) / (2 * n_bits))
    finite_correction = 2 * delta * (1 + binary_entropy(qber + delta))

    key_rate = asymptotic_rate - finite_correction

    return max(0.0, key_rate)


def compute_edp(
    qber_values: np.ndarray,
    threshold: float = DEFAULT_QBER_THRESHOLD
) -> float:
    """
    Compute Eavesdropping Detection Probability.

    EDP = fraction of trials where QBER > threshold

    Args:
        qber_values: Array of QBER values from multiple trials
        threshold: Detection threshold (default 11%)

    Returns:
        EDP as a fraction (0.0 to 1.0)
    """
    qber_values = np.asarray(qber_values)
    if len(qber_values) == 0:
        return 0.0

    detections = np.sum(qber_values > threshold)
    return float(detections) / len(qber_values)


@dataclass
class TTestResult:
    """Container for t-test results."""
    statistic: float
    p_value: float
    significant: bool
    effect_size: float  # Cohen's d
    mean_diff: float
    ci_lower: float
    ci_upper: float

    def __repr__(self) -> str:
        sig_str = "SIGNIFICANT" if self.significant else "not significant"
        return (f"TTestResult(t={self.statistic:.3f}, p={self.p_value:.4e}, "
                f"{sig_str}, Cohen's d={self.effect_size:.3f})")


def two_sample_ttest(
    sample1: np.ndarray,
    sample2: np.ndarray,
    alpha: float = 0.01,
    alternative: str = 'two-sided'
) -> TTestResult:
    """
    Perform two-sample t-test comparing two protocol results.

    Args:
        sample1: First sample (e.g., KGR values from protocol 1)
        sample2: Second sample (e.g., KGR values from protocol 2)
        alpha: Significance level (default 0.01 as per paper)
        alternative: 'two-sided', 'less', or 'greater'

    Returns:
        TTestResult with test statistics and interpretation
    """
    sample1 = np.asarray(sample1)
    sample2 = np.asarray(sample2)

    # Perform t-test
    result = stats.ttest_ind(sample1, sample2, alternative=alternative)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt(
        ((len(sample1) - 1) * np.var(sample1, ddof=1) +
         (len(sample2) - 1) * np.var(sample2, ddof=1)) /
        (len(sample1) + len(sample2) - 2)
    )
    cohens_d = (np.mean(sample1) - np.mean(sample2)) / pooled_std if pooled_std > 0 else 0

    # Confidence interval for difference of means
    mean_diff = np.mean(sample1) - np.mean(sample2)
    se_diff = np.sqrt(np.var(sample1, ddof=1)/len(sample1) +
                      np.var(sample2, ddof=1)/len(sample2))
    t_crit = stats.t.ppf(1 - alpha/2, len(sample1) + len(sample2) - 2)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    return TTestResult(
        statistic=result.statistic,
        p_value=result.pvalue,
        significant=result.pvalue < alpha,
        effect_size=cohens_d,
        mean_diff=mean_diff,
        ci_lower=ci_lower,
        ci_upper=ci_upper
    )


def paired_ttest(
    sample1: np.ndarray,
    sample2: np.ndarray,
    alpha: float = 0.01
) -> TTestResult:
    """
    Perform paired t-test for matched trials.

    Use when the same random bits/bases are used for both protocols
    in each trial (paired design as per paper methodology).

    Args:
        sample1: First sample values
        sample2: Second sample values (paired with sample1)
        alpha: Significance level

    Returns:
        TTestResult with test statistics
    """
    sample1 = np.asarray(sample1)
    sample2 = np.asarray(sample2)

    if len(sample1) != len(sample2):
        raise ValueError("Paired samples must have equal length")

    # Paired t-test
    result = stats.ttest_rel(sample1, sample2)

    # Effect size for paired data
    diff = sample1 - sample2
    cohens_d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0

    # Confidence interval
    mean_diff = np.mean(diff)
    se_diff = np.std(diff, ddof=1) / np.sqrt(len(diff))
    t_crit = stats.t.ppf(1 - alpha/2, len(diff) - 1)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    return TTestResult(
        statistic=result.statistic,
        p_value=result.pvalue,
        significant=result.pvalue < alpha,
        effect_size=cohens_d,
        mean_diff=mean_diff,
        ci_lower=ci_lower,
        ci_upper=ci_upper
    )


def compute_win_counts(
    results_dict: dict,
    metric: str = 'kgr',
    higher_is_better: bool = True
) -> dict:
    """
    Count how many times each protocol "wins" across noise levels.

    Args:
        results_dict: Dict mapping protocol names to lists of metric values
                     (one value per noise level)
        metric: Name of metric being compared (for documentation)
        higher_is_better: True for KGR/EDP, False for QBER

    Returns:
        Dict mapping protocol names to win counts
    """
    protocols = list(results_dict.keys())
    n_levels = len(results_dict[protocols[0]])

    win_counts = {p: 0 for p in protocols}

    for i in range(n_levels):
        values = {p: results_dict[p][i] for p in protocols}
        if higher_is_better:
            winner = max(values, key=values.get)
        else:
            winner = min(values, key=values.get)
        win_counts[winner] += 1

    return win_counts


def theoretical_qber_majority_vote(p: float) -> float:
    """
    Compute theoretical QBER for three-qubit majority vote protocol.

    QBER_logical = P(2 or 3 errors in triple)
                 = 3p²(1-p) + p³
                 ≈ (3/2)p² for small p

    Args:
        p: Physical depolarizing noise probability per qubit

    Returns:
        Expected logical QBER after majority decoding
    """
    # Exact formula: probability of majority errors
    # P(exactly 2 errors) = C(3,2) * p^2 * (1-p)
    # P(exactly 3 errors) = p^3
    return 3 * (p ** 2) * (1 - p) + p ** 3


def summary_statistics(
    values: np.ndarray
) -> dict:
    """
    Compute summary statistics for a set of trial results.

    Args:
        values: Array of metric values from trials

    Returns:
        Dict with mean, std, sem, ci_95_lower, ci_95_upper, min, max
    """
    values = np.asarray(values)
    n = len(values)

    if n == 0:
        return {
            'mean': 0.0, 'std': 0.0, 'sem': 0.0,
            'ci_95_lower': 0.0, 'ci_95_upper': 0.0,
            'min': 0.0, 'max': 0.0, 'n': 0
        }

    mean = np.mean(values)
    std = np.std(values, ddof=1) if n > 1 else 0.0
    sem = std / np.sqrt(n) if n > 0 else 0.0

    # 95% confidence interval
    t_crit = stats.t.ppf(0.975, n - 1) if n > 1 else 0.0
    ci_lower = mean - t_crit * sem
    ci_upper = mean + t_crit * sem

    return {
        'mean': mean,
        'std': std,
        'sem': sem,
        'ci_95_lower': ci_lower,
        'ci_95_upper': ci_upper,
        'min': np.min(values),
        'max': np.max(values),
        'n': n
    }
