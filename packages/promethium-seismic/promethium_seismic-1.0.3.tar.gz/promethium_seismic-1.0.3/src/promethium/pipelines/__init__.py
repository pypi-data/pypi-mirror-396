# Promethium Pipelines Module

"""
High-level end-to-end workflows for seismic data reconstruction.

This module provides pipeline abstractions that combine preprocessing,
model inference, and postprocessing into cohesive workflows.
"""

from promethium.pipelines.recovery import SeismicRecoveryPipeline

__all__ = [
    "SeismicRecoveryPipeline",
]
