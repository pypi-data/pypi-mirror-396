"""
Acceso Solana Python SDK

A comprehensive Python SDK for Solana blockchain operations via Acceso API.
"""

__version__ = "1.0.0"
__author__ = "Acceso"
__email__ = "dev@acceso.dev"

from .client import SolanaClient, SolanaError
from .types import (
    SolanaConfig,
    # Wallet
    Wallet,
    WalletBalance,
    # Tokens
    TokenInfo,
    TokenBalance,
    TokenHolding,
    # NFTs
    NFT,
    NFTMetadata,
    Collection,
    # Transactions
    Transaction,
    TransactionSignature,
    TransferResult,
    # Staking
    StakeAccount,
    Validator,
    StakeResult,
    # Swap
    SwapQuote,
    SwapResult,
    # DeFi
    DeFiPosition,
)

__all__ = [
    "SolanaClient",
    "SolanaError",
    "SolanaConfig",
    # Wallet
    "Wallet",
    "WalletBalance",
    # Tokens
    "TokenInfo",
    "TokenBalance",
    "TokenHolding",
    # NFTs
    "NFT",
    "NFTMetadata",
    "Collection",
    # Transactions
    "Transaction",
    "TransactionSignature",
    "TransferResult",
    # Staking
    "StakeAccount",
    "Validator",
    "StakeResult",
    # Swap
    "SwapQuote",
    "SwapResult",
    # DeFi
    "DeFiPosition",
]
