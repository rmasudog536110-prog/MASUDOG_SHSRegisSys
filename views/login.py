import sys
import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QCheckBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QPixmap, QAction

class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)
    register_requested = pyqtSignal()

    def __init__(self, auth_controller, student_controller):
        super().__init__()
        self.username_input = None
        self.password_input = None
        self.remember_checkbox = None
        self.eye_action = None
        self.auth_controller = auth_controller
        self.student_controller = student_controller
        self.settings = QSettings("MachcreatorDev", "StudentRegisSys")
        self.init_ui()

    def init_ui(self):
        self.setObjectName("loginWindow")
        self.setStyleSheet("QWidget#loginWindow { background-color: #06B6D4; }")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        login_container = QFrame()
        login_container.setObjectName("loginContainer")
        login_container.setStyleSheet(
            "QFrame#loginContainer { background-color: white; border: 1px solid #dee2e6; border-radius: 10px; }"
        )
        login_container.setMinimumSize(600, 700)
        login_container.setMaximumWidth(600)
        login_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        login_container.setLayout(self.create_login_form())
        main_layout.addWidget(login_container)
        self.setLayout(main_layout)
        self._load_remembered_credentials()
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def _load_remembered_credentials(self):
        remember_checked = self.settings.value("remember_me", type=bool)
        if remember_checked:
            self.remember_checkbox.setChecked(True)
            username = self.settings.value("last_username", type=str)
            if username:
                self.username_input.setText(username)
                self.password_input.setFocus()

    def create_login_form(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)

        logo_label = QLabel()
        pixmap = QPixmap(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\LOGO (1).png")
        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        title_label = QLabel("Sign In")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Sign in to manage student accounts")
        subtitle_label.setFont(QFont("Arial", 11))
        subtitle_label.setStyleSheet("color: #6c757d;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)

        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        username_label.setStyleSheet("color: #495057;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet(
            "QLineEdit { padding: 12px 12px 12px 35px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; color: #2c3e50; font-size:15px; }"
            "QLineEdit:focus { border: 2px solid #007bff; }"
        )
        user_icon = qta.icon('fa5s.user', color='#6c757d', font_size=16)
        self.username_input.addAction(QAction(user_icon, "", self.username_input), QLineEdit.ActionPosition.LeadingPosition)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        password_label.setStyleSheet("color: #495057;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet(
            "QLineEdit { padding: 12px 12px 12px 35px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; color: #2c3e50; font-size:15px; }"
            "QLineEdit:focus { border: 2px solid #007bff; }"
        )
        lock_icon = qta.icon('fa5s.lock', color='#6c757d', font_size=16)
        self.password_input.addAction(QAction(lock_icon, "", self.password_input), QLineEdit.ActionPosition.LeadingPosition)
        self.eye_action = QAction(qta.icon('fa5s.eye', color='#6c757d', font_size=16), "Toggle Visibility", self.password_input)
        self.eye_action.setCheckable(True)
        self.eye_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.eye_action, QLineEdit.ActionPosition.TrailingPosition)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Arial", 10))
        self.remember_checkbox.setStyleSheet("color: #6c757d;")
        layout.addWidget(self.remember_checkbox)

        login_button = QPushButton("Sign In")
        login_button.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        login_button.setFixedHeight(50)
        login_button.setStyleSheet(
            "QPushButton { background-color: #0056b3; color: white; border-radius: 6px; }"
            "QPushButton:hover { background-color: #06B6D4; }"
            "QPushButton:pressed { background-color: #004085; }"
        )
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        forgot_button = QPushButton("Forgot Password?")
        forgot_button.setFont(QFont("Arial", 10))
        forgot_button.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #6c757d; text-decoration: underline; }"
            "QPushButton:hover { color: #007bff; text-decoration: underline; }"
        )
        forgot_button.clicked.connect(self.forgot_password)
        layout.addWidget(forgot_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addStretch()
        self.username_input.setFocus()
        return layout

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Please enter your username")
            self.username_input.setFocus()
            return
        if not password:
            QMessageBox.warning(self, "Validation Error", "Please enter your password")
            self.password_input.setFocus()
            return
        user = self.auth_controller.login(username, password)
        if user:
            if self.remember_checkbox.isChecked():
                self.settings.setValue("remember_me", True)
                self.settings.setValue("last_username", username)
            else:
                self.settings.setValue("remember_me", False)
                self.settings.remove("last_username")
            self.login_successful.emit(user)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()

    def toggle_password_visibility(self):
        if self.eye_action.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_action.setIcon(qta.icon('fa5s.eye-slash', color='#6c757d', font_size=16))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_action.setIcon(qta.icon('fa5s.eye', color='#6c757d', font_size=16))

    def forgot_password(self):
        QMessageBox.information(self, "Forgot Password", "Please contact the system administrator to reset your password.")

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()
