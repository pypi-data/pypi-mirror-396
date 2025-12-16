"""
Attack models for QKD security analysis.

Implements various eavesdropping strategies for testing
protocol security under adversarial conditions.
"""

from .intercept_resend import InterceptResendAttack, apply_intercept_resend

__all__ = [
    "InterceptResendAttack",
    "apply_intercept_resend",
]
