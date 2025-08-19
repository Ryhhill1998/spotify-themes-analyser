class ProfileOrchestrator:
    def __init__(self, repository: ):
        self.repository = repository
        self.spotify_service = SpotifyTopArtistsService()

    def get_top_artists(self, user_id: str, time_range: str) -> list[TopArtist]:
        top_artists = self.spotify_service.get_top_artists(user_id=user_id, time_range=time_range)
        collection_date = date.today()

        previous_top_artists = self.repository.get_previous_top_artists(user_id=user_id, time_range=time_range)

        if not previous_top_artists:
            return self._store_and_return_top_artists(user_id, top_artists, time_range, collection_date)

        return self._update_and_return_top_artists(user_id, top_artists, previous_top_artists, time_range, collection_date)

    def _store_and_return_top_artists(self, user_id: str, top_artists: list[TopArtist], time_range: str, collection_date: date) -> list[TopArtist]:
        self.repository.store_top_artists(user_id=user_id, top_artists=top_artists, time_range=time_range, collection_date=collection_date)
        return top_artists

    def _update_and_return_top_artists(self, user_id: str, top_artists: list[TopArtist], previous_top_artists: list[PreviousTopArtist], time_range: str, collection_date: date) -> list[TopArtist]:
        for artist in top_artists:
            artist.calculate_position_change(previous_top_items=previous_top_artists)

        self._calculate_and_populate_position_change(previous_top_items=previous_top_artists, current_top_items=top_artists)    