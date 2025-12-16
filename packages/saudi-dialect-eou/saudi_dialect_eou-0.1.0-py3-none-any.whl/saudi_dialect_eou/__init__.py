"""
Saudi Arabic End-of-Utterance detection module.

This module provides the Arabic EOU model for detecting
when a user has finished speaking in Arabic conversations.
"""

from .arabic_model import ArabicEOUModel
from .version import __version__

__all__ = ["ArabicEOUModel", "__version__"]
