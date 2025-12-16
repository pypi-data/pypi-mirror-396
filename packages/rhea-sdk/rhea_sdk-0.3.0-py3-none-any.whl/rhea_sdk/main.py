from decimal import Decimal
from typing import Iterable

from py_near.account import Account, TransactionResult

from rhea_sdk.constances import TESTNET_CHAIN_ID, WRAP_NEAR_TESTNET_CONTRACT, WRAP_NEAR_MAINNET_CONTRACT, NEAR
from rhea_sdk.dcl import DCL
from rhea_sdk.exceptions import AccountInitializationError, TransactionError, AccountHasNoTokensError, \
    AccountHasNoStateError, EmptyStorageBalance
from rhea_sdk.lending.lending import Lending
from rhea_sdk.utils.fastnear import FastNearClient


class Rhea:
    """
    A high-level interface for interacting with the NEAR blockchain and Rhea Finance.
        Args:
            account: An initialized py_near Account object
            storage_auto_deposit: Whether to automatically handle storage deposits (default: True)
    """

    def __init__(
            self,
            account: Account,
            storage_auto_deposit: bool = True,
    ) -> None:
        if not self._is_account_initialized(account):
            raise AccountInitializationError(
                "You must call 'await account.startup()' before providing it to Rhea init method"
            )
        self._account = account
        self.storage_auto_deposit = storage_auto_deposit

    @property
    def account_id(self) -> str:
        """Returns the account ID associated with this Rhea instance."""
        return self._account.account_id

    @property
    def chain_id(self) -> str:
        """Returns the NEAR chain ID (testnet/mainnet) for this account."""
        return self._account.chain_id

    @property
    def wnear_contract(self) -> str:
        """Returns the appropriate wNEAR contract address based on current chain."""
        if self.chain_id == TESTNET_CHAIN_ID:
            return WRAP_NEAR_TESTNET_CONTRACT
        return WRAP_NEAR_MAINNET_CONTRACT

    @property
    def dcl(self) -> DCL:
        """Returns a DCL interface instance."""
        return DCL(self)

    @property
    def lending(self) -> Lending:
        """Returns a Lending interface instance."""
        return Lending(self)

    @property
    def _fastnear(self) -> FastNearClient:
        """Internal FastNearClient instance for quick data access."""
        return FastNearClient(self.chain_id)

    @staticmethod
    def _is_account_initialized(account: Account) -> bool:
        """Check if the provided py_near Account has been initialized."""
        return bool(account._lock)

    async def get_token_metadata(self, token_contract_id: str) -> dict:
        """
        Retrieve metadata for a fungible token contract.
            Args:
                token_contract_id: The contract ID of the token
            Returns:
                Dictionary containing token metadata (name, symbol, decimals, etc.)
        """
        result = await self._account.view_function(token_contract_id, "ft_metadata", {})
        return result.result

    async def get_token_balance(self, token_contract_id: str, account_id: str = None) -> str:
        """
        Get the balance of a specific token for an account.
            Args:
                token_contract_id: The contract ID of the token
                account_id: Account ID to check balance for (default: current account)
            Returns:
                Token balance as a string
        """
        account_id = account_id or self.account_id
        data = await self._fastnear.get_full_account_data(account_id)
        if not data.get("tokens"):
            raise AccountHasNoTokensError(f"No tokens available for account {account_id}")
        for token_ in data["tokens"]:
            if token_["contract_id"] == token_contract_id:
                return await self.convert_to_human_readable(token_["balance"], token_contract_id)
        return "0"

    async def get_near_balance(self, account_id: str = None) -> str:
        """
        Get the NEAR balance for an account.
            Args:
                account_id: Account ID to check balance for (default: current account)
            Returns:
                NEAR balance as a string
        """
        account_id = account_id or self.account_id
        data = await self._fastnear.get_full_account_data(account_id)
        if not data.get("state"):
            raise AccountHasNoStateError(f"No state available for account {account_id}")
        return await self.convert_to_human_readable(data["state"]["balance"])

    async def get_storage_balance(self, contract_id: str, account_id: str = None) -> str:
        """
        Get total storage balance for an account on a specific contract.
            Args:
                contract_id: The contract ID to check storage for
                account_id: Account ID to check (default: current account)
            Returns:
                Total storage balance as a string
        """
        account_id = account_id or self.account_id
        result = await self._account.view_function(
            contract_id,
            "storage_balance_of",
            {"account_id": account_id},
        )
        if result.result:
            return await self.convert_to_human_readable(result.result["total"])
        return "0"

    async def get_min_storage_balance(self, contract_id: str) -> str:
        """
        Get min storage balance required for interacting with the contract.
            Args:
                contract_id: The contract ID to get min storage balance required of
            Returns:
                Min storage balance as a string
        """
        result = await self._account.view_function(contract_id, "storage_balance_bounds", {})
        if result.result:
            return await self.convert_to_human_readable(result.result["min"])
        return "0"

    async def storage_deposit(
            self,
            contract_id: str,
            amount: str,
    ) -> TransactionResult:
        """
        Deposit storage for interacting with a contract.
            Args:
                contract_id: The contract ID to deposit storage for
                amount: Amount of NEAR to deposit
            Returns:
                Transaction result object
        """
        converted_amount = int(await self.convert_to_atomic_units(amount))
        result = await self._account.function_call(
            contract_id,
            "storage_deposit",
            {},
            amount=converted_amount,
        )
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        return result

    async def ensure_storage_balances(self, contracts_ids: Iterable[str]) -> None:
        """
        Check storage balances for given contracts and deposit if needed.
            Args:
                contracts_ids: Iterable of contract IDs to check.
            Raises:
                EmptyStorageBalance: If storage balance is required but not auto-deposited.
        """
        for contract_id in contracts_ids:
            if await self.get_storage_balance(contract_id) == "0":
                if self.storage_auto_deposit:
                    min_storage_balance = await self.get_min_storage_balance(contract_id)
                    await self.storage_deposit(contract_id, min_storage_balance)
                else:
                    raise EmptyStorageBalance(f"Storage balance deposit for {contract_id} required")

    async def wrap_near(self, amount: str) -> None:
        """
        Convert NEAR to wNEAR (wrapped NEAR).
            Args:
                amount: Amount of NEAR to wrap
            Returns:
                Transaction result
        """
        converted_amount = int(await self.convert_to_atomic_units(amount))
        result = await self._account.function_call(
            self.wnear_contract,
            "near_deposit",
            {},
            amount=converted_amount,
        )
        if result.status.get("Failure"):
            raise TransactionError(result.status)

    async def unwrap_near(self, amount: str) -> None:
        """
        Convert wNEAR back to NEAR.
            Args:
                amount: Amount of wNEAR to unwrap
            Returns:
                Transaction result
        """
        converted_amount = await self.convert_to_atomic_units(amount)
        result = await self._account.function_call(
            self.wnear_contract,
            "near_withdraw",
            {"amount": converted_amount},
            amount=1,
        )
        if result.status.get("Failure"):
            raise TransactionError(result.status)

    async def convert_to_atomic_units(self, amount: str, token_contract_id: str = None) -> str:
        """
        Convert a human-readable token amount to atomic units (base units).
            For native NEAR tokens, converts using the standard NEAR decimal places (24).
            For other tokens, uses the token's specific decimals from its metadata.
            Args:
                amount: Human-readable amount to convert (as string to preserve precision)
                token_contract_id: Contract ID of the token. If None, assumes native NEAR.
            Returns:
                Amount in atomic units as a string
        """
        if amount == "0":
            return "0"
        if not token_contract_id:
            return str(int(Decimal(amount) * Decimal(NEAR)))
        token_metadata = await self.get_token_metadata(token_contract_id)
        return str(int(Decimal(amount) * 10 ** int(token_metadata["decimals"])))

    async def convert_to_human_readable(self, amount: str, token_contract_id: str = None) -> str:
        """
        Convert token amount in atomic units (base units) to a human-readable amount.
            For native NEAR tokens, converts using the standard NEAR decimal places (24).
            For other tokens, uses the token's specific decimals from its metadata.
            Args:
                amount: amount in atomic units (base units) to convert
                token_contract_id: Contract ID of the token. If None, assumes native NEAR.
            Returns:
                Human-readable amount as a string
        """
        if amount == "0":
            return "0"
        if not token_contract_id:
            return str(Decimal(amount) / Decimal(NEAR))
        token_metadata = await self.get_token_metadata(token_contract_id)
        return str(Decimal(amount) / 10 ** int(token_metadata["decimals"]))
