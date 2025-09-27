from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.exceptions import (
    AgentRunError,
    UsageLimitExceeded,
    UnexpectedModelBehavior,
)
from loguru import logger

from src.models.domain import EmotionalProfile


class ModelServiceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ModelService:
    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        instructions: str,
    ):
        settings = GoogleModelSettings(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        provider = GoogleProvider(api_key=api_key)
        model = GoogleModel(model, provider=provider)
        self.agent = Agent(
            model=model,
            model_settings=settings,
            instructions=instructions,
            output_type=EmotionalProfile,
        )

    async def get_emotional_profile(self, lyrics: str) -> EmotionalProfile:
        try:
            result = await self.agent.run(user_prompt=lyrics)
            return result.output
        except UsageLimitExceeded as e:
            logger.warning(
                f"Usage limit exceeded for emotional profile generation: {str(e)}"
            )
            raise ModelServiceException(f"Usage limit exceeded: {str(e)}") from e
        except UnexpectedModelBehavior as e:
            logger.warning(
                f"Unexpected model behavior during emotional profile generation: {str(e)}"
            )
            raise ModelServiceException(f"Unexpected model behavior: {str(e)}") from e
        except AgentRunError as e:
            logger.warning(
                f"Agent run error during emotional profile generation: {str(e)}"
            )
            raise ModelServiceException(f"Agent run error: {str(e)}") from e
