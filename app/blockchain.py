# app/blockchain.py
import json
from web3 import Web3
import config
from app.keystore import load_private_key
from pathlib import Path

# Ruta y carga de ABI del contrato
BASE = Path(__file__).parent.parent  # 'FotosBlockchain'
ABI_FILE = BASE / "Contract" / "build" / "contracts" / "Notarizacion.json"
w3 = Web3(Web3.HTTPProvider(config.ETH_NODE_URL))
with open(ABI_FILE, 'r') as f:
    data = json.load(f)
    CONTRACT_ABI = data['abi']  # extrae únicamente la lista ABI

contract = w3.eth.contract(address=config.CONTRACT_ADDRESS, abi=CONTRACT_ABI)



def get_gas_price() -> int:
    """Obtiene el precio de gas actual en Gwei."""
    return w3.eth.gas_price // 10**9


def build_transaction(hash_bytes: bytes, signature: bytes, public_key) -> dict:
    """Prepara la transacción que invoca notarizar(bytes32 hash)."""
    # Cargar clave privada y obtener bytes
    private_key = load_private_key()
    priv_int = private_key.private_numbers().private_value
    private_key_bytes = priv_int.to_bytes(32, byteorder='big')

    # Crear cuenta desde la clave privada
    account = w3.eth.account.from_key(private_key_bytes)

    # Construir la transacción
    tx = contract.functions.notarizar(hash_bytes).buildTransaction({
        'chainId': config.CHAIN_ID,
        'gas': config.GAS_LIMIT,
        'gasPrice': w3.toWei(config.GAS_PRICE_GWEI, 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address)
    })
    # Firmar la transacción
    signed_tx = account.sign_transaction(tx)
    return signed_tx


def send_transaction(signed_tx) -> str:
    """Envía la transacción y devuelve el hash."""
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()


def wait_for_confirmation(tx_hash: str, timeout=120) -> bool:
    """Espera la confirmación de la transacción."""
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    return receipt.status == 1