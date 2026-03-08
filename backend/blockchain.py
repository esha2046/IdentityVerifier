"""
Blockchain integration — Polygon Amoy testnet
Stores verification hashes on-chain for immutability.

Contract: 0xE18d86C6Ab641b175c1cf3a1e458d0e437d617A1
Network:  Polygon Amoy (Chain ID: 80002)
"""

import hashlib
from web3 import Web3
from config import CONTRACT_ADDRESS, WALLET_ADDRESS, WALLET_PRIVATE_KEY, AMOY_RPC_URL

# ── ABI — only the functions we need ──────────────────────────────────────────
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "verificationId", "type": "uint256"},
            {"internalType": "bytes32",  "name": "hash",           "type": "bytes32"}
        ],
        "name": "storeVerification",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "verificationId", "type": "uint256"}
        ],
        "name": "getVerification",
        "outputs": [
            {"internalType": "bytes32", "name": "hash",      "type": "bytes32"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "verificationId", "type": "uint256"},
            {"internalType": "bytes32",  "name": "hash",           "type": "bytes32"}
        ],
        "name": "verifyHash",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalVerifications",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "internalType": "uint256", "name": "verificationId", "type": "uint256"},
            {"indexed": False, "internalType": "bytes32",  "name": "hash",           "type": "bytes32"},
            {"indexed": False, "internalType": "uint256",  "name": "timestamp",      "type": "uint256"}
        ],
        "name": "VerificationStored",
        "type": "event"
    }
]


# ── Web3 connection ────────────────────────────────────────────────────────────

def get_web3():
    """Connect to Polygon Amoy RPC"""
    w3 = Web3(Web3.HTTPProvider(AMOY_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Could not connect to Amoy RPC: {AMOY_RPC_URL}")
    return w3


def get_contract(w3):
    """Get contract instance"""
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )


# ── Hash builder ───────────────────────────────────────────────────────────────

def build_verification_hash(verification_id: int, anchor_id: int, platform: str, profile_url: str) -> bytes:
    """
    Build a deterministic bytes32 hash for a verification record.
    Same inputs always produce the same hash — useful for later verification.
    """
    raw = f"{verification_id}:{anchor_id}:{platform}:{profile_url}"
    return hashlib.sha256(raw.encode()).digest()  # 32 bytes


# ── Main functions ─────────────────────────────────────────────────────────────

def store_verification_on_chain(verification_id: int, anchor_id: int, platform: str, profile_url: str) -> dict:
    """
    Store a verification hash on the Polygon Amoy blockchain.

    Returns a dict with:
        success      (bool)
        tx_hash      (str)   — transaction hash
        polygonscan  (str)   — link to view on Polygonscan
        hash_stored  (str)   — the hex hash stored on-chain
        error        (str)   — only present if success is False
    """
    try:
        w3       = get_web3()
        contract = get_contract(w3)

        # Build the hash
        hash_bytes = build_verification_hash(verification_id, anchor_id, platform, profile_url)
        hash_hex   = '0x' + hash_bytes.hex()

        # Check not already stored
        existing_hash, _ = contract.functions.getVerification(verification_id).call()
        if existing_hash != b'\x00' * 32:
            return {
                'success':     True,
                'tx_hash':     None,
                'polygonscan': None,
                'hash_stored': '0x' + existing_hash.hex(),
                'note':        'Already stored on-chain'
            }

        # Build transaction
        wallet   = Web3.to_checksum_address(WALLET_ADDRESS)
        nonce    = w3.eth.get_transaction_count(wallet)
        gas_price = w3.eth.gas_price

        txn = contract.functions.storeVerification(
            verification_id,
            hash_bytes
        ).build_transaction({
            'chainId':  80002,
            'from':     wallet,
            'nonce':    nonce,
            'gasPrice': gas_price,
            'gas':      100000,
        })

        # Sign and send
        private_key = WALLET_PRIVATE_KEY
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key

        signed  = w3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hex  = tx_hash.hex()

        # Wait for receipt (up to 60 seconds)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        if receipt['status'] == 1:
            return {
                'success':     True,
                'tx_hash':     tx_hex,
                'polygonscan': f"https://amoy.polygonscan.com/tx/{tx_hex}",
                'hash_stored': hash_hex,
                'block':       receipt['blockNumber']
            }
        else:
            return {
                'success': False,
                'error':   'Transaction failed on-chain',
                'tx_hash': tx_hex
            }

    except Exception as e:
        return {
            'success': False,
            'error':   str(e)
        }


def get_verification_from_chain(verification_id: int) -> dict:
    """
    Fetch a stored verification hash from the blockchain.
    Returns the hash and timestamp if found.
    """
    try:
        w3       = get_web3()
        contract = get_contract(w3)

        hash_bytes, timestamp = contract.functions.getVerification(verification_id).call()

        if hash_bytes == b'\x00' * 32:
            return {'success': True, 'stored': False}

        return {
            'success':   True,
            'stored':    True,
            'hash':      '0x' + hash_bytes.hex(),
            'timestamp': timestamp,
            'polygonscan': f"https://amoy.polygonscan.com/address/{CONTRACT_ADDRESS}"
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def check_connection() -> dict:
    """Health check for blockchain connection"""
    try:
        w3       = get_web3()
        contract = get_contract(w3)
        total    = contract.functions.totalVerifications().call()
        block    = w3.eth.block_number
        return {
            'success':             True,
            'connected':           True,
            'network':             'Polygon Amoy',
            'chain_id':            80002,
            'current_block':       block,
            'total_verifications': total,
            'contract':            CONTRACT_ADDRESS
        }
    except Exception as e:
        return {
            'success':   False,
            'connected': False,
            'error':     str(e)
        }