from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from src.models.enums import TimeRange
from src.models.domain import Artist, TopGenre

class TopGenresPipeline:
    def __init__(self, top_genres_repository: TopGenresRepository):
        self.top_genres_repository = top_genres_repository

    def run(self, artists: list[Artist], user_id: str, time_range: TimeRange, collection_date: date):
        # find most common genres
        all_genres = [genre for artist in artists for genre in artist.genres]
        genre_counts = Counter(all_genres)
        most_common_genres = genre_counts.most_common(5)

        # convert to TopGenre objects
        total = len(all_genres)

        top_genres = [
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

        # Store in db
        self.top_genres_repository.add_many(top_genres)
        