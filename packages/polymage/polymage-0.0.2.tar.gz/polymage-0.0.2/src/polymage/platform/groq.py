from groq import Groq

from src.polymage.platform.platfom import Platform


"""
groq platform

groq support LLm and audio2text models
you can find the list of supported models here : https://console.groq.com/docs/models
"""


class GroqPlatform(Platform):
    def __init__(self, api_key: str, **kwargs):
        super().__init__("groq", api_key=api_key, **kwargs)
        self.client = Groq(api_key=api_key)

    def _text2text(self, model: str, prompt: str) -> str:
        messages = []
        messages.append({"role": "user", "content": prompt})
        #
        # TODO manage system prompt
        #
        #if agent.system_prompt:
        #    messages.append({"role": "system", "content": agent.system_prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                # Controls randomness: lowering results in less random completions.
                # As the temperature approaches zero, the model will become deterministic
                # and repetitive.
                temperature=0.8,
                # The maximum number of tokens to generate. Requests can use up to
                # 32,768 tokens shared between prompt and completion.
                max_tokens=4096,
                # Controls diversity via nucleus sampling: 0.5 means half of all
                # likelihood-weighted options are considered.
                top_p=1,
                # A stop sequence is a predefined or user-specified text string that
                # signals an AI to stop generating content, ensuring its responses
                # remain focused and concise. Examples include punctuation marks and
                # markers like "[end]".
                stop=None,
                # If set, partial message deltas will be sent.
                stream=False,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")
