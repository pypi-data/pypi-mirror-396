import httpx

from rhea_sdk.constances import MAINNET_CHAIN_ID, TESTNET_CHAIN_ID


class FastNearClient:

    def __init__(self, chain_id: str = MAINNET_CHAIN_ID):
        self.chain_id = chain_id
        self.base_url = self._get_base_url(self.chain_id)

    @staticmethod
    def _get_base_url(chain_id: str):
        if chain_id == TESTNET_CHAIN_ID:
            return "https://test.api.fastnear.com"
        return "https://api.fastnear.com"


    async def get_full_account_data(self, account_id: str) -> dict:
        url = self.base_url + f"/v1/account/{account_id}/full"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
