# steganography.py (Versi Definitif dengan Manipulasi Biner)
import random
import struct
from kripto import encrypt, decrypt

class ComplexSteganographer:
    def __init__(self):
        self.EOM_DELIMITER = "0" * 24

    def _bytes_to_binary(self, data_bytes):
        return ''.join(format(byte, '08b') for byte in data_bytes)

    def _binary_to_bytes(self, binary_str):
        # Hanya pangkas jika memang ada sisa, jangan pangkas seluruh string jika sudah kelipatan 8
        if len(binary_str) % 8 != 0:
            binary_str = binary_str[:-(len(binary_str) % 8)]
        if not binary_str:
            return b''
        return int(binary_str, 2).to_bytes(len(binary_str) // 8, byteorder='big')

    def _get_embedding_path(self, password, total_vertices):
        indices = list(range(total_vertices))
        random.seed(password)
        random.shuffle(indices)
        return indices

    def _float_to_bits(self, f):
        """Mengubah float menjadi representasi biner 32-bit."""
        s = struct.pack('>f', f)
        return ''.join(format(c, '08b') for c in s)

    def _bits_to_float(self, b):
        """Mengubah biner 32-bit kembali menjadi float."""
        s = int(b, 2).to_bytes(4, byteorder='big')
        return struct.unpack('>f', s)[0]
    
    def encode(self, input_model_path, output_model_path, secret_message_path, password):
        print("Memulai proses encoding (digit desimal)...")
        # 1. Enkripsi pesan
        with open(secret_message_path, 'r', encoding='utf-8') as f:
            secret_message = f.read().encode('utf-8')
        encrypted_message_bytes = encrypt(secret_message, password)
        if not encrypted_message_bytes:
            raise Exception("Enkripsi gagal.")
        binary_message = self._bytes_to_binary(encrypted_message_bytes) + self.EOM_DELIMITER
        print(f"[DEBUG] Jumlah bit terenkripsi+delimiter: {len(binary_message)}")

        # 2. Baca file dan dapatkan vertex
        with open(input_model_path, 'r') as f:
            lines = f.readlines()
        vertex_indices_in_lines = [i for i, line in enumerate(lines) if line.startswith('v ')]

        # 3. Cek kapasitas
        if len(binary_message) > len(vertex_indices_in_lines) * 3:
            raise ValueError("Pesan terenkripsi terlalu panjang.")

        # 4. Buat jalur rahasia
        embedding_path = self._get_embedding_path(password, len(vertex_indices_in_lines))

        # 5. Lakukan penyisipan pada digit desimal ke-8
        message_idx = 0
        for embed_idx in embedding_path:
            if message_idx >= len(binary_message):
                break
            line_idx_to_modify = vertex_indices_in_lines[embed_idx]
            parts = lines[line_idx_to_modify].split()
            new_coords_str = [parts[0]]
            for i in range(1, 4):
                if message_idx < len(binary_message):
                    coord_str = parts[i]
                    if '.' in coord_str and len(coord_str.split('.')[-1]) >= 8:
                        # Ganti digit ke-8 setelah koma
                        int_part, frac_part = coord_str.split('.')
                        frac_part = list(frac_part)
                        frac_part[7] = binary_message[message_idx]
                        new_coord = int_part + '.' + ''.join(frac_part)
                        new_coords_str.append(new_coord)
                        message_idx += 1
                    else:
                        # Jika tidak cukup digit, tambahkan nol lalu ganti digit ke-8
                        int_part, frac_part = coord_str.split('.') if '.' in coord_str else (coord_str, '0')
                        frac_part = list(frac_part.ljust(8, '0'))
                        frac_part[7] = binary_message[message_idx]
                        new_coord = int_part + '.' + ''.join(frac_part)
                        new_coords_str.append(new_coord)
                        message_idx += 1
                else:
                    new_coords_str.append(parts[i])
            lines[line_idx_to_modify] = " ".join(new_coords_str) + "\n"

        # 6. Tulis file output
        with open(output_model_path, 'w') as f:
            f.writelines(lines)
        print(f"Encoding sukses! Model baru disimpan di '{output_model_path}'")

    def decode(self, stego_model_path, password):
        print("Memulai proses decoding (digit desimal)...")
        with open(stego_model_path, 'r') as f:
            vertex_lines = [line for line in f if line.startswith('v ')]

        # 1. Buat kembali jalur rahasia
        embedding_path = self._get_embedding_path(password, len(vertex_lines))

        extracted_bits = ""
        # 2. Ekstrak bit dari digit desimal ke-8
        for vertex_index in embedding_path:
            if vertex_index < len(vertex_lines):
                line = vertex_lines[vertex_index]
                parts = line.split()
                for i in range(1, 4):
                    if i < len(parts):
                        coord_str = parts[i]
                        if '.' in coord_str and len(coord_str.split('.')[-1]) >= 8:
                            extracted_bits += coord_str.split('.')[-1][7]
                        else:
                            extracted_bits += '0'  # fallback jika tidak cukup digit

        # 3. Cari delimiter dan dekripsi
        print(f"[DEBUG] Jumlah bit diekstrak: {len(extracted_bits)}")
        delimiter_pos = extracted_bits.find(self.EOM_DELIMITER)
        if delimiter_pos != -1:
            encrypted_bits = extracted_bits[:delimiter_pos]
            # Pastikan hanya bit kelipatan 8 yang diambil
            if len(encrypted_bits) < 128:
                print("WARNING: Hasil ekstraksi terlalu pendek, kemungkinan data korup atau presisi float tidak cukup.")
            if len(encrypted_bits) % 8 != 0:
                encrypted_bits = encrypted_bits[:-(len(encrypted_bits) % 8)]
            if not encrypted_bits:
                print("Decoding gagal: tidak ada bit terenkripsi yang valid.")
                return None
            encrypted_bytes = self._binary_to_bytes(encrypted_bits)
            decrypted_message_bytes = decrypt(encrypted_bytes, password)
            if decrypted_message_bytes:
                print("Decoding sukses!")
                return decrypted_message_bytes.decode('utf-8')
        print("Decoding gagal.")
        return None