from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel
from PIL import Image

class Platform(ABC):
    """Abstract base for AI platform connectors"""

    def generate(self, model: str, prompt: str, **kwargs) -> Any:
        """
        Polymorphic entry point that dispatches to the appropriate internal method
        based on the presence of an input image and/or expected output type.
        """
        print(f"Generate model={model}, prompt={prompt}, kwargs={kwargs}")
        image: Optional[Image.Image] = kwargs.get("image", None)
        output_type: str = kwargs.get("output_type", "text")  # 'text' or 'image'

        if image is not None:
            # Image input → multimodal
            if output_type == "image":
                return self._image2image(model, prompt, image, **kwargs)
            else:
                return self._image2text(model, prompt, image, **kwargs)
        else:
            # Text-only input
            if output_type == "image":
                return self._text2image(model, prompt, **kwargs)
            else:
                return self._text2text(model, prompt, **kwargs)


    def generate_data(self, model: str, response_model: BaseModel, prompt: str, **kwargs) -> Any:
        """
            Polymorphic entry point that dispatches to the appropriate internal method
            based on the presence of an input image.
            use for text to text or image to text structured output
        """
        image: Optional[Image.Image] = kwargs.get("image", None)
        if image is not None:
            # Image input → multimodal
            return self._image2data(model, response_model, prompt, image, **kwargs)
        else:
            return self._text2data(model, response_model, prompt, **kwargs)


    @abstractmethod
    def _text2text(self, model: str, prompt: str, **kwargs) -> Any:
        """Platform-specific execution interface"""
        pass

    @abstractmethod
    def _text2data(self, model: str, response_model: BaseModel, prompt: str, **kwargs) -> Any:
        """Platform-specific execution interface"""
        pass

    @abstractmethod
    def _text2image(self, model: str, prompt: str, **kwargs) -> Image.Image:
        """Platform-specific execution interface"""
        pass

    @abstractmethod
    def _image2text(self, model: str, prompt: str, image: Image.Image, **kwargs) -> str:
        """Platform-specific execution interface"""
        pass

    @abstractmethod
    def _image2data(self, model: str, response_model: BaseModel, prompt: str, image: Image.Image, **kwargs) -> Any:
        """Platform-specific execution interface"""
        pass

    @abstractmethod
    def _image2image(self, model: str, prompt: str, image: Image.Image, **kwargs) -> Image.Image:
        """Platform-specific execution interface"""
        pass


