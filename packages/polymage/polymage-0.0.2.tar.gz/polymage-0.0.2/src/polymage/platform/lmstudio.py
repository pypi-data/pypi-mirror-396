import instructor
from typing import Optional, Any
from openai import OpenAI
from pydantic import BaseModel
from PIL import Image

from polymage.imageutils import image_to_base64
from polymage.platform.platfom import Platform

#
# example : https://github.com/YorkieDev/lmstudioservercodeexamples?tab=readme-ov-file#vision-analysis-python
#

class LMStudioPlatform(Platform):
    def __init__(self, host: str = "127.0.0.1:1234", **kwargs):
        self.host = host


    def _text2text(self, model: str, prompt: str, **kwargs) -> str:
        system_prompt: Optional[str] = kwargs.get("system_promt", "")

        client = OpenAI(
                base_url="http://localhost:1234/v1",  # LM Studio's default endpoint
                api_key="lm-studio"  # Dummy key (LM Studio doesn't require real keys)
        )
        response = client.chat.completions.create(
		    model=model,  # e.g., "gpt-4o" or local model like "llama-3"
		    messages=[
			    {"role": "system", "content": system_prompt},
			    {"role": "user", "content": prompt}
		    ],
		    temperature=0.8
	    )
        return response.choices[0].message.content


    def _text2data(self, model: str, response_model: BaseModel, prompt: str, **kwargs) -> Any:
        # Patch the OpenAI client with Instructor
        client = instructor.patch(
            OpenAI(
                base_url="http://localhost:1234/v1",  # LM Studio's default endpoint
                api_key="lm-studio"  # Dummy key (LM Studio doesn't require real keys)
            ),
            mode=instructor.Mode.JSON  # CRITICAL FOR NON-OPENAI MODELS
        )

        # Get structured response
        response_data = client.chat.completions.create(
            model=model,  # Must match LM Studio's loaded model name
            response_model=response_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_retries=3  # Auto-retry on validation failures
        )

        return response_data.model_dump_json(indent=2)



    def _image2text(self, model: str, prompt: str, image: Image.Image) -> str:
        client = OpenAI(
                base_url="http://localhost:1234/v1",  # LM Studio's default endpoint
                api_key="lm-studio"  # Dummy key (LM Studio doesn't require real keys)
        )

        base64_image = image_to_base64(image)

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{base64_image}"},
                    ],
                }
            ],
        )
        return response.model_dump_json(indent=2)

    def _image2data(self, model: str, response_model: BaseModel, prompt: str, image: Image.Image, **kwargs) -> str:
        # Patch the OpenAI client with Instructor
        client = instructor.patch(
            OpenAI(
                base_url="http://localhost:1234/v1",  # LM Studio's default endpoint
                api_key="lm-studio"  # Dummy key (LM Studio doesn't require real keys)
            ),
            mode=instructor.Mode.JSON  # CRITICAL FOR NON-OPENAI MODELS
        )

        # Get structured response
        response_data = client.chat.completions.create(
            model="your-model-name-here",  # Must match LM Studio's loaded model name
            response_model=response_model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_retries=3  # Auto-retry on validation failures
        )

        return response_data.model_dump_json(indent=2)


    def _text2image(self, model: str, prompt: str, **kwargs) -> Image.Image:
        """Platform-specific execution interface"""
        pass

    def _image2image(self, model: str, prompt: str, image: Image.Image, **kwargs) -> Image.Image:
        """Platform-specific execution interface"""
        pass

