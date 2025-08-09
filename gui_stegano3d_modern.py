import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
    QFileDialog, QLineEdit, QTextEdit, QMessageBox, QGroupBox, QFrame,
    QScrollArea, QSplitter, QTabWidget, QProgressBar, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QLinearGradient, QBrush
from blockchain_utils import (hash_file, store_hash_on_chain, verify_hash_on_chain, 
                            is_blockchain_available, get_blockchain_status)
from Steganography import ComplexSteganographer
import os

# Untuk viewer 3D
from vedo import Plotter, load
import threading

class ModernButton(QPushButton):
    def __init__(self, text, color="#3498db", hover_color="#2980b9"):
        super().__init__(text)
        self.color = color
        self.hover_color = hover_color
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {color}, stop: 1 {hover_color});
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 12px 20px;
                text-align: center;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {hover_color}, stop: 1 {color});
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {hover_color};
                transform: translateY(0px);
            }}
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11px;
                background: white;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: #f8f9fa;
            }
        """)

class ModernGroupBox(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin: 15px 0px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 20px;
                padding: 5px 10px;
                background: white;
                border-radius: 5px;
            }
        """)

class StatusBar(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setAlignment(Qt.AlignCenter)
        self.update_status("Aplikasi Siap", "success")
        
    def update_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c", 
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, colors["info"])
        self.setText(message)
        self.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                font-weight: bold;
                font-size: 10px;
                border-radius: 15px;
                padding: 5px 15px;
            }}
        """)

class Stegano3DApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🔐 Steganografi 3D Premium - GUI Modern')
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 650)
        self.steg = ComplexSteganographer()
        self.status_bar = StatusBar()
        
        # Set background gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #74b9ff, stop: 1 #0984e3);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        self.init_ui()
        self.input_obj = ''
        self.output_obj = ''
        
        # Update blockchain status
        self.update_blockchain_status()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content dengan tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.95);
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        # Tab 1: Steganografi
        stego_tab = self.create_steganography_tab()
        tab_widget.addTab(stego_tab, "🔐 Steganografi")
        
        # Tab 2: Blockchain
        blockchain_tab = self.create_blockchain_tab()
        tab_widget.addTab(blockchain_tab, "⛓️ Blockchain")
        
        # Tab 3: 3D Viewer
        viewer_tab = self.create_viewer_tab()
        tab_widget.addTab(viewer_tab, "🎯 3D Viewer")
        
        main_layout.addWidget(tab_widget)
        
        # Status bar
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)

    def create_header(self):
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("🔐 STEGANOGRAFI 3D PREMIUM")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_frame.setLayout(header_layout)
        return header_frame

    def create_steganography_tab(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout()
        
        # File Selection Group
        file_group = ModernGroupBox("📁 Pilihan File")
        file_layout = QVBoxLayout()
        
        # OBJ File
        obj_layout = QHBoxLayout()
        obj_layout.addWidget(QLabel("File OBJ:"))
        self.obj_path = ModernLineEdit("Pilih file OBJ 3D model...")
        self.obj_btn = ModernButton("📂 Browse", "#e67e22", "#d35400")
        self.obj_btn.clicked.connect(self.pilih_obj)
        obj_layout.addWidget(self.obj_path)
        obj_layout.addWidget(self.obj_btn)
        file_layout.addLayout(obj_layout)
        
        # Message File
        pesan_layout = QHBoxLayout()
        pesan_layout.addWidget(QLabel("File Pesan:"))
        self.pesan_path = ModernLineEdit("Pilih file pesan untuk disembunyikan...")
        self.pesan_btn = ModernButton("📂 Browse", "#e67e22", "#d35400")
        self.pesan_btn.clicked.connect(self.pilih_pesan)
        pesan_layout.addWidget(self.pesan_path)
        pesan_layout.addWidget(self.pesan_btn)
        file_layout.addLayout(pesan_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Security Group
        security_group = ModernGroupBox("🔒 Keamanan")
        security_layout = QVBoxLayout()
        
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = ModernLineEdit("Masukkan password untuk enkripsi...")
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.pass_input)
        security_layout.addLayout(pass_layout)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Action Buttons
        action_group = ModernGroupBox("⚡ Aksi Steganografi")
        action_layout = QHBoxLayout()
        
        self.encode_btn = ModernButton("🔐 ENCODE\nSisipkan Pesan", "#27ae60", "#229954")
        self.encode_btn.clicked.connect(self.encode)
        
        self.decode_btn = ModernButton("🔓 DECODE\nEkstrak Pesan", "#e74c3c", "#c0392b")
        self.decode_btn.clicked.connect(self.decode)
        
        action_layout.addWidget(self.encode_btn)
        action_layout.addWidget(self.decode_btn)
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # Results
        results_group = ModernGroupBox("📊 Hasil")
        results_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 10px;
                background: #f8f9fa;
            }
        """)
        results_layout.addWidget(self.result_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area

    def create_blockchain_tab(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout()
        
        # Blockchain Status
        status_group = ModernGroupBox("⛓️ Status Blockchain")
        status_layout = QVBoxLayout()
        
        self.blockchain_status_label = QLabel()
        self.blockchain_status_label.setStyleSheet("""
            QLabel {
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.blockchain_status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Blockchain Credentials
        cred_group = ModernGroupBox("🔑 Kredensial Blockchain (Opsional)")
        cred_layout = QVBoxLayout()
        
        pk_layout = QHBoxLayout()
        pk_layout.addWidget(QLabel("Private Key:"))
        self.pk_input = ModernLineEdit("Private key Ethereum (opsional untuk blockchain)")
        self.pk_input.setEchoMode(QLineEdit.Password)
        pk_layout.addWidget(self.pk_input)
        cred_layout.addLayout(pk_layout)
        
        addr_layout = QHBoxLayout()
        addr_layout.addWidget(QLabel("ETH Address:"))
        self.addr_input = ModernLineEdit("Alamat Ethereum (opsional untuk blockchain)")
        addr_layout.addWidget(self.addr_input)
        cred_layout.addLayout(addr_layout)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Blockchain Actions
        blockchain_group = ModernGroupBox("🔗 Aksi Blockchain")
        blockchain_layout = QHBoxLayout()
        
        self.hash_btn = ModernButton("📝 HASH FILE\nHitung & Simpan", "#9b59b6", "#8e44ad")
        self.hash_btn.clicked.connect(self.hash_and_store)
        
        self.verify_btn = ModernButton("✅ VERIFY HASH\nVerifikasi Integritas", "#f39c12", "#e67e22")
        self.verify_btn.clicked.connect(self.verify_hash)
        
        blockchain_layout.addWidget(self.hash_btn)
        blockchain_layout.addWidget(self.verify_btn)
        blockchain_group.setLayout(blockchain_layout)
        layout.addWidget(blockchain_group)
        
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area

    def create_viewer_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 3D Viewer Group
        viewer_group = ModernGroupBox("🎯 3D Model Viewer")
        viewer_layout = QVBoxLayout()
        
        info_label = QLabel("Gunakan viewer 3D untuk melihat model OBJ sebelum dan sesudah steganografi")
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                padding: 10px;
                background: transparent;
                border: none;
            }
        """)
        viewer_layout.addWidget(info_label)
        
        self.viewer_btn = ModernButton("🎯 TAMPILKAN 3D MODEL\nBuka Viewer", "#1abc9c", "#16a085")
        self.viewer_btn.clicked.connect(self.tampil_3d)
        viewer_layout.addWidget(self.viewer_btn)
        
        viewer_group.setLayout(viewer_layout)
        layout.addWidget(viewer_group)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setMaximumHeight(200)
        instructions.setHtml("""
        <h3 style="color: #2c3e50;">📖 Petunjuk Penggunaan:</h3>
        <ol style="color: #34495e; font-size: 11px;">
        <li><b>Pilih File OBJ:</b> Browse dan pilih model 3D dalam format .obj</li>
        <li><b>Pilih File Pesan:</b> Browse dan pilih file teks yang akan disembunyikan</li>
        <li><b>Set Password:</b> Masukkan password untuk enkripsi pesan</li>
        <li><b>Encode:</b> Sisipkan pesan ke dalam model 3D</li>
        <li><b>Hash & Store:</b> Hitung hash file untuk verifikasi integritas</li>
        <li><b>Decode:</b> Ekstrak pesan tersembunyi dari model 3D</li>
        <li><b>3D Viewer:</b> Lihat model 3D sebelum/sesudah proses steganografi</li>
        </ol>
        """)
        instructions.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.9);
            }
        """)
        layout.addWidget(instructions)
        
        widget.setLayout(layout)
        return widget

    def update_blockchain_status(self):
        status = get_blockchain_status()
        if "✓" in status:
            color = "#27ae60"
        else:
            color = "#e74c3c"
            
        self.blockchain_status_label.setText(status)
        self.blockchain_status_label.setStyleSheet(f"""
            QLabel {{
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                background: {color};
                color: white;
            }}
        """)

    def pilih_obj(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File OBJ', '.', 'OBJ Files (*.obj)')
        if fname:
            self.obj_path.setText(fname)
            self.input_obj = fname
            self.status_bar.update_status(f"File OBJ dipilih: {os.path.basename(fname)}", "success")

    def pilih_pesan(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File Pesan', '.', 'Text Files (*.txt)')
        if fname:
            self.pesan_path.setText(fname)
            self.status_bar.update_status(f"File pesan dipilih: {os.path.basename(fname)}", "success")

    def encode(self):
        if not self.input_obj:
            QMessageBox.warning(self, 'Error', 'Pilih file OBJ terlebih dahulu!')
            return
        if not self.pesan_path.text():
            QMessageBox.warning(self, 'Error', 'Pilih file pesan terlebih dahulu!')
            return
        if not self.pass_input.text():
            QMessageBox.warning(self, 'Error', 'Masukkan password!')
            return
        
        self.status_bar.update_status("Proses encoding...", "info")
        
        try:
            # Simpan file output
            output_file, _ = QFileDialog.getSaveFileName(self, 'Simpan File OBJ Hasil', 'output_stego.obj', 'OBJ Files (*.obj)')
            if not output_file:
                return
            
            # Encode
            result = self.steg.encode(self.input_obj, self.pesan_path.text(), output_file, self.pass_input.text())
            
            if result:
                self.output_obj = output_file
                self.result_text.append(f"✅ ENCODE BERHASIL!\n📁 Output: {output_file}\n")
                self.status_bar.update_status("Encoding berhasil!", "success")
            else:
                self.result_text.append("❌ ENCODE GAGAL!\n")
                self.status_bar.update_status("Encoding gagal!", "error")
                
        except Exception as e:
            QMessageBox.critical(self, 'Error Encode', f'Error: {e}')
            self.status_bar.update_status("Error saat encoding!", "error")

    def decode(self):
        if not self.input_obj:
            QMessageBox.warning(self, 'Error', 'Pilih file OBJ yang berisi pesan tersembunyi!')
            return
        if not self.pass_input.text():
            QMessageBox.warning(self, 'Error', 'Masukkan password!')
            return
        
        self.status_bar.update_status("Proses decoding...", "info")
        
        try:
            # File output untuk pesan
            output_msg, _ = QFileDialog.getSaveFileName(self, 'Simpan Pesan Hasil Decode', 'decoded_message.txt', 'Text Files (*.txt)')
            if not output_msg:
                return
            
            # Decode
            result = self.steg.decode(self.input_obj, output_msg, self.pass_input.text())
            
            if result:
                self.result_text.append(f"✅ DECODE BERHASIL!\n📁 Pesan disimpan: {output_msg}\n")
                self.status_bar.update_status("Decoding berhasil!", "success")
                
                # Tampilkan preview pesan
                try:
                    with open(output_msg, 'r', encoding='utf-8') as f:
                        msg_preview = f.read()[:200]
                        self.result_text.append(f"📝 Preview Pesan:\n{msg_preview}{'...' if len(msg_preview) >= 200 else ''}\n")
                except:
                    pass
            else:
                self.result_text.append("❌ DECODE GAGAL!\n")
                self.status_bar.update_status("Decoding gagal!", "error")
                
        except Exception as e:
            QMessageBox.critical(self, 'Error Decode', f'Error: {e}')
            self.status_bar.update_status("Error saat decoding!", "error")

    def hash_and_store(self):
        if not self.output_obj:
            QMessageBox.warning(self, 'Error', 'Tidak ada file output untuk di-hash!\nLakukan encode terlebih dahulu.')
            return
        
        self.status_bar.update_status("Menghitung hash file...", "info")
        
        try:
            file_hash = hash_file(self.output_obj)
            
            # Cek apakah blockchain fields diisi
            private_key = self.pk_input.text().strip()
            eth_address = self.addr_input.text().strip()
            
            if private_key and eth_address and is_blockchain_available():
                # Mode blockchain penuh
                try:
                    tx_hash = store_hash_on_chain(file_hash, private_key, eth_address)
                    QMessageBox.information(self, 'Blockchain Success', 
                        f'✅ Hash berhasil disimpan di blockchain!\n\n'
                        f'📋 File Hash: {file_hash}\n\n'
                        f'🔗 Transaction Hash: {tx_hash}')
                    self.status_bar.update_status("Hash disimpan di blockchain!", "success")
                except Exception as e:
                    QMessageBox.critical(self, 'Blockchain Error', f'❌ Gagal simpan ke blockchain: {e}')
                    # Fallback ke hash saja
                    QMessageBox.information(self, 'File Hash', 
                        f'📋 Hash SHA256 file:\n{file_hash}\n\n'
                        f'💡 Catatan: Untuk menyimpan ke blockchain, isi Private Key dan ETH Address.')
                    self.status_bar.update_status("Hash dihitung (blockchain gagal)", "warning")
            else:
                # Mode hash saja
                QMessageBox.information(self, 'File Hash', 
                    f'📋 Hash SHA256 file:\n{file_hash}\n\n'
                    f'💡 Catatan: Untuk menyimpan ke blockchain, isi Private Key dan ETH Address.')
                self.status_bar.update_status("Hash berhasil dihitung", "success")
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal menghitung hash: {e}')
            self.status_bar.update_status("Error saat hash!", "error")

    def verify_hash(self):
        if not self.output_obj:
            QMessageBox.warning(self, 'Error', 'Pilih file output hasil encode!')
            return
        
        self.status_bar.update_status("Memverifikasi hash...", "info")
        
        try:
            file_hash = hash_file(self.output_obj)
            
            # Tampilkan status blockchain dan hash file
            status = get_blockchain_status()
            msg = f"📋 Hash SHA256 file:\n{file_hash}\n\n🔗 Status: {status}"
            
            if is_blockchain_available():
                # Blockchain tersedia, coba verifikasi
                try:
                    valid = verify_hash_on_chain(file_hash)
                    if valid:
                        msg += "\n\n✅ Hash file VALID di blockchain!"
                        QMessageBox.information(self, 'Verifikasi Berhasil', msg)
                        self.status_bar.update_status("Hash valid di blockchain!", "success")
                    else:
                        msg += "\n\n❌ Hash file TIDAK ditemukan di blockchain!"
                        QMessageBox.warning(self, 'Verifikasi Gagal', msg)
                        self.status_bar.update_status("Hash tidak ditemukan di blockchain", "warning")
                except Exception as e:
                    msg += f"\n\n❌ Error verifikasi blockchain: {e}"
                    QMessageBox.critical(self, 'Error Blockchain', msg)
                    self.status_bar.update_status("Error verifikasi blockchain", "error")
            else:
                # Blockchain tidak tersedia, hanya tampilkan hash
                msg += "\n\n💡 Catatan: Verifikasi blockchain tidak tersedia.\nHanya menampilkan hash lokal."
                QMessageBox.information(self, 'Hash File', msg)
                self.status_bar.update_status("Hash ditampilkan (blockchain offline)", "info")
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Gagal membaca file: {e}')
            self.status_bar.update_status("Error saat verifikasi!", "error")

    def tampil_3d(self):
        # Pilih file untuk ditampilkan (asli atau hasil encode)
        fname, _ = QFileDialog.getOpenFileName(self, 'Pilih File OBJ untuk Ditampilkan', '.', 'OBJ Files (*.obj)')
        if not fname:
            return
        
        self.status_bar.update_status(f"Membuka 3D viewer: {os.path.basename(fname)}", "info")
        
        # Jalankan viewer di thread terpisah agar GUI tidak freeze
        threading.Thread(target=self._show_vedo, args=(fname,), daemon=True).start()

    def _show_vedo(self, fname):
        try:
            plt = Plotter(title=f"🎯 3D Model Viewer: {os.path.basename(fname)}", axes=1, bg='lightblue')
            mesh = load(fname)
            plt.show(mesh, viewup='z', interactive=True)
        except Exception as e:
            print(f"Error tampil 3D: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Steganografi 3D Premium")
    
    # Set aplikasi style
    app.setStyle('Fusion')
    
    win = Stegano3DApp()
    win.show()
    sys.exit(app.exec_())
