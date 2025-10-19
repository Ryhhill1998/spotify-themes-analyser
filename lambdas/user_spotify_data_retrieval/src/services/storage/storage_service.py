import abc
from profile import Profile

from src.models.domain import (
    Artist,
    TopArtist,
    TopEmotion,
    TopGenre,
    TopTrack,
    Track,
    TrackEmotionalProfile,
    TrackLyrics,
)


class StorageService(abc.ABC):

    @abc.abstractmethod
    def upsert_profile(self, profile: Profile) -> None:
        pass

    @abc.abstractmethod
    def upsert_artists(self, artists: list[Artist]) -> None:
        pass

    @abc.abstractmethod
    def upsert_tracks(self, tracks: list[Track]) -> None:
        pass

    @abc.abstractmethod
    def store_track_lyrics(self, track_lyrics: list[TrackLyrics]) -> None:
        pass

    @abc.abstractmethod
    def get_track_lyrics(self, track_ids: list[str]) -> list[TrackLyrics]:
        pass

    @abc.abstractmethod
    def store_emotional_profiles(
        self, emotional_profiles: list[TrackEmotionalProfile]
    ) -> None:
        pass

    @abc.abstractmethod
    def get_emotional_profiles(
        self, track_ids: list[str]
    ) -> list[TrackEmotionalProfile]:
        pass

    @abc.abstractmethod
    def store_top_artists(self, top_artists: list[TopArtist]) -> None:
        pass

    @abc.abstractmethod
    def store_top_tracks(self, top_tracks: list[TopTrack]) -> None:
        pass

    @abc.abstractmethod
    def store_top_genres(self, top_genres: list[TopGenre]) -> None:
        pass

    @abc.abstractmethod
    def store_top_emotions(self, top_emotions: list[TopEmotion]) -> None:
        pass
