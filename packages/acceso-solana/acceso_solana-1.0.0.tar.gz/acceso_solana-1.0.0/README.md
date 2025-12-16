# Acceso Solana Python SDK

Comprehensive Python SDK for Solana blockchain operations via Acceso API.

## Installation

```bash
pip install acceso-solana
```

## Features

- 💰 **Wallet Operations** - Balance, tokens, NFTs
- 🪙 **Token Transfers** - SPL token operations
- 🎨 **NFT Support** - Mint, transfer, query NFTs
- 📈 **Staking** - Delegate, undelegate, withdraw
- 🔄 **Token Swaps** - Jupiter aggregator integration
- 📜 **Transactions** - History and details
- 🏦 **DeFi** - Protocol positions

## Quick Start

```python
from acceso_solana import SolanaClient, SolanaConfig

# Initialize client
client = SolanaClient(SolanaConfig(api_key="your_api_key"))

# Get wallet balance
balance = client.get_balance("YourWalletAddress...")
print(f"Balance: {balance.sol} SOL ({balance.lamports} lamports)")
```

## Wallet Operations

```python
# Get full wallet info
wallet = client.get_wallet("WalletAddress...")
print(f"Address: {wallet.address}")
print(f"Balance: {wallet.sol_balance} SOL")

# Get all token holdings
tokens = client.get_token_holdings("WalletAddress...")
for token in tokens:
    print(f"{token.symbol}: {token.ui_amount}")
```

## Token Operations

```python
# Get token info
usdc = client.get_token_info("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
print(f"{usdc.name} ({usdc.symbol}), Decimals: {usdc.decimals}")

# Get token balance
balance = client.get_token_balance(
    wallet="YourWallet...",
    mint="TokenMint...",
)
print(f"Balance: {balance.ui_amount}")

# Transfer tokens
result = client.transfer_token(
    from_keypair="YourBase58Keypair...",
    to_address="RecipientAddress...",
    mint="TokenMint...",
    amount="1000000",  # In base units
)
print(f"Transfer: {result.signature}")

# Transfer SOL
result = client.transfer_sol(
    from_keypair="YourBase58Keypair...",
    to_address="RecipientAddress...",
    lamports=1_000_000_000,  # 1 SOL
)
print(f"Transfer: {result.signature}")
```

## NFT Operations

```python
# Get NFT details
nft = client.get_nft("NFTMintAddress...")
print(f"{nft.name} by collection {nft.collection}")
print(f"Image: {nft.metadata.image}")

# Get all NFTs for wallet
nfts = client.get_nfts("WalletAddress...")
for nft in nfts:
    print(f"- {nft.name}")

# Mint NFT
nft = client.mint_nft(
    payer_keypair="YourBase58Keypair...",
    name="My NFT",
    symbol="MNFT",
    uri="https://example.com/metadata.json",
    collection="OptionalCollectionAddress...",
)
print(f"Minted: {nft.mint}")

# Transfer NFT
result = client.transfer_nft(
    from_keypair="YourBase58Keypair...",
    to_address="RecipientAddress...",
    mint="NFTMintAddress...",
)
print(f"Transfer: {result.signature}")
```

## Staking

```python
# Get validators
validators = client.get_validators(limit=10, sort_by="apy")
for v in validators:
    print(f"{v.name}: {v.apy}% APY, {v.commission}% commission")

# Get stake accounts
stakes = client.get_stake_accounts("WalletAddress...")
for stake in stakes:
    print(f"{stake.address}: {stake.lamports} lamports to {stake.voter}")

# Create stake delegation
result = client.stake(
    staker_keypair="YourBase58Keypair...",
    validator="ValidatorVoteAccount...",
    lamports=5_000_000_000,  # 5 SOL
)
print(f"Staked to {result.stake_account}")

# Unstake (deactivate)
result = client.unstake(
    staker_keypair="YourBase58Keypair...",
    stake_account="StakeAccountAddress...",
)
print(f"Deactivated: {result.signature}")

# Withdraw (after cooldown)
result = client.withdraw_stake(
    staker_keypair="YourBase58Keypair...",
    stake_account="StakeAccountAddress...",
)
print(f"Withdrawn: {result.signature}")
```

## Token Swaps (Jupiter)

```python
from acceso_solana.types import SOL_MINT, USDC_MINT

# Get swap quote
quote = client.get_swap_quote(
    input_mint=SOL_MINT,
    output_mint=USDC_MINT,
    amount="1000000000",  # 1 SOL
    slippage_bps=50,  # 0.5%
)
print(f"1 SOL = {quote.out_amount} USDC")
print(f"Price impact: {quote.price_impact_pct}%")

# Execute swap
result = client.execute_swap(
    user_keypair="YourBase58Keypair...",
    input_mint=SOL_MINT,
    output_mint=USDC_MINT,
    amount="1000000000",
    slippage_bps=50,
)
print(f"Swapped! TX: {result.signature}")
print(f"Received: {result.out_amount}")
```

## Transaction History

```python
# Get recent transactions
txs = client.get_transactions("WalletAddress...", limit=10)
for tx in txs:
    print(f"{tx.signature}: slot {tx.slot}")

# Get transaction details
tx = client.get_transaction("TransactionSignature...")
print(f"Fee: {tx.fee} lamports")
print(f"Status: {tx.status}")
```

## DeFi Positions

```python
# Get all DeFi positions
positions = client.get_defi_positions("WalletAddress...")
for pos in positions:
    print(f"{pos.protocol} {pos.type}: ${pos.value_usd:.2f}")
```

## Utility Methods

```python
# Get current slot
slot = client.get_slot()
print(f"Current slot: {slot}")

# Get epoch info
epoch = client.get_epoch()
print(f"Epoch: {epoch}")

# Get recent blockhash
blockhash = client.get_recent_blockhash()
print(f"Blockhash: {blockhash}")

# Airdrop (devnet only)
sig = client.airdrop("WalletAddress...", lamports=1_000_000_000)
print(f"Airdrop: {sig}")
```

## Context Manager

```python
with SolanaClient(SolanaConfig(api_key="your_key")) as client:
    balance = client.get_balance("WalletAddress...")
# Session automatically closed
```

## Error Handling

```python
from acceso_solana import SolanaClient, SolanaError

try:
    balance = client.get_balance("InvalidAddress")
except SolanaError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status}")
```

## Constants

```python
from acceso_solana.types import (
    SOL_MINT,      # Wrapped SOL mint
    USDC_MINT,     # USDC mint
    USDT_MINT,     # USDT mint
    LAMPORTS_PER_SOL,  # 1_000_000_000
)
```

## Types

```python
from acceso_solana import (
    SolanaConfig,
    Wallet,
    WalletBalance,
    TokenInfo,
    TokenBalance,
    TokenHolding,
    NFT,
    NFTMetadata,
    Collection,
    Transaction,
    TransactionSignature,
    TransferResult,
    StakeAccount,
    Validator,
    StakeResult,
    SwapQuote,
    SwapResult,
    DeFiPosition,
)
```

## License

MIT
