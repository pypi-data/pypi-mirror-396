from typing import Any

import requests

from safe_kit.errors import SafeServiceError
from safe_kit.types import (
    SafeMultisigTransactionResponse,
    SafeServiceInfo,
    SafeTransactionData,
)


class SafeServiceClient:
    """
    Client for interacting with the Safe Transaction Service API.
    """

    def __init__(self, service_url: str):
        self.service_url = service_url.rstrip("/")

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            if response.content:
                return response.json()
            return None
        except requests.HTTPError as e:
            raise SafeServiceError(f"Service error: {e}", response.status_code) from e
        except Exception as e:
            raise SafeServiceError(f"Unexpected error: {e}") from e

    def get_service_info(self) -> SafeServiceInfo:
        """
        Returns information about the Safe Transaction Service.
        """
        response = requests.get(f"{self.service_url}/v1/about/")
        data = self._handle_response(response)
        return SafeServiceInfo(**data)

    def propose_transaction(
        self,
        safe_address: str,
        safe_tx_data: SafeTransactionData,
        safe_tx_hash: str,
        sender_address: str,
        signature: str,
        origin: str | None = None,
    ) -> None:
        """
        Proposes a transaction to the Safe Transaction Service.
        """
        url = f"{self.service_url}/v1/safes/{safe_address}/multisig-transactions/"
        
        payload = {
            "to": safe_tx_data.to,
            "value": safe_tx_data.value,
            "data": safe_tx_data.data if safe_tx_data.data else None,
            "operation": safe_tx_data.operation,
            "safeTxGas": safe_tx_data.safe_tx_gas,
            "baseGas": safe_tx_data.base_gas,
            "gasPrice": safe_tx_data.gas_price,
            "gasToken": safe_tx_data.gas_token,
            "refundReceiver": safe_tx_data.refund_receiver,
            "nonce": safe_tx_data.nonce,
            "contractTransactionHash": safe_tx_hash,
            "sender": sender_address,
            "signature": signature,
            "origin": origin,
        }
        
        response = requests.post(url, json=payload)
        self._handle_response(response)

    def get_pending_transactions(
        self, safe_address: str, current_nonce: int | None = None
    ) -> list[SafeMultisigTransactionResponse]:
        """
        Returns the list of pending transactions for a Safe.
        """
        url = f"{self.service_url}/v1/safes/{safe_address}/multisig-transactions/"
        params = {"executed": "false", "trusted": "true"}
        if current_nonce is not None:
            params["nonce__gte"] = str(current_nonce)
            
        response = requests.get(url, params=params)
        data = self._handle_response(response)
        results = data.get("results", [])
        return [SafeMultisigTransactionResponse(**tx) for tx in results]

    def confirm_transaction(self, safe_tx_hash: str, signature: str) -> None:
        """
        Adds a confirmation (signature) to a pending transaction.
        """
        url = (
            f"{self.service_url}/v1/multisig-transactions/{safe_tx_hash}/confirmations/"
        )
        payload = {"signature": signature}
        
        response = requests.post(url, json=payload)
        self._handle_response(response)
