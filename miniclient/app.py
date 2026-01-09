import sys
import json
import os
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QLineEdit, QPushButton, QListWidget, QLabel, 
                              QStackedWidget, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QFont

load_dotenv()

class OverlayTimer(QWidget):
    def __init__(self, record, parent_window):
        super().__init__()
        self.record = record
        self.parent_window = parent_window
        self.dragging = False
        self.drag_position = None

        flags = (Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.Tool)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Container widget with background
        container = QWidget()
        container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 100);
            border-radius: 5px;
        """)

        # Layout for time and info labels
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(1)

        self.color_bar = QLabel()
        self.color_bar.setFixedHeight(3)
        self.color_bar.setStyleSheet("""
            background-color: #aaaaaa;
            border-radius: 2px;
        """)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 35px;
            font-weight: bold;
            background-color: transparent;
            padding: 0px;
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            color: #c8c8c8;
            font-size: 16px;
            background-color: transparent;
            padding: 0px;
        """)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(self.color_bar)
        content_layout.addWidget(self.time_label)
        content_layout.addWidget(self.info_label)
        container.setLayout(content_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.resize(200, 100)
        saved_pos = self.parent_window.get_overlay_position()
        if saved_pos:
            self.move(saved_pos)
        else:
            self.move(0, 0)
        self.update_time()
        self.update_info()

    def update_time(self):
        timein_str = self.record.get('timein')
        if timein_str:
            try:
                timein = datetime.strptime(timein_str, '%Y-%m-%dT%H:%M:%SZ')
                elapsed = datetime.utcnow() - timein
                elapsed_str = self.format_elapsed(elapsed.total_seconds())
                self.time_label.setText(elapsed_str)
            except Exception as e:
                print(f"Error updating time: {e}")

    def update_info(self):
        domain = self.record.get('domain_name', 'Unknown')
        category = self.record.get('category_name', 'Unknown')
        domain_color = self.record.get('domain_color', '#aaaaaa')
        
        if not domain_color or domain_color == 'null':
            domain_color = '#aaaaaa'
        
        self.info_label.setText(f"{domain} - {category}")
        self.color_bar.setStyleSheet(f"""
            background-color: {domain_color};
            border-radius: 2px;
        """)

    def format_elapsed(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def mousePressEvent(self, event):
        if (event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and 
            event.buttons() == Qt.MouseButton.RightButton):
            self.switch_to_least_time_timer()
        elif (event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            self.close()
            self.parent_window.show()
            self.parent_window.load_records()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.parent_window.save_overlay_position(self.pos())
        self.dragging = False
        event.accept()

    def switch_to_least_time_timer(self):
        try:
            headers = {'Authorization': f'Bearer {self.parent_window.access_token}'}
            response = requests.get(f"{self.parent_window.api_base}/timerecords", headers=headers)

            if response.status_code == 200:
                records = response.json()
                open_records = [r for r in records if r.get('timeout') is None]

                if not open_records:
                    return

                min_record = None
                min_elapsed = float('inf')

                for record in open_records:
                    timein_str = record.get('timein')
                    if timein_str:
                        try:
                            timein = datetime.strptime(timein_str, '%Y-%m-%dT%H:%M:%SZ')
                            elapsed = (datetime.utcnow() - timein).total_seconds()
                            if elapsed < min_elapsed:
                                min_elapsed = elapsed
                                min_record = record
                        except Exception as e:
                            print(f"Error parsing time: {e}")

                if min_record and min_record.get('id') != self.record.get('id'):
                    domain_attr = self.parent_window.attributes_cache.get(min_record.get('domain_id'), {})
                    category_attr = self.parent_window.attributes_cache.get(min_record.get('category_id'), {})

                    min_record['domain_name'] = domain_attr.get('name', 'Unknown') if isinstance(domain_attr, dict) else 'Unknown'
                    min_record['category_name'] = category_attr.get('name', 'Unknown') if isinstance(category_attr, dict) else 'Unknown'
                    min_record['domain_color'] = domain_attr.get('color') if isinstance(domain_attr, dict) else None

                    self.record = min_record
                    self.update_time()
                    self.update_info()
            elif response.status_code == 401:
                self.parent_window.attempt_refresh()
        except Exception as e:
            print(f"Error switching timer: {e}")

class TimecardClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timecard Client")
        self.setGeometry(100, 100, 600, 500)

        self.api_base = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
        self.config_file = Path.home() / ".timecard_client.json"
        self.access_token = None
        self.refresh_token = None
        self.attributes_cache = {}

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_widget = self.create_login_widget()
        self.records_widget = self.create_records_widget()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.records_widget)

        self.load_credentials()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_times)
        self.timer.start(1000)

    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        layout.addWidget(QLabel("Timecard Login"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_records_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("Open Timecard Records")
        self.records_list = QListWidget()
        self.records_list.itemClicked.connect(self.on_record_clicked)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_records)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)

        layout.addWidget(self.status_label)
        layout.addWidget(self.records_list)
        layout.addWidget(refresh_btn)
        layout.addWidget(logout_btn)

        widget.setLayout(layout)
        return widget

    def load_credentials(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.overlay_position = data.get('overlay_position')
                    if self.access_token:
                        if self.verify_token():
                            self.stacked_widget.setCurrentIndex(1)
                            self.load_records()
                        else:
                            self.attempt_refresh()
            except Exception as e:
                print(f"Error loading credentials: {e}")
        else:
            self.overlay_position = None

    def save_credentials(self):
        try:
            data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token
            }
            if hasattr(self, 'overlay_position') and self.overlay_position:
                data['overlay_position'] = self.overlay_position
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving credentials: {e}")

    def verify_token(self):
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.api_base}/timerecords", headers=headers)
            return response.status_code == 200
        except:
            return False

    def attempt_refresh(self):
        try:
            headers = {'Authorization': f'Bearer {self.refresh_token}'}
            response = requests.post(f"{self.api_base}/refresh", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.save_credentials()
                self.stacked_widget.setCurrentIndex(1)
                self.load_records()
            else:
                self.access_token = None
                self.refresh_token = None
        except Exception as e:
            print(f"Error refreshing token: {e}")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.post(f"{self.api_base}/login", 
                                     json={'username': username, 'password': password})
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                self.save_credentials()
                self.password_input.clear()
                self.stacked_widget.setCurrentIndex(1)
                self.load_records()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {e}")

    def logout(self):
        self.access_token = None
        self.refresh_token = None
        if self.config_file.exists():
            self.config_file.unlink()
        self.records_list.clear()
        self.stacked_widget.setCurrentIndex(0)

    def load_records(self):
        if not self.access_token:
            return

        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}

            attrs_response = requests.get(f"{self.api_base}/recordattributes", headers=headers)
            if attrs_response.status_code == 200:
                attributes = attrs_response.json()
                self.attributes_cache = {attr['id']: attr for attr in attributes}

            response = requests.get(f"{self.api_base}/timerecords", headers=headers)

            if response.status_code == 200:
                records = response.json()
                self.open_records = []
                for r in records:
                    if r.get('timeout') is None:
                        domain_attr = self.attributes_cache.get(r.get('domain_id'), {})
                        category_attr = self.attributes_cache.get(r.get('category_id'), {})
                        
                        r['domain_name'] = domain_attr.get('name', 'Unknown') if isinstance(domain_attr, dict) else 'Unknown'
                        r['category_name'] = category_attr.get('name', 'Unknown') if isinstance(category_attr, dict) else 'Unknown'
                        r['domain_color'] = domain_attr.get('color') if isinstance(domain_attr, dict) else None
                        
                        self.open_records.append(r)
                self.display_records()
            elif response.status_code == 401:
                self.attempt_refresh()
            else:
                QMessageBox.warning(self, "Error", f"Failed to load records: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {e}")

    def display_records(self):
        self.records_list.clear()
        for record in self.open_records:
            self.add_record_item(record)

    def add_record_item(self, record):
        timein_str = record.get('timein')
        if timein_str:
            try:
                timein = datetime.strptime(timein_str, '%Y-%m-%dT%H:%M:%SZ')
                elapsed = datetime.utcnow() - timein
                elapsed_str = self.format_elapsed(elapsed.total_seconds())

                domain = record.get('domain_name', 'Unknown')
                category = record.get('category_name', 'Unknown')
                item_text = f"{domain} - {category} | {elapsed_str}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, record)
                self.records_list.addItem(item)
            except Exception as e:
                print(f"Error parsing time: {e}")

    def update_elapsed_times(self):
        if not hasattr(self, 'open_records') or not self.open_records:
            return

        for i in range(self.records_list.count()):
            item = self.records_list.item(i)
            record = item.data(Qt.ItemDataRole.UserRole)

            timein_str = record.get('timein')
            if timein_str:
                try:
                    timein = datetime.strptime(timein_str, '%Y-%m-%dT%H:%M:%SZ')
                    elapsed = datetime.utcnow() - timein
                    elapsed_str = self.format_elapsed(elapsed.total_seconds())

                    domain = record.get('domain_name', 'Unknown')
                    category = record.get('category_name', 'Unknown')
                    item_text = f"{domain} - {category} | {elapsed_str}"
                    item.setText(item_text)
                except Exception as e:
                    print(f"Error updating time: {e}")

    def on_record_clicked(self, item):
        record = item.data(Qt.ItemDataRole.UserRole)
        if record:
            self.hide()
            self.overlay = OverlayTimer(record, self)
            self.overlay.show()

    def format_elapsed(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def save_overlay_position(self, position):
        self.overlay_position = {'x': position.x(), 'y': position.y()}
        self.save_credentials()

    def get_overlay_position(self):
        if hasattr(self, 'overlay_position') and self.overlay_position:
            return QPoint(self.overlay_position['x'], self.overlay_position['y'])
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TimecardClient()
    client.show()
    sys.exit(app.exec())

