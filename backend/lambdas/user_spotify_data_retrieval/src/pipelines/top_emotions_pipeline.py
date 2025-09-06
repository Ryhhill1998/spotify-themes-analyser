from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from statistics import mean
from typing import Annotated

from pydantic import BaseModel, Field

from src.models.domain import TopEmotion, Track
from src.models.enums import TimeRange


@dataclass
class LyricsRequest:
    track_id: str
    track_name: str
    track_artist: str


class LyricsResponse(BaseModel):
    track_id: str
    lyrics: str


@dataclass
class EmotionalProfileRequest:
    track_id: str
    lyrics: str


EmotionPercentage = Annotated[float, Field(ge=0, le=1)]


class EmotionalProfile(BaseModel):
    joy: EmotionPercentage
    sadness: EmotionPercentage
    anger: EmotionPercentage
    fear: EmotionPercentage
    love: EmotionPercentage
    hope: EmotionPercentage
    nostalgia: EmotionPercentage
    loneliness: EmotionPercentage
    confidence: EmotionPercentage
    despair: EmotionPercentage
    excitement: EmotionPercentage
    mystery: EmotionPercentage
    defiance: EmotionPercentage
    gratitude: EmotionPercentage
    spirituality: EmotionPercentage


class EmotionalProfileResponse:
    track_id: str
    emotional_profile: EmotionalProfile


class TopEmotionsPipeline:
    def __init__(
        self, 
        lyrics_service: LyricsService,
        lyrics_repository: LyricsRepository,
        emotional_profile_service: EmotionalProfileService,
        emotional_profile_repository: EmotionalProfileRepository,
        top_emotions_repository: TopEmotionsRepository,
    ):
        self.lyrics_service = lyrics_service
        self.lyrics_repository = lyrics_repository
        self.emotional_profile_service = emotional_profile_service
        self.emotional_profile_repository = emotional_profile_repository
        self.top_emotions_repository = top_emotions_repository

    @staticmethod
    def _get_top_emotions(
        emotional_profile_responses: list[EmotionalProfileResponse],
        user_id: str, 
        time_range: TimeRange, 
        collection_date: date,
    ) -> list[TopEmotion]:
        all_emotion_percentages = defaultdict(list)

        # collect all percentages for each emotion
        for profile_response in emotional_profile_responses:
            emotional_profile_dict = profile_response.emotional_profile.model_dump()
            
            for emotion, percentage in emotional_profile_dict.items():
                all_emotion_percentages[emotion].append(percentage)

        # find average percentage for each emotion
        average_emotion_percentages = {
            emotion: mean(percentages) 
            for emotion, percentages in all_emotion_percentages.items()
        }

        # get top 5 emotions by average percentage
        highest_percentage_emotions = dict(
            sorted(
                average_emotion_percentages.items(), 
                key=lambda _, percentage: percentage,
                reverse=True,
            )[:5]
        )

        # convert to TopEmotion objects
        total = sum(highest_percentage_emotions.values())

        return [
            TopEmotion(
                user_id=user_id,
                collection_date=collection_date,
                time_range=time_range,
                position=index + 1,
                emotion_id=emotion,
                percentage=round(percentage / total, 2),
            )
            for index, (emotion, percentage) in enumerate(highest_percentage_emotions.items())
        ]

    async def run(
        self, 
        tracks: list[Track], 
        user_id: str, 
        time_range: TimeRange, 
        collection_date: date,
    ) -> None:
        # create lyrics request objects from tracks
        lyrics_requests = [
            LyricsRequest(
                track_id=track.id, 
                track_name=track.name, 
                track_artist=track.artist_ids[0],
            ) 
            for track in tracks
        ]

        # get lyrics responses from lyrics service
        lyrics_responses = await self.lyrics_requests.get_lyrics(lyrics_requests)

        # create emotional profile requests from lyrics
        emotional_profile_requests = [
            EmotionalProfileRequest(
                track_id=lyrics.track_id, 
                lyrics=lyrics.lyrics,
            )
            for lyrics in lyrics_responses
        ]

        # get emotional profile responses from emotional profile service
        emotional_profile_responses = await self.emotional_profile_service.get_emotional_profile(
            emotional_profile_requests
        )

        # calculate top emotions
        top_emotions = self._get_top_emotions(
            emotional_profile_responses=emotional_profile_responses,
            user_id=user_id,
            time_range=time_range,
            collection_date=collection_date,
        )

        # store in db
