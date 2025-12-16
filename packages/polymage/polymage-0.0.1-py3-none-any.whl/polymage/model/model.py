from abc import ABC
from typing import Dict, Optional, Any


class Model(ABC):
    name: str
    type: str  # e.g., "text2text", "text2image", "image2image"
    default_params: Dict[str, Any]

    def __init__(self, name: str, type: str, **overrides):
        self.name = name
        self.type = type
        self.params = {**self.default_params, **overrides}

    def get_payload(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build platform-agnostic payload (agent may further modify)."""
        raise NotImplementedError
