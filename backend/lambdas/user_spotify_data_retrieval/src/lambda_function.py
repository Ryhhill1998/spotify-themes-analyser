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
