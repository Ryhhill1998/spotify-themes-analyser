from backend.lambdas.user_spotify_data_retrieval.src.services.spotify_service import SpotifyService


class TopArtistsPipeline:
    def __init__(self, spotify_service: SpotifyService, artist_repo: ArtistRepository):
        self.spotify_service = spotify_service
        self.artist_repo = artist_repo

    def run(self, access_token: str, user_id: str):
        """
        Executes the pipeline to fetch and store top artists for a user.

        :param user_id: The Spotify user ID.
        """
        top_artists = self.fetch_top_artists(user_id)
        self.store_top_artists(user_id, top_artists)
        return top_artists