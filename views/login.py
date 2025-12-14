from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QCheckBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon,QAction


class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)
    register_requested = pyqtSignal()

    def __init__(self, user_controller, student_controller):
        super().__init__()
        self.eye_button = None
        self.remember_checkbox = None
        self.password_input = None
        self.username_input = None
        self.user_controller = user_controller
        self.student_controller = student_controller
        self.init_ui()

    def init_ui(self):
        self.setObjectName("loginWindow")
        self.setStyleSheet("""
            QWidget#loginWindow {
                background-color: #06B6D4;
            }
        """)

        # Main layout (centered login panel)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Login form container
        login_container = QFrame()
        login_container.setObjectName("loginContainer")
        login_container.setStyleSheet("""
            QFrame#loginContainer {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
            }
        """)
        login_container.setMinimumSize(600, 700)
        login_container.setMaximumWidth(600)
        login_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Add login form to container
        login_layout = self.create_login_form()
        login_container.setLayout(login_layout)

        main_layout.addWidget(login_container)
        self.setLayout(main_layout)

        # Set focus to username field
        self.username_input.setFocus()

        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def create_login_form(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\LOGO (1).png")
        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel("Sign In")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Sign in to manage student accounts")
        subtitle_label.setFont(QFont("Arial", 11))
        subtitle_label.setStyleSheet("color: #6c757d;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        layout.addSpacing(20)

        # Username
        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        username_label.setStyleSheet("color: #495057;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit { padding: 12px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; color: #2c3e50; font-size:15px;}
            QLineEdit:focus { border: 2px solid #007bff; }
        """)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Password Label
        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        password_label.setStyleSheet("color: #495057;")

        # Container for password + eye
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit { padding: 12px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; color: #2c3e50; font-size:15px;}
            QLineEdit:focus { border: 2px solid #007bff; }
        """)

        # Eye button
        self.eye_button = QAction(QIcon(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\eye.png"), "", self.password_input)
        self.eye_button.setCheckable(True)
        self.eye_button.triggered.connect(self.toggle_password_visibility)

        # Add password and eye to layout
        self.password_input.addAction(self.eye_button, QLineEdit.ActionPosition.TrailingPosition)
        password_layout.addWidget(self.password_input)

        # Add to main layout
        layout.addWidget(password_label)
        layout.addWidget(password_container)

        # Remember me
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Arial", 10))
        self.remember_checkbox.setStyleSheet("color: #6c757d;")
        layout.addWidget(self.remember_checkbox)

        # Login Button
        login_button = QPushButton("Sign In")
        login_button.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        login_button.setFixedHeight(50)
        login_button.setStyleSheet("""
            QPushButton { background-color: #0056b3; color: white; border-radius: 6px; }
            QPushButton:hover { background-color: #06B6D4; }
            QPushButton:pressed { background-color: #004085; }
        """)
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        # Forgot Password
        forgot_button = QPushButton("Forgot Password?")
        forgot_button.setFont(QFont("Arial", 10))
        forgot_button.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #6c757d; text-decoration: underline; }
            QPushButton:hover { color: #007bff; text-decoration: underline; }
        """)
        forgot_button.clicked.connect(self.forgot_password)
        layout.addWidget(forgot_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)
        layout.addStretch()
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
        user = self.user_controller.verify_login(username, password)
        if user:
            self.login_successful.emit(user)
            print("User Successfully Logged In")
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()

    def toggle_password_visibility(self):
        if self.eye_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_button.setIcon(QIcon(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\eye-slash.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_button.setIcon(QIcon(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\eye.png"))

    def forgot_password(self):
        QMessageBox.information(self, "Forgot Password",
                                "Please contact the system administrator to reset your password.")

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

