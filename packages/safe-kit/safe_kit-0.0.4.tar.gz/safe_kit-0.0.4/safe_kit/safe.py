from typing import cast

from hexbytes import HexBytes

from safe_kit.adapter import EthAdapter
from safe_kit.errors import handle_contract_error
from safe_kit.multisend import MultiSend
from safe_kit.types import SafeTransaction, SafeTransactionData


class Safe:
    """
    The main class for interacting with a Safe.
    """

    def __init__(self, eth_adapter: EthAdapter, safe_address: str):
        self.eth_adapter = eth_adapter
        self.safe_address = safe_address
        self.contract = self.eth_adapter.get_safe_contract(safe_address)

    @classmethod
    def create(cls, eth_adapter: EthAdapter, safe_address: str) -> "Safe":
        """
        Factory method to create a Safe instance.
        """
        return cls(eth_adapter, safe_address)

    def get_address(self) -> str:
        """
        Returns the address of the Safe.
        """
        return self.safe_address

    def get_balance(self) -> int:
        """
        Returns the ETH balance of the Safe.
        """
        return self.eth_adapter.get_balance(self.safe_address)

    def get_nonce(self) -> int:
        """
        Returns the current nonce of the Safe.
        """
        return cast(int, self.contract.functions.nonce().call())

    def get_threshold(self) -> int:
        """
        Returns the threshold of the Safe.
        """
        return cast(int, self.contract.functions.getThreshold().call())

    def get_owners(self) -> list[str]:
        """
        Returns the owners of the Safe.
        """
        return cast(list[str], self.contract.functions.getOwners().call())

    def get_version(self) -> str:
        """
        Returns the version of the Safe contract.
        """
        return cast(str, self.contract.functions.VERSION().call())

    def is_owner(self, address: str) -> bool:
        """
        Checks if an address is an owner of the Safe.
        """
        return cast(bool, self.contract.functions.isOwner(address).call())

    def create_transaction(
        self, transaction_data: SafeTransactionData
    ) -> SafeTransaction:
        """
        Creates a Safe transaction ready to be signed.
        """
        if transaction_data.nonce is None:
            transaction_data.nonce = self.get_nonce()

        return SafeTransaction(data=transaction_data)

    def sign_transaction(
        self, safe_transaction: SafeTransaction, method: str = "eth_sign_typed_data"
    ) -> SafeTransaction:
        """
        Signs a Safe transaction with the current signer.
        Supported methods: "eth_sign_typed_data" (EIP-712), "eth_sign" (legacy).
        """
        signer_address = self.eth_adapter.get_signer_address()
        if not signer_address:
            raise ValueError("No signer configured in the adapter")

        chain_id = self.eth_adapter.get_chain_id()

        if method == "eth_sign_typed_data":
            eip712_data = safe_transaction.data.get_eip712_data(
                chain_id, self.safe_address
            )
            signature = self.eth_adapter.sign_typed_data(eip712_data)
        elif method == "eth_sign":
            tx_hash = self.get_transaction_hash(safe_transaction)
            signature = self.eth_adapter.sign_message(tx_hash)
            # Adjust v for eth_sign: v += 4
            # Signature is r(32) + s(32) + v(1)
            # We need to parse it, adjust v, and reconstruct
            sig_bytes = HexBytes(signature)
            r = sig_bytes[:32]
            s = sig_bytes[32:64]
            v = sig_bytes[64]
            v += 4
            signature = (r + s + bytes([v])).hex()
        else:
            raise ValueError(f"Unsupported signing method: {method}")

        safe_transaction.add_signature(signer_address, signature)
        return safe_transaction

    def get_transaction_hash(self, safe_transaction: SafeTransaction) -> str:
        """
        Returns the hash of the Safe transaction.
        """

        return cast(
            str,
            self.contract.functions.getTransactionHash(
                safe_transaction.data.to,
                safe_transaction.data.value,
                HexBytes(safe_transaction.data.data),
                safe_transaction.data.operation,
                safe_transaction.data.safe_tx_gas,
                safe_transaction.data.base_gas,
                safe_transaction.data.gas_price,
                safe_transaction.data.gas_token,
                safe_transaction.data.refund_receiver,
                safe_transaction.data.nonce,
            )
            .call()
            .hex(),
        )

    def approve_hash(self, hash_to_approve: str) -> str:
        """
        Approves a hash on-chain.
        """
        try:
            tx_hash = self.contract.functions.approveHash(
                HexBytes(hash_to_approve)
            ).transact({"from": self.eth_adapter.get_signer_address()})
            return cast(str, tx_hash.hex())
        except Exception as e:
            raise handle_contract_error(e) from e

    def execute_transaction(self, safe_transaction: SafeTransaction) -> str:
        """
        Executes a Safe transaction.
        """
        # Sort signatures
        sorted_signatures = safe_transaction.sorted_signatures_bytes

        try:
            tx_hash = self.contract.functions.execTransaction(
                safe_transaction.data.to,
                safe_transaction.data.value,
                HexBytes(safe_transaction.data.data),
                safe_transaction.data.operation,
                safe_transaction.data.safe_tx_gas,
                safe_transaction.data.base_gas,
                safe_transaction.data.gas_price,
                safe_transaction.data.gas_token,
                safe_transaction.data.refund_receiver,
                sorted_signatures,
            ).transact({"from": self.eth_adapter.get_signer_address()})

            return cast(str, tx_hash.hex())
        except Exception as e:
            raise handle_contract_error(e) from e

    def _get_previous_owner(self, owner: str) -> str:
        owners = self.get_owners()
        try:
            index = owners.index(owner)
        except ValueError:
            raise ValueError(f"Address {owner} is not an owner") from None

        if index == 0:
            return "0x0000000000000000000000000000000000000001"  # Sentinel
        return owners[index - 1]

    def create_add_owner_transaction(
        self, owner: str, threshold: int | None = None
    ) -> SafeTransaction:
        """
        Creates a transaction to add a new owner to the Safe.
        """
        if threshold is None:
            threshold = self.get_threshold()

        data = self.contract.encodeABI(
            fn_name="addOwnerWithThreshold", args=[owner, threshold]
        )

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def create_remove_owner_transaction(
        self, owner: str, threshold: int | None = None
    ) -> SafeTransaction:
        """
        Creates a transaction to remove an owner from the Safe.
        """
        if threshold is None:
            threshold = self.get_threshold()

        prev_owner = self._get_previous_owner(owner)

        data = self.contract.encodeABI(
            fn_name="removeOwner", args=[prev_owner, owner, threshold]
        )

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def create_swap_owner_transaction(
        self, old_owner: str, new_owner: str
    ) -> SafeTransaction:
        """
        Creates a transaction to replace an existing owner with a new one.
        """
        prev_owner = self._get_previous_owner(old_owner)

        data = self.contract.encodeABI(
            fn_name="swapOwner", args=[prev_owner, old_owner, new_owner]
        )

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def create_change_threshold_transaction(self, threshold: int) -> SafeTransaction:
        """
        Creates a transaction to change the threshold of the Safe.
        """
        data = self.contract.encodeABI(fn_name="changeThreshold", args=[threshold])

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def get_modules(self) -> list[str]:
        """
        Returns the modules enabled on the Safe.
        """
        # Sentinel address for modules
        start = "0x0000000000000000000000000000000000000001"
        page_size = 10
        modules = []

        while True:
            array, next_module = self.contract.functions.getModulesPaginated(
                start, page_size
            ).call()
            modules.extend(array)

            if (
                next_module == "0x0000000000000000000000000000000000000001"
                or next_module == "0x0000000000000000000000000000000000000000"
            ):
                break
            start = next_module

        return modules

    def is_module_enabled(self, module_address: str) -> bool:
        """
        Checks if a module is enabled on the Safe.
        """
        return cast(
            bool, self.contract.functions.isModuleEnabled(module_address).call()
        )

    def create_enable_module_transaction(self, module_address: str) -> SafeTransaction:
        """
        Creates a transaction to enable a Safe module.
        """
        data = self.contract.encodeABI(fn_name="enableModule", args=[module_address])

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def create_disable_module_transaction(self, module_address: str) -> SafeTransaction:
        """
        Creates a transaction to disable a Safe module.
        """
        modules = self.get_modules()
        try:
            index = modules.index(module_address)
        except ValueError:
            raise ValueError(f"Module {module_address} is not enabled") from None

        if index == 0:
            prev_module = "0x0000000000000000000000000000000000000001"
        else:
            prev_module = modules[index - 1]

        data = self.contract.encodeABI(
            fn_name="disableModule", args=[prev_module, module_address]
        )

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def create_erc20_transfer_transaction(
        self, token_address: str, to: str, amount: int
    ) -> SafeTransaction:
        """
        Creates a transaction to transfer ERC20 tokens.
        """
        from safe_kit.abis import ERC20_ABI

        token_contract = self.eth_adapter.get_contract(token_address, ERC20_ABI)

        data = token_contract.encodeABI(fn_name="transfer", args=[to, amount])

        return self.create_transaction(
            SafeTransactionData(to=token_address, value=0, data=data, operation=0)
        )

    def create_erc721_transfer_transaction(
        self, token_address: str, to: str, token_id: int
    ) -> SafeTransaction:
        """
        Creates a transaction to transfer ERC721 tokens.
        """
        from safe_kit.abis import ERC721_ABI

        token_contract = self.eth_adapter.get_contract(token_address, ERC721_ABI)

        data = token_contract.encodeABI(
            fn_name="safeTransferFrom", args=[self.safe_address, to, token_id]
        )

        return self.create_transaction(
            SafeTransactionData(to=token_address, value=0, data=data, operation=0)
        )

    def create_native_transfer_transaction(
        self, to: str, amount: int
    ) -> SafeTransaction:
        """
        Creates a transaction to transfer native tokens (ETH).
        """
        return self.create_transaction(
            SafeTransactionData(to=to, value=amount, data="0x", operation=0)
        )

    def create_rejection_transaction(self, nonce: int) -> SafeTransaction:
        """
        Creates a transaction to reject a pending transaction (by reusing the nonce).
        """
        return self.create_transaction(
            SafeTransactionData(
                to=self.safe_address, value=0, data="0x", operation=0, nonce=nonce
            )
        )

    def create_multi_send_transaction(
        self, transactions: list[SafeTransactionData], multi_send_address: str
    ) -> SafeTransaction:
        """
        Creates a MultiSend transaction.
        """
        from safe_kit.abis import MULTI_SEND_ABI

        encoded_txs = MultiSend.encode_transactions(transactions)

        multi_send_contract = self.eth_adapter.get_contract(
            multi_send_address, MULTI_SEND_ABI
        )

        data = multi_send_contract.encodeABI(fn_name="multiSend", args=[encoded_txs])

        # MultiSend transactions are DelegateCalls (operation=1)
        # to the MultiSend contract
        return self.create_transaction(
            SafeTransactionData(
                to=multi_send_address,
                value=0,
                data=data,
                operation=1,  # DelegateCall
            )
        )

    def estimate_transaction_gas(self, safe_transaction: SafeTransaction) -> int:
        """
        Estimates the gas required for a Safe transaction.
        """
        return cast(
            int,
            self.contract.functions.requiredTxGas(
                safe_transaction.data.to,
                safe_transaction.data.value,
                HexBytes(safe_transaction.data.data),
                safe_transaction.data.operation,
                safe_transaction.data.safe_tx_gas,
                safe_transaction.data.base_gas,
                safe_transaction.data.gas_price,
                safe_transaction.data.gas_token,
                safe_transaction.data.refund_receiver,
                safe_transaction.sorted_signatures_bytes,
            ).call(),
        )

    def check_signatures(self, safe_transaction: SafeTransaction) -> None:
        """
        Checks if the signatures on the transaction are valid.
        Raises an error if signatures are invalid.
        """
        tx_hash = self.get_transaction_hash(safe_transaction)
        # Convert hex string hash to bytes
        tx_hash_bytes = HexBytes(tx_hash)

        self.contract.functions.checkSignatures(
            tx_hash_bytes,
            HexBytes(safe_transaction.data.data),
            safe_transaction.sorted_signatures_bytes,
        ).call()

    def get_guard(self) -> str:
        """
        Returns the guard address of the Safe.
        """
        # keccak256("guard_manager.guard.address")
        slot = 0x4A204F620C8C5CCDCA3FD54D003B6D13435454A733A569F8E4A6426EA62BF7A0
        data = self.eth_adapter.get_storage_at(self.safe_address, slot)
        # Convert bytes to address (last 20 bytes)
        return "0x" + data.hex()[-40:]

    def create_set_guard_transaction(self, guard_address: str) -> SafeTransaction:
        """
        Creates a transaction to set the guard of the Safe.
        """
        data = self.contract.encodeABI(fn_name="setGuard", args=[guard_address])

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )

    def get_fallback_handler(self) -> str:
        """
        Returns the fallback handler address of the Safe.
        """
        # keccak256("fallback_manager.handler.address")
        slot = 0x6C9A6C4A39284E37ED1CF53D337577D14212A4870FB976A4366C693B939918D5
        data = self.eth_adapter.get_storage_at(self.safe_address, slot)
        return "0x" + data.hex()[-40:]

    def create_set_fallback_handler_transaction(
        self, handler_address: str
    ) -> SafeTransaction:
        """
        Creates a transaction to set the fallback handler of the Safe.
        """
        data = self.contract.encodeABI(
            fn_name="setFallbackHandler", args=[handler_address]
        )

        return self.create_transaction(
            SafeTransactionData(to=self.safe_address, value=0, data=data, operation=0)
        )
