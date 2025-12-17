from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class THORNodeBlockIdParts(BaseModel):
    total: int
    hash: str


class THORNodeBlockId(BaseModel):
    hash: str
    parts: THORNodeBlockIdParts


class THORNodeBlockHeaderVersion(BaseModel):
    block: str
    app: str


class THORNodeBlockHeader(BaseModel):
    version: THORNodeBlockHeaderVersion
    chain_id: str
    height: int
    time: str
    last_block_id: THORNodeBlockId
    last_commit_hash: str
    data_hash: str
    validators_hash: str
    next_validators_hash: str
    consensus_hash: str
    app_hash: str
    last_results_hash: str
    evidence_hash: str
    proposer_address: str


class THORNodeBlockTxResult(BaseModel):
    code: Optional[int] = None
    data: Optional[str] = None
    log: Optional[str] = None
    info: Optional[str] = None
    gas_wanted: Optional[str] = None
    gas_used: Optional[str] = None
    events: Optional[List[Dict[str, str]]] = None
    codespace: Optional[str] = None


class THORNodeBlockTx(BaseModel):
    hash: str
    tx: Dict[str, Any]
    result: THORNodeBlockTxResult


class THORNodeBlock(BaseModel):
    id: THORNodeBlockId
    header: THORNodeBlockHeader
    begin_block_events: List[Dict[str, str]]
    end_block_events: List[Dict[str, str]]
    finalize_block_events: List[Dict[str, str]]
    txs: Optional[List[THORNodeBlockTx]] = None
