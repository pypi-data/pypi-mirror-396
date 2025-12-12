import torch
import numpy as np
from typing import Dict, Any, Callable, List

class SeismicTransform:
    """Base class for seismic data augmentations."""
    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class Compose:
    """Composes several transforms together."""
    def __init__(self, transforms: List[Callable]):
        self.transforms = transforms

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        for t in self.transforms:
            sample = t(sample)
        return sample

class ToTensor(SeismicTransform):
    """Convert numpy arrays to PyTorch tensors."""
    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        for key in ["input", "target"]:
            if key in sample and isinstance(sample[key], np.ndarray):
                # Ensure float32 for training
                sample[key] = torch.from_numpy(sample[key]).float()
        return sample

class Normalize(SeismicTransform):
    """
    Standardize data: (x - mean) / std.
    Can be Global or Per-Sample.
    SoTA approach for seismic: Trace-wise RMS normalization often preferred for amplitude preservation rel to events.
    """
    def __init__(self, mode: str = "std", mean: float = 0.0, std: float = 1.0):
        self.mode = mode
        self.mean = mean
        self.std = std

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        data = sample["input"]
        
        if self.mode == "std":
            data = (data - self.mean) / (self.std + 1e-8)
        elif self.mode == "minmax":
            dmin, dmax = data.min(), data.max()
            data = (data - dmin) / (dmax - dmin + 1e-8)
        elif self.mode == "rms":
            rms = np.sqrt(np.mean(data**2))
            data = data / (rms + 1e-8)
            
        sample["input"] = data
        return sample

class RandomPolarityFlip(SeismicTransform):
    """Randomly invert the trace polarity."""
    def __init__(self, p: float = 0.5):
        self.p = p

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        if np.random.rand() < self.p:
            sample["input"] = -sample["input"]
            if "target" in sample:
                sample["target"] = -sample["target"]
        return sample

class RandomGain(SeismicTransform):
    """Random amplitude scaling."""
    def __init__(self, factor_range: tuple = (0.5, 1.5)):
        self.low, self.high = factor_range

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        factor = np.random.uniform(self.low, self.high)
        sample["input"] *= factor
        # Gain usually applied to input only if target is "clean" ground truth
        # But if it's reconstruction, we might want to scale target too? 
        # Usually Gain is specific to Input Augmentation.
        return sample
