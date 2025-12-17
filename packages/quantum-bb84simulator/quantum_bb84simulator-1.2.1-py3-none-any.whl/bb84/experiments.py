"""
Experiment framework for BB84 protocol comparison studies.

Provides tools for:
- Parameter sweeps across noise levels
- Multi-trial statistical analysis
- Protocol comparison with significance testing
- Data export for further analysis

Reference: Balakrishnan et al., "Enhancing BB84 QKD under Depolarizing Noise"
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Union, Callable
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
import warnings

from .protocols import StandardBB84, BitwiseBB84, MajorityVoteBB84, ProtocolResult
from .metrics import (
    compute_qber, compute_kgr, compute_edp,
    two_sample_ttest, paired_ttest, summary_statistics,
    compute_win_counts, DEFAULT_QBER_THRESHOLD
)


# Protocol name to class mapping
PROTOCOL_CLASSES = {
    'standard': StandardBB84,
    'bitwise': BitwiseBB84,
    'majority_vote': MajorityVoteBB84,
    'StandardBB84': StandardBB84,
    'BitwiseBB84': BitwiseBB84,
    'MajorityVoteBB84': MajorityVoteBB84,
}


@dataclass
class ExperimentConfig:
    """Configuration for a protocol comparison experiment."""
    protocols: List[str] = field(default_factory=lambda: ['standard', 'bitwise', 'majority_vote'])
    noise_probs: List[float] = field(default_factory=lambda: [i/100 for i in range(1, 21)])
    n_trials: int = 100
    n_bits: int = 10000
    eavesdropper: bool = False
    eve_interception_rate: float = 1.0
    seed: Optional[int] = None
    parallel: bool = True
    n_workers: Optional[int] = None

    def __post_init__(self):
        if self.n_workers is None:
            self.n_workers = max(1, multiprocessing.cpu_count() - 1)


@dataclass
class ExperimentResults:
    """Container for experiment results with analysis methods."""
    config: ExperimentConfig
    data: pd.DataFrame
    summary: Optional[pd.DataFrame] = None

    def __post_init__(self):
        if self.summary is None:
            self.summary = self._compute_summary()

    def _compute_summary(self) -> pd.DataFrame:
        """Compute summary statistics per protocol and noise level."""
        grouped = self.data.groupby(['protocol', 'noise_prob'])
        summary = grouped.agg({
            'qber': ['mean', 'std', 'min', 'max'],
            'kgr': ['mean', 'std', 'min', 'max'],
            'sifting_rate': ['mean', 'std'],
        }).reset_index()
        summary.columns = ['_'.join(col).strip('_') for col in summary.columns]
        return summary

    def get_protocol_data(self, protocol: str) -> pd.DataFrame:
        """Get data for a specific protocol."""
        return self.data[self.data['protocol'] == protocol]

    def compare_protocols(
        self,
        protocol1: str,
        protocol2: str,
        metric: str = 'kgr',
        alpha: float = 0.01
    ) -> pd.DataFrame:
        """
        Statistical comparison of two protocols across noise levels.

        Args:
            protocol1: First protocol name
            protocol2: Second protocol name
            metric: Metric to compare ('kgr', 'qber', 'sifting_rate')
            alpha: Significance level

        Returns:
            DataFrame with t-test results per noise level
        """
        results = []
        for noise_prob in self.config.noise_probs:
            data1 = self.data[
                (self.data['protocol'] == protocol1) &
                (self.data['noise_prob'] == noise_prob)
            ][metric].values

            data2 = self.data[
                (self.data['protocol'] == protocol2) &
                (self.data['noise_prob'] == noise_prob)
            ][metric].values

            if len(data1) > 0 and len(data2) > 0:
                ttest = two_sample_ttest(data1, data2, alpha=alpha)
                results.append({
                    'noise_prob': noise_prob,
                    f'{protocol1}_mean': np.mean(data1),
                    f'{protocol2}_mean': np.mean(data2),
                    'difference': np.mean(data1) - np.mean(data2),
                    't_statistic': ttest.statistic,
                    'p_value': ttest.p_value,
                    'significant': ttest.significant,
                    'effect_size': ttest.effect_size
                })

        return pd.DataFrame(results)

    def get_win_counts(self, metric: str = 'kgr') -> Dict[str, int]:
        """
        Count wins per protocol across noise levels.

        Args:
            metric: Metric to evaluate ('kgr', 'qber')

        Returns:
            Dict mapping protocol names to win counts
        """
        higher_is_better = metric in ['kgr', 'sifting_rate', 'edp']

        # Get mean values per protocol per noise level
        results_dict = {}
        for protocol in self.config.protocols:
            means = []
            for noise_prob in self.config.noise_probs:
                data = self.data[
                    (self.data['protocol'] == protocol) &
                    (self.data['noise_prob'] == noise_prob)
                ][metric].mean()
                means.append(data)
            results_dict[protocol] = means

        return compute_win_counts(results_dict, metric, higher_is_better)

    def to_csv(self, filepath: str, include_summary: bool = True):
        """Export results to CSV file(s)."""
        self.data.to_csv(filepath, index=False)
        if include_summary:
            summary_path = filepath.replace('.csv', '_summary.csv')
            self.summary.to_csv(summary_path, index=False)

    def plot_comparison(
        self,
        metric: str = 'kgr',
        figsize: tuple = (10, 6),
        show_error_bars: bool = True
    ):
        """
        Plot metric comparison across protocols and noise levels.

        Args:
            metric: Metric to plot ('kgr', 'qber', 'sifting_rate')
            figsize: Figure size
            show_error_bars: Whether to show standard deviation bars
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize)

        colors = {'standard': 'blue', 'bitwise': 'green', 'majority_vote': 'red'}
        labels = {
            'standard': 'Standard BB84',
            'bitwise': 'Bitwise BB84',
            'majority_vote': 'Three-Qubit Majority Vote'
        }

        for protocol in self.config.protocols:
            proto_data = self.summary[self.summary['protocol'] == protocol]
            x = proto_data['noise_prob']
            y = proto_data[f'{metric}_mean']

            color = colors.get(protocol, None)
            label = labels.get(protocol, protocol)

            if show_error_bars and f'{metric}_std' in proto_data.columns:
                yerr = proto_data[f'{metric}_std']
                ax.errorbar(x, y, yerr=yerr, label=label, color=color,
                           marker='o', capsize=3, capthick=1)
            else:
                ax.plot(x, y, label=label, color=color, marker='o')

        ax.set_xlabel('Depolarizing Noise Probability (p)')
        ax.set_ylabel(metric.upper())
        ax.set_title(f'{metric.upper()} vs Noise Level')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig, ax

    def plot_win_counts(self, figsize: tuple = (12, 4)):
        """Plot win count comparison for all metrics."""
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=figsize)
        metrics = ['kgr', 'qber', 'sifting_rate']
        titles = ['Key Generation Rate', 'QBER (lower is better)', 'Sifting Rate']

        colors = {'standard': 'blue', 'bitwise': 'green', 'majority_vote': 'red'}

        for ax, metric, title in zip(axes, metrics, titles):
            wins = self.get_win_counts(metric)
            protocols = list(wins.keys())
            counts = list(wins.values())
            bar_colors = [colors.get(p, 'gray') for p in protocols]

            ax.bar(protocols, counts, color=bar_colors)
            ax.set_ylabel('Win Count')
            ax.set_title(title)
            ax.set_ylim(0, len(self.config.noise_probs))

        plt.tight_layout()
        return fig, axes


def _run_single_trial(args: tuple) -> dict:
    """
    Run a single trial for a specific protocol and noise level.

    Args:
        args: Tuple of (protocol_name, noise_prob, n_bits, eavesdropper,
                       eve_rate, trial_seed)

    Returns:
        Dict with trial results
    """
    protocol_name, noise_prob, n_bits, eavesdropper, eve_rate, trial_seed = args

    protocol_class = PROTOCOL_CLASSES[protocol_name]
    protocol = protocol_class(seed=trial_seed)

    result = protocol.run(
        n_bits=n_bits,
        noise_prob=noise_prob,
        eavesdropper=eavesdropper,
        eve_interception_rate=eve_rate
    )

    return {
        'protocol': protocol_name,
        'noise_prob': noise_prob,
        'trial_seed': trial_seed,
        'qber': result.qber,
        'kgr': result.kgr,
        'sifting_rate': result.sifting_rate,
        'n_sifted': len(result.sifted_key_alice),
        'n_qubits_sent': result.n_qubits_sent,
        'eavesdropper': eavesdropper
    }


def run_noise_sweep(
    protocols: List[str] = ['standard', 'bitwise', 'majority_vote'],
    noise_probs: List[float] = None,
    n_trials: int = 100,
    n_bits: int = 10000,
    eavesdropper: bool = False,
    eve_interception_rate: float = 1.0,
    seed: Optional[int] = None,
    parallel: bool = True,
    n_workers: Optional[int] = None,
    show_progress: bool = True
) -> ExperimentResults:
    """
    Run comprehensive noise sweep experiment across protocols.

    This replicates the experimental methodology from the paper:
    - Sweep depolarizing noise from p=0.01 to p=0.20
    - Run 100 trials per setting
    - Compare KGR, QBER, and sifting rate

    Args:
        protocols: List of protocol names to compare
        noise_probs: List of noise probabilities to test
                    (default: 0.01 to 0.20 in 0.01 increments)
        n_trials: Number of trials per setting (default 100)
        n_bits: Bits per trial (default 10000)
        eavesdropper: Whether to simulate Eve
        eve_interception_rate: Fraction Eve intercepts
        seed: Base random seed for reproducibility
        parallel: Use parallel processing
        n_workers: Number of worker processes
        show_progress: Show progress bar

    Returns:
        ExperimentResults with all data and analysis methods
    """
    if noise_probs is None:
        noise_probs = [i/100 for i in range(1, 21)]

    if n_workers is None:
        n_workers = max(1, multiprocessing.cpu_count() - 1)

    config = ExperimentConfig(
        protocols=protocols,
        noise_probs=noise_probs,
        n_trials=n_trials,
        n_bits=n_bits,
        eavesdropper=eavesdropper,
        eve_interception_rate=eve_interception_rate,
        seed=seed,
        parallel=parallel,
        n_workers=n_workers
    )

    # Generate all trial configurations
    rng = np.random.default_rng(seed)
    trial_args = []

    for protocol in protocols:
        for noise_prob in noise_probs:
            for trial in range(n_trials):
                trial_seed = rng.integers(0, 2**31)
                trial_args.append((
                    protocol, noise_prob, n_bits,
                    eavesdropper, eve_interception_rate, trial_seed
                ))

    # Run trials
    results = []

    if parallel and n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(_run_single_trial, args)
                      for args in trial_args]

            iterator = as_completed(futures)
            if show_progress:
                iterator = tqdm(iterator, total=len(futures),
                               desc="Running experiments")

            for future in iterator:
                try:
                    results.append(future.result())
                except Exception as e:
                    warnings.warn(f"Trial failed: {e}")
    else:
        iterator = trial_args
        if show_progress:
            iterator = tqdm(iterator, desc="Running experiments")

        for args in iterator:
            try:
                results.append(_run_single_trial(args))
            except Exception as e:
                warnings.warn(f"Trial failed: {e}")

    df = pd.DataFrame(results)
    return ExperimentResults(config=config, data=df)


def run_eavesdropping_experiment(
    protocols: List[str] = ['standard', 'bitwise', 'majority_vote'],
    noise_probs: List[float] = None,
    n_trials: int = 100,
    n_bits: int = 10000,
    detection_threshold: float = DEFAULT_QBER_THRESHOLD,
    seed: Optional[int] = None,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Run eavesdropping detection experiment.

    Compares EDP (Eavesdropping Detection Probability) across protocols.

    Args:
        protocols: Protocols to compare
        noise_probs: Noise levels to test
        n_trials: Trials per setting
        n_bits: Bits per trial
        detection_threshold: QBER threshold for detection (default 11%)
        seed: Random seed
        show_progress: Show progress bar

    Returns:
        DataFrame with EDP results per protocol and noise level
    """
    if noise_probs is None:
        noise_probs = [i/100 for i in range(1, 21)]

    # Run with eavesdropper
    results_eve = run_noise_sweep(
        protocols=protocols,
        noise_probs=noise_probs,
        n_trials=n_trials,
        n_bits=n_bits,
        eavesdropper=True,
        seed=seed,
        show_progress=show_progress
    )

    # Calculate EDP for each protocol/noise combination
    edp_results = []
    for protocol in protocols:
        for noise_prob in noise_probs:
            qber_values = results_eve.data[
                (results_eve.data['protocol'] == protocol) &
                (results_eve.data['noise_prob'] == noise_prob)
            ]['qber'].values

            edp = compute_edp(qber_values, threshold=detection_threshold)
            edp_results.append({
                'protocol': protocol,
                'noise_prob': noise_prob,
                'edp': edp,
                'mean_qber': np.mean(qber_values),
                'std_qber': np.std(qber_values)
            })

    return pd.DataFrame(edp_results)


def quick_comparison(
    n_bits: int = 1000,
    noise_prob: float = 0.10,
    seed: Optional[int] = None
) -> Dict[str, ProtocolResult]:
    """
    Quick single-run comparison of all three protocols.

    Useful for demonstrations and quick tests.

    Args:
        n_bits: Number of bits to transmit
        noise_prob: Depolarizing noise probability
        seed: Random seed

    Returns:
        Dict mapping protocol names to their results
    """
    results = {}

    for name, cls in [('standard', StandardBB84),
                      ('bitwise', BitwiseBB84),
                      ('majority_vote', MajorityVoteBB84)]:
        protocol = cls(seed=seed)
        results[name] = protocol.run(n_bits=n_bits, noise_prob=noise_prob)

    return results
