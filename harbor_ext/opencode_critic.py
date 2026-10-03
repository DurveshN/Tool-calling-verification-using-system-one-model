"""Harbor agent: stock OpenCode + the post-tool-call critic plugin (critic/).

Use: harbor run -a harbor_ext.opencode_critic:OpenCodeCritic ... --ae CRITIC_MODE=none|llm|clef|clef-flash
The critic mode and API keys come from agent env (--ae). Everything else is inherited unchanged from OpenCode.
Container layout: ~/.config/opencode/plugins/critic.js imports ../critic/core.js (+ questions.json beside it).
"""
from pathlib import Path

from harbor.agents.installed.opencode import OpenCode
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

CRITIC_DIR = Path(__file__).resolve().parent.parent / "critic"


class OpenCodeCritic(OpenCode):
    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        for name in ("critic.js", "core.js", "questions.json"):
            await environment.upload_file(CRITIC_DIR / name, f"/tmp/critic_{name}")
        await self.exec_as_agent(
            environment,
            command=(
                "mkdir -p ~/.config/opencode/plugins ~/.config/opencode/critic && "
                "cp /tmp/critic_critic.js ~/.config/opencode/plugins/critic.js && "
                "cp /tmp/critic_core.js ~/.config/opencode/critic/core.js && "
                "cp /tmp/critic_questions.json ~/.config/opencode/critic/questions.json"
            ),
        )
        await super().run(instruction, environment, context)
