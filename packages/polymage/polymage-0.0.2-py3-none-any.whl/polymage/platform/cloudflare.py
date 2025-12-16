import os
import random
import requests

from src.polymage.platform.platfom import Platform


"""
Clouflare provide AI workers with some free tier

Clouflare support LLm and some other multimedia models
you can find the list of supported models here : https://developers.cloudflare.com/workers-ai/models/
"""


class CloudflarePlatform(Platform):
    def __init__(self, **kwargs):
        super().__init__("cloudflare", **kwargs)

    def _text2image(self, agent: Agent, model: str, prompt: str) -> str:
        CLOUDFLARE_ID = os.environ['CLOUDFLARE_ID']
        CLOUDFLARE_TOKEN = os.environ['CLOUDFLARE_TOKEN']
        random_seed = random.randint(0, 2 ** 32 - 1)
        url = "https://api.cloudflare.com/client/v4/accounts/" + CLOUDFLARE_ID + "/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + CLOUDFLARE_TOKEN
        }
        data = {
            'steps': 5,
            'seed': random_seed,
            'prompt': prompt
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            result = response.json()
            #print(f"RESULT = {result}")
            return result['result']['image']

        except Exception as e:
            print(f"Error generating image: {e}")
            raise
