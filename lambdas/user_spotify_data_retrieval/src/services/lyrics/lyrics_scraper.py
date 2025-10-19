import asyncio
import random
import re
import string
import unicodedata
import httpx
import bs4
from loguru import logger


class LyricsScraperException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class LyricsScraper:
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        headers: dict[str, str],
        semaphore: asyncio.Semaphore,
    ):
        self.client = client
        self.base_url = base_url
        self.headers = headers
        self.semaphore = semaphore

    @staticmethod
    def _format_string_for_url(s: str) -> str:
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

        def handle_parentheses(match):
            """Removes content if it contains 'feat' or 'with'"""

            content = match.group(1).lower()
            return "" if "feat" in content or "with" in content else content

        s = re.sub(r"\(([^)]*)\)", handle_parentheses, s)

        # Remove ' - feat' and 'feat'
        s = re.sub(r"\s*-\s*feat.*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*feat.*", "", s, flags=re.IGNORECASE)

        # Replace special characters and punctuation
        s = s.replace("$", "-").replace("&", "and")
        s = s.translate(str.maketrans("", "", string.punctuation.replace("-", "")))

        # Convert to lowercase, replace hyphens with '-' and remove leading/trailing '-'
        s = s.lower().replace(" ", "-").strip("-")

        s = re.sub(r"-+", "-", s)

        return s

    def _get_url(self, artist: str, title: str) -> str:
        artist = self._format_string_for_url(artist).capitalize()
        title = self._format_string_for_url(title)

        return f"{self.base_url}/{artist}-{title}-lyrics"

    async def _make_limited_request(self, url: str, delay: float) -> httpx.Response:
        async with self.semaphore:
            await asyncio.sleep(delay)
            response = await self.client.get(
                url=url, headers=self.headers, follow_redirects=True
            )

        return response

    async def _get_html(self, url: str) -> str:
        try:
            response = await self._make_limited_request(
                url=url, delay=random.uniform(0.25, 1)
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            raise LyricsScraperException(f"Failed to get page html - {e}")
        except httpx.RequestError as e:
            raise LyricsScraperException(f"Request failed - {e}")

    def _extract_lyrics_from_html(self, html: str) -> str | None:
        soup = bs4.BeautifulSoup(html, "html.parser")
        lyrics_containers = soup.select("div[data-lyrics-container='true']")

        if not lyrics_containers:
            logger.info("Lyrics containers not found")
            return

        cleaned_lyrics = []

        for container in lyrics_containers:
            section = ""

            for element in container.contents:
                if isinstance(element, bs4.Tag):
                    if element.name in ["br", "i", "b"]:
                        section += str(element)
                    elif element.name == "a":
                        section += "".join([str(el) for el in element.find("span")])
                else:
                    section += str(element)

            cleaned_lyrics.append(section)

        return "<br/>".join(cleaned_lyrics)

    async def get_lyrics(self, artist_name: str, track_title: str) -> str:
        logger.info(f"Scraping lyrics for {artist_name} - {track_title}")
        url = self._get_url(artist_name, track_title)

        logger.info(f"Making request to {url}")
        html = await self._get_html(url)

        lyrics = self._extract_lyrics_from_html(html)

        if not lyrics:
            logger.error(f"Lyrics not found for {artist_name} - {track_title}")
            raise LyricsScraperException(
                f"Lyrics not found for {artist_name} - {track_title}"
            )

        logger.info(f"Successfully scraped lyrics for {artist_name} - {track_title}")

        return lyrics
