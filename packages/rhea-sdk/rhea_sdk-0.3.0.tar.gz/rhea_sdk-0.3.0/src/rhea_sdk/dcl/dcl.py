import json
import math
import re

from py_near.models import TransactionResult

from rhea_sdk.constances import DCL_POOL_FEE_LIST, CONSTANT_D, RHEA_DCL_TESTNET_CONTRACT, TESTNET_CHAIN_ID, \
    RHEA_DCL_MAINNET_CONTRACT
from rhea_sdk.exceptions import TransactionError, TransactionReceiptError, PoolFeeError


class DCL:
    """This class provides methods to interact with DCL pools."""

    def __init__(self, rhea: "Rhea"):
        self._rhea = rhea

    @property
    def dcl_contract_id(self) -> str:
        """
        Get the DCL contract ID based on the current chain ID.
            Returns:
                str: The DCL contract ID for the current network (testnet or mainnet).
        """
        if self._rhea.chain_id == TESTNET_CHAIN_ID:
            return RHEA_DCL_TESTNET_CONTRACT
        return RHEA_DCL_MAINNET_CONTRACT

    @staticmethod
    def get_pool_id(token_a: str, token_b: str, fee: int) -> str:
        """
        Generate a pool ID from two tokens and a fee.
            Args:
                token_a: First token contract ID.
                token_b: Second token contract ID.
                fee: Pool fee rate (must be in DCL_POOL_FEE_LIST).
            Returns:
                str: The generated pool ID in format "token_a|token_b|fee".
        """
        if fee not in DCL_POOL_FEE_LIST:
            raise PoolFeeError(f"fee must be one of {DCL_POOL_FEE_LIST}")
        return "|".join(sorted([token_a, token_b]) + [str(fee)])

    async def get_pool(self, pool_id: str) -> dict:
        """
        Get information about a specific pool.
            Args:
                pool_id: The ID of the pool to query.
            Returns:
                dict: Information about the requested pool.
        """
        result = await self._rhea._account.view_function(self.dcl_contract_id, "get_pool", {"pool_id": pool_id})
        return result.result

    async def get_pools(self) -> list[dict]:
        """
        Get a list of all available pools.
            Returns:
                list[dict]: A list of all pools and their information.
        """
        result = await self._rhea._account.view_function(self.dcl_contract_id, "list_pools", {})
        return result.result

    async def get_tokens_price(self, pool_id: str) -> dict[str, str]:
        """
        Get the current price of tokens in a pool.
            Args:
                pool_id: The ID of the pool to query.
            Returns:
                dict[str, str]: A dictionary with token prices where keys are token contract IDs
                               and values are price strings.
        """
        pool = await self.get_pool(pool_id)
        token_a, token_b, fee = pool_id.split("|")
        return {
            token_a: str(math.pow(CONSTANT_D, pool["current_point"] - 1) / (10 ** 18)),
            token_b: str(math.pow(CONSTANT_D, -pool["current_point"] - 1) * (10 ** 18)),
        }

    async def quote(
        self,
        token_in: str,
        token_out: str,
        pool_id: str,
        amount: str,
        tag: str = None,
    ) -> str:
        """
        Get a quote for a potential swap.
            Args:
                token_in: Input token contract ID.
                token_out: Output token contract ID.
                pool_id: The pool ID to get a quote from.
                amount: The amount of input token to swap.
                tag: Optional tag for the quote.
            Returns:
                Expected output amount as a string
        """
        amount = await self._rhea.convert_to_atomic_units(amount, token_in)
        json_args = {
            "pool_ids": [pool_id],
            "input_amount": amount,
            "input_token": token_in,
            "output_token": token_out,
            "tag": tag,
        }
        result = await self._rhea._account.view_function(self.dcl_contract_id, "quote", json_args)
        return await self._rhea.convert_to_human_readable(result.result["amount"], token_out)

    async def quote_by_output(
        self,
        token_in: str,
        token_out: str,
        pool_id: str,
        output_amount: str,
        tag: str = None,
    ) -> str:
        """
        Get a quote for a potential swap based on desired output amount.
            Args:
                token_in: Input token contract ID.
                token_out: Output token contract ID.
                pool_id: The pool ID to get a quote from.
                output_amount: The desired amount of output token.
                tag: Optional tag for the quote.
            Returns:
                Required input amount as a string
        """
        output_amount = await self._rhea.convert_to_atomic_units(output_amount, token_out)
        json_args = {
            "pool_ids": [pool_id],
            "output_amount": output_amount,
            "input_token": token_in,
            "output_token": token_out,
            "tag": tag,
        }
        result = await self._rhea._account.view_function(self.dcl_contract_id, "quote_by_output", json_args)
        return await self._rhea.convert_to_human_readable(result.result["amount"], token_in)

    async def swap(
        self,
        token_in: str,
        token_out: str,
        pool_id: str,
        amount: str,
        min_output_amount: str = "0",
    ) -> TransactionResult:
        """
        Execute a token swap in a DCL pool.
            Args:
                token_in: The input token contract ID.
                token_out: The output token contract ID.
                pool_id: The ID of the pool to swap in.
                amount: The amount of input token to swap.
                min_output_amount: The minimum amount of output token to receive (default "0").

            Returns:
                TransactionResult: The result of the swap transaction.
        """
        contracts = (token_in, token_out)
        await self._rhea.ensure_storage_balances(contracts)
        amount = await self._rhea.convert_to_atomic_units(amount, token_in)
        if min_output_amount != "0":
            min_output_amount = await self._rhea.convert_to_atomic_units(min_output_amount, token_out)
        msg = json.dumps({
            "Swap": {
                "pool_ids": [pool_id],
                "output_token": token_out,
                "min_output_amount": min_output_amount,
            }
        })

        json_args = {
            "receiver_id": self.dcl_contract_id,
            "amount": amount,
            "msg": msg,
        }
        result = await self._rhea._account.function_call(token_in, "ft_transfer_call", json_args, amount=1)
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        if result.receipt_outcome[1].status.get("Failure"):
            raise TransactionError(result.receipt_outcome[1].status)
        if token_out == self._rhea.wnear_contract:
            amount_out = self._get_amount_out(result)
            converted_amount_out = await self._rhea.convert_to_human_readable(amount_out)
            await self._rhea.wrap_near(converted_amount_out)
        return result

    async def swap_by_output(
        self,
        token_in: str,
        token_out: str,
        pool_id: str,
        output_amount: str,
        max_input_amount: str,
    ) -> TransactionResult:
        """
        Execute a token swap in a DCL pool to get a specific amount of output token.
            Args:
                token_in: The input token contract ID.
                token_out: The output token contract ID.
                pool_id: The ID of the pool to swap in.
                output_amount: The desired amount of output token.
                max_input_amount: The maximum amount of input token to swap.

            Returns:
                TransactionResult: The result of the swap transaction.
        """
        contracts = (token_in, token_out)
        await self._rhea.ensure_storage_balances(contracts)
        output_amount = await self._rhea.convert_to_atomic_units(output_amount, token_out)
        max_input_amount = await self._rhea.convert_to_atomic_units(max_input_amount, token_in)
        msg = json.dumps({
            "SwapByOutput": {
                "pool_ids": [pool_id],
                "output_token": token_out,
                "output_amount": output_amount,
            }
        })

        json_args = {
            "receiver_id": self.dcl_contract_id,
            "amount": max_input_amount,
            "msg": msg,
        }
        result = await self._rhea._account.function_call(token_in, "ft_transfer_call", json_args, amount=1)
        if result.status.get("Failure"):
            raise TransactionError(result.status)
        if token_out == self._rhea.wnear_contract:
            amount_out = self._get_amount_out(result)
            converted_amount_out = await self._rhea.convert_to_human_readable(amount_out)
            await self._rhea.wrap_near(converted_amount_out)
        return result


    @staticmethod
    def _get_amount_out(transaction_result: TransactionResult):
        match = re.search(r'"amount_out":"(\d+)"', transaction_result.receipt_outcome[1].logs[0])
        if match:
            return match.group(1)
        raise TransactionReceiptError("Error while getting transaction amount_out")
