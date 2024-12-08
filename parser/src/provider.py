import asyncio
from parser.src.utils import retry

import aiohttp


class HTTPProvider:
    def __init__(self, **session_conf):
        self._session = None
        self._session_conf = session_conf

    async def _setup_session(self) -> aiohttp.ClientSession:
        connector = aiohttp.TCPConnector(ssl=False)
        session = aiohttp.ClientSession(
            connector=connector,
            raise_for_status=False,
            timeout=aiohttp.ClientTimeout(total=60),
            **self._session_conf
        )
        return session

    @retry(
        Exception,
        aiohttp.ClientResponseError,
        aiohttp.ClientConnectionError,
        asyncio.TimeoutError,
        aiohttp.client_exceptions.ServerDisconnectedError,
        asyncio.exceptions.CancelledError,
        asyncio.exceptions.TimeoutError,
        TimeoutError,
        attempts=7,
        delay=6,
        backoff=3,
    )
    async def _request(self, method: str, url: str, **conf) -> aiohttp.ClientResponse:
        if self._session is None:
            self._session = await self._setup_session()

        try:
            async with self._session.request(method=method, url=url, **conf) as res:
                if res.status // 100 == 5:
                    res.raise_for_status()
                elif res.status == 302:
                    res.raise_for_status()
                return await res.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
            print(e)
            raise Exception(str(e))

    async def get(self, url, **conf):
        return await self._request("GET", url, **conf)

    async def post(self, url, **conf):
        return await self._request("POST", url, **conf)

    async def close(self):
        if self._session is not None:
            await self._session.close()


class GoszakupProvider:
    graphql_url = "https://ows.goszakup.gov.kz/v3/graphql"

    def __init__(self, token, **provider_conf):
        self.provider = HTTPProvider(**provider_conf)
        self._headers = {
            "Authorization": f"Bearer {token}",
        }

    async def execute(
        self,
        url: str,
        query: str,
        variables: dict = None,
        **conf,
    ):
        if variables is None:
            variables = {}

        return await self.provider.post(
            url=url,
            json={
                "query": query,
                "variables": variables
            }, **conf
        )

    async def parse_graphql(self, query: str, sort_key: str, after: int = 0):
        running = True

        while running:
            print("current `after` {}".format(after))

            response_content = await self.execute(
                url=self.graphql_url,
                query=query,
                headers=self._headers,
                variables={"after": after}
            )
            batch = response_content["data"]["items"]
            meta = response_content["extensions"]["pageInfo"]

            after = min(entry[sort_key] for entry in batch)
            running = meta["hasNextPage"]

            yield batch
