from pydantic import BaseModel
from typing import List, Optional


class THORNodePubKeySet(BaseModel):
    secp256k1: Optional[str] = None
    ed25519: Optional[str] = None


class THORNodeBondProvider(BaseModel):
    bond_address: str
    bond: str


class THORNodeBondProviders(BaseModel):
    node_operator_fee: str
    providers: Optional[List[THORNodeBondProvider]] = []


class THORNodeChainHeight(BaseModel):
    chain: str
    height: int


class THORNodeJail(BaseModel):
    release_height: Optional[int] = None
    reason: Optional[str] = None


class THORNodePreflightStatus(BaseModel):
    status: str
    reason: str
    code: int


class THORNodeNode(BaseModel):
    node_address: str
    status: str
    pub_key_set: THORNodePubKeySet
    validator_cons_pub_key: str
    peer_id: str
    active_block_height: int
    status_since: int
    node_operator_address: str
    total_bond: str
    bond_providers: THORNodeBondProviders
    signer_membership: Optional[List[str]] = []
    requested_to_leave: bool
    forced_to_leave: bool
    leave_height: int
    ip_address: str
    version: str
    slash_points: int
    jail: THORNodeJail
    current_award: str
    observe_chains: Optional[List[THORNodeChainHeight]] = []
    maintenance: bool
    missing_blocks: int
    preflight_status: THORNodePreflightStatus
