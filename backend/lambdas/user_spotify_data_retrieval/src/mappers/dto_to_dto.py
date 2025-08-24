from src.models.dto import Track, Artist, EnrichedTrack


def enrich_tracks_with_artists(tracks: list[Track], artists: list[Artist]) -> list[EnrichedTrack]:
    artists_by_id: dict[str, Artist] = {artist.id: artist for artist in artists}

    enriched_tracks: list[EnrichedTrack] = []

    for track in tracks:
        artist_ids = [artist.id for artist in track.artists]
        artists = [
            artists_by_id[artist_id] for artist_id in artist_ids
            if artist_id in artists_by_id
        ]
        enriched_track = EnrichedTrack(
            id=track.id,
            name=track.name,
            images=track.images,
            spotify_url=track.spotify_url,
            release_date=track.release_date,
            explicit=track.explicit,
            duration_ms=track.duration_ms,
            popularity=track.popularity,
            artists=artists
        )
        enriched_tracks.append(enriched_track)

    return enriched_tracks
