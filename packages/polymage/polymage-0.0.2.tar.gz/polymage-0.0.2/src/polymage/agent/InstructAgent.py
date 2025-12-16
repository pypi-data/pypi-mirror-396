from typing import Any

from polymage.agent.agent import Agent


class InstructAgent(Agent):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


	def run(self, prompt: str, **kwargs) -> Any:
		platform=self.platform
		model=self.model
		system_prompt=self.system_prompt

		return platform.generate(model=model, prompt=prompt, system_prompt=system_prompt, **kwargs)
