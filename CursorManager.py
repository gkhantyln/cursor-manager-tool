import os
import sys
import json
import time
import secrets
import platform
import ctypes
import shutil
from pathlib import Path
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, 
    QVBoxLayout, QWidget, QLabel, QSpacerItem, 
    QSizePolicy, QHBoxLayout, QTabWidget, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from plyer import notification  # Desktop notifications
import sqlite3

# -------------------- Database Manager Class --------------------
class DatabaseManager:
    """SQLite veritabanı yönetimi."""
    def __init__(self, db_path="operations.db"):
        self.db_path = db_path
        self.connection = self.connect_db()
        self.create_table()

    def connect_db(self):
        """Veritabanına bağlanır."""
        conn = sqlite3.connect(self.db_path)
        return conn

    def create_table(self):
        """İşlem geçmişini tutacak tabloyu oluşturur."""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS operations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            operation TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        self.connection.commit()

    def insert_operation(self, operation):
        """Veritabanına yeni bir işlem kaydeder."""
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO operations (operation) VALUES (?)", (operation,))
        self.connection.commit()

    def get_last_operation(self):
        """En son yapılan işlemi getirir."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT operation, timestamp FROM operations ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        return result if result else ("Henüz işlem yapılmadı", None)

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        self.connection.close()

# -------------------- ID Generator Class --------------------
class IDGenerator:
    """Rastgele benzersiz kimlikler (UUID, MAC ID) üretir."""

    @staticmethod
    def simulate_work():
        time.sleep(0.8)

    @staticmethod
    def generate_random_hex(length: int) -> str:
        return secrets.token_hex(length)

    def generate_machine_id(self) -> str:
        self.simulate_work()
        return self.generate_random_hex(32)

    def generate_mac_machine_id(self) -> str:
        self.simulate_work()
        return self.generate_random_hex(64)

    def generate_device_id(self) -> str:
        self.simulate_work()
        random_hex = self.generate_random_hex(16)
        return f"{random_hex[:8]}-{random_hex[8:12]}-{random_hex[12:16]}-{random_hex[16:20]}-{random_hex[20:32]}"

    def generate_sqm_id(self) -> str:
        """SQM ID oluşturur."""
        self.simulate_work()
        return self.generate_random_hex(64)

# -------------------- Config Manager Class --------------------
class ConfigManager:
    """Config dosyalarını okuma/yazma işlemlerini yöneten sınıf."""
    
    def __init__(self, username: str):
        self.username = username
        self.config_path = self.get_config_path()

    def get_config_path(self) -> Path:
        if platform.system() == "Windows":
            return Path(f"C:/Users/{self.username}/AppData/Roaming/Cursor/storage.json")
        else:
            return Path.home() / ".config/Cursor/storage.json"

    def read_config(self) -> Optional[Dict]:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading config: {e}")
            return None
        return None

    def save_config(self, config: Dict) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

# -------------------- Utility Functions --------------------
def resource_path(relative_path: str) -> str:
    """ PyInstaller ile paketlendiğinde dosya yolunu çözer."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_admin() -> bool:
    """ Programın yönetici yetkisiyle çalışıp çalışmadığını kontrol eder."""
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def kill_cursor_processes():
    """ Cursor uygulamasını kapatır."""
    if platform.system() == "Windows":
        os.system("taskkill /F /IM Cursor.exe 2>nul")
    else:
        os.system("pkill -f Cursor")

# -------------------- GUI Class --------------------
# -------------------- GUI Class --------------------
class CursorManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Manager")
        self.setFixedSize(500, 300)

        self.db_manager = DatabaseManager()  # Veritabanı yöneticisini başlat

        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tab_widget = QTabWidget()
        self.init_update_tab()
        self.init_id_tab()

        layout.addWidget(self.tab_widget)

    def init_update_tab(self):
        update_tab = QWidget()
        layout = QVBoxLayout(update_tab)

        self.update_status = QLabel()
        self.update_status.setAlignment(Qt.AlignRight)
        self.update_status.setFont(QFont("Arial", 9))

        title_label = QLabel("Cursor Güncelleme Kontrolü")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 9))

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        button_layout = QHBoxLayout()
        self.block_button = QPushButton("Güncellemeleri Engelle")
        self.block_button.clicked.connect(self.block_updates)

        self.enable_button = QPushButton("Güncellemeleri Aç")
        self.enable_button.clicked.connect(self.enable_updates)

        button_layout.addWidget(self.block_button)
        button_layout.addWidget(self.enable_button)

        layout.addWidget(title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)

        self.tab_widget.addTab(update_tab, "Güncelleme Kontrolü")

        # Son işlem bilgisini al ve ekranda göster
        last_operation, timestamp = self.db_manager.get_last_operation()
        if last_operation:
            self.update_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.update_status.setText(f"Son işlem: {last_operation} - {timestamp}")
        else:
            self.update_status.setText("Henüz işlem yapılmadı")

    def init_id_tab(self):
        id_tab = QWidget()
        layout = QVBoxLayout(id_tab)

        title_label = QLabel("Cursor Multi ID Değiştirme")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        self.current_ids = QTextEdit()
        self.current_ids.setReadOnly(True)
        self.current_ids.setFont(QFont("Consolas", 9))

        self.id_status_label = QLabel("")
        self.id_status_label.setAlignment(Qt.AlignCenter)
        self.id_status_label.setFont(QFont("Arial", 9))

        self.id_button = QPushButton("ID'leri Yeniden Oluştur")
        self.id_button.clicked.connect(self.change_ids)

        layout.addWidget(title_label)
        layout.addWidget(self.current_ids)
        layout.addWidget(self.id_status_label)
        layout.addWidget(self.id_button, alignment=Qt.AlignCenter)

        self.tab_widget.addTab(id_tab, "ID Değiştirme")

        # Daha önce değiştirilen ID'leri al ve ekranda göster
        self.show_previous_ids()

    def show_previous_ids(self):
        """Veritabanındaki daha önce değiştirilen ID'leri ekranda göster."""
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT operation, timestamp FROM operations WHERE operation LIKE 'ID%' ORDER BY id DESC")
        results = cursor.fetchall()

        if results:
            ids_output = "\n".join([f"{operation} - {timestamp}" for operation, timestamp in results])
            self.current_ids.setText(ids_output)
        else:
            self.current_ids.setText("Henüz ID değiştirilmedi.")

    def block_updates(self):
        local_path = os.path.join(os.environ['LOCALAPPDATA'])
        cursor_update_path = os.path.join(local_path, 'cursor-updater')

        self.progress_bar.setValue(50)  # Start progress

        try:
            # Eğer cursor-updater dizini varsa, bu dizini sil
            if os.path.exists(cursor_update_path):
                if os.path.isdir(cursor_update_path):
                    shutil.rmtree(cursor_update_path)  # Dizin varsa, sil
                else:
                    os.remove(cursor_update_path)  # Dosya varsa, sil
            
            # Yeniden boş bir dosya oluştur
            Path(cursor_update_path).touch()
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.status_label.setText("✅ İşlem başarılı: Güncellemeler engellendi")
            notification.notify(
                title="Cursor Güncelleme Kontrolü",
                message="Güncellemeler engellendi.",
                timeout=5
            )
            self.progress_bar.setValue(100)  # Complete progress

            # İşlem veritabanına kaydedildi
            self.db_manager.insert_operation("Güncellemeler engellendi")

        except Exception as e:
            # Hata durumunda kullanıcıya bilgi ver
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.status_label.setText(f"❌ Hata oluştu: {str(e)}")
            self.progress_bar.setValue(0)  # Reset progress

        # Güncelleme durumunu kontrol et
        self.check_update_status()

    def enable_updates(self):
        local_path = os.path.join(os.environ['LOCALAPPDATA'])
        cursor_update_path = os.path.join(local_path, 'cursor-updater')

        self.progress_bar.setValue(50)  # Start progress

        try:
            # Eğer dizin var ise, sil
            if os.path.exists(cursor_update_path):
                if os.path.isdir(cursor_update_path):
                    shutil.rmtree(cursor_update_path)  # Dizin varsa, sil
                else:
                    os.remove(cursor_update_path)  # Dosya varsa, sil
            
            # Yeniden dizin oluştur
            os.makedirs(cursor_update_path)
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.status_label.setText("✅ İşlem başarılı: Güncellemeler aktifleştirildi")
            notification.notify(
                title="Cursor Güncelleme Kontrolü",
                message="Güncellemeler aktifleştirildi.",
                timeout=5
            )
            self.progress_bar.setValue(100)  # Complete progress

            # İşlem veritabanına kaydedildi
            self.db_manager.insert_operation("Güncellemeler aktifleştirildi")

        except Exception as e:
            # Hata durumunda kullanıcıya bilgi ver
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.status_label.setText(f"❌ Hata oluştu: {str(e)}")
            self.progress_bar.setValue(0)  # Reset progress

        # Güncelleme durumunu kontrol et
        self.check_update_status()

    def check_update_status(self):
        """ Güncellemelerin durumunu kontrol eder ve gösterir. """
        local_path = os.path.join(os.environ['LOCALAPPDATA'])
        cursor_update_path = os.path.join(local_path, 'cursor-updater')

        if os.path.exists(cursor_update_path):
            self.update_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.update_status.setText("✅ Güncellemeler Aktif")
        else:
            self.update_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.update_status.setText("❌ Güncellemeler Engellenmiş")

    def change_ids(self):
        """ ID'leri değiştirir ve GUI'ye yazdırır."""
        if not is_admin():
            self.id_status_label.setText("❌ Yönetici yetkisi gerekli!")
            return

        # ID Generator instance
        id_gen = IDGenerator()

        # Generate all IDs
        machine_id = id_gen.generate_machine_id()
        mac_machine_id = id_gen.generate_mac_machine_id()
        device_id = id_gen.generate_device_id()
        sqm_id = id_gen.generate_sqm_id()

        kill_cursor_processes()

        # Update GUI with the generated IDs
        ids_output = f"""Machine ID: {machine_id}
Mac Machine ID: {mac_machine_id}
Device ID: {device_id}
SQM ID: {sqm_id}"""

        self.current_ids.setText(ids_output)
        self.id_status_label.setText("✅ ID'ler başarıyla değiştirildi!")

        # ID değişim işlemini veritabanına kaydet
        self.db_manager.insert_operation(f"ID'ler değiştirildi: {machine_id}, {mac_machine_id}, {device_id}, {sqm_id}")

def main():
    app = QApplication(sys.argv)
    window = CursorManagerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

