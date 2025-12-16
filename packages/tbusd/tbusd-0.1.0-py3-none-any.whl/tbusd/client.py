"""
TBUSD Client - Gasless transfers via meta-transactions
"""

import requests
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_abi import encode

from .exceptions import (
    TBUSDError,
    RateLimitError,
    InsufficientBalanceError,
    AuthenticationError,
    RelayerError,
)

# Contract addresses on Base mainnet
TBUSD_ADDRESS = "0xA2a61C3E298EB7Ef510757B4eD388C793E1A5b4c"
FORWARDER_ADDRESS = "0x91b67A56A21eB749e19C29FE066C32dF892359D3"
BASE_CHAIN_ID = 8453

# API endpoint
API_BASE = "https://tbusd.io/api"

# EIP-712 domain for MinimalForwarderV2
EIP712_DOMAIN = {
    "name": "MinimalForwarder",
    "version": "0.0.2",
    "chainId": BASE_CHAIN_ID,
    "verifyingContract": FORWARDER_ADDRESS,
}

# EIP-712 types
EIP712_TYPES = {
    "ForwardRequest": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "gas", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "data", "type": "bytes"},
    ]
}


class Client:
    """
    TBUSD Client for gasless transfers.

    Args:
        api_key: Your TBUSD API key (get one at https://tbusd.io/developers)
        private_key: Your wallet's private key (for signing transactions)
        rpc_url: Optional custom RPC URL for balance checks (defaults to public Base RPC)

    Example:
        client = Client(
            api_key="tbusd_abc123...",
            private_key="0x..."
        )
        tx = client.transfer(to="0x...", amount=10.0)
    """

    def __init__(
        self,
        api_key: str,
        private_key: str,
        rpc_url: str = "https://mainnet.base.org",
    ):
        self.api_key = api_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.rpc_url = rpc_url
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def transfer(self, to: str, amount: float) -> dict:
        """
        Send TBUSD to an address (gasless).

        Args:
            to: Recipient address (0x...)
            amount: Amount of TBUSD to send (e.g., 10.5)

        Returns:
            dict with txHash, gasUsed, success

        Raises:
            RateLimitError: If daily limit exceeded
            InsufficientBalanceError: If not enough TBUSD
            TBUSDError: For other errors
        """
        # Convert amount to wei (18 decimals)
        amount_wei = int(amount * 10**18)

        # Get current nonce from relayer
        nonce = self._get_nonce()

        # Encode the transfer call
        transfer_data = self._encode_transfer(to, amount_wei)

        # Build the forward request
        request = {
            "from": self.address,
            "to": TBUSD_ADDRESS,
            "value": 0,
            "gas": 150000,  # Enough for transfer + forwarder overhead
            "nonce": nonce,
            "data": transfer_data,
        }

        # Sign with EIP-712
        signature = self._sign_request(request)

        # Submit to relayer
        response = self._session.post(
            f"{API_BASE}/relay",
            json={
                "request": {
                    "from": request["from"],
                    "to": request["to"],
                    "value": str(request["value"]),
                    "gas": str(request["gas"]),
                    "nonce": str(request["nonce"]),
                    "data": request["data"],
                },
                "signature": signature,
            },
        )

        return self._handle_response(response)

    def balance(self, address: str = None) -> float:
        """
        Get TBUSD balance for an address.

        Args:
            address: Address to check (defaults to your wallet)

        Returns:
            Balance in TBUSD (float)
        """
        if address is None:
            address = self.address

        # Call balanceOf via JSON-RPC
        data = "0x70a08231" + encode(["address"], [address]).hex()

        response = requests.post(
            self.rpc_url,
            json={
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {"to": TBUSD_ADDRESS, "data": data},
                    "latest",
                ],
                "id": 1,
            },
        )

        result = response.json().get("result", "0x0")
        balance_wei = int(result, 16)
        return balance_wei / 10**18

    def usage(self) -> dict:
        """
        Check your API usage and remaining daily limit.

        Returns:
            dict with today's usage, remaining, total_transactions
        """
        response = self._session.get(f"{API_BASE}/usage")
        return self._handle_response(response)

    def health(self) -> bool:
        """
        Check if the relayer is operational.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _get_nonce(self) -> int:
        """Get current nonce for this address from forwarder"""
        response = requests.get(f"{API_BASE}/nonce/{self.address}")
        if response.status_code != 200:
            raise RelayerError(f"Failed to get nonce: {response.text}")
        data = response.json()
        return int(data.get("nonce", 0))

    def _encode_transfer(self, to: str, amount_wei: int) -> str:
        """Encode ERC20 transfer(address,uint256) call"""
        # transfer(address,uint256) selector = 0xa9059cbb
        selector = bytes.fromhex("a9059cbb")
        params = encode(["address", "uint256"], [to, amount_wei])
        return "0x" + (selector + params).hex()

    def _sign_request(self, request: dict) -> str:
        """Sign a forward request using EIP-712"""
        # Convert data to bytes if it's a hex string
        data_bytes = bytes.fromhex(request["data"][2:]) if request["data"].startswith("0x") else bytes.fromhex(request["data"])

        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                **EIP712_TYPES,
            },
            "primaryType": "ForwardRequest",
            "domain": EIP712_DOMAIN,
            "message": {
                "from": request["from"],
                "to": request["to"],
                "value": request["value"],
                "gas": request["gas"],
                "nonce": request["nonce"],
                "data": data_bytes,
            },
        }

        signable = encode_typed_data(full_message=typed_data)
        signed = self.account.sign_message(signable)
        return signed.signature.hex()

    def _handle_response(self, response: requests.Response) -> dict:
        """Handle API response and raise appropriate errors"""
        try:
            data = response.json()
        except Exception:
            raise RelayerError(f"Invalid response: {response.text}")

        if response.status_code == 200:
            return data

        error = data.get("error", "Unknown error")

        if response.status_code == 429:
            raise RateLimitError(error)
        elif response.status_code == 403:
            raise AuthenticationError(error)
        elif response.status_code == 502:
            raise RelayerError(error)
        elif "insufficient" in error.lower() or "balance" in error.lower():
            raise InsufficientBalanceError(error)
        else:
            raise TBUSDError(error)
