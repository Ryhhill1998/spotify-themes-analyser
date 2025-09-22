import asyncio
from collections import defaultdict
from datetime import date
from statistics import mean
import heapq

from src.repositories.track_emotional_profiles_repository import (
    TrackEmotionalProfilesRepository,
)
from src.repositories.track_lyrics_repository import TrackLyricsRepository
from src.repositories.top_items.top_emotions_repository import TopEmotionsRepository
from src.services.emotional_profile_service import EmotionalProfileService
from backend.lambdas.user_spotify_data_retrieval.src.services.lyrics_scraper import (
    LyricsScraper,
)
from src.utils.calculations import calculate_position_changes
from src.models.domain import (
    TrackEmotionalProfileRequest,
    TrackLyricsRequest,
    TrackLyrics,
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
        lyrics_service: LyricsScraper,
        lyrics_repository: TrackLyricsRepository,
        emotional_profile_service: EmotionalProfileService,
        emotional_profile_repository: TrackEmotionalProfilesRepository,
        top_emotions_repository: TopEmotionsRepository,
    ):
        self.lyrics_service = lyrics_service
        self.lyrics_repository = lyrics_repository
        self.emotional_profile_service = emotional_profile_service
        self.emotional_profile_repository = emotional_profile_repository
        self.top_emotions_repository = top_emotions_repository

    async def _get_track_lyrics(self, request: TrackLyricsRequest) -> TrackLyrics:
        lyrics = await self.lyrics_service.get_lyrics(
            artist_name=request.track_artist, track_title=request.track_name
        )
        return TrackLyrics(track_id=request.track_id, lyrics=lyrics)

    async def _get_several_track_lyrics(
        self, lyrics_requests: list[TrackLyricsRequest]
    ) -> list[TrackLyrics]:
        tasks = [self._get_track_lyrics(request) for request in lyrics_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [res for res in results if isinstance(res, TrackLyrics)]

    async def _get_track_emotional_profile(
        self, request: TrackEmotionalProfileRequest
    ) -> TrackEmotionalProfile:
        emotional_profile = await self.emotional_profile_service.get_emotional_profile(
            request.lyrics
        )
        return TrackEmotionalProfile(
            track_id=request.track_id, emotional_profile=emotional_profile
        )

    async def _get_several_track_emotional_profiles(
        self, emotional_profile_requests: list[TrackEmotionalProfileRequest]
    ) -> list[TrackEmotionalProfile]:
        tasks = [
            self._get_track_emotional_profile(request)
            for request in emotional_profile_requests
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [res for res in results if isinstance(res, TrackEmotionalProfile)]

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
        emotional_profile_responses: list[TrackEmotionalProfile],
        user_id: str,
        time_range: TimeRange,
        collection_date: date,
        n: int = 5,
    ) -> list[TopEmotion]:
        average_emotion_percentages = TopEmotionsPipeline._aggregate_emotions(
            emotional_profile_responses
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
        track_ids = set(track.id for track in tracks)

        # see which tracks already have emotional profiles stored
        existing_track_emotional_profiles: list[TrackEmotionalProfile] = (
            self.emotional_profile_repository.get_many(track_ids)
        )
        track_ids -= set(
            profile.track_id for profile in existing_track_emotional_profiles
        )

        # see which of the remaining tracks have lyrics stored
        existing_track_lyrics: list[TrackLyrics] = self.lyrics_repository.get_many(
            track_ids
        )
        track_ids -= set(lyrics.track_id for lyrics in existing_track_lyrics)

        # create lyrics request objects from tracks
        lyrics_requests = [
            TrackLyricsRequest(
                track_id=track.id,
                track_name=track.name,
                track_artist=track.artists[0].name,
            )
            for track in tracks
            if track.id in track_ids
        ]

        # get track lyrics from lyrics service and store in db
        new_track_lyrics: list[TrackLyrics] = await self._get_several_track_lyrics(
            lyrics_requests
        )
        self.lyrics_repository.add_many(new_track_lyrics)

        # create emotional profile requests from lyrics
        all_track_lyrics: list[TrackLyrics] = [
            *new_track_lyrics,
            *existing_track_lyrics,
        ]

        emotional_profile_requests = [
            TrackEmotionalProfileRequest(
                track_id=lyrics.track_id,
                lyrics=lyrics.lyrics,
            )
            for lyrics in all_track_lyrics
        ]

        # get emotional profile responses from emotional profile service and store in db
        new_track_emotional_profiles: list[TrackEmotionalProfile] = (
            await self._get_several_track_emotional_profiles(emotional_profile_requests)
        )
        print(f"{new_track_emotional_profiles = }")
        self.emotional_profile_repository.add_many(new_track_emotional_profiles)

        # calculate top emotions
        all_track_emotional_profiles: list[TrackEmotionalProfile] = [
            *new_track_emotional_profiles,
            *existing_track_emotional_profiles,
        ]

        top_emotions: list[TopEmotion] = self._get_top_emotions(
            emotional_profile_responses=all_track_emotional_profiles,
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
