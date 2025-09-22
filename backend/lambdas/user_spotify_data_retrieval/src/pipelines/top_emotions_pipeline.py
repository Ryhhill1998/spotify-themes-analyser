from collections import defaultdict
from datetime import date
from statistics import mean
import heapq

from src.services.emotional_profiles.emotional_profiles_service import (
    EmotionalProfilesService,
)
from src.services.lyrics.lyrics_service import LyricsService
from src.repositories.top_items.top_emotions_repository import TopEmotionsRepository
from src.utils.calculations import calculate_position_changes
from src.models.domain import (
    TrackEmotionalProfileRequest,
    TrackLyrics,
    TrackLyricsRequest,
    TopEmotion,
    Track,
    TrackEmotionalProfile,
)
from src.models.enums import TimeRange


class TopEmotionsPipelineException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TopEmotionsPipeline:
    def __init__(
        self,
        lyrics_service: LyricsService,
        emotional_profile_service: EmotionalProfilesService,
        top_emotions_repository: TopEmotionsRepository,
    ):
        self.lyrics_service = lyrics_service
        self.emotional_profile_service = emotional_profile_service
        self.top_emotions_repository = top_emotions_repository

    @staticmethod
    def _aggregate_emotions(
        emotional_profile_responses: list[TrackEmotionalProfile],
    ) -> dict[str, float]:
        all_emotion_percentages = defaultdict(list)

        # collect all percentages for each emotion
        for profile_response in emotional_profile_responses:
            emotional_profile_dict = profile_response.emotional_profile.model_dump()

            for emotion, percentage in emotional_profile_dict.items():
                all_emotion_percentages[emotion].append(percentage)

        # find average percentage for each emotion
        return {
            emotion: mean(percentages)
            for emotion, percentages in all_emotion_percentages.items()
        }

    @staticmethod
    def _rank_and_normalise_emotions(
        average_emotions: dict[str, float], n: int
    ) -> dict[str, float]:
        top_n_emotions = heapq.nlargest(
            n, average_emotions.items(), key=lambda item: item[1]
        )

        total = sum(percentage for _, percentage in top_n_emotions)

        return {
            emotion: round(percentage / total, 2)
            for emotion, percentage in top_n_emotions
        }

    @staticmethod
    def _get_top_emotions(
        emotional_profiles: list[TrackEmotionalProfile],
        user_id: str,
        time_range: TimeRange,
        collection_date: date,
        n: int = 5,
    ) -> list[TopEmotion]:
        average_emotion_percentages = TopEmotionsPipeline._aggregate_emotions(
            emotional_profiles
        )

        top_emotions_dict = TopEmotionsPipeline._rank_and_normalise_emotions(
            average_emotions=average_emotion_percentages, n=n
        )

        return [
            TopEmotion(
                user_id=user_id,
                collection_date=collection_date,
                time_range=time_range,
                position=index + 1,
                emotion_id=emotion,
                percentage=percentage,
            )
            for index, (emotion, percentage) in enumerate(top_emotions_dict.items())
        ]

    async def run(
        self,
        tracks: list[Track],
        user_id: str,
        time_range: TimeRange,
        collection_date: date,
    ) -> None:
        lyrics_requests = [
            TrackLyricsRequest(
                track_id=track.id,
                track_name=track.name,
                track_artist=track.artists[0].name,
            )
            for track in tracks
        ]
        track_lyrics: list[TrackLyrics] = await self.lyrics_service.get_many_lyrics(
            lyrics_requests
        )

        emotional_profile_requests = [
            TrackEmotionalProfileRequest(
                track_id=lyrics.track_id,
                lyrics=lyrics.lyrics,
            )
            for lyrics in track_lyrics
        ]
        track_emotional_profiles: list[TrackEmotionalProfile] = (
            await self.emotional_profile_service.get_many_emotional_profiles(
                emotional_profile_requests
            )
        )

        top_emotions: list[TopEmotion] = self._get_top_emotions(
            emotional_profiles=track_emotional_profiles,
            user_id=user_id,
            time_range=time_range,
            collection_date=collection_date,
        )

        # store in db
        previous_top_emotions: list[TopEmotion] = (
            self.top_emotions_repository.get_previous_top_items(
                user_id=user_id, time_range=time_range
            )
        )
        calculate_position_changes(
            previous_items=previous_top_emotions, current_items=top_emotions
        )

        self.top_emotions_repository.add_many(top_emotions)
