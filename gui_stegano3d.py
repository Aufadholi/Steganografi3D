import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from Steganography import ComplexSteganographer
import os

# Untuk viewer 3D
from vedo import Plotter, load
import threading

class Stegano3DApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Steganografi 3D OBJ - GUI')
        self.setGeometry(100, 100, 500, 350)
        self.steg = ComplexSteganographer()
        self.init_ui()
        self.input_obj = ''
        self.output_obj = ''
        self.pesan_file = ''

    def init_ui(self):
        layout = QVBoxLayout()

        # Pilih file OBJ
        self.obj_label = QLabel('File OBJ asli:')
        self.obj_path = QLineEdit()
        self.obj_btn = QPushButton('Pilih File OBJ')
        self.obj_btn.clicked.connect(self.pilih_obj)
        obj_row = QHBoxLayout()
        obj_row.addWidget(self.obj_label)
        obj_row.addWidget(self.obj_path)
        obj_row.addWidget(self.obj_btn)
        layout.addLayout(obj_row)

        # Pilih file pesan
        self.pesan_label = QLabel('File Pesan:')
        self.pesan_path = QLineEdit()
        self.pesan_btn = QPushButton('Pilih File Pesan')
        self.pesan_btn.clicked.connect(self.pilih_pesan)
        pesan_row = QHBoxLayout()
        pesan_row.addWidget(self.pesan_label)
        pesan_row.addWidget(self.pesan_path)
        pesan_row.addWidget(self.pesan_btn)
        layout.addLayout(pesan_row)

        # Password
        self.pass_label = QLabel('Password:')
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_row = QHBoxLayout()
        pass_row.addWidget(self.pass_label)
        pass_row.addWidget(self.pass_input)
        layout.addLayout(pass_row)

        # Tombol encode/decode
        self.encode_btn = QPushButton('Encode (Sisipkan Pesan)')
        self.encode_btn.clicked.connect(self.encode)
        self.decode_btn = QPushButton('Decode (Ekstrak Pesan)')
        self.decode_btn.clicked.connect(self.decode)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.encode_btn)
        btn_row.addWidget(self.decode_btn)
        layout.addLayout(btn_row)

        # Tombol viewer 3D
        self.view_btn = QPushButton('Tampilkan 3D OBJ')
        self.view_btn.clicked.connect(self.tampil_3d)
        layout.addWidget(self.view_btn)

        # Output pesan hasil decode
        self.result_label = QLabel('Hasil Ekstraksi:')
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def pilih_obj(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File OBJ', '.', 'OBJ Files (*.obj)')
        if fname:
            self.input_obj = fname
            self.obj_path.setText(fname)
            # Set output_obj otomatis
            base, ext = os.path.splitext(fname)
            self.output_obj = base + '_stego_complex' + ext

    def pilih_pesan(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File Pesan', '.', 'Text Files (*.txt)')
        if fname:
            self.pesan_file = fname
            self.pesan_path.setText(fname)

    def encode(self):
        if not self.input_obj or not self.pesan_file or not self.pass_input.text():
            QMessageBox.warning(self, 'Error', 'Lengkapi semua input!')
            return
        try:
            self.steg.encode(self.input_obj, self.output_obj, self.pesan_file, self.pass_input.text())
            QMessageBox.information(self, 'Sukses', f'Pesan berhasil disisipkan!\nFile output: {self.output_obj}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal encode: {e}')

    def decode(self):
        if not self.output_obj or not self.pass_input.text():
            QMessageBox.warning(self, 'Error', 'Pilih file OBJ hasil encode dan masukkan password!')
            return
        try:
            pesan = self.steg.decode(self.output_obj, self.pass_input.text())
            if pesan:
                self.result_text.setPlainText(pesan)
                QMessageBox.information(self, 'Sukses', 'Pesan berhasil diekstrak!')
            else:
                self.result_text.setPlainText('')
                QMessageBox.warning(self, 'Gagal', 'Pesan tidak ditemukan atau password salah.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal decode: {e}')

    def tampil_3d(self):
        # Pilih file untuk ditampilkan (asli atau hasil encode)
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File OBJ untuk Ditampilkan', '.', 'OBJ Files (*.obj)')
        if not fname:
            return
        # Jalankan viewer di thread terpisah agar GUI tidak freeze
        threading.Thread(target=self._show_vedo, args=(fname,), daemon=True).start()

    def _show_vedo(self, fname):
        plt = Plotter(title=fname, axes=1, bg='white')
        mesh = load(fname)
        plt.show(mesh, viewup='z', interactive=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Stegano3DApp()
    win.show()
    sys.exit(app.exec_())
