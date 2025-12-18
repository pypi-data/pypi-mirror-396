import aiohttp
from typing import Any

TMDB_READ_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNTkxMmVmOWFhM2IxNzg2Zjk3ZTE1NWY1YmQ3ZjY1MSIsInN1YiI6IjY1M2NjNWUyZTg5NGE2MDBmZjE2N2FmYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xrIXsMFJpI1o1j5g2QpQcFP1X3AfRjFA5FlBFO5Naw8"


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None
        self.headers = {
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()

    async def _request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        session = await self.get_session()
        async with session.get(
            f"{self.BASE_URL}/{endpoint}", params=params
        ) as response:
            if response.status != 200:
                raise Exception(f"TMDB Error: {response.status}")
            return await response.json()

    async def search(self, query: str, page: int = 1) -> dict[str, Any]:
        return await self._request(
            "search/multi",
            params={"query": query, "page": str(page), "include_adult": "false"},
        )

    async def get_external_ids(self, media_type: str, tmdb_id: int) -> dict[str, Any]:
        return await self._request(f"{media_type}/{tmdb_id}/external_ids")


tmdb_client = TMDBClient()
