# viewer.py (Tidak ada perubahan)
import open3d as o3d
import os

def tampilkan_model_3d(path_file, nama_jendela):
    if not os.path.exists(path_file):
        print(f"File tidak ditemukan: {path_file}")
        return

    print(f"Memuat model: {nama_jendela}")
    mesh = o3d.io.read_triangle_mesh(path_file)
    if not mesh.has_triangles():
        print("Gagal memuat model atau model tidak valid.")
        return

    mesh.paint_uniform_color([0.8, 0.8, 0.8])
    mesh.compute_vertex_normals()

    print(f"Menampilkan '{nama_jendela}'. Tutup jendela ini untuk melanjutkan.")
    o3d.visualization.draw_geometries([mesh], window_name=nama_jendela)

if __name__ == "__main__":
    nama_file_input = input("Masukkan nama file .obj dari folder 'data' untuk ditampilkan (contoh: teapot.obj): ")

    model_asli_path = os.path.join('data', nama_file_input)
    # Sesuaikan nama file stego dengan output dari main.py
    nama_file_stego = nama_file_input.replace('.obj', '_stego_complex.obj')
    model_stego_path = os.path.join('data', nama_file_stego)

    print("\n--- MEMBANDINGKAN MODEL 3D ---")
    tampilkan_model_3d(model_asli_path, f"Model Asli - {nama_file_input}")
    tampilkan_model_3d(model_stego_path, f"Model Stego - {nama_file_stego}")
    print("\nProses perbandingan selesai.")