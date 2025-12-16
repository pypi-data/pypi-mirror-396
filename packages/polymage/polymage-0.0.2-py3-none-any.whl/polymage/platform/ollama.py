from ollama import chat
from PIL import Image

from src.polymage.platform.platfom import Platform

class OllamaPlatform(Platform):
    def __init__(self, host: str = "http://localhost:11434", **kwargs):
        super().__init__("ollama", **kwargs)
        self.host = host


    def _text2text(self, model: str, prompt: str, **kwargs) -> str:
        payload = {
                'role': 'user',
                'content': prompt,
        }

        try:
            response = chat(model=model, messages=[payload])
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")


    def _image2text(self, model: str, prompt: str, image: Image.Image) -> str:
        """
        Not implemented yet
        :param model:
        :param prompt:
        :param image:
        :return:
        """
        pass
