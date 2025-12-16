"""
Type definitions for Solana SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


@dataclass
class SolanaConfig:
    """Configuration for Solana client"""
    api_key: str
    api_url: str = "https://api.acceso.dev"
    timeout: int = 30
    debug: bool = False


# ========================================
# Wallet Types
# ========================================

@dataclass
class Wallet:
    """A Solana wallet"""
    address: str
    lamports: int
    sol_balance: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Wallet":
        lamports = data.get("lamports", 0)
        return cls(
            address=data.get("address", ""),
            lamports=lamports,
            sol_balance=data.get("sol_balance", data.get("solBalance", lamports / 1e9)),
        )


@dataclass
class WalletBalance:
    """Wallet balance info"""
    address: str
    lamports: int
    sol: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletBalance":
        lamports = data.get("lamports", 0)
        return cls(
            address=data.get("address", ""),
            lamports=lamports,
            sol=data.get("sol", lamports / 1e9),
        )


# ========================================
# Token Types
# ========================================

@dataclass
class TokenInfo:
    """Token metadata"""
    address: str
    name: str
    symbol: str
    decimals: int
    supply: Optional[str] = None
    logo_uri: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenInfo":
        return cls(
            address=data.get("address", data.get("mint", "")),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            decimals=data.get("decimals", 9),
            supply=data.get("supply"),
            logo_uri=data.get("logo_uri", data.get("logoUri")),
        )


@dataclass
class TokenBalance:
    """Token balance for an account"""
    mint: str
    owner: str
    amount: str
    decimals: int
    ui_amount: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenBalance":
        return cls(
            mint=data.get("mint", ""),
            owner=data.get("owner", ""),
            amount=data.get("amount", "0"),
            decimals=data.get("decimals", 9),
            ui_amount=data.get("ui_amount", data.get("uiAmount", 0)),
        )


@dataclass
class TokenHolding:
    """Token holding with metadata"""
    mint: str
    amount: str
    decimals: int
    ui_amount: float
    name: Optional[str] = None
    symbol: Optional[str] = None
    logo_uri: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenHolding":
        return cls(
            mint=data.get("mint", ""),
            amount=data.get("amount", "0"),
            decimals=data.get("decimals", 9),
            ui_amount=data.get("ui_amount", data.get("uiAmount", 0)),
            name=data.get("name"),
            symbol=data.get("symbol"),
            logo_uri=data.get("logo_uri", data.get("logoUri")),
        )


# ========================================
# NFT Types
# ========================================

@dataclass
class NFTMetadata:
    """NFT metadata"""
    name: str
    symbol: str
    description: Optional[str] = None
    image: Optional[str] = None
    external_url: Optional[str] = None
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NFTMetadata":
        return cls(
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            description=data.get("description"),
            image=data.get("image"),
            external_url=data.get("external_url", data.get("externalUrl")),
            attributes=data.get("attributes", []),
        )


@dataclass
class NFT:
    """A Solana NFT"""
    mint: str
    owner: str
    name: str
    symbol: str
    uri: str
    metadata: Optional[NFTMetadata] = None
    collection: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NFT":
        metadata = None
        if "metadata" in data and data["metadata"]:
            metadata = NFTMetadata.from_dict(data["metadata"])
        
        return cls(
            mint=data.get("mint", ""),
            owner=data.get("owner", ""),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            uri=data.get("uri", ""),
            metadata=metadata,
            collection=data.get("collection"),
        )


@dataclass
class Collection:
    """NFT Collection"""
    address: str
    name: str
    symbol: str
    size: int
    floor_price: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Collection":
        return cls(
            address=data.get("address", ""),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            size=data.get("size", 0),
            floor_price=data.get("floor_price", data.get("floorPrice")),
        )


# ========================================
# Transaction Types
# ========================================

@dataclass
class TransactionSignature:
    """Transaction signature info"""
    signature: str
    slot: int
    block_time: Optional[int] = None
    err: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionSignature":
        return cls(
            signature=data.get("signature", ""),
            slot=data.get("slot", 0),
            block_time=data.get("block_time", data.get("blockTime")),
            err=data.get("err"),
        )


@dataclass
class Transaction:
    """Full transaction details"""
    signature: str
    slot: int
    block_time: Optional[int] = None
    fee: int = 0
    status: str = "unknown"
    instructions: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        return cls(
            signature=data.get("signature", ""),
            slot=data.get("slot", 0),
            block_time=data.get("block_time", data.get("blockTime")),
            fee=data.get("fee", 0),
            status=data.get("status", "unknown"),
            instructions=data.get("instructions", []),
        )


@dataclass
class TransferResult:
    """Result of a transfer operation"""
    signature: str
    from_address: str
    to_address: str
    amount: str
    status: str = "confirmed"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferResult":
        return cls(
            signature=data.get("signature", ""),
            from_address=data.get("from_address", data.get("from", "")),
            to_address=data.get("to_address", data.get("to", "")),
            amount=data.get("amount", "0"),
            status=data.get("status", "confirmed"),
        )


# ========================================
# Staking Types
# ========================================

@dataclass
class StakeAccount:
    """Stake account info"""
    address: str
    lamports: int
    voter: str
    state: str
    activation_epoch: Optional[int] = None
    deactivation_epoch: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StakeAccount":
        return cls(
            address=data.get("address", ""),
            lamports=data.get("lamports", 0),
            voter=data.get("voter", ""),
            state=data.get("state", "inactive"),
            activation_epoch=data.get("activation_epoch", data.get("activationEpoch")),
            deactivation_epoch=data.get("deactivation_epoch", data.get("deactivationEpoch")),
        )


@dataclass
class Validator:
    """Validator info"""
    vote_pubkey: str
    node_pubkey: str
    stake: int
    commission: int
    name: Optional[str] = None
    website: Optional[str] = None
    apy: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Validator":
        return cls(
            vote_pubkey=data.get("vote_pubkey", data.get("votePubkey", "")),
            node_pubkey=data.get("node_pubkey", data.get("nodePubkey", "")),
            stake=data.get("stake", 0),
            commission=data.get("commission", 0),
            name=data.get("name"),
            website=data.get("website"),
            apy=data.get("apy"),
        )


@dataclass
class StakeResult:
    """Result of a staking operation"""
    signature: str
    stake_account: str
    amount: int
    validator: str
    status: str = "confirmed"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StakeResult":
        return cls(
            signature=data.get("signature", ""),
            stake_account=data.get("stake_account", data.get("stakeAccount", "")),
            amount=data.get("amount", 0),
            validator=data.get("validator", ""),
            status=data.get("status", "confirmed"),
        )


# ========================================
# Swap Types
# ========================================

@dataclass
class SwapQuote:
    """Swap quote from Jupiter"""
    input_mint: str
    output_mint: str
    in_amount: str
    out_amount: str
    price_impact_pct: float
    route_plan: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SwapQuote":
        return cls(
            input_mint=data.get("input_mint", data.get("inputMint", "")),
            output_mint=data.get("output_mint", data.get("outputMint", "")),
            in_amount=data.get("in_amount", data.get("inAmount", "0")),
            out_amount=data.get("out_amount", data.get("outAmount", "0")),
            price_impact_pct=data.get("price_impact_pct", data.get("priceImpactPct", 0)),
            route_plan=data.get("route_plan", data.get("routePlan", [])),
        )


@dataclass
class SwapResult:
    """Result of a swap operation"""
    signature: str
    input_mint: str
    output_mint: str
    in_amount: str
    out_amount: str
    status: str = "confirmed"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SwapResult":
        return cls(
            signature=data.get("signature", ""),
            input_mint=data.get("input_mint", data.get("inputMint", "")),
            output_mint=data.get("output_mint", data.get("outputMint", "")),
            in_amount=data.get("in_amount", data.get("inAmount", "0")),
            out_amount=data.get("out_amount", data.get("outAmount", "0")),
            status=data.get("status", "confirmed"),
        )


# ========================================
# DeFi Types
# ========================================

@dataclass
class DeFiPosition:
    """DeFi position info"""
    protocol: str
    type: str
    value_usd: float
    tokens: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeFiPosition":
        return cls(
            protocol=data.get("protocol", ""),
            type=data.get("type", ""),
            value_usd=data.get("value_usd", data.get("valueUsd", 0)),
            tokens=data.get("tokens", []),
        )


# ========================================
# Constants
# ========================================

# Common token mints
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"

# Lamports per SOL
LAMPORTS_PER_SOL = 1_000_000_000
