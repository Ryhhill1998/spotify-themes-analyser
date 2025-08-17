# 1. Get top artists from Spotify API.
# 2. Format artists in correct way for DB.
# 3. Get latest data from DB.
# 4. If no previous data, store artists directly in DB.
# 5. If previous data, find position differences with data just fetched and store in DB.
# 6. Return top artist objects.

from src.components.top_artists.repository import TopArtistsRepository


class TopArtistsManager:
    def __init__(self, repository: TopArtistsRepository):
        self.repository = repository