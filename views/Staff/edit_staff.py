from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QScrollArea, QWidget, QMessageBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
)

from controllers.userController import UserController



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

    def _update_staff(self):
        data = self._get_form_data()

        required_fields = [
            "first_name", "middle_name", "last_name",
            "email", "phone_number", "address", "username"
        ]

        for field in required_fields:
            if not data.get(field):
                QMessageBox.warning(self, "Validation Error",
                                    "Please fill in all fields (Suffix and Password are optional).")
                # Note: We usually DO NOT clear inputs on Edit error because users hate re-typing existing data
                return

        if "@" not in data["email"]:
            QMessageBox.warning(self, "Validation Error", "Invalid Email: Please include an '@' symbol.")
            return

        if not data["phone_number"].isdigit():
            QMessageBox.warning(self, "Validation Error", "Invalid Phone Number: Please enter integers only.")
            return

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

    def clear_inputs(self):
        """Helper to clear all input fields."""
        self.first_name.clear()
        self.middle_name.clear()
        self.last_name.clear()
        self.suffix.clear()
        self.email.clear()
        self.phone_number.clear()
        self.address.clear()
        self.username.clear()
        self.password.clear()
        # Reset Combos if desired
        self.role_combo.setCurrentIndex(0)
        self.department_combo.setCurrentIndex(0)
        if self.edit_mode:
            self.status_combo.setCurrentIndex(0)