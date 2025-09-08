from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from src.models.domain import EmotionalProfile


class EmotionalProfileService:
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
        result = await self.agent.run(user_prompt=lyrics)
        return result.output
    