class SpotifyService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def _get_bearer_auth_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}
    
    async def get_profile(self, access_token: str):
        pass

    async def get_top_artists(self, access_token: str, time_range: str, limit: int = 50):
        pass

    async def get_top_tracks(self, access_token: str, time_range: str, limit: int = 50):
        pass
