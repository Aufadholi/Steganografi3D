# main.py (Versi Kompleks)
from Steganography import ComplexSteganographer
import os
import getpass # Untuk input password tersembunyi

def jalankan_proyek_kompleks():
    steg = ComplexSteganographer()

    # 1. Meminta input dari pengguna
    nama_file = input("Masukkan nama file .obj dari folder 'data': ")
    password = getpass.getpass("Masukkan password rahasia: ")

    input_model = os.path.join('data', nama_file)
    if not os.path.exists(input_model):
        print(f"ERROR: File '{input_model}' tidak ditemukan!")
        return
        
    output_model = os.path.join('data', nama_file.replace('.obj', '_stego_complex.obj'))
    secret_file = 'data/pesan.txt'

    # --- ENCODE ---
    try:
        steg.encode(input_model, output_model, secret_file, password)
    except Exception as e:
        print(f"Terjadi error saat encoding: {e}")
        return

    print("-" * 40)

    # --- DECODE ---
    print("Sekarang, mari kita coba dekripsi model yang baru dibuat.")
    # Minta password lagi untuk simulasi dunia nyata
    password_decode = getpass.getpass("Masukkan password untuk dekripsi: ")
    
    pesan_terekstrak = steg.decode(output_model, password_decode)

    if pesan_terekstrak:
        print("\n--- HASIL EKSTRAKSI ---")
        print(f"Pesan yang ditemukan: '{pesan_terekstrak}'")
        print("-----------------------")

if __name__ == "__main__":
    jalankan_proyek_kompleks()