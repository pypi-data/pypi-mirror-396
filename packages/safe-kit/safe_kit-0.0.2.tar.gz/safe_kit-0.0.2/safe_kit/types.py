from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SafeAccountConfig(BaseModel):
    """
    Configuration for deploying a new Safe.
    """

    owners: list[str]
    threshold: int
    to: str = "0x0000000000000000000000000000000000000000"
    data: str = "0x"
    fallback_handler: str = "0x0000000000000000000000000000000000000000"
    payment_token: str = "0x0000000000000000000000000000000000000000"
    payment: int = 0
    payment_receiver: str = "0x0000000000000000000000000000000000000000"


class SafeTransactionData(BaseModel):
    """
    Model representing the data of a Safe transaction.
    """

    to: str
    value: int
    data: str
    operation: int = 0
    safe_tx_gas: int = 0
    base_gas: int = 0
    gas_price: int = 0
    gas_token: str = "0x0000000000000000000000000000000000000000"
    refund_receiver: str = "0x0000000000000000000000000000000000000000"
    nonce: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_eip712_data(self, chain_id: int, safe_address: str) -> dict[str, Any]:
        from hexbytes import HexBytes

        return {
            "types": {
                "EIP712Domain": [
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "SafeTx": [
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "data", "type": "bytes"},
                    {"name": "operation", "type": "uint8"},
                    {"name": "safeTxGas", "type": "uint256"},
                    {"name": "baseGas", "type": "uint256"},
                    {"name": "gasPrice", "type": "uint256"},
                    {"name": "gasToken", "type": "address"},
                    {"name": "refundReceiver", "type": "address"},
                    {"name": "nonce", "type": "uint256"},
                ],
            },
            "primaryType": "SafeTx",
            "domain": {
                "chainId": chain_id,
                "verifyingContract": safe_address,
            },
            "message": {
                "to": self.to,
                "value": self.value,
                "data": HexBytes(self.data),
                "operation": self.operation,
                "safeTxGas": self.safe_tx_gas,
                "baseGas": self.base_gas,
                "gasPrice": self.gas_price,
                "gasToken": self.gas_token,
                "refundReceiver": self.refund_receiver,
                "nonce": self.nonce if self.nonce is not None else 0,
            },
        }


class SafeTransaction(BaseModel):
    """
    Model representing a complete Safe transaction including signatures.
    """

    data: SafeTransactionData
    signatures: dict[str, str] = Field(default_factory=dict)

    def add_signature(self, owner: str, signature: str) -> None:
        self.signatures[owner] = signature

    @property
    def sorted_signatures_bytes(self) -> bytes:
        from hexbytes import HexBytes

        # Sort by owner address
        sorted_owners = sorted(self.signatures.keys(), key=lambda x: int(x, 16))
        signature_bytes = b""
        for owner in sorted_owners:
            signature_bytes += HexBytes(self.signatures[owner])
        return signature_bytes
