from abc import ABC, abstractmethod
from typing import Any, Optional
from web3 import Web3
from eth_account.signers.local import LocalAccount

class EthAdapter(ABC):
    """
    Abstract base class for Ethereum adapters.
    """
    
    @abstractmethod
    def get_balance(self, address: str) -> int:
        pass

    @abstractmethod
    def get_chain_id(self) -> int:
        pass

    @abstractmethod
    def get_safe_contract(self, safe_address: str) -> Any:
        pass

    @abstractmethod
    def get_contract(self, address: str, abi: list[Any]) -> Any:
        pass

    @abstractmethod
    def get_signer_address(self) -> Optional[str]:


        pass

    @abstractmethod
    def sign_message(self, message: str) -> str:
        pass

    @abstractmethod
    def sign_typed_data(self, data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_storage_at(self, address: str, position: int) -> bytes:
        pass

class Web3Adapter(EthAdapter):
    """
    Web3.py implementation of the EthAdapter.
    """
    def __init__(self, web3: Web3, signer: Optional[LocalAccount] = None):
        self.web3 = web3
        self.signer = signer

    def get_balance(self, address: str) -> int:
        return self.web3.eth.get_balance(address)

    def get_chain_id(self) -> int:
        return self.web3.eth.chain_id

    def get_safe_contract(self, safe_address: str) -> Any:
        from safe_kit.abis import SAFE_ABI
        return self.web3.eth.contract(address=safe_address, abi=SAFE_ABI)

    def get_contract(self, address: str, abi: list[Any]) -> Any:
        return self.web3.eth.contract(address=address, abi=abi)

    def get_signer_address(self) -> Optional[str]:


        if self.signer:
            return self.signer.address
        return None

    def sign_message(self, message: str) -> str:
        if not self.signer:
            raise ValueError("No signer available")
        # This is a simplified signing for demonstration
        from eth_account.messages import encode_defunct
        signable_message = encode_defunct(text=message)
        signed_message = self.signer.sign_message(signable_message)
        return signed_message.signature.hex()

    def sign_typed_data(self, data: dict[str, Any]) -> str:
        if not self.signer:
            raise ValueError("No signer available")
        from eth_account.messages import encode_structured_data
        
        signable_message = encode_structured_data(primitive=data)
        signed_message = self.signer.sign_message(signable_message)
        return signed_message.signature.hex()

    def get_storage_at(self, address: str, position: int) -> bytes:
        return self.web3.eth.get_storage_at(address, position)


