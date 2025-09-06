from collections import Counter
from datetime import date

from src.utils.calculations import calculate_position_changes
from src.repositories.top_items.top_genres_repository import TopGenresRepository
from src.models.enums import TimeRange
from src.models.domain import Artist, TopGenre

class TopGenresPipeline:
    def __init__(self, top_genres_repository: TopGenresRepository):
        self.top_genres_repository = top_genres_repository

    @staticmethod
    def _get_top_genres(
        artists: list[Artist], 
        user_id: str, 
        time_range: TimeRange, 
        collection_date: date,
    ) -> list[TopGenre]:
        # find most common genres
        all_genres = [genre for artist in artists for genre in artist.genres]
        genre_counts = Counter(all_genres)
        most_common_genres = genre_counts.most_common(5)

        # convert to TopGenre objects
        total = sum([genre[1] for genre in most_common_genres])

        return [
            TopGenre(
                user_id=user_id, 
                collection_date=collection_date, 
                time_range=time_range, 
                position=index + 1, 
                genre_id=genre, 
                percentage=round(count / total, 2),
            )
            for index, (genre, count) in enumerate(most_common_genres)
        ]

    def run(
        self, 
        artists: list[Artist], 
        user_id: str, 
        time_range: TimeRange, 
        collection_date: date,
    ) -> None:
        top_genres = self._get_top_genres(
            artists=artists, 
            user_id=user_id, 
            time_range=time_range, 
            collection_date=collection_date,
        )

        previous_top_genres: list[TopGenre] = self.top_genres_repository.get_previous_top_items(user_id=user_id, time_range=time_range)
        calculate_position_changes(previous_items=previous_top_genres, current_items=top_genres)

        self.top_genres_repository.add_many(top_genres)
        