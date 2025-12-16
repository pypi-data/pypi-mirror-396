from abc import ABC
from typing import Any, Optional

from polymage.platform.platfom import Platform


class Agent(ABC):
	def __init__(
			self,
			platform: Platform,
			model: str,
			system_prompt: Optional[str] = None,
	):
		self.platform=platform
		self.model=model
		self.system_prompt=system_prompt or ""

	def run(self, prompt: str, **kwargs) -> Any:
		platform=self.platform
		model=self.model
		system_prompt=self.system_prompt

		return platform.generate(model=model, prompt=prompt, system_prompt=system_prompt, **kwargs)

