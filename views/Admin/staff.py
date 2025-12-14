import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from models.db import Database
from controllers.userController import UserController  # adjust import path if needed


class CreateStaffForm(QDialog):
    def __init__(self, user_controller: UserController):
        super().__init__()
        self.user_controller = user_controller
        self.setWindowTitle("Create Staff Account")
        self.resize(1200, 800)  # initial size
        self.setMinimumSize(1000, 700)  # minimum allowed size
        self.setMaximumSize(1600, 1000)  # optional maximum
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ---------------- Back to Dashboard Button ----------------
        dashboard_btn = QPushButton("<- Back to Dashboard")
        dashboard_btn.clicked.connect(self.close)  # closes dialog
        main_layout.addWidget(dashboard_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setSpacing(15)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ---------------- Staff Personal Information ----------------
        self.layout.addWidget(QLabel("<b>Staff Personal Information</b>"))

        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.last_name = QLineEdit()
        self.suffix = QLineEdit()
        self.email = QLineEdit()
        self.phone_number = QLineEdit()
        self.address = QTextEdit()
        self.address.setFixedHeight(50)

        personal_fields = [
            ("First Name:", self.first_name),
            ("Middle Name:", self.middle_name),
            ("Last Name:", self.last_name),
            ("Suffix:", self.suffix),
            ("Email:", self.email),
            ("Phone Number:", self.phone_number),
            ("Address:", self.address),
        ]

        grid_personal = QGridLayout()
        grid_personal.setHorizontalSpacing(20)
        grid_personal.setVerticalSpacing(10)

        # Two-column layout
        row, col = 0, 0
        half = len(personal_fields) // 2 + len(personal_fields) % 2
        for i, (label_text, widget) in enumerate(personal_fields):
            grid_personal.addWidget(QLabel(label_text), row, col*2)
            grid_personal.addWidget(widget, row, col*2+1)
            row += 1
            if row >= half:
                row = 0
                col += 1
        self.layout.addLayout(grid_personal)

        # ---------------- Staff Account Information ----------------
        self.layout.addWidget(QLabel("<b>Account Information</b>"))
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "staff", "faculty", "other"])

        grid_account = QGridLayout()
        grid_account.setHorizontalSpacing(20)
        grid_account.setVerticalSpacing(10)
        grid_account.addWidget(QLabel("Username:"), 0, 0)
        grid_account.addWidget(self.username, 0, 1)
        grid_account.addWidget(QLabel("Password:"), 1, 0)
        grid_account.addWidget(self.password, 1, 1)
        grid_account.addWidget(QLabel("Role:"), 2, 0)
        grid_account.addWidget(self.role_combo, 2, 1)
        self.layout.addLayout(grid_account)

        # ---------------- Submit Button ----------------
        self.submit_button = QPushButton("Create Staff Account")
        self.submit_button.clicked.connect(self.submit_form)
        self.layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def submit_form(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        role = self.role_combo.currentText()

        if not username or not password:
            print("Username and password cannot be empty")
            return

        if self.user_controller.check_username_exists(username):
            print("Username already exists")
            return

        # Create personal info first
        personal_info_data = {
            "first_name": self.first_name.text(),
            "middle_name": self.middle_name.text(),
            "last_name": self.last_name.text(),
            "suffix": self.suffix.text(),
            "email": self.email.text(),
            "phone_number": self.phone_number.text(),
            "address": self.address.toPlainText(),
        }

        try:
            cursor = self.user_controller.db.connection.cursor()
            cursor.execute("""
                INSERT INTO personal_information (
                    first_name, middle_name, last_name, suffix, email, phone_number, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                personal_info_data["first_name"], personal_info_data["middle_name"],
                personal_info_data["last_name"], personal_info_data["suffix"],
                personal_info_data["email"], personal_info_data["phone_number"],
                personal_info_data["address"]
            ))
            personal_info_id = cursor.lastrowid

            # Create user account
            self.user_controller.create_user(username, password, role, personal_info_id)

            self.user_controller.db.connection.commit()
            cursor.close()
            print(f"Staff account '{username}' created successfully!")
            self.accept()
        except Exception as e:
            self.user_controller.db.connection.rollback()
            print(f"Error creating staff account: {e}")

