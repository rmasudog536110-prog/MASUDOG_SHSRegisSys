import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QScrollArea, QWidget, QMessageBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
)
from PyQt6.QtCore import Qt
from controllers.userController import UserController
from controllers.authController import AuthController
from PyQt6.QtGui import QColor  # QColor added for StudentTabs


# --- STAFF FORM CLASS (Base for Create and Edit) ---
class StaffFormBase(QDialog):
    def __init__(self, user_controller: UserController, user_id=None):
        super().__init__()
        self.user_controller = user_controller
        self.user_id = user_id
        self.edit_mode = bool(user_id)
        self.personal_info_id = None

        self.setWindowTitle("Edit Staff Account" if self.edit_mode else "Create Staff Account")
        self.setMinimumSize(800, 500)
        self.setMaximumSize(1600, 1000)

        self.init_ui()

        if self.edit_mode:
            self._load_staff_data()

    def init_ui(self):
        # ... (Layout setup is mostly correct, omitting for brevity) ...
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        self.setStyleSheet("""
            QDialog { background-color: #F3F6F8; }
            QWidget { background-color: #F3F6F8; }
            QLabel { color: #111827; }
            QLineEdit, QComboBox, QTextEdit { 
                background: white; border: 1px solid #0EA5E9; padding: 6px; 
                border-radius: 4px; color: #111827;
            }
            QComboBox QAbstractItemView {color: #111827; selection-background-color: #0EA5E9; selection-color: white;}
            QPushButton { color: white; background-color: #0EA5E9; border-radius: 6px; padding: 8px; }
            QPushButton#backBtn { background: transparent; color: #0EA5E9; padding: 4px; border: 1px solid #111827; }
            QScrollArea { border: none; background-color: transparent; }
        """)

        dashboard_btn = QPushButton("<- Back to Dashboard")
        dashboard_btn.setObjectName("backBtn")
        dashboard_btn.clicked.connect(self.close)
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
            ("First Name:", self.first_name), ("Middle Name:", self.middle_name),
            ("Last Name:", self.last_name), ("Suffix:", self.suffix),
            ("Email:", self.email), ("Phone Number:", self.phone_number),
            ("Address:", self.address),
        ]

        grid_personal = QGridLayout()
        grid_personal.setHorizontalSpacing(20)
        grid_personal.setVerticalSpacing(10)

        row, col = 0, 0
        half = len(personal_fields) // 2 + len(personal_fields) % 2
        for i, (label_text, widget) in enumerate(personal_fields):
            grid_personal.addWidget(QLabel(label_text), row, col * 2)
            grid_personal.addWidget(widget, row, col * 2 + 1)
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
        self.role_combo.addItems(["admin", "staff"])
        self.department_combo = QComboBox()
        self.department_combo.addItems(["Administration", "Registrar"])
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive"])

        grid_account = QGridLayout()
        grid_account.setHorizontalSpacing(20)
        grid_account.setVerticalSpacing(10)
        grid_account.addWidget(QLabel("Username:"), 0, 0)
        grid_account.addWidget(self.username, 0, 1)

        # Updated password label based on mode
        password_label = "Password:"
        if self.edit_mode:
            password_label = "Password (leave blank to keep current):"

        grid_account.addWidget(QLabel(password_label), 1, 0)
        grid_account.addWidget(self.password, 1, 1)
        grid_account.addWidget(QLabel("Role:"), 2, 0)
        grid_account.addWidget(self.role_combo, 2, 1)
        grid_account.addWidget(QLabel("Department:"), 3, 0)
        grid_account.addWidget(self.department_combo, 3, 1)
        
        # Add status field only in edit mode
        if self.edit_mode:
            grid_account.addWidget(QLabel("Status:"), 4, 0)
            grid_account.addWidget(self.status_combo, 4, 1)
        
        self.layout.addLayout(grid_account)

        # ---------------- Submit Button ----------------
        button_text = "Save Changes" if self.edit_mode else "Create Staff Account"
        self.submit_button = QPushButton(button_text)
        self.submit_button.setStyleSheet("background-color: #0EA5E9; color: white; padding: 12px; border-radius: 6px;")
        self.submit_button.clicked.connect(self._handle_submission)
        self.layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def _load_staff_data(self):
        """Loads existing staff data into the form fields."""
        staff = self.user_controller.get_user_by_id(self.user_id)

        if not staff:
            QMessageBox.critical(self, "Error", f"Staff with ID {self.user_id} not found.")
            self.reject()
            return

        self.personal_info_id = staff.get("personal_info_id")

        self.username.setText(staff.get("username", ""))
        self.first_name.setText(staff.get("first_name", ""))
        self.middle_name.setText(staff.get("middle_name", ""))
        self.last_name.setText(staff.get("last_name", ""))
        self.suffix.setText(staff.get("suffix", ""))
        self.email.setText(staff.get("email", ""))
        self.phone_number.setText(staff.get("phone_number", ""))
        self.address.setText(staff.get("address", ""))

        index = self.role_combo.findText(staff.get("role", "staff"))
        if index != -1:
            self.role_combo.setCurrentIndex(index)
        
        # Load department
        dept_index = self.department_combo.findText(staff.get("department", "Administration"))
        if dept_index != -1:
            self.department_combo.setCurrentIndex(dept_index)
        
        # Load status if in edit mode
        if self.edit_mode:
            status_index = self.status_combo.findText(staff.get("status", "active"))
            if status_index != -1:
                self.status_combo.setCurrentIndex(status_index)

    def _handle_submission(self):
        """Routes to create or update based on edit_mode."""
        if self.edit_mode:
            self._update_staff()
        else:
            self._create_staff()

    def _get_form_data(self):
        """Helper to collect form data."""
        data = {
            "first_name": self.first_name.text().strip(),
            "middle_name": self.middle_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "suffix": self.suffix.text().strip(),
            "email": self.email.text().strip(),
            "phone_number": self.phone_number.text().strip(),
            "address": self.address.toPlainText().strip(),
            "username": self.username.text().strip(),
            "password": self.password.text().strip(),
            "role": self.role_combo.currentText(),
            "department": self.department_combo.currentText(),
        }
        
        # Include status only in edit mode
        if self.edit_mode:
            data["status"] = self.status_combo.currentText()
        
        return data

    def _create_staff(self):
        data = self._get_form_data()

        if not data["username"] or not data["password"]:
            QMessageBox.warning(self, "Validation", "Username and password cannot be empty.")
            return

        if self.user_controller.check_username_exists(data["username"]):
            QMessageBox.warning(self, "Validation", "Username already exists.")
            return

        try:
            # 1. Insert Personal Info
            personal_info_id = self.user_controller.create_personal_info(
                data["first_name"], data["middle_name"], data["last_name"],
                data["suffix"], data["email"], data["phone_number"], data["address"]
            )

            if personal_info_id is None:
                raise Exception("Failed to create personal information entry.")

            # 2. Get Department ID
            department_id = self.user_controller.get_department_id(data["department"])

            # 3. Create User Account
            self.user_controller.create_user(
                data["username"], data["password"], data["role"], personal_info_id, department_id
            )

            QMessageBox.information(self, "Success", f"Staff account '{data['username']}' created successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating staff account: {e}")
            print(f"Error creating staff account: {e}")

    def _update_staff(self):
        data = self._get_form_data()

        if not data["username"]:
            QMessageBox.warning(self, "Validation", "Username cannot be empty.")
            return

        # Check for username conflict only if the username was changed
        current_user = self.user_controller.get_user_by_id(self.user_id)
        if current_user and current_user.get("username") != data["username"]:
            if self.user_controller.check_username_exists(data["username"]):
                QMessageBox.warning(self, "Validation", "New username already exists.")
                return

        try:
            # 1. Update Personal Info
            self.user_controller.update_personal_info(
                self.personal_info_id, data["first_name"], data["middle_name"], data["last_name"],
                data["suffix"], data["email"], data["phone_number"], data["address"]
            )

            # 2. Get Department ID
            department_id = self.user_controller.get_department_id(data["department"])

            # 3. Update User Account
            user_update_data = {
                "username": data["username"],
                "role": data["role"],
                "password": data["password"] if data["password"] else None,  # Only update if password field is not empty
                "status": data.get("status"),  # Include status from edit form
                "department_id": department_id
            }
            self.user_controller.update_user(self.user_id, **user_update_data)

            QMessageBox.information(self, "Success", f"Staff account '{data['username']}' updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating staff account: {e}")
            print(f"Error updating staff account: {e}")


# Class used for creating a new staff member (just an alias for clarity)
class CreateStaffForm(StaffFormBase):
    def __init__(self, user_controller: UserController):
        super().__init__(user_controller, user_id=None)


# Simplified edit form matching EditStudentForm style
class EditStaffForm(QDialog):
    def __init__(self, user_controller: UserController, user_id):
        super().__init__()
        self.user_controller = user_controller
        self.user_id = user_id
        self.personal_info_id = None

        self.setWindowTitle("Edit Staff")
        self.resize(500, 400)

        self.init_ui()
        self.load_staff()

    def init_ui(self):
        from PyQt6.QtWidgets import QFormLayout
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        # Theme consistent with dashboard
        self.setStyleSheet("""
            QDialog { background-color: #F3F6F8; }
            QLabel { color: #111827; }
            QLineEdit, QComboBox { background: white; border: 1px solid #0EA5E9; padding: 6px; border-radius: 4px; color: #111827; }
            QPushButton { background-color: #0EA5E9; color: white; padding: 8px; border-radius: 6px; }
        """)
        self.form = QFormLayout()

        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.last_name = QLineEdit()
        self.suffix = QLineEdit()
        self.email = QLineEdit()
        self.phone_number = QLineEdit()
        self.address = QLineEdit()
        self.username = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["admin", "staff"])
        self.department = QComboBox()
        self.department.addItems(["Administration", "Registrar"])
        self.status = QComboBox()
        self.status.addItems(["active", "inactive"])

        self.form.addRow("First Name", self.first_name)
        self.form.addRow("Middle Name", self.middle_name)
        self.form.addRow("Last Name", self.last_name)
        self.form.addRow("Suffix", self.suffix)
        self.form.addRow("Email", self.email)
        self.form.addRow("Phone", self.phone_number)
        self.form.addRow("Address", self.address)
        self.form.addRow("Username", self.username)
        self.form.addRow("Role", self.role)
        self.form.addRow("Department", self.department)
        self.form.addRow("Status", self.status)

        layout.addLayout(self.form)

        # Buttons
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.save_btn)

    def load_staff(self):
        staff = self.user_controller.get_user_by_id(self.user_id)
        if not staff or not isinstance(staff, dict):
            QMessageBox.critical(self, "Error", "Staff not found")
            self.reject()
            return

        self.personal_info_id = staff.get("personal_info_id")
        if self.personal_info_id is None:
            QMessageBox.critical(self, "Error", "Invalid staff data")
            self.reject()
            return

        self.first_name.setText(staff.get("first_name", ""))
        self.middle_name.setText(staff.get("middle_name") or "")
        self.last_name.setText(staff.get("last_name", ""))
        self.suffix.setText(staff.get("suffix") or "")
        self.email.setText(staff.get("email", ""))
        self.phone_number.setText(staff.get("phone_number") or "")
        self.address.setText(staff.get("address") or "")
        self.username.setText(staff.get("username", ""))

        # Set role dropdown
        role_index = self.role.findText(staff.get("role", "staff"))
        if role_index != -1:
            self.role.setCurrentIndex(role_index)

        # Set department dropdown
        dept_index = self.department.findText(staff.get("department", "Administration"))
        if dept_index != -1:
            self.department.setCurrentIndex(dept_index)

        # Set status dropdown
        status_index = self.status.findText(staff.get("status", "active"))
        if status_index != -1:
            self.status.setCurrentIndex(status_index)

    def save_changes(self):
        if self.personal_info_id is None:
            QMessageBox.critical(self, "Error", "Cannot save. Invalid staff data.")
            return

        first_name = self.first_name.text().strip()
        middle_name = self.middle_name.text().strip()
        last_name = self.last_name.text().strip()
        suffix = self.suffix.text().strip()
        email = self.email.text().strip()
        phone_number = self.phone_number.text().strip()
        address = self.address.text().strip()
        username = self.username.text().strip()
        role = self.role.currentText()
        department = self.department.currentText()
        status = self.status.currentText()

        if not username:
            QMessageBox.warning(self, "Validation", "Username cannot be empty.")
            return

        # Check for username conflict only if the username was changed
        current_staff = self.user_controller.get_user_by_id(self.user_id)
        if current_staff and current_staff.get("username") != username:
            if self.user_controller.check_username_exists(username):
                QMessageBox.warning(self, "Validation", "Username already exists.")
                return

        try:
            # Update personal info
            self.user_controller.update_personal_info(
                self.personal_info_id, first_name, middle_name, last_name,
                suffix, email, phone_number, address
            )

            # Get department ID
            department_id = self.user_controller.get_department_id(department)

            # Update user account
            self.user_controller.update_user(
                self.user_id, username=username, role=role, status=status, department_id=department_id
            )

            QMessageBox.information(self, "Success", f"Staff account '{username}' updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating staff account: {e}")
            print(f"Error updating staff account: {e}")