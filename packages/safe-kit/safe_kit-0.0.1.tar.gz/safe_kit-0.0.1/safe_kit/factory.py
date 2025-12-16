from hexbytes import HexBytes
from safe_kit.adapter import EthAdapter
from safe_kit.safe import Safe
from safe_kit.types import SafeAccountConfig
from safe_kit.abis import SAFE_PROXY_FACTORY_ABI
from safe_kit.errors import handle_contract_error

class SafeFactory:
    """
    Factory class to deploy new Safe contracts.
    """

    def __init__(
        self, 
        eth_adapter: EthAdapter, 
        safe_singleton_address: str,
        safe_proxy_factory_address: str
    ):
        self.eth_adapter = eth_adapter
        self.safe_singleton_address = safe_singleton_address
        self.safe_proxy_factory_address = safe_proxy_factory_address
        self.proxy_factory_contract = self.eth_adapter.get_contract(
            address=safe_proxy_factory_address, 
            abi=SAFE_PROXY_FACTORY_ABI
        )

    def _get_initializer_data(self, config: SafeAccountConfig) -> bytes:
        safe_singleton = self.eth_adapter.get_safe_contract(self.safe_singleton_address)
        return safe_singleton.encodeABI(
            fn_name="setup",
            args=[
                config.owners,
                config.threshold,
                config.to,
                HexBytes(config.data),
                config.fallback_handler,
                config.payment_token,
                config.payment,
                config.payment_receiver
            ]
        )

    def predict_safe_address(self, config: SafeAccountConfig, salt_nonce: int = 0) -> str:
        """
        Predicts the address of the Safe that would be deployed with the given configuration.
        """
        initializer = self._get_initializer_data(config)
        return self.proxy_factory_contract.functions.createProxyWithNonce(
            self.safe_singleton_address,
            initializer,
            salt_nonce
        ).call()

    def deploy_safe(self, config: SafeAccountConfig, salt_nonce: int = 0) -> Safe:
        """
        Deploys a new Safe contract.
        Returns a Safe instance with the predicted address.
        """
        signer = self.eth_adapter.get_signer_address()
        if not signer:
            raise ValueError("No signer configured in the adapter")

        initializer = self._get_initializer_data(config)
        
        try:
            self.proxy_factory_contract.functions.createProxyWithNonce(
                self.safe_singleton_address,
                initializer,
                salt_nonce
            ).transact({"from": signer})
        except Exception as e:
            raise handle_contract_error(e)
        
        safe_address = self.predict_safe_address(config, salt_nonce)
        return Safe(self.eth_adapter, safe_address)
