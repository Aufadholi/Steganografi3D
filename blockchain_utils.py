import hashlib
from web3 import Web3

# Konfigurasi Blockchain
# Untuk testing tanpa blockchain, biarkan kosong
# Untuk Sepolia testnet: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
INFURA_URL = ''  # Kosongkan untuk mode offline
CONTRACT_ADDRESS = '0x7EF2e0048f5bAeDe046f6BF797943daF4ED8CB47'  # Contract address (jika ada)
CONTRACT_ABI = [
    # ABI minimal untuk fungsi storeHash dan verifyHash
    {
        "inputs": [
            {"internalType": "bytes32", "name": "fileHash", "type": "bytes32"}
        ],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "fileHash", "type": "bytes32"}
        ],
        "name": "verifyHash",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Inisialisasi web3 dan kontrak dengan penanganan error
blockchain_available = False
try:
    # Skip blockchain jika URL kosong atau placeholder
    if not INFURA_URL or '127.0.0.1' in INFURA_URL:
        print("Info: Mode offline - blockchain dinonaktifkan")
        w3 = None
        contract = None
        blockchain_available = False
    else:
        print(f"Menghubungkan ke blockchain: {INFURA_URL}")
        w3 = Web3(Web3.HTTPProvider(INFURA_URL))
        if w3.is_connected():
            contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)
            blockchain_available = True
            print("✓ Blockchain terhubung")
        else:
            w3 = None
            contract = None
            blockchain_available = False
            print("✗ Gagal terhubung ke blockchain")
except Exception as e:
    print(f"Warning: Blockchain setup gagal: {e}")
    w3 = None
    contract = None
    blockchain_available = False

def hash_file(filepath):
    """Hitung hash SHA256 file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def store_hash_on_chain(file_hash, private_key, from_address):
    """Simpan hash ke blockchain (perlu ETH testnet)."""
    if not blockchain_available or not contract or not w3:
        raise Exception("Blockchain tidak tersedia.\n\nUntuk menggunakan blockchain:\n1. Isi INFURA_URL dengan endpoint valid (contoh: https://sepolia.infura.io/v3/YOUR_PROJECT_ID)\n2. Pastikan CONTRACT_ADDRESS benar\n3. Restart aplikasi")
    
    # Konversi alamat ke format checksum yang benar
    from_address = Web3.to_checksum_address(from_address)
    
    # Konversi hash string ke bytes32
    hash_bytes = bytes.fromhex(file_hash)
    
    tx = contract.functions.storeHash(hash_bytes).build_transaction({
        'from': from_address,
        'nonce': w3.eth.get_transaction_count(from_address),
        'gas': 200000,
        'gasPrice': w3.toWei('10', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def verify_hash_on_chain(file_hash):
    """Verifikasi hash file di blockchain."""
    if not blockchain_available or not contract or not w3:
        raise Exception("Blockchain tidak tersedia.\n\nUntuk menggunakan blockchain:\n1. Isi INFURA_URL dengan endpoint valid (contoh: https://sepolia.infura.io/v3/YOUR_PROJECT_ID)\n2. Pastikan CONTRACT_ADDRESS benar\n3. Restart aplikasi\n\nSaat ini hanya dapat menampilkan hash lokal.")
    
    # Konversi hash string ke bytes32
    hash_bytes = bytes.fromhex(file_hash)
    
    return contract.functions.verifyHash(hash_bytes).call()

def is_blockchain_available():
    """Cek apakah blockchain tersedia."""
    return blockchain_available

def get_blockchain_status():
    """Dapatkan status blockchain dengan penjelasan."""
    if blockchain_available:
        return "✓ Blockchain terhubung dan siap digunakan"
    else:
        if not INFURA_URL:
            return "✗ Blockchain offline (INFURA_URL kosong)"
        else:
            return f"✗ Blockchain tidak tersedia (cek koneksi ke: {INFURA_URL})"
