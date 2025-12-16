"""
TBUSD Python SDK - Gasless transfers on Base L2

Example:
    from tbusd import Client

    client = Client(
        api_key="tbusd_your_api_key",
        private_key="0x..."  # Your wallet private key
    )

    # Send TBUSD (no gas needed!)
    tx = client.transfer(to="0x...", amount=10.0)
    print(f"Sent! TX: {tx['txHash']}")

    # Check balance
    balance = client.balance()
    print(f"Balance: {balance} TBUSD")
"""

from .client import Client
from .exceptions import TBUSDError, RateLimitError, InsufficientBalanceError

__version__ = "0.1.0"
__all__ = ["Client", "TBUSDError", "RateLimitError", "InsufficientBalanceError"]
