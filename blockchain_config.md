# Konfigurasi Blockchain untuk Steganografi 3D

## Mode Saat Ini: OFFLINE
Aplikasi saat ini berjalan dalam mode offline. Fitur hash file tetap berfungsi, tetapi penyimpanan dan verifikasi di blockchain dinonaktifkan.

## Cara Mengaktifkan Blockchain

### 1. Untuk Ethereum Sepolia Testnet (Disarankan untuk testing):

Edit file `blockchain_utils.py`, ubah baris:
```python
INFURA_URL = ''  # Kosongkan untuk mode offline
```

Menjadi:
```python
INFURA_URL = 'https://sepolia.infura.io/v3/YOUR_PROJECT_ID'
```

### 2. Langkah-langkah Setup:

1. **Buat akun Infura**: https://infura.io/
2. **Buat project baru** dan salin Project ID
3. **Ganti YOUR_PROJECT_ID** dengan Project ID dari Infura
4. **Deploy smart contract** ke Sepolia testnet
5. **Update CONTRACT_ADDRESS** dengan alamat contract yang baru
6. **Restart aplikasi**

### 3. Mendapatkan ETH Testnet (Sepolia):

- Faucet 1: https://faucets.chain.link/sepolia
- Faucet 2: https://sepoliafaucet.com/
- Faucet 3: https://www.alchemy.com/faucets/ethereum-sepolia

### 4. Smart Contract:

File `Stegano3DHash.sol` sudah tersedia untuk deployment. Deploy menggunakan:
- Remix IDE: https://remix.ethereum.org/
- Hardhat
- Truffle

## Mode Testing Lokal

Untuk testing tanpa ETH testnet, biarkan `INFURA_URL = ''`. Aplikasi akan:
- ✓ Menghitung hash SHA256 file
- ✓ Menampilkan hash untuk verifikasi manual
- ✗ Tidak menyimpan ke blockchain
- ✗ Tidak melakukan verifikasi blockchain

## Troubleshooting

### Error "Blockchain tidak tersedia"
1. Pastikan INFURA_URL terisi dengan benar
2. Cek koneksi internet
3. Pastikan Infura project aktif
4. Restart aplikasi setelah perubahan konfigurasi

### Error pada verifikasi
- Hash hanya bisa diverifikasi jika sebelumnya disimpan di blockchain
- Pastikan menggunakan alamat Ethereum yang sama
- Pastikan contract address benar

## Status Blockchain

Aplikasi akan menampilkan status blockchain saat startup:
- `✓ Blockchain terhubung` = Siap digunakan
- `✗ Blockchain offline` = Mode offline (hash lokal saja)
- `✗ Blockchain tidak tersedia` = Ada masalah konfigurasi
