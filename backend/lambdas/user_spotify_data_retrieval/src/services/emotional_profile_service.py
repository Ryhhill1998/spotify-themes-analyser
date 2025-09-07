import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from src.models.domain import EmotionalProfile, TrackEmotionalProfile


class EmotionalProfileService:
    def __init__(
        self, 
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
        provider = GoogleProvider(vertexai=True)
        model = GoogleModel(model, provider=provider)
        self.agent = Agent(
            model=model, 
            model_settings=settings, 
            instructions=instructions, 
            output_type=EmotionalProfile,
        )

    async def get_emotional_profile(self, lyrics: str) -> EmotionalProfile:
        return await self.agent.run(user_prompt=lyrics)
    

with open("/Users/ryanhenzell-hill/Documents/full_stack_projects/spotify-themes-analyser-new/spotify-themes-analyser/backend/lambdas/user_spotify_data_retrieval/src/services/prompt.txt") as file:
    instructions = file.read()    


with open("/Users/ryanhenzell-hill/Documents/full_stack_projects/spotify-themes-analyser-new/spotify-themes-analyser/backend/lambdas/user_spotify_data_retrieval/src/services/lyrics.txt") as file:
    lyrics = file.read()


async def main():
    eps = EmotionalProfileService(model="gemini-2.0-flash", temperature=0, max_tokens=8000, top_p=0.95, instructions=instructions)
    response = await eps.get_emotional_profile(lyrics=f"Lyrics:\n\n{lyrics}")
    emotional_profile_response = TrackEmotionalProfile(track_id="1", emotional_profile=response.output)
    print(emotional_profile_response)

asyncio.run(main())
