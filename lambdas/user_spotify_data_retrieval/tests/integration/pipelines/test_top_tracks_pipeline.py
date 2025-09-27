import datetime
import re
from typing import AsyncGenerator
import httpx
import pytest

import pytest_asyncio
from sqlalchemy.orm import Session

from src.repositories.artists_repository import ArtistsRepository
from src.models.shared import Image, TrackArtist
from src.models.domain import Track, TopTrack
from src.models.enums import PositionChange, TimeRange
from src.models.db import TrackDB, ProfileDB, TopTrackDB
from src.repositories.tracks_repository import TracksRepository
from src.repositories.top_items.top_tracks_repository import (
    TopTracksRepository,
    TopTracksRepositoryException,
)
from src.services.spotify_service import SpotifyService
from src.pipelines.top_tracks_pipeline import (
    TopTracksPipeline,
    TopTracksPipelineException,
)

TOP_TRACKS_DATA = {
    "items": [
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                        },
                        "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                        "id": "2n2RSaZqBuUUukhbLlpnE6",
                        "name": "Sleep Token",
                        "type": "artist",
                        "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                    }
                ],
                "available_markets": ["MG", "MU", "MZ"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/1lS7FeRcSUuIGqyg99UGpj"
                },
                "href": "https://api.spotify.com/v1/albums/1lS7FeRcSUuIGqyg99UGpj",
                "id": "1lS7FeRcSUuIGqyg99UGpj",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "Even In Arcadia",
                "release_date": "2025-05-09",
                "release_date_precision": "day",
                "total_tracks": 10,
                "type": "album",
                "uri": "spotify:album:1lS7FeRcSUuIGqyg99UGpj",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                    },
                    "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                    "id": "2n2RSaZqBuUUukhbLlpnE6",
                    "name": "Sleep Token",
                    "type": "artist",
                    "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                }
            ],
            "available_markets": ["AR", "XK"],
            "disc_number": 1,
            "duration_ms": 466463,
            "explicit": False,
            "external_ids": {"isrc": "USRC12500013"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/4Lojbtk7XNMdSKRHSFbdkm"
            },
            "href": "https://api.spotify.com/v1/tracks/4Lojbtk7XNMdSKRHSFbdkm",
            "id": "4Lojbtk7XNMdSKRHSFbdkm",
            "is_local": False,
            "is_playable": True,
            "name": "Look To Windward",
            "popularity": 73,
            "preview_url": None,
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:4Lojbtk7XNMdSKRHSFbdkm",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6Ad91Jof8Niiw0lGLLi3NW"
                        },
                        "href": "https://api.spotify.com/v1/artists/6Ad91Jof8Niiw0lGLLi3NW",
                        "id": "6Ad91Jof8Niiw0lGLLi3NW",
                        "name": "YUNGBLUD",
                        "type": "artist",
                        "uri": "spotify:artist:6Ad91Jof8Niiw0lGLLi3NW",
                    }
                ],
                "available_markets": ["PW"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/19PD2IPfceDn9fLAa05TFE"
                },
                "href": "https://api.spotify.com/v1/albums/19PD2IPfceDn9fLAa05TFE",
                "id": "19PD2IPfceDn9fLAa05TFE",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b2737808f0d7992027b6b10254dd",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e027808f0d7992027b6b10254dd",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d000048517808f0d7992027b6b10254dd",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "Idols",
                "release_date": "2025-06-20",
                "release_date_precision": "day",
                "total_tracks": 12,
                "type": "album",
                "uri": "spotify:album:19PD2IPfceDn9fLAa05TFE",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6Ad91Jof8Niiw0lGLLi3NW"
                    },
                    "href": "https://api.spotify.com/v1/artists/6Ad91Jof8Niiw0lGLLi3NW",
                    "id": "6Ad91Jof8Niiw0lGLLi3NW",
                    "name": "YUNGBLUD",
                    "type": "artist",
                    "uri": "spotify:artist:6Ad91Jof8Niiw0lGLLi3NW",
                }
            ],
            "available_markets": ["NG", "TZ", "UG", "BZ", "BF", "UZ", "ZW"],
            "disc_number": 1,
            "duration_ms": 246946,
            "explicit": False,
            "external_ids": {"isrc": "USUG12501758"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/42GKyvz5KBsHTBaLpo3cqJ"
            },
            "href": "https://api.spotify.com/v1/tracks/42GKyvz5KBsHTBaLpo3cqJ",
            "id": "42GKyvz5KBsHTBaLpo3cqJ",
            "is_local": False,
            "is_playable": True,
            "name": "Zombie",
            "popularity": 73,
            "preview_url": None,
            "track_number": 4,
            "type": "track",
            "uri": "spotify:track:42GKyvz5KBsHTBaLpo3cqJ",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/4IWBUUAFIplrNtaOHcJPRM"
                        },
                        "href": "https://api.spotify.com/v1/artists/4IWBUUAFIplrNtaOHcJPRM",
                        "id": "4IWBUUAFIplrNtaOHcJPRM",
                        "name": "James Arthur",
                        "type": "artist",
                        "uri": "spotify:artist:4IWBUUAFIplrNtaOHcJPRM",
                    }
                ],
                "available_markets": ["DO", "DE", "EE", "SV"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/7nktQKQFOMkh40iOTOzzBS"
                },
                "href": "https://api.spotify.com/v1/albums/7nktQKQFOMkh40iOTOzzBS",
                "id": "7nktQKQFOMkh40iOTOzzBS",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273765c38475815f11c5487299e",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02765c38475815f11c5487299e",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851765c38475815f11c5487299e",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "PISCES",
                "release_date": "2025-04-25",
                "release_date_precision": "day",
                "total_tracks": 12,
                "type": "album",
                "uri": "spotify:album:7nktQKQFOMkh40iOTOzzBS",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/4IWBUUAFIplrNtaOHcJPRM"
                    },
                    "href": "https://api.spotify.com/v1/artists/4IWBUUAFIplrNtaOHcJPRM",
                    "id": "4IWBUUAFIplrNtaOHcJPRM",
                    "name": "James Arthur",
                    "type": "artist",
                    "uri": "spotify:artist:4IWBUUAFIplrNtaOHcJPRM",
                }
            ],
            "available_markets": ["CL", "CO", "CR", "CY"],
            "disc_number": 1,
            "duration_ms": 255084,
            "explicit": False,
            "external_ids": {"isrc": "DEE862402264"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/0871iIk4stdN902Gj33P2d"
            },
            "href": "https://api.spotify.com/v1/tracks/0871iIk4stdN902Gj33P2d",
            "id": "0871iIk4stdN902Gj33P2d",
            "is_local": False,
            "is_playable": True,
            "name": "Embers",
            "popularity": 46,
            "preview_url": None,
            "track_number": 8,
            "type": "track",
            "uri": "spotify:track:0871iIk4stdN902Gj33P2d",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                        },
                        "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                        "id": "6NnBBumbcMYsaPTHFhPtXD",
                        "name": "VOILÀ",
                        "type": "artist",
                        "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                    }
                ],
                "available_markets": ["CI", "DJ", "CD", "CG"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/5k77pSc53QUp8WNIXwseu7"
                },
                "href": "https://api.spotify.com/v1/albums/5k77pSc53QUp8WNIXwseu7",
                "id": "5k77pSc53QUp8WNIXwseu7",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "The Last Laugh (Part I)",
                "release_date": "2025-06-20",
                "release_date_precision": "day",
                "total_tracks": 14,
                "type": "album",
                "uri": "spotify:album:5k77pSc53QUp8WNIXwseu7",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                    },
                    "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                    "id": "6NnBBumbcMYsaPTHFhPtXD",
                    "name": "VOILÀ",
                    "type": "artist",
                    "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                }
            ],
            "available_markets": ["KH", "CM", "TD", "KM", "GQ", "SZ", "GA"],
            "disc_number": 1,
            "duration_ms": 245000,
            "explicit": False,
            "external_ids": {"isrc": "QM24S2501952"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/71w4bqfvnINCpLnypPM9Dj"
            },
            "href": "https://api.spotify.com/v1/tracks/71w4bqfvnINCpLnypPM9Dj",
            "id": "71w4bqfvnINCpLnypPM9Dj",
            "is_local": False,
            "is_playable": True,
            "name": "Good Grief",
            "popularity": 48,
            "preview_url": None,
            "track_number": 13,
            "type": "track",
            "uri": "spotify:track:71w4bqfvnINCpLnypPM9Dj",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                        },
                        "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                        "id": "2n2RSaZqBuUUukhbLlpnE6",
                        "name": "Sleep Token",
                        "type": "artist",
                        "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                    }
                ],
                "available_markets": ["GR", "GT", "HN", "HK", "HU"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/1lS7FeRcSUuIGqyg99UGpj"
                },
                "href": "https://api.spotify.com/v1/albums/1lS7FeRcSUuIGqyg99UGpj",
                "id": "1lS7FeRcSUuIGqyg99UGpj",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "Even In Arcadia",
                "release_date": "2025-05-09",
                "release_date_precision": "day",
                "total_tracks": 10,
                "type": "album",
                "uri": "spotify:album:1lS7FeRcSUuIGqyg99UGpj",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                    },
                    "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                    "id": "2n2RSaZqBuUUukhbLlpnE6",
                    "name": "Sleep Token",
                    "type": "artist",
                    "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                }
            ],
            "available_markets": ["IQ", "LY", "TJ", "VE", "ET", "XK"],
            "disc_number": 1,
            "duration_ms": 214648,
            "explicit": True,
            "external_ids": {"isrc": "USRC12500015"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/0Uvf2v96tJ5CuyK0LtyAgd"
            },
            "href": "https://api.spotify.com/v1/tracks/0Uvf2v96tJ5CuyK0LtyAgd",
            "id": "0Uvf2v96tJ5CuyK0LtyAgd",
            "is_local": False,
            "is_playable": True,
            "name": "Past Self",
            "popularity": 73,
            "preview_url": None,
            "track_number": 3,
            "type": "track",
            "uri": "spotify:track:0Uvf2v96tJ5CuyK0LtyAgd",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                        },
                        "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                        "id": "6NnBBumbcMYsaPTHFhPtXD",
                        "name": "VOILÀ",
                        "type": "artist",
                        "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                    }
                ],
                "available_markets": ["AR", "AU", "AT", "BE", "BO", "CA"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/5k77pSc53QUp8WNIXwseu7"
                },
                "href": "https://api.spotify.com/v1/albums/5k77pSc53QUp8WNIXwseu7",
                "id": "5k77pSc53QUp8WNIXwseu7",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "The Last Laugh (Part I)",
                "release_date": "2025-06-20",
                "release_date_precision": "day",
                "total_tracks": 14,
                "type": "album",
                "uri": "spotify:album:5k77pSc53QUp8WNIXwseu7",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                    },
                    "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                    "id": "6NnBBumbcMYsaPTHFhPtXD",
                    "name": "VOILÀ",
                    "type": "artist",
                    "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                },
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/4OTFxPi5CtWyj1NThDe6z5"
                    },
                    "href": "https://api.spotify.com/v1/artists/4OTFxPi5CtWyj1NThDe6z5",
                    "id": "4OTFxPi5CtWyj1NThDe6z5",
                    "name": "Weathers",
                    "type": "artist",
                    "uri": "spotify:artist:4OTFxPi5CtWyj1NThDe6z5",
                },
            ],
            "available_markets": ["AR", "AU", "AT", "BE", "BO", "BR", "BG"],
            "disc_number": 1,
            "duration_ms": 194000,
            "explicit": True,
            "external_ids": {"isrc": "QM24S2501016"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/3bUp4O9m98QM9kvVpqtQKP"
            },
            "href": "https://api.spotify.com/v1/tracks/3bUp4O9m98QM9kvVpqtQKP",
            "id": "3bUp4O9m98QM9kvVpqtQKP",
            "is_local": False,
            "is_playable": True,
            "name": "Unhappy Hour (with Weathers)",
            "popularity": 45,
            "preview_url": None,
            "track_number": 8,
            "type": "track",
            "uri": "spotify:track:3bUp4O9m98QM9kvVpqtQKP",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz"
                        },
                        "href": "https://api.spotify.com/v1/artists/6XyY86QOPPrYVGvF9ch6wz",
                        "id": "6XyY86QOPPrYVGvF9ch6wz",
                        "name": "Linkin Park",
                        "type": "artist",
                        "uri": "spotify:artist:6XyY86QOPPrYVGvF9ch6wz",
                    }
                ],
                "available_markets": ["ZA", "SA", "IQ", "VE"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/5QfFvOMOJ0CrIDmu33RmSJ"
                },
                "href": "https://api.spotify.com/v1/albums/5QfFvOMOJ0CrIDmu33RmSJ",
                "id": "5QfFvOMOJ0CrIDmu33RmSJ",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273a493a67f01bcfe65b23bc910",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02a493a67f01bcfe65b23bc910",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851a493a67f01bcfe65b23bc910",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "From Zero (Deluxe Edition)",
                "release_date": "2025-05-16",
                "release_date_precision": "day",
                "total_tracks": 14,
                "type": "album",
                "uri": "spotify:album:5QfFvOMOJ0CrIDmu33RmSJ",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz"
                    },
                    "href": "https://api.spotify.com/v1/artists/6XyY86QOPPrYVGvF9ch6wz",
                    "id": "6XyY86QOPPrYVGvF9ch6wz",
                    "name": "Linkin Park",
                    "type": "artist",
                    "uri": "spotify:artist:6XyY86QOPPrYVGvF9ch6wz",
                }
            ],
            "available_markets": ["AR", "JO", "PS", "IN"],
            "disc_number": 1,
            "duration_ms": 183223,
            "explicit": False,
            "external_ids": {"isrc": "USWB12500290"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/2SwdMXPvGdciXamSjfoNH9"
            },
            "href": "https://api.spotify.com/v1/tracks/2SwdMXPvGdciXamSjfoNH9",
            "id": "2SwdMXPvGdciXamSjfoNH9",
            "is_local": False,
            "is_playable": True,
            "name": "Up From the Bottom",
            "popularity": 75,
            "preview_url": None,
            "track_number": 12,
            "type": "track",
            "uri": "spotify:track:2SwdMXPvGdciXamSjfoNH9",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye"
                        },
                        "href": "https://api.spotify.com/v1/artists/3T55D3LMiygE9eSKFpiAye",
                        "id": "3T55D3LMiygE9eSKFpiAye",
                        "name": "Badflower",
                        "type": "artist",
                        "uri": "spotify:artist:3T55D3LMiygE9eSKFpiAye",
                    }
                ],
                "available_markets": ["MZ", "AO", "CI", "DJ", "ZM"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/1ApjqWf9VPtgc5RgWcLk68"
                },
                "href": "https://api.spotify.com/v1/albums/1ApjqWf9VPtgc5RgWcLk68",
                "id": "1ApjqWf9VPtgc5RgWcLk68",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b2732c8255cfcc8dde98740db7c3",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e022c8255cfcc8dde98740db7c3",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d000048512c8255cfcc8dde98740db7c3",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "No Place Like Home",
                "release_date": "2025-06-20",
                "release_date_precision": "day",
                "total_tracks": 13,
                "type": "album",
                "uri": "spotify:album:1ApjqWf9VPtgc5RgWcLk68",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye"
                    },
                    "href": "https://api.spotify.com/v1/artists/3T55D3LMiygE9eSKFpiAye",
                    "id": "3T55D3LMiygE9eSKFpiAye",
                    "name": "Badflower",
                    "type": "artist",
                    "uri": "spotify:artist:3T55D3LMiygE9eSKFpiAye",
                }
            ],
            "disc_number": 1,
            "duration_ms": 229920,
            "explicit": True,
            "external_ids": {"isrc": "QZRD92506600"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/1eXMGoTPkICi00jcVc8LQy"
            },
            "href": "https://api.spotify.com/v1/tracks/1eXMGoTPkICi00jcVc8LQy",
            "id": "1eXMGoTPkICi00jcVc8LQy",
            "is_local": False,
            "is_playable": True,
            "name": "Story Of Our Lives",
            "popularity": 40,
            "preview_url": None,
            "track_number": 4,
            "type": "track",
            "uri": "spotify:track:1eXMGoTPkICi00jcVc8LQy",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                        },
                        "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                        "id": "2n2RSaZqBuUUukhbLlpnE6",
                        "name": "Sleep Token",
                        "type": "artist",
                        "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                    }
                ],
                "available_markets": [],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/1lS7FeRcSUuIGqyg99UGpj"
                },
                "href": "https://api.spotify.com/v1/albums/1lS7FeRcSUuIGqyg99UGpj",
                "id": "1lS7FeRcSUuIGqyg99UGpj",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "Even In Arcadia",
                "release_date": "2025-05-09",
                "release_date_precision": "day",
                "total_tracks": 10,
                "type": "album",
                "uri": "spotify:album:1lS7FeRcSUuIGqyg99UGpj",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
                    },
                    "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
                    "id": "2n2RSaZqBuUUukhbLlpnE6",
                    "name": "Sleep Token",
                    "type": "artist",
                    "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
                }
            ],
            "available_markets": ["AR", "AU", "AT", "BE", "BO", "BR"],
            "disc_number": 1,
            "duration_ms": 268369,
            "explicit": False,
            "external_ids": {"isrc": "USRC12500018"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/4IixOTCzviJgIigKleiVbo"
            },
            "href": "https://api.spotify.com/v1/tracks/4IixOTCzviJgIigKleiVbo",
            "id": "4IixOTCzviJgIigKleiVbo",
            "is_local": False,
            "is_playable": True,
            "name": "Even In Arcadia",
            "popularity": 72,
            "preview_url": None,
            "track_number": 6,
            "type": "track",
            "uri": "spotify:track:4IixOTCzviJgIigKleiVbo",
        },
        {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                        },
                        "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                        "id": "6NnBBumbcMYsaPTHFhPtXD",
                        "name": "VOILÀ",
                        "type": "artist",
                        "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                    }
                ],
                "available_markets": ["BB", "BZ", "BT", "BW", "BF", "CV", "CW"],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/5k77pSc53QUp8WNIXwseu7"
                },
                "href": "https://api.spotify.com/v1/albums/5k77pSc53QUp8WNIXwseu7",
                "id": "5k77pSc53QUp8WNIXwseu7",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
                        "width": 640,
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
                        "width": 300,
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
                        "width": 64,
                    },
                ],
                "is_playable": True,
                "name": "The Last Laugh (Part I)",
                "release_date": "2025-06-20",
                "release_date_precision": "day",
                "total_tracks": 14,
                "type": "album",
                "uri": "spotify:album:5k77pSc53QUp8WNIXwseu7",
            },
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
                    },
                    "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
                    "id": "6NnBBumbcMYsaPTHFhPtXD",
                    "name": "VOILÀ",
                    "type": "artist",
                    "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
                }
            ],
            "available_markets": ["AR", "AU"],
            "disc_number": 1,
            "duration_ms": 219000,
            "explicit": False,
            "external_ids": {"isrc": "QM24S2501960"},
            "external_urls": {
                "spotify": "https://open.spotify.com/track/60mJhDxOT1LtHFtoBAcZxa"
            },
            "href": "https://api.spotify.com/v1/tracks/60mJhDxOT1LtHFtoBAcZxa",
            "id": "60mJhDxOT1LtHFtoBAcZxa",
            "is_local": False,
            "is_playable": True,
            "name": "The Last Laugh?",
            "popularity": 45,
            "preview_url": None,
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:60mJhDxOT1LtHFtoBAcZxa",
        },
    ]
}

ARTISTS_DATA = {
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
            },
            "followers": {"href": None, "total": 2710561},
            "genres": ["progressive metal", "metalcore"],
            "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "2n2RSaZqBuUUukhbLlpnE6",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5ebd00c2ff422829437e6b5f1e0",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab67616100005174d00c2ff422829437e6b5f1e0",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f178d00c2ff422829437e6b5f1e0",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "Sleep Token",
            "popularity": 82,
            "type": "artist",
            "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6Ad91Jof8Niiw0lGLLi3NW"
            },
            "followers": {"href": None, "total": 3100156},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/6Ad91Jof8Niiw0lGLLi3NW?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "6Ad91Jof8Niiw0lGLLi3NW",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5eb7c9287712c4355e54c94e0d0",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab676161000051747c9287712c4355e54c94e0d0",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f1787c9287712c4355e54c94e0d0",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "YUNGBLUD",
            "popularity": 78,
            "type": "artist",
            "uri": "spotify:artist:6Ad91Jof8Niiw0lGLLi3NW",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/4IWBUUAFIplrNtaOHcJPRM"
            },
            "followers": {"href": None, "total": 20722129},
            "genres": ["soft pop"],
            "href": "https://api.spotify.com/v1/artists/4IWBUUAFIplrNtaOHcJPRM?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "4IWBUUAFIplrNtaOHcJPRM",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5eb5a55e66595e80fb12dc5f5fa",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab676161000051745a55e66595e80fb12dc5f5fa",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f1785a55e66595e80fb12dc5f5fa",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "James Arthur",
            "popularity": 83,
            "type": "artist",
            "uri": "spotify:artist:4IWBUUAFIplrNtaOHcJPRM",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
            },
            "followers": {"href": None, "total": 331103},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "6NnBBumbcMYsaPTHFhPtXD",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5eb2b8c0a420a952a14a2e23c9c",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab676161000051742b8c0a420a952a14a2e23c9c",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f1782b8c0a420a952a14a2e23c9c",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "VOILÀ",
            "popularity": 70,
            "type": "artist",
            "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz"
            },
            "followers": {"href": None, "total": 31331065},
            "genres": ["nu metal", "rap metal", "rock", "alternative metal"],
            "href": "https://api.spotify.com/v1/artists/6XyY86QOPPrYVGvF9ch6wz?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "6XyY86QOPPrYVGvF9ch6wz",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5eb527d95dabbe8b8b527e8136f",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab67616100005174527d95dabbe8b8b527e8136f",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f178527d95dabbe8b8b527e8136f",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "Linkin Park",
            "popularity": 92,
            "type": "artist",
            "uri": "spotify:artist:6XyY86QOPPrYVGvF9ch6wz",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye"
            },
            "followers": {"href": None, "total": 354863},
            "genres": ["post-grunge"],
            "href": "https://api.spotify.com/v1/artists/3T55D3LMiygE9eSKFpiAye?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "3T55D3LMiygE9eSKFpiAye",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5ebd1634326a43dfa2aea839053",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab67616100005174d1634326a43dfa2aea839053",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f178d1634326a43dfa2aea839053",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "Badflower",
            "popularity": 56,
            "type": "artist",
            "uri": "spotify:artist:3T55D3LMiygE9eSKFpiAye",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/4OTFxPi5CtWyj1NThDe6z5"
            },
            "followers": {"href": None, "total": 314623},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/4OTFxPi5CtWyj1NThDe6z5?locale=en-GB%2Cen-US%3Bq%3D0.9%2Cen%3Bq%3D0.8",
            "id": "4OTFxPi5CtWyj1NThDe6z5",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab6761610000e5ebe650e4a00f56efec44be31a5",
                    "height": 640,
                    "width": 640,
                },
                {
                    "url": "https://i.scdn.co/image/ab67616100005174e650e4a00f56efec44be31a5",
                    "height": 320,
                    "width": 320,
                },
                {
                    "url": "https://i.scdn.co/image/ab6761610000f178e650e4a00f56efec44be31a5",
                    "height": 160,
                    "width": 160,
                },
            ],
            "name": "Weathers",
            "popularity": 54,
            "type": "artist",
            "uri": "spotify:artist:4OTFxPi5CtWyj1NThDe6z5",
        },
    ]
}

EXPECTED_TRACKS = [
    Track(
        id="4Lojbtk7XNMdSKRHSFbdkm",
        name="Look To Windward",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
            ),
        ],
        spotify_url="https://open.spotify.com/track/4Lojbtk7XNMdSKRHSFbdkm",
        album_name="Even In Arcadia",
        release_date="2025-05-09",
        explicit=False,
        duration_ms=466463,
        popularity=73,
        artists=[TrackArtist(id="2n2RSaZqBuUUukhbLlpnE6", name="Sleep Token")],
    ),
    Track(
        id="42GKyvz5KBsHTBaLpo3cqJ",
        name="Zombie",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b2737808f0d7992027b6b10254dd",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e027808f0d7992027b6b10254dd",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d000048517808f0d7992027b6b10254dd",
            ),
        ],
        spotify_url="https://open.spotify.com/track/42GKyvz5KBsHTBaLpo3cqJ",
        album_name="Idols",
        release_date="2025-06-20",
        explicit=False,
        duration_ms=246946,
        popularity=73,
        artists=[TrackArtist(id="6Ad91Jof8Niiw0lGLLi3NW", name="YUNGBLUD")],
    ),
    Track(
        id="0871iIk4stdN902Gj33P2d",
        name="Embers",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b273765c38475815f11c5487299e",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e02765c38475815f11c5487299e",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d00004851765c38475815f11c5487299e",
            ),
        ],
        spotify_url="https://open.spotify.com/track/0871iIk4stdN902Gj33P2d",
        album_name="PISCES",
        release_date="2025-04-25",
        explicit=False,
        duration_ms=255084,
        popularity=46,
        artists=[TrackArtist(id="4IWBUUAFIplrNtaOHcJPRM", name="James Arthur")],
    ),
    Track(
        id="71w4bqfvnINCpLnypPM9Dj",
        name="Good Grief",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
            ),
        ],
        spotify_url="https://open.spotify.com/track/71w4bqfvnINCpLnypPM9Dj",
        album_name="The Last Laugh (Part I)",
        release_date="2025-06-20",
        explicit=False,
        duration_ms=245000,
        popularity=48,
        artists=[TrackArtist(id="6NnBBumbcMYsaPTHFhPtXD", name="VOILÀ")],
    ),
    Track(
        id="0Uvf2v96tJ5CuyK0LtyAgd",
        name="Past Self",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
            ),
        ],
        spotify_url="https://open.spotify.com/track/0Uvf2v96tJ5CuyK0LtyAgd",
        album_name="Even In Arcadia",
        release_date="2025-05-09",
        explicit=True,
        duration_ms=214648,
        popularity=73,
        artists=[TrackArtist(id="2n2RSaZqBuUUukhbLlpnE6", name="Sleep Token")],
    ),
    Track(
        id="3bUp4O9m98QM9kvVpqtQKP",
        name="Unhappy Hour (with Weathers)",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
            ),
        ],
        spotify_url="https://open.spotify.com/track/3bUp4O9m98QM9kvVpqtQKP",
        album_name="The Last Laugh (Part I)",
        release_date="2025-06-20",
        explicit=True,
        duration_ms=194000,
        popularity=45,
        artists=[
            TrackArtist(id="6NnBBumbcMYsaPTHFhPtXD", name="VOILÀ"),
            TrackArtist(id="4OTFxPi5CtWyj1NThDe6z5", name="Weathers"),
        ],
    ),
    Track(
        id="2SwdMXPvGdciXamSjfoNH9",
        name="Up From the Bottom",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b273a493a67f01bcfe65b23bc910",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e02a493a67f01bcfe65b23bc910",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d00004851a493a67f01bcfe65b23bc910",
            ),
        ],
        spotify_url="https://open.spotify.com/track/2SwdMXPvGdciXamSjfoNH9",
        album_name="From Zero (Deluxe Edition)",
        release_date="2025-05-16",
        explicit=False,
        duration_ms=183223,
        popularity=75,
        artists=[TrackArtist(id="6XyY86QOPPrYVGvF9ch6wz", name="Linkin Park")],
    ),
    Track(
        id="1eXMGoTPkICi00jcVc8LQy",
        name="Story Of Our Lives",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b2732c8255cfcc8dde98740db7c3",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e022c8255cfcc8dde98740db7c3",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d000048512c8255cfcc8dde98740db7c3",
            ),
        ],
        spotify_url="https://open.spotify.com/track/1eXMGoTPkICi00jcVc8LQy",
        album_name="No Place Like Home",
        release_date="2025-06-20",
        explicit=True,
        duration_ms=229920,
        popularity=40,
        artists=[TrackArtist(id="3T55D3LMiygE9eSKFpiAye", name="Badflower")],
    ),
    Track(
        id="4IixOTCzviJgIigKleiVbo",
        name="Even In Arcadia",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b2730e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e020e48dcb579fd8e59d0a3c218",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d000048510e48dcb579fd8e59d0a3c218",
            ),
        ],
        spotify_url="https://open.spotify.com/track/4IixOTCzviJgIigKleiVbo",
        album_name="Even In Arcadia",
        release_date="2025-05-09",
        explicit=False,
        duration_ms=268369,
        popularity=72,
        artists=[TrackArtist(id="2n2RSaZqBuUUukhbLlpnE6", name="Sleep Token")],
    ),
    Track(
        id="60mJhDxOT1LtHFtoBAcZxa",
        name="The Last Laugh?",
        images=[
            Image(
                height=640,
                width=640,
                url="https://i.scdn.co/image/ab67616d0000b273f017130e0c378fc869fc469e",
            ),
            Image(
                height=300,
                width=300,
                url="https://i.scdn.co/image/ab67616d00001e02f017130e0c378fc869fc469e",
            ),
            Image(
                height=64,
                width=64,
                url="https://i.scdn.co/image/ab67616d00004851f017130e0c378fc869fc469e",
            ),
        ],
        spotify_url="https://open.spotify.com/track/60mJhDxOT1LtHFtoBAcZxa",
        album_name="The Last Laugh (Part I)",
        release_date="2025-06-20",
        explicit=False,
        duration_ms=219000,
        popularity=45,
        artists=[TrackArtist(id="6NnBBumbcMYsaPTHFhPtXD", name="VOILÀ")],
    ),
]


@pytest_asyncio.fixture
async def spotify_service(httpx_mock) -> AsyncGenerator[SpotifyService, None]:
    top_tracks_url_pattern = re.compile("http://localhost:8000/me/top/tracks.*")
    httpx_mock.add_response(
        method="GET",
        url=top_tracks_url_pattern,
        json=TOP_TRACKS_DATA,
        status_code=200,
    )
    artists_url_pattern = re.compile("http://localhost:8000/artists.*")
    httpx_mock.add_response(
        method="GET",
        url=artists_url_pattern,
        json=ARTISTS_DATA,
        status_code=200,
    )

    async with httpx.AsyncClient() as client:
        yield SpotifyService(client=client, base_url="http://localhost:8000")


@pytest.fixture
def top_tracks_pipeline(
    db_session: Session, spotify_service: SpotifyService
) -> TopTracksPipeline:
    artists_repository = ArtistsRepository(db_session)
    tracks_repository = TracksRepository(db_session)
    top_tracks_repository = TopTracksRepository(db_session)

    return TopTracksPipeline(
        spotify_service=spotify_service,
        artists_repository=artists_repository,
        tracks_repository=tracks_repository,
        top_tracks_repository=top_tracks_repository,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_returns_expected_tracks(
    top_tracks_pipeline: TopTracksPipeline, existing_profile: ProfileDB
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    tracks = await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    assert tracks == EXPECTED_TRACKS


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_adds_tracks_to_db(
    db_session: Session,
    top_tracks_pipeline: TopTracksPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    db_tracks = db_session.query(TrackDB).all()
    db_track_ids = {track.id for track in db_tracks}
    expected_track_ids = {track.id for track in EXPECTED_TRACKS}
    assert db_track_ids == expected_track_ids


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_adds_top_tracks_to_db(
    db_session: Session,
    top_tracks_pipeline: TopTracksPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    top_tracks = [
        TopTrack(
            user_id=track.user_id,
            track_id=track.track_id,
            collection_date=track.collection_date,
            time_range=track.time_range,
            position=track.position,
            position_change=track.position_change,
        )
        for track in db_session.query(TopTrackDB).all()
    ]
    expected_top_tracks = [
        TopTrack(
            user_id=existing_profile.id,
            track_id=track.id,
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            position_change=None,
        )
        for index, track in enumerate(EXPECTED_TRACKS)
    ]
    assert top_tracks == expected_top_tracks


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_adds_top_tracks_to_db_with_expected_position_changes(
    db_session: Session,
    top_tracks_pipeline: TopTracksPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()
    up_track_ids = set(
        ["4Lojbtk7XNMdSKRHSFbdkm", "0871iIk4stdN902Gj33P2d"]
    )  # 4->1, 6->3
    down_track_ids = set(
        ["42GKyvz5KBsHTBaLpo3cqJ", "0Uvf2v96tJ5CuyK0LtyAgd"]
    )  # 1->2, 2->5
    new_track_ids = set(["2SwdMXPvGdciXamSjfoNH9"])  # New track at 7
    tracks_to_add = [*EXPECTED_TRACKS]
    tracks_to_add.pop(6)  # Remove track 7 to simulate it being a new track
    db_session.add_all(
        [
            TrackDB(
                id=track.id,
                name=track.name,
                images=[image.model_dump() for image in track.images],
                spotify_url=track.spotify_url,
                album_name=track.album_name,
                release_date=track.release_date,
                explicit=track.explicit,
                duration_ms=track.duration_ms,
                popularity=track.popularity,
            )
            for track in tracks_to_add
        ]
    )
    db_session.commit()
    positions = [4, 1, 6, 4, 2, 6, 8, 9, 10]  # Previous positions of the tracks
    # Add previous top tracks with different positions
    top_tracks_to_add = [
        TopTrackDB(
            user_id=existing_profile.id,
            track_id=track.id,
            collection_date=collection_date - datetime.timedelta(days=7),
            time_range=time_range,
            position=positions[index],
            position_change=None,
        )
        for index, track in enumerate(tracks_to_add)
    ]
    db_session.add_all(top_tracks_to_add)
    db_session.commit()

    await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    db_session.commit()
    top_tracks = [
        TopTrack(
            user_id=track.user_id,
            track_id=track.track_id,
            collection_date=track.collection_date,
            time_range=track.time_range,
            position=track.position,
            position_change=track.position_change,
        )
        for track in db_session.query(TopTrackDB)
        .where(TopTrackDB.collection_date == collection_date)
        .all()
    ]
    expected_top_tracks = [
        TopTrack(
            user_id=existing_profile.id,
            track_id=track.id,
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            position_change=None,
        )
        for index, track in enumerate(EXPECTED_TRACKS)
    ]
    for top_track in expected_top_tracks:
        if top_track.track_id in up_track_ids:
            top_track.position_change = PositionChange.UP
        elif top_track.track_id in down_track_ids:
            top_track.position_change = PositionChange.DOWN
        elif top_track.track_id in new_track_ids:
            top_track.position_change = PositionChange.NEW
    assert top_tracks == expected_top_tracks


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_updates_track_if_already_exists(
    db_session: Session,
    top_tracks_pipeline: TopTracksPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()
    existing_track = EXPECTED_TRACKS[0]
    db_session.add(
        TrackDB(
            id=existing_track.id,
            name=existing_track.name + " Old",
            images=[image.model_dump() for image in existing_track.images],
            spotify_url=existing_track.spotify_url,
            album_name=existing_track.album_name,
            release_date=existing_track.release_date,
            explicit=existing_track.explicit,
            duration_ms=existing_track.duration_ms,
            popularity=existing_track.popularity,
        )
    )
    db_session.commit()

    await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    db_track = db_session.get(TrackDB, existing_track.id)
    assert db_track.id == existing_track.id
    assert db_track.name == existing_track.name
    assert db_track.images == [image.model_dump() for image in existing_track.images]
    assert db_track.spotify_url == existing_track.spotify_url
    assert db_track.album_name == existing_track.album_name
    assert db_track.release_date == existing_track.release_date
    assert db_track.explicit == existing_track.explicit
    assert db_track.duration_ms == existing_track.duration_ms
    assert db_track.popularity == existing_track.popularity


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_tracks_pipeline_run_raises_exception_if_top_track_exists(
    db_session: Session,
    top_tracks_pipeline: TopTracksPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()
    existing_track = EXPECTED_TRACKS[0]
    db_session.add(
        TrackDB(
            id=existing_track.id,
            name=existing_track.name,
            images=[image.model_dump() for image in existing_track.images],
            spotify_url=existing_track.spotify_url,
            album_name=existing_track.album_name,
            release_date=existing_track.release_date,
            explicit=existing_track.explicit,
            duration_ms=existing_track.duration_ms,
            popularity=existing_track.popularity,
        )
    )
    db_session.commit()
    db_session.add(
        TopTrackDB(
            user_id=existing_profile.id,
            track_id=existing_track.id,
            collection_date=collection_date,
            time_range=time_range,
            position=1,
            position_change=None,
        )
    )
    db_session.commit()

    with pytest.raises(TopTracksPipelineException):
        await top_tracks_pipeline.run(
            access_token=access_token,
            user_id=user_id,
            time_range=time_range,
            collection_date=collection_date,
        )
