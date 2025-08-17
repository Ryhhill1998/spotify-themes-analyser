from src.components.top_artists import get_top_artists_orchestrator


async def main(event):
    top_artists_orchestrator = get_top_artists_orchestrator()
    top_artists = await top_artists_orchestrator.get_and_store_top_artists(
        user_id=event["user_id"],
        access_token=event["access_token"],
        time_range=event["time_range"],
        collection_date=event["collection_date"],
    )


def handler(event, context):
    # 1. Extract user_id and access_token from event.
    # 2. Get top artists from Spotify API.
    # 3. Get top genres from top artists.
    # 4. Get top tracks from Spotify API.
    # 5. Get top emotions from top tracks - get lyrics for each track and then get emotions from lyrics.
    # 6. Get latest data for each top items table from database.
    # 7. Find position differences and add to objects.
    # 8. Store items in database.
    
    return {"Status": "Running"}
