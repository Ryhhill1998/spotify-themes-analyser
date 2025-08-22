from collections import defaultdict
from dataclasses import dataclass
from src.components.top_genres.models.domain import TopGenre
from src.components.top_artists.models.domain import TopArtist


@dataclass
class Genre:
    name: str
    count: int


class TopGenresDataService:
    def get_top_genres(self, top_artists: list[TopArtist]) -> list[TopGenre]:
        all_genres = [genre for artist in top_artists for genre in artist.genres]
        genres_map = defaultdict(int)

        for genre in all_genres:
            genres_map[genre] += 1

        genres = [Genre(name=genre, count=count) for genre, count in genres_map.items()]
        genres.sort(key=lambda genre: genre.count, reverse=True)
        genres = genres[:5]
        total_count = sum(genre.count for genre in genres)
        top_genres = [
            TopGenre(
                id=genre.name,
                name=genre.name, 
                percentage=round(genre.count / total_count, 2),
                position=index + 1,
            ) 
            for index, genre in enumerate(genres)
        ]
        return top_genres
