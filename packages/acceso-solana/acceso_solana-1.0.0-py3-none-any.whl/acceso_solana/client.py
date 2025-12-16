"""
Solana API Client
"""

import logging
from typing import Any, Dict, List, Optional, Union

import requests

from .types import (
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


class SolanaError(Exception):
    """Exception raised for Solana API errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class SolanaClient:
    """
    Comprehensive Solana client via Acceso API.
    
    Features:
    - Wallet operations (balance, tokens, NFTs)
    - Token transfers and info
    - NFT minting and transfers
    - Staking and delegation
    - Token swaps via Jupiter
    - Transaction history
    - DeFi positions
    
    Example:
        >>> from acceso_solana import SolanaClient, SolanaConfig
        >>> 
        >>> client = SolanaClient(SolanaConfig(api_key="your_key"))
        >>> 
        >>> # Get wallet balance
        >>> balance = client.get_balance("YourWallet...")
        >>> print(f"Balance: {balance.sol} SOL")
    """
    
    def __init__(self, config: Union[SolanaConfig, Dict[str, Any]]):
        if isinstance(config, dict):
            config = SolanaConfig(**config)
        
        self.config = config
        self.api_url = config.api_url.rstrip("/")
        self.timeout = config.timeout
        self.debug = config.debug
        
        self.logger = logging.getLogger("acceso_solana")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
        })
    
    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Any:
        url = f"{self.api_url}{path}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                params=params,
                timeout=self.timeout,
            )
            
            data = response.json()
            
            if not response.ok:
                raise SolanaError(
                    data.get("error", f"HTTP {response.status_code}"),
                    status=response.status_code,
                )
            
            return data.get("data", data)
            
        except requests.Timeout:
            raise SolanaError("Request timeout", code="TIMEOUT")
        except requests.RequestException as e:
            raise SolanaError(f"Network error: {e}", code="NETWORK_ERROR")
    
    # ========================================
    # Wallet Operations
    # ========================================
    
    def get_balance(self, address: str) -> WalletBalance:
        """
        Get SOL balance for a wallet.
        
        Args:
            address: Wallet public key
        
        Returns:
            WalletBalance with lamports and SOL amount
        """
        data = self._request("GET", f"/v1/solana/balance/{address}")
        return WalletBalance.from_dict(data)
    
    def get_wallet(self, address: str) -> Wallet:
        """
        Get full wallet info.
        
        Args:
            address: Wallet public key
        
        Returns:
            Wallet with balance and metadata
        """
        data = self._request("GET", f"/v1/solana/wallet/{address}")
        return Wallet.from_dict(data)
    
    # ========================================
    # Token Operations
    # ========================================
    
    def get_token_info(self, mint: str) -> TokenInfo:
        """
        Get token metadata.
        
        Args:
            mint: Token mint address
        
        Returns:
            TokenInfo with name, symbol, decimals
        """
        data = self._request("GET", f"/v1/solana/token/{mint}")
        return TokenInfo.from_dict(data)
    
    def get_token_balance(self, wallet: str, mint: str) -> TokenBalance:
        """
        Get specific token balance for a wallet.
        
        Args:
            wallet: Wallet public key
            mint: Token mint address
        
        Returns:
            TokenBalance
        """
        data = self._request("GET", f"/v1/solana/token-balance/{wallet}/{mint}")
        return TokenBalance.from_dict(data)
    
    def get_token_holdings(self, wallet: str) -> List[TokenHolding]:
        """
        Get all token holdings for a wallet.
        
        Args:
            wallet: Wallet public key
        
        Returns:
            List of TokenHolding
        """
        data = self._request("GET", f"/v1/solana/tokens/{wallet}")
        return [TokenHolding.from_dict(t) for t in data]
    
    def transfer_token(
        self,
        from_keypair: str,
        to_address: str,
        mint: str,
        amount: str,
    ) -> TransferResult:
        """
        Transfer SPL tokens.
        
        Args:
            from_keypair: Sender's keypair (base58)
            to_address: Recipient address
            mint: Token mint address
            amount: Amount in base units
        
        Returns:
            TransferResult with signature
        """
        data = self._request("POST", "/v1/solana/transfer-token", {
            "from_keypair": from_keypair,
            "to": to_address,
            "mint": mint,
            "amount": amount,
        })
        return TransferResult.from_dict(data)
    
    def transfer_sol(
        self,
        from_keypair: str,
        to_address: str,
        lamports: int,
    ) -> TransferResult:
        """
        Transfer SOL.
        
        Args:
            from_keypair: Sender's keypair (base58)
            to_address: Recipient address
            lamports: Amount in lamports
        
        Returns:
            TransferResult with signature
        """
        data = self._request("POST", "/v1/solana/transfer", {
            "from_keypair": from_keypair,
            "to": to_address,
            "lamports": lamports,
        })
        return TransferResult.from_dict(data)
    
    # ========================================
    # NFT Operations
    # ========================================
    
    def get_nft(self, mint: str) -> NFT:
        """
        Get NFT details.
        
        Args:
            mint: NFT mint address
        
        Returns:
            NFT with metadata
        """
        data = self._request("GET", f"/v1/solana/nft/{mint}")
        return NFT.from_dict(data)
    
    def get_nfts(self, wallet: str) -> List[NFT]:
        """
        Get all NFTs owned by a wallet.
        
        Args:
            wallet: Wallet public key
        
        Returns:
            List of NFT
        """
        data = self._request("GET", f"/v1/solana/nfts/{wallet}")
        return [NFT.from_dict(n) for n in data]
    
    def get_collection(self, address: str) -> Collection:
        """
        Get NFT collection info.
        
        Args:
            address: Collection address
        
        Returns:
            Collection info
        """
        data = self._request("GET", f"/v1/solana/collection/{address}")
        return Collection.from_dict(data)
    
    def mint_nft(
        self,
        payer_keypair: str,
        name: str,
        symbol: str,
        uri: str,
        collection: Optional[str] = None,
    ) -> NFT:
        """
        Mint a new NFT.
        
        Args:
            payer_keypair: Payer's keypair (base58)
            name: NFT name
            symbol: NFT symbol
            uri: Metadata URI
            collection: Optional collection address
        
        Returns:
            Minted NFT
        """
        body = {
            "payer_keypair": payer_keypair,
            "name": name,
            "symbol": symbol,
            "uri": uri,
        }
        if collection:
            body["collection"] = collection
        
        data = self._request("POST", "/v1/solana/mint-nft", body)
        return NFT.from_dict(data)
    
    def transfer_nft(
        self,
        from_keypair: str,
        to_address: str,
        mint: str,
    ) -> TransferResult:
        """
        Transfer an NFT.
        
        Args:
            from_keypair: Sender's keypair (base58)
            to_address: Recipient address
            mint: NFT mint address
        
        Returns:
            TransferResult with signature
        """
        data = self._request("POST", "/v1/solana/transfer-nft", {
            "from_keypair": from_keypair,
            "to": to_address,
            "mint": mint,
        })
        return TransferResult.from_dict(data)
    
    # ========================================
    # Transaction Operations
    # ========================================
    
    def get_transaction(self, signature: str) -> Transaction:
        """
        Get transaction details.
        
        Args:
            signature: Transaction signature
        
        Returns:
            Transaction details
        """
        data = self._request("GET", f"/v1/solana/transaction/{signature}")
        return Transaction.from_dict(data)
    
    def get_transactions(
        self,
        wallet: str,
        limit: int = 20,
        before: Optional[str] = None,
    ) -> List[TransactionSignature]:
        """
        Get transaction history for a wallet.
        
        Args:
            wallet: Wallet public key
            limit: Max number of transactions
            before: Signature to start before
        
        Returns:
            List of TransactionSignature
        """
        params = {"limit": limit}
        if before:
            params["before"] = before
        
        data = self._request("GET", f"/v1/solana/transactions/{wallet}", params=params)
        return [TransactionSignature.from_dict(t) for t in data]
    
    # ========================================
    # Staking Operations
    # ========================================
    
    def get_stake_accounts(self, wallet: str) -> List[StakeAccount]:
        """
        Get all stake accounts for a wallet.
        
        Args:
            wallet: Wallet public key
        
        Returns:
            List of StakeAccount
        """
        data = self._request("GET", f"/v1/solana/stake-accounts/{wallet}")
        return [StakeAccount.from_dict(s) for s in data]
    
    def get_validators(
        self,
        limit: int = 100,
        sort_by: str = "stake",
    ) -> List[Validator]:
        """
        Get list of validators.
        
        Args:
            limit: Max number of validators
            sort_by: Sort field (stake, apy, commission)
        
        Returns:
            List of Validator
        """
        data = self._request("GET", "/v1/solana/validators", params={
            "limit": limit,
            "sort_by": sort_by,
        })
        return [Validator.from_dict(v) for v in data]
    
    def stake(
        self,
        staker_keypair: str,
        validator: str,
        lamports: int,
    ) -> StakeResult:
        """
        Create a stake delegation.
        
        Args:
            staker_keypair: Staker's keypair (base58)
            validator: Validator vote account
            lamports: Amount to stake
        
        Returns:
            StakeResult with stake account
        """
        data = self._request("POST", "/v1/solana/stake", {
            "staker_keypair": staker_keypair,
            "validator": validator,
            "lamports": lamports,
        })
        return StakeResult.from_dict(data)
    
    def unstake(
        self,
        staker_keypair: str,
        stake_account: str,
    ) -> TransferResult:
        """
        Deactivate a stake account.
        
        Args:
            staker_keypair: Staker's keypair (base58)
            stake_account: Stake account address
        
        Returns:
            TransferResult with signature
        """
        data = self._request("POST", "/v1/solana/unstake", {
            "staker_keypair": staker_keypair,
            "stake_account": stake_account,
        })
        return TransferResult.from_dict(data)
    
    def withdraw_stake(
        self,
        staker_keypair: str,
        stake_account: str,
        lamports: Optional[int] = None,
    ) -> TransferResult:
        """
        Withdraw from a deactivated stake account.
        
        Args:
            staker_keypair: Staker's keypair (base58)
            stake_account: Stake account address
            lamports: Amount to withdraw (all if None)
        
        Returns:
            TransferResult with signature
        """
        body = {
            "staker_keypair": staker_keypair,
            "stake_account": stake_account,
        }
        if lamports:
            body["lamports"] = lamports
        
        data = self._request("POST", "/v1/solana/withdraw-stake", body)
        return TransferResult.from_dict(data)
    
    # ========================================
    # Swap Operations (Jupiter)
    # ========================================
    
    def get_swap_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: str,
        slippage_bps: int = 50,
    ) -> SwapQuote:
        """
        Get a swap quote from Jupiter.
        
        Args:
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap (in base units)
            slippage_bps: Slippage tolerance in basis points
        
        Returns:
            SwapQuote with output amount and route
        """
        data = self._request("POST", "/v1/solana/swap/quote", {
            "input_mint": input_mint,
            "output_mint": output_mint,
            "amount": amount,
            "slippage_bps": slippage_bps,
        })
        return SwapQuote.from_dict(data)
    
    def execute_swap(
        self,
        user_keypair: str,
        input_mint: str,
        output_mint: str,
        amount: str,
        slippage_bps: int = 50,
    ) -> SwapResult:
        """
        Execute a token swap via Jupiter.
        
        Args:
            user_keypair: User's keypair (base58)
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap (in base units)
            slippage_bps: Slippage tolerance in basis points
        
        Returns:
            SwapResult with signature and amounts
        """
        data = self._request("POST", "/v1/solana/swap", {
            "user_keypair": user_keypair,
            "input_mint": input_mint,
            "output_mint": output_mint,
            "amount": amount,
            "slippage_bps": slippage_bps,
        })
        return SwapResult.from_dict(data)
    
    # ========================================
    # DeFi Operations
    # ========================================
    
    def get_defi_positions(self, wallet: str) -> List[DeFiPosition]:
        """
        Get DeFi positions for a wallet.
        
        Args:
            wallet: Wallet public key
        
        Returns:
            List of DeFiPosition across protocols
        """
        data = self._request("GET", f"/v1/solana/defi/{wallet}")
        return [DeFiPosition.from_dict(p) for p in data]
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def get_recent_blockhash(self) -> str:
        """Get recent blockhash for transactions."""
        data = self._request("GET", "/v1/solana/blockhash")
        return data.get("blockhash", "")
    
    def get_slot(self) -> int:
        """Get current slot."""
        data = self._request("GET", "/v1/solana/slot")
        return data.get("slot", 0)
    
    def get_epoch(self) -> Dict[str, Any]:
        """Get current epoch info."""
        return self._request("GET", "/v1/solana/epoch")
    
    def airdrop(self, address: str, lamports: int = 1_000_000_000) -> str:
        """
        Request SOL airdrop (devnet only).
        
        Args:
            address: Wallet address
            lamports: Amount to airdrop
        
        Returns:
            Transaction signature
        """
        data = self._request("POST", "/v1/solana/airdrop", {
            "address": address,
            "lamports": lamports,
        })
        return data.get("signature", "")
    
    def close(self) -> None:
        """Close the client session."""
        self._session.close()
    
    def __enter__(self) -> "SolanaClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
