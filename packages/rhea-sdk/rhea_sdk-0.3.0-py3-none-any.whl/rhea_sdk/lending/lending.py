import json

from py_near.models import TransactionResult

from rhea_sdk.constances import TESTNET_CHAIN_ID, LENDING_TESTNET_CONTRACT, LENDING_MAINNET_CONTRACT
from rhea_sdk.exceptions import TransactionError


class Lending:
    """This class provides methods to interact with lending protocol."""

    def __init__(self, rhea: "Rhea"):
        self._rhea = rhea

    @property
    def lending_contract_id(self) -> str:
        """
        Get the lending contract ID based on the current chain ID.
            Returns:
                str: The lending contract ID for the current network (testnet or mainnet).
        """
        if self._rhea.chain_id == TESTNET_CHAIN_ID:
            return LENDING_TESTNET_CONTRACT
        return LENDING_MAINNET_CONTRACT

    async def get_account(self, account_id: str = None) -> dict | None:
        """
        Get an account lending info.
            Args:
                account_id: Lending info for a provided Account ID (default: current account).
            Returns:
                Dictionary with an account lending info.
        """
        account_id = account_id or self._rhea.account_id
        json_args = {"account_id": account_id}
        result = await self._rhea._account.view_function(self.lending_contract_id, "get_account", json_args)
        return result.result

    async def get_asset(self, token_id: str) -> dict | None:
        """
        Get a token lending info.
            Args:
                token_id: Lending info for a provided Token ID.
            Returns:
                Dictionary with a token lending info.
        """
        json_args = {"token_id": token_id}
        result = await self._rhea._account.view_function(self.lending_contract_id, "get_asset", json_args)
        return result.result

    async def supply(self, token_id: str, amount: str) -> TransactionResult:
        """
        Supply a token as a collateral
            Args:
                token_id: Token ID to supply.
                amount: Amount to supply.
            Returns:
                TransactionResult
        """
        amount = await self._rhea.convert_to_atomic_units(amount, token_id)
        msg = json.dumps(
            {"Execute": {"actions": [{"IncreaseCollateral": {"token_id": token_id, "max_amount": amount}}]}}
        )
        json_args = {
            "receiver_id": self.lending_contract_id,
            "amount": amount,
            "msg": msg,
        }
        result = await self._rhea._account.function_call(token_id, "ft_transfer_call", json_args, amount=1)
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        return result

    async def borrow(self, token_id: str, amount: str) -> TransactionResult:
        """
        Borrow a token
            Args:
                token_id: Token ID to borrow.
                amount: Amount to borrow.
            Returns:
                TransactionResult.
        """
        amount = await self._rhea.convert_to_atomic_units(amount, token_id)
        json_args = {
            "actions": [
                {
                    "Borrow": {
                        "token_id": token_id,
                        "amount": amount,
                    },
                },
                {
                    "Withdraw": {
                        "token_id": token_id,
                        "max_amount": amount,
                    },
                },
            ],
        }
        result = await self._rhea._account.function_call(self.lending_contract_id, "execute_with_pyth", json_args, amount=1)
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        return result

    async def repay(self, token_id: str, amount: str) -> TransactionResult:
        """
        Repay with a token
            Args:
                token_id: Token ID to repay.
                amount: Amount to repay.
            Returns:
                TransactionResult
        """
        amount = await self._rhea.convert_to_atomic_units(amount, token_id)
        msg = json.dumps({"Execute": {"actions": [{"Repay": {"token_id": token_id}}]}})
        json_args = {
            "receiver_id": self.lending_contract_id,
            "amount": amount,
            "msg": msg,
        }
        result = await self._rhea._account.function_call(token_id, "ft_transfer_call", json_args, amount=1)
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        return result
