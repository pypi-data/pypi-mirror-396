from typing_extensions import deprecated
import requests
from typing import Optional
from thornode_py.models.thronode_models_auth import THORNodeAccountsResponse
from thornode_py.models.thronode_models_bank import THORNodeBalancesResponse
from thornode_py.models.thronode_models_health import THORNodePing
from thornode_py.models.thronode_models_liquidiry_provider import THORNodeLiquidityProvider, THORNodeLiquidityProviderSummary
from thornode_py.models.thronode_models_node import THORNodeNode
from thornode_py.models.thronode_models_oracle import THORNodeOraclePrice, THORNodeOraclePrices
from thornode_py.models.thronode_models_pool import THORNodePool, THORNodeDerivedPool
from thornode_py.models.thronode_models_pool_slip import THORNodePoolSlip
from thornode_py.models.thronode_models_rune_pool import THORNodeRunePool, THORNodeRuneProvider
from thornode_py.models.thronode_models_tcy_claimer import THORNodeTcyClaimerResult, THORNodeTcyClaimersResult
from thornode_py.models.thronode_models_tcy_staker import THORNodeTcyStaker, THORNodeTcyStakersResult
from thornode_py.models.thronode_models_thorname import THORNodeThorname
from thornode_py.models.thronode_models_saver import THORNodeSaver
from thornode_py.models.thronode_models_borrower import THORNodeBorrower
from thornode_py.models.thronode_models_transaction import (
    THORNodeTxResponse,
    THORNodeTxDetailsResponse,
    THORNodeTxStagesResponse,
    THORNodeTxStatusResponse,
)
from thornode_py.models.thronode_models_vault import (
    THORNodeVault,
    THORNodeVaultPubkeysResponse,
)
from thornode_py.models.thronode_models_network import (
    THORNodeNetwork,
    THORNodeOutboundFee,
    THORNodeInboundAddress,
    THORNodeLastBlock,
    THORNodeVersion,
)
from thornode_py.models.thronode_models_streaming_swap import THORNodeStreamingSwap
from thornode_py.models.thronode_models_trade_unit import THORNodeTradeUnit
from thornode_py.models.thronode_models_secured_asset import THORNodeSecuredAsset
from thornode_py.models.thronode_models_queue import THORNodeQueue


class THORNodeAPI:
    def __init__(self, base_url: str = "https://thornode.ninerealms.com", timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout

    # Auth
    #-------------------------------------------------------------------------------------------------------------------
    def accounts(self, address: str, height: Optional[int] = None) -> THORNodeAccountsResponse:
        url = f"{self.base_url}/auth/accounts/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeAccountsResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Bank
    #-------------------------------------------------------------------------------------------------------------------
    def balances(self, address: str, height: Optional[int] = None) -> THORNodeBalancesResponse:
        url = f"{self.base_url}/bank/balances/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeBalancesResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Health
    #-------------------------------------------------------------------------------------------------------------------
    def ping(self) -> THORNodePing:
        url = f"{self.base_url}/thorchain/ping"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodePing.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Pools
    #-------------------------------------------------------------------------------------------------------------------
    def pool(self, asset: str, height: Optional[int] = None) -> THORNodePool:
        url = f"{self.base_url}/thorchain/pool/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodePool.model_validate(data)

    def pools(self, height: Optional[int] = None) -> list[THORNodePool]:
        url = f"{self.base_url}/thorchain/pools"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodePool.model_validate(item) for item in data]

    def dpool(self, asset: str, height: Optional[int] = None) -> THORNodeDerivedPool:
        url = f"{self.base_url}/thorchain/dpool/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeDerivedPool.model_validate(data)

    def dpools(self, height: Optional[int] = None) -> list[THORNodeDerivedPool]:
        url = f"{self.base_url}/thorchain/dpools"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeDerivedPool.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Pool Slip
    #-------------------------------------------------------------------------------------------------------------------
    def slip(self, asset: str, height: Optional[int] = None) -> list[THORNodePoolSlip]:
        url = f"{self.base_url}/thorchain/slip/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodePoolSlip.model_validate(item) for item in data]

    def slips(self, height: Optional[int] = None) -> list[THORNodePoolSlip]:
        url = f"{self.base_url}/thorchain/slips"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodePoolSlip.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Liquidity Providers
    #-------------------------------------------------------------------------------------------------------------------
    def liquidity_provider(self, asset: str, address: str, height: Optional[int] = None) -> THORNodeLiquidityProvider:
        url = f"{self.base_url}/thorchain/pool/{asset}/liquidity_provider/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeLiquidityProvider.model_validate(data)

    def liquidity_providers(self, asset: str, height: Optional[int] = None) -> list[THORNodeLiquidityProviderSummary]:
        url = f"{self.base_url}/thorchain/pool/{asset}/liquidity_providers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeLiquidityProviderSummary.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------


    # Oracle
    #-------------------------------------------------------------------------------------------------------------------
    def price(self, symbol: str, height: Optional[int] = None) -> THORNodeOraclePrice:
        url = f"{self.base_url}/thorchain/oracle/price/{symbol}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeOraclePrice.model_validate(data)

    def prices(self, height: Optional[int] = None) -> THORNodeOraclePrices:
        url = f"{self.base_url}/thorchain/oracle/prices"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeOraclePrices.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # TCY Stakers
    #-------------------------------------------------------------------------------------------------------------------
    def tcy_staker(self, address: str, height: Optional[int] = None) -> THORNodeTcyStaker:
        url = f"{self.base_url}/thorchain/tcy_staker/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTcyStaker.model_validate(data)

    def tcy_stakers(self, height: Optional[int] = None) -> THORNodeTcyStakersResult:
        url = f"{self.base_url}/thorchain/tcy_stakers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTcyStakersResult.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # TCY Claimers
    #-------------------------------------------------------------------------------------------------------------------
    def tcy_claimer(self, address: str, height: Optional[int] = None) -> THORNodeTcyClaimerResult:
        url = f"{self.base_url}/thorchain/tcy_claimer/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTcyClaimerResult.model_validate(data)

    def tcy_claimers(self, height: Optional[int] = None) -> THORNodeTcyClaimersResult:
        url = f"{self.base_url}/thorchain/tcy_claimers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTcyClaimersResult.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # RUNE Pool
    #-------------------------------------------------------------------------------------------------------------------
    def runepool(self, height: Optional[int] = None) -> THORNodeRunePool:
        url = f"{self.base_url}/thorchain/runepool"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeRunePool.model_validate(data)

    def rune_provider(self, address: str, height: Optional[int] = None) -> THORNodeRuneProvider:
        url = f"{self.base_url}/thorchain/rune_provider/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeRuneProvider.model_validate(data)

    def rune_providers(self, height: Optional[int] = None) -> list[THORNodeRuneProvider]:
        url = f"{self.base_url}/thorchain/rune_providers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeRuneProvider.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Savers
    #-------------------------------------------------------------------------------------------------------------------
    def saver(self, asset: str, address: str, height: Optional[int] = None) -> THORNodeSaver:
        url = f"{self.base_url}/thorchain/pool/{asset}/saver/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeSaver.model_validate(data)

    def savers(self, asset: str, height: Optional[int] = None) -> list[THORNodeSaver]:
        url = f"{self.base_url}/thorchain/pool/{asset}/savers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeSaver.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Borrowers
    #-------------------------------------------------------------------------------------------------------------------
    @deprecated("This endpoint in THORNode is no longer implemented")
    def borrower(self, asset: str, address: str, height: Optional[int] = None) -> THORNodeBorrower:
        url = f"{self.base_url}/thorchain/pool/{asset}/borrower/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeBorrower.model_validate(data)

    @deprecated("This endpoint in THORNode is no longer implemented")
    def borrowers(self, asset: str, height: Optional[int] = None) -> list[THORNodeBorrower]:
        url = f"{self.base_url}/thorchain/pool/{asset}/borrowers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeBorrower.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Transactions
    #-------------------------------------------------------------------------------------------------------------------
    def tx(self, hash: str, height: Optional[int] = None) -> THORNodeTxResponse:
        url = f"{self.base_url}/thorchain/tx/{hash}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTxResponse.model_validate(data)

    def tx_signers(self, hash: str, height: Optional[int] = None) -> THORNodeTxDetailsResponse:
        url = f"{self.base_url}/thorchain/tx/{hash}/signers"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTxDetailsResponse.model_validate(data)

    def tx_details(self, hash: str, height: Optional[int] = None) -> THORNodeTxDetailsResponse:
        url = f"{self.base_url}/thorchain/tx/details/{hash}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTxDetailsResponse.model_validate(data)

    def tx_stages(self, hash: str, height: Optional[int] = None) -> THORNodeTxStagesResponse:
        url = f"{self.base_url}/thorchain/tx/stages/{hash}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTxStagesResponse.model_validate(data)

    def tx_status(self, hash: str, height: Optional[int] = None) -> THORNodeTxStatusResponse:
        url = f"{self.base_url}/thorchain/tx/status/{hash}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTxStatusResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Nodes
    #-------------------------------------------------------------------------------------------------------------------
    def node(self, address: str, height: Optional[int] = None) -> THORNodeNode:
        url = f"{self.base_url}/thorchain/node/{address}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeNode.model_validate(data)

    def nodes(self, height: Optional[int] = None) -> list[THORNodeNode]:
        url = f"{self.base_url}/thorchain/nodes"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeNode.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Vaults
    #-------------------------------------------------------------------------------------------------------------------
    def vaults_asgard(self, height: Optional[int] = None) -> list[THORNodeVault]:
        url = f"{self.base_url}/thorchain/vaults/asgard"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeVault.model_validate(item) for item in data]

    def vault(self, pubkey: str, height: Optional[int] = None) -> THORNodeVault:
        url = f"{self.base_url}/thorchain/vault/{pubkey}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeVault.model_validate(data)

    def vault_pubkeys(self, height: Optional[int] = None) -> THORNodeVaultPubkeysResponse:
        url = f"{self.base_url}/thorchain/vaults/pubkeys"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeVaultPubkeysResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Network
    #-------------------------------------------------------------------------------------------------------------------
    def network(self, height: Optional[int] = None) -> THORNodeNetwork:
        url = f"{self.base_url}/thorchain/network"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeNetwork.model_validate(data)

    def outbound_fees(self, height: Optional[int] = None) -> list[THORNodeOutboundFee]:
        url = f"{self.base_url}/thorchain/outbound_fees"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeOutboundFee.model_validate(item) for item in data]

    def outbound_fee(self, asset: str, height: Optional[int] = None) -> list[THORNodeOutboundFee]:
        url = f"{self.base_url}/thorchain/outbound_fee/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeOutboundFee.model_validate(item) for item in data]

    def inbound_addresses(self, height: Optional[int] = None) -> list[THORNodeInboundAddress]:
        url = f"{self.base_url}/thorchain/inbound_addresses"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeInboundAddress.model_validate(item) for item in data]

    def lastblock(self, height: Optional[int] = None) -> list[THORNodeLastBlock]:
        url = f"{self.base_url}/thorchain/lastblock"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeLastBlock.model_validate(item) for item in data]

    def lastblock_chain(self, chain: str, height: Optional[int] = None) -> list[THORNodeLastBlock]:
        url = f"{self.base_url}/thorchain/lastblock/{chain}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeLastBlock.model_validate(item) for item in data]

    def version(self, height: Optional[int] = None) -> THORNodeVersion:
        url = f"{self.base_url}/thorchain/version"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeVersion.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------


    # Streaming Swap
    #-------------------------------------------------------------------------------------------------------------------
    def streaming_swap(self, hash: str, height: Optional[int] = None) -> THORNodeStreamingSwap:
        url = f"{self.base_url}/thorchain/swap/streaming/{hash}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeStreamingSwap.model_validate(data)

    def streaming_swaps(self, height: Optional[int] = None) -> list[THORNodeStreamingSwap]:
        url = f"{self.base_url}/thorchain/swaps/streaming"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeStreamingSwap.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Clout
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------



    # Trade Unit
    #-------------------------------------------------------------------------------------------------------------------
    def trade_unit(self, asset: str, height: Optional[int] = None) -> THORNodeTradeUnit:
        url = f"{self.base_url}/thorchain/trade/unit/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeTradeUnit.model_validate(data)

    def trade_units(self, height: Optional[int] = None) -> list[THORNodeTradeUnit]:
        url = f"{self.base_url}/thorchain/trade/units"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeTradeUnit.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Trade Account
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------



    # Secured Asset
    #-------------------------------------------------------------------------------------------------------------------
    def secured_asset(self, asset: str, height: Optional[int] = None) -> THORNodeSecuredAsset:
        url = f"{self.base_url}/thorchain/securedasset/{asset}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeSecuredAsset.model_validate(data)

    def secured_assets(self, height: Optional[int] = None) -> list[THORNodeSecuredAsset]:
        url = f"{self.base_url}/thorchain/securedassets"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeSecuredAsset.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # Swap
    #-------------------------------------------------------------------------------------------------------------------
    def queue_swap_details(self, tx_id: str, height: Optional[int] = None):
        from thornode_py.models.thronode_models_swap import THORNodeSwapDetailsResponse
        url = f"{self.base_url}/thorchain/queue/swap/details/{tx_id}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeSwapDetailsResponse.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Queue
    #-------------------------------------------------------------------------------------------------------------------
    def queue(self, height: Optional[int] = None) -> THORNodeQueue:
        url = f"{self.base_url}/thorchain/queue"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQueue.model_validate(data)

    def queue_swap(self, height: Optional[int] = None):
        from thornode_py.models.thronode_models_swap import THORNodeMsgSwap
        url = f"{self.base_url}/thorchain/queue/swap"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeMsgSwap.model_validate(item) for item in data]

    def queue_outbound(self, height: Optional[int] = None):
        from thornode_py.models.thronode_models_transaction import THORNodeTxAction
        url = f"{self.base_url}/thorchain/queue/outbound"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return [THORNodeTxAction.model_validate(item) for item in data]
    #-------------------------------------------------------------------------------------------------------------------



    # TSS
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------



    # Thornames
    #-------------------------------------------------------------------------------------------------------------------
    def thorname(self, name: str, height: Optional[int] = None) -> THORNodeThorname:
        url = f"{self.base_url}/thorchain/thorname/{name}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeThorname.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Mimir
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------



    # Quote
    #-------------------------------------------------------------------------------------------------------------------
    def quote_swap(
        self,
        from_asset: str,
        to_asset: str,
        amount: int,
        destination: Optional[str] = None,
        refund_address: Optional[str] = None,
        streaming_interval: Optional[int] = None,
        streaming_quantity: Optional[int] = None,
        tolerance_bps: Optional[int] = None,
        liquidity_tolerance_bps: Optional[int] = None,
        affiliate_bps: Optional[int] = None,
        affiliate: Optional[str] = None,
        height: Optional[int] = None,
    ):
        from thornode_py.models.thronode_models_quote import THORNodeQuoteSwap
        url = f"{self.base_url}/thorchain/quote/swap"
        params = {
            "from_asset": from_asset,
            "to_asset": to_asset,
            "amount": amount,
        }
        if destination is not None:
            params["destination"] = destination
        if refund_address is not None:
            params["refund_address"] = refund_address
        if streaming_interval is not None:
            params["streaming_interval"] = streaming_interval
        if streaming_quantity is not None:
            params["streaming_quantity"] = streaming_quantity
        if tolerance_bps is not None:
            params["tolerance_bps"] = tolerance_bps
        if liquidity_tolerance_bps is not None:
            params["liquidity_tolerance_bps"] = liquidity_tolerance_bps
        if affiliate_bps is not None:
            params["affiliate_bps"] = affiliate_bps
        if affiliate is not None:
            params["affiliate"] = affiliate
        if height is not None:
            params["height"] = height
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQuoteSwap.model_validate(data)

    # Saver feature doesn't work currently
    def quote_saver_deposit(self, asset: str, amount: int, height: Optional[int] = None):
        from thornode_py.models.thronode_models_quote import THORNodeQuoteSaverDeposit
        url = f"{self.base_url}/thorchain/quote/saver/deposit"
        params = {"asset": asset, "amount": amount}
        if height is not None:
            params["height"] = height
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQuoteSaverDeposit.model_validate(data)

    # Saver feature doesn't work currently
    def quote_saver_withdraw(
        self, asset: str, address: str, withdraw_bps: int, height: Optional[int] = None
    ):
        from thornode_py.models.thronode_models_quote import THORNodeQuoteSaverWithdraw
        url = f"{self.base_url}/thorchain/quote/saver/withdraw"
        params = {"asset": asset, "address": address, "withdraw_bps": withdraw_bps}
        if height is not None:
            params["height"] = height
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQuoteSaverWithdraw.model_validate(data)

    # Loans are currently paused
    def quote_loan_open(
        self,
        from_asset: str,
        amount: int,
        to_asset: str,
        destination: str,
        min_out: Optional[str] = None,
        affiliate_bps: Optional[int] = None,
        affiliate: Optional[str] = None,
        height: Optional[int] = None,
    ):
        from thornode_py.models.thronode_models_quote import THORNodeQuoteLoanOpen
        url = f"{self.base_url}/thorchain/quote/loan/open"
        params = {
            "from_asset": from_asset,
            "amount": amount,
            "to_asset": to_asset,
            "destination": destination,
        }
        if min_out is not None:
            params["min_out"] = min_out
        if affiliate_bps is not None:
            params["affiliate_bps"] = affiliate_bps
        if affiliate is not None:
            params["affiliate"] = affiliate
        if height is not None:
            params["height"] = height
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQuoteLoanOpen.model_validate(data)

    # Loans are currently paused
    def quote_loan_close(
        self,
        from_asset: str,
        repay_bps: int,
        to_asset: str,
        loan_owner: str,
        min_out: Optional[str] = None,
        height: Optional[int] = None,
    ):
        from thornode_py.models.thronode_models_quote import THORNodeQuoteLoanClose
        url = f"{self.base_url}/thorchain/quote/loan/close"
        params = {
            "from_asset": from_asset,
            "repay_bps": repay_bps,
            "to_asset": to_asset,
            "loan_owner": loan_owner,
        }
        if min_out is not None:
            params["min_out"] = min_out
        if height is not None:
            params["height"] = height
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeQuoteLoanClose.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Invariants
    #-------------------------------------------------------------------------------------------------------------------
    def invariant(self, invariant: str, height: Optional[int] = None):
        from thornode_py.models.thronode_models_invariant import THORNodeInvariant
        url = f"{self.base_url}/thorchain/invariant/{invariant}"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeInvariant.model_validate(data)

    def invariants(self, height: Optional[int] = None):
        from thornode_py.models.thronode_models_invariant import THORNodeInvariants
        url = f"{self.base_url}/thorchain/invariants"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeInvariants.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------



    # Block
    #-------------------------------------------------------------------------------------------------------------------
    def block(self, height: Optional[int] = None):
        from thornode_py.models.thronode_models_block import THORNodeBlock
        url = f"{self.base_url}/thorchain/block"
        params = {"height": height} if height is not None else None
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return THORNodeBlock.model_validate(data)
    #-------------------------------------------------------------------------------------------------------------------
