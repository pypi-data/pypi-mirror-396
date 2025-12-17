from pydantic import BaseModel
from typing import List, Optional
from .thronode_models_transaction import THORNodeCoin


class THORNodeVaultRouter(BaseModel):
    chain: Optional[str] = None
    router: Optional[str] = None


class THORNodeVaultAddress(BaseModel):
    chain: str
    address: str


class THORNodeVault(BaseModel):
    block_height: Optional[int] = None
    pub_key: Optional[str] = None
    pub_key_eddsa: Optional[str] = None
    coins: List[THORNodeCoin]
    type: Optional[str] = None
    status: Optional[str] = None
    status_since: Optional[int] = None
    membership: Optional[List[str]] = None
    chains: Optional[List[str]] = None
    inbound_tx_count: Optional[int] = None
    outbound_tx_count: Optional[int] = None
    pending_tx_block_heights: Optional[List[int]] = None
    routers: List[THORNodeVaultRouter]
    addresses: List[THORNodeVaultAddress]
    frozen: Optional[List[str]] = None


class THORNodeVaultYggdrasil(BaseModel):
    block_height: Optional[int] = None
    pub_key: Optional[str] = None
    coins: List[THORNodeCoin]
    type: Optional[str] = None
    status_since: Optional[int] = None
    membership: Optional[List[str]] = None
    chains: Optional[List[str]] = None
    inbound_tx_count: Optional[int] = None
    outbound_tx_count: Optional[int] = None
    pending_tx_block_heights: Optional[List[int]] = None
    routers: List[THORNodeVaultRouter]
    status: Optional[str] = None
    bond: str
    total_value: str
    addresses: List[THORNodeVaultAddress]


class THORNodeVaultInfo(BaseModel):
    pub_key: str
    pub_key_eddsa: Optional[str] = None
    routers: List[THORNodeVaultRouter]


class THORNodeVaultPubkeysResponse(BaseModel):
    asgard: List[THORNodeVaultInfo]
    yggdrasil: Optional[List[THORNodeVaultInfo]] = []
    inactive: List[THORNodeVaultInfo]
