# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework
# Main package initialization

"""
Promethium is a state-of-the-art, AI-driven framework for seismic signal 
reconstruction, denoising, and geophysical data enhancement.

Developed in December 2025 with cutting-edge deep learning architectures
and production-grade engineering practices.

Quick Start:
    >>> import promethium
    >>> from promethium import read_segy, SeismicRecoveryPipeline
    >>> 
    >>> # Load seismic data
    >>> data = read_segy("survey.sgy")
    >>> 
    >>> # Create and run reconstruction pipeline
    >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
    >>> result = pipeline.run(data)
    >>> 
    >>> # Evaluate reconstruction quality
    >>> metrics = promethium.evaluate_reconstruction(data, result)
    >>> print(metrics)

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
Licensed under CC BY-NC 4.0
"""

__version__ = "1.0.0"
__author__ = "Olaf Yunus Laitinen Imanov"
__license__ = "CC BY-NC 4.0"

# Core utilities
from promethium.core.config import settings, get_settings
from promethium.core.logging import get_logger

# I/O functions - reading and writing seismic data formats
from promethium.io import read_segy, write_segy

# Signal processing utilities
from promethium.signal import (
    bandpass_filter,
    lowpass_filter,
    highpass_filter,
)

# ML components
from promethium.ml import (
    InferenceEngine,
    load_model,
    reconstruct,
    compute_snr,
    compute_ssim,
)

# High-level pipelines
from promethium.pipelines import SeismicRecoveryPipeline

# Evaluation metrics
from promethium.evaluation import (
    signal_to_noise_ratio,
    mean_squared_error,
    peak_signal_to_noise_ratio,
    structural_similarity_index,
    frequency_domain_correlation,
    phase_coherence,
    evaluate_reconstruction,
)

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core
    "settings",
    "get_settings",
    "get_logger",
    # I/O
    "read_segy",
    "write_segy",
    # Signal processing
    "bandpass_filter",
    "lowpass_filter",
    "highpass_filter",
    # ML
    "InferenceEngine",
    "load_model",
    "reconstruct",
    "compute_snr",
    "compute_ssim",
    # Pipelines
    "SeismicRecoveryPipeline",
    # Evaluation
    "signal_to_noise_ratio",
    "mean_squared_error",
    "peak_signal_to_noise_ratio",
    "structural_similarity_index",
    "frequency_domain_correlation",
    "phase_coherence",
    "evaluate_reconstruction",
]

