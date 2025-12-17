from pydantic import BaseModel
from typing import List, Optional


class THORNodeCoin(BaseModel):
    asset: str
    amount: str
    decimals: Optional[int] = None


class THORNodeTx(BaseModel):
    id: Optional[str] = None
    chain: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    coins: List[THORNodeCoin]
    gas: Optional[List[THORNodeCoin]] = []
    memo: Optional[str] = None


class THORNodeTxObserved(BaseModel):
    tx: THORNodeTx
    observed_pub_key: Optional[str] = None
    observed_pub_key_eddsa: Optional[str] = None
    external_observed_height: Optional[int] = None
    external_confirmation_delay_height: Optional[int] = None
    aggregator: Optional[str] = None
    aggregator_target: Optional[str] = None
    aggregator_target_limit: Optional[str] = None
    signers: Optional[List[str]] = None
    keysign_ms: Optional[int] = None
    out_hashes: Optional[List[str]] = None
    status: Optional[str] = None


class THORNodeTxAction(BaseModel):
    height: Optional[int] = None
    in_hash: Optional[str] = None
    out_hash: Optional[str] = None
    chain: str
    to_address: str
    vault_pub_key: Optional[str] = None
    vault_pub_key_eddsa: Optional[str] = None
    coin: THORNodeCoin
    max_gas: List[THORNodeCoin]
    gas_rate: Optional[int] = None
    memo: Optional[str] = None
    aggregator: Optional[str] = None
    aggregator_target_asset: Optional[str] = None
    aggregator_target_limit: Optional[str] = None
    clout_spent: Optional[str] = None


class THORNodeTssMetric(BaseModel):
    address: Optional[str] = None
    tss_time: Optional[int] = None


class THORNodeTxKeysignMetric(BaseModel):
    tx_id: Optional[str] = None
    node_tss_times: Optional[List[THORNodeTssMetric]] = []


class THORNodeTxResponse(BaseModel):
    observed_tx: Optional[THORNodeTxObserved] = None
    consensus_height: Optional[int] = None
    finalised_height: Optional[int] = None
    outbound_height: Optional[int] = None
    keysign_metric: Optional[THORNodeTxKeysignMetric] = None


class THORNodeTxDetailsResponse(BaseModel):
    tx_id: Optional[str] = None
    tx: THORNodeTxObserved
    txs: List[THORNodeTxObserved]
    actions: List[THORNodeTxAction]
    out_txs: List[THORNodeTx]
    consensus_height: Optional[int] = None
    finalised_height: Optional[int] = None
    updated_vault: Optional[bool] = None
    reverted: Optional[bool] = None
    outbound_height: Optional[int] = None


# Stages
class THORNodeTxStagesInboundObserved(BaseModel):
    started: Optional[bool] = None
    pre_confirmation_count: Optional[int] = None
    final_count: int
    completed: bool


class THORNodeTxStagesInboundConfirmationCounted(BaseModel):
    counting_start_height: Optional[int] = None
    remaining_confirmation_required: Optional[int] = None
    completed: bool


class THORNodeTxStagesSwapStatus(BaseModel):
    failure_reason: Optional[str] = None
    refund_reason: Optional[str] = None
    completed: Optional[bool] = None


class THORNodeTxStagesSwapFinalised(BaseModel):
    completed: bool


class THORNodeTxStagesOutboundDelay(BaseModel):
    remaining_delay_blocks: Optional[int] = None
    remaining_delay_seconds: Optional[int] = None
    completed: bool


class THORNodeTxStagesOutboundSigned(BaseModel):
    scheduled_outbound_height: Optional[int] = None
    blocks_since_scheduled: Optional[int] = None
    completed: bool


class THORNodeTxStagesResponse(BaseModel):
    inbound_observed: THORNodeTxStagesInboundObserved
    inbound_confirmation_counted: Optional[THORNodeTxStagesInboundConfirmationCounted] = None
    swap_status: Optional[THORNodeTxStagesSwapStatus] = None
    swap_finalised: Optional[THORNodeTxStagesSwapFinalised] = None
    outbound_delay: Optional[THORNodeTxStagesOutboundDelay] = None
    outbound_signed: Optional[THORNodeTxStagesOutboundSigned] = None


class THORNodeTxPlannedOut(BaseModel):
    chain: str
    to_address: str
    coin: THORNodeCoin
    refund: bool


class THORNodeTxStatusResponse(BaseModel):
    tx: Optional[THORNodeTx] = None
    planned_out_txs: Optional[List[THORNodeTxPlannedOut]] = None
    out_txs: Optional[List[THORNodeTx]] = None
    stages: THORNodeTxStagesResponse
