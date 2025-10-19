import asyncio
from loguru import logger
from src.models.domain import TrackEmotionalProfile, TrackEmotionalProfileRequest
from src.services.emotional_profiles.model_service import (
    EmotionalProfileCalculator,
)
from src.repositories.track_emotional_profiles_repository import (
    TrackEmotionalProfilesRepository,
)


class EmotionalProfilesServiceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EmotionalProfilesService:
    def __init__(
        self,
        emotional_profile_repository: TrackEmotionalProfilesRepository,
        emotional_profile_calculator: EmotionalProfileCalculator,
    ):
        self.emotional_profile_repository = emotional_profile_repository
        self.emotional_profile_calculator = emotional_profile_calculator

    async def _calculate_emotional_profile(
        self, request: TrackEmotionalProfileRequest
    ) -> TrackEmotionalProfile:
        emotional_profile = (
            await self.emotional_profile_calculator.get_emotional_profile(
                request.lyrics
            )
        )
        return TrackEmotionalProfile(
            track_id=request.track_id, emotional_profile=emotional_profile
        )

    async def _calculate_many_emotional_profiles(
        self, requests: list[TrackEmotionalProfileRequest]
    ) -> list[TrackEmotionalProfile]:
        tasks = [self._calculate_emotional_profile(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        for request, result in zip(requests, results):
            if isinstance(result, TrackEmotionalProfile):
                successful_results.append(result)
            elif isinstance(result, Exception):
                logger.warning(
                    f"Failed to calculate emotional profile for track {request.track_id}: {result}"
                )

        if not successful_results:
            raise EmotionalProfilesServiceException(
                "No emotional profiles were successfully calculated"
            )

        return successful_results

    async def get_many_emotional_profiles(
        self, requests: list[TrackEmotionalProfileRequest]
    ) -> list[TrackEmotionalProfile]:
        # Check which emotional profiles are already in the DB
        track_ids = set(request.track_id for request in requests)
        existing_profiles = self.emotional_profile_repository.get_many(track_ids)
        track_ids -= set(profile.track_id for profile in existing_profiles)

        # Determine which requests need emotional profile calculation
        profile_requests = [
            request for request in requests if request.track_id in track_ids
        ]

        # Calculate missing emotional profiles
        new_profiles = await self._calculate_many_emotional_profiles(profile_requests)

        # Store newly calculated emotional profiles in the DB
        self.emotional_profile_repository.add_many(new_profiles)

        # Combine existing and newly calculated emotional profiles
        return [*existing_profiles, *new_profiles]
