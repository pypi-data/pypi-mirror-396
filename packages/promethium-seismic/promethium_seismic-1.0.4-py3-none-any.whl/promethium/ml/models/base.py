import torch.nn as nn
from typing import Dict, Any

class PromethiumModel(nn.Module):
    """
    Base class for all Promethium models.
    Enforces a standard forward interface and config storage.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    def forward(self, x):
        raise NotImplementedError

    def get_config(self) -> Dict[str, Any]:
        return self.config
