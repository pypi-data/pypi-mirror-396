import base64
from io import BytesIO

import requests
from typing import Any
from PIL import Image

import polymage.imageutils
from polymage.platform.platfom import Platform

#
# installed models default params
#
highdream_fast_settings = {
    "model": "hidream_i1_fast_q8p.ckpt",
    "negative_prompt": "",
    "steps": 14,
    "batch_count": 1,
    "sampler": "DPM++ 2M Trailing",
    "seed": -1,
    "hires_fix": False,
    "tiled_decoding": False,
    "clip_skip": 1,
    "shift": 1.0,
    "guidance_scale": 1.0,
    "resolution_dependent_shift": False
}

flux_kontext_settings = {
    "model": "flux_1_kontext_dev_q8p.ckpt",
    "negative_prompt": "",
    "steps": 8,
    "batch_count": 1,
    "sampler": "DPM++ 2M Trailing",
    "seed": -1,
    "hires_fix": False,
    "tiled_decoding": False,
    "clip_skip": 1,
    "shift": 1.0,
    "guidance_scale": 2.0,
    "resolution_dependent_shift": True,
    "loras": [{"file": "flux.1_turbo_alpha_lora_f16.ckpt", "weight": 1, "mode": "all"}],
}

qwen_image_edit_settings_4_steps = {
    "model": "qwen_image_edit_2509_q8p.ckpt",
    "negative_prompt": "",
    "steps": 5,
    "batch_count": 1,
    "sampler": "DPM++ 2M Trailing",
    "seed": -1,
    "hires_fix": False,
    "tiled_decoding": False,
    "clip_skip": 1,
    "shift": 1.0,
    "guidance_scale": 2.0,
    "resolution_dependent_shift": True,
    "loras": [{"file": "qwen_image_edit_2509_lightning_4_step_v1.0_lora_f16.ckpt", "weight": 1, "mode": "all"}],
}

qwen_image_edit_settings_8_steps = {
    "model": "qwen_image_edit_2509_q8p.ckpt",
    "negative_prompt": "",
    "steps": 8,
    "batch_count": 1,
    "sampler": "DPM++ 2M Trailing",
    "seed": -1,
    "hires_fix": False,
    "tiled_decoding": False,
    "clip_skip": 1,
    "shift": 1.0,
    "guidance_scale": 2.0,
    "resolution_dependent_shift": True,
    "loras": [{"file": "qwen_image_edit_2509_lightning_8_step_v1.0_lora_f16.ckpt", "weight": 1, "mode": "all"}],
}



MODELS_SETTINGS = {
    "highdream_fast": highdream_fast_settings,
    "flux_kontext": flux_kontext_settings,
    "qwen_image_edit_4_steps": qwen_image_edit_settings_4_steps,
    "qwen_image_edit_8_steps": qwen_image_edit_settings_8_steps,
}

class DrawThingsPlatform(Platform):
    def __init__(self, host: str = "127.0.0.1:7860", **kwargs):
        self.host = host


    def _text2image(self, model: str, prompt: str) -> Image:
        payload = MODELS_SETTINGS[model]
        payload["prompt"] = prompt

        try:
            response = requests.post(f"http://{self.host}/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()
            json_data = response.json()
            base64_string = json_data["images"][0]
            image = omniagent.base64_to_image(base64_string)
            return image
        except Exception as e:
            raise RuntimeError(f"DrawThings API error: {e}")


    def _image2image(self, model: str, prompt: str, image: Image) -> Image:
        payload = MODELS_SETTINGS[model]
        payload["prompt"] = prompt
        base64_image = omniagent.image_to_base64(image)
        payload["init_images"] = [base64_image]

        try:
            response = requests.post(f"http://{self.host}/sdapi/v1/img2img", json=payload)
            response.raise_for_status()
            json_data = response.json()
            base64_string = json_data["images"][0]
            return base64_string
        except Exception as e:
            raise RuntimeError(f"DrawThings API error: {e}")
