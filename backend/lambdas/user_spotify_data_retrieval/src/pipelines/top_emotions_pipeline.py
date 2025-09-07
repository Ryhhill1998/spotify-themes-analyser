from collections import defaultdict
from datetime import date
from statistics import mean

from backend.lambdas.user_spotify_data_retrieval.src.utils.calculations import calculate_position_changes
from src.models.domain import EmotionalProfileRequest, LyricsRequest, TrackLyrics, TopEmotion, Track, TrackEmotionalProfile
from src.models.enums import TimeRange


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
        emotional_profile_responses: list[TrackEmotionalProfile],
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
        # see which tracks already have emotional profiles stored
        track_ids = set(track.id for track in tracks)
        existing_track_emotional_profiles: list[TrackEmotionalProfile] = self.emotional_profile_repository.get_many(track_ids)
        track_ids -= set(profile.track_id for profile in existing_track_emotional_profiles)

        # see which of the remaining tracks have lyrics stored
        existing_track_lyrics: list[TrackLyrics] = self.lyrics_repository.get_many(track_ids)
        track_ids -= set(lyrics.track_id for lyrics in existing_track_lyrics)

        # create lyrics request objects from tracks
        lyrics_requests = [
            LyricsRequest(
                track_id=track.id, 
                track_name=track.name, 
                track_artist=track.artist_ids[0],
            ) 
            for track in tracks
            if track.id in track_ids
        ]

        # get track lyrics from lyrics service and store in db
        new_track_lyrics = await self.lyrics_requests.get_lyrics(lyrics_requests)
        self.lyrics_repository.add_many(new_track_lyrics)

        # create emotional profile requests from lyrics
        all_track_lyrics = [*new_track_lyrics, *existing_track_lyrics]

        emotional_profile_requests = [
            EmotionalProfileRequest(
                track_id=lyrics.track_id, 
                lyrics=lyrics.lyrics,
            )
            for lyrics in all_track_lyrics
        ]

        # get emotional profile responses from emotional profile service and store in db
        new_track_emotional_profiles = await self.emotional_profile_service.get_emotional_profile(
            emotional_profile_requests
        )
        self.emotional_profile_repository.add_many(new_track_emotional_profiles)

        # calculate top emotions
        all_track_emotional_profiles = [*new_track_emotional_profiles, *existing_track_emotional_profiles]

        top_emotions = self._get_top_emotions(
            emotional_profile_responses=all_track_emotional_profiles,
            user_id=user_id,
            time_range=time_range,
            collection_date=collection_date,
        )

        # store in db
        previous_top_emotions: list[TopEmotion] = self.top_emotions_repository.get_previous_top_items(user_id=user_id, time_range=time_range)
        calculate_position_changes(previous_items=previous_top_emotions, current_items=top_emotions)

        self.top_emotions_repository.add_many(top_emotions)
