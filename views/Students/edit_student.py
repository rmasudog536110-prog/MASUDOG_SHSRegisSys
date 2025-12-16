from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox

class EditStudentForm(QDialog):
    def __init__(self, student_controller, student_id):
        super().__init__()
        self.student_controller = student_controller
        self.student_id = student_id
        self.personal_info_id = None

        self.setWindowTitle("Edit Student")
        self.resize(500, 400)

        self.init_ui()
        self.load_student()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        # Theme consistent with dashboard
        self.setStyleSheet("""
            QDialog { background-color: #F3F6F8; }
            QLabel { color: #111827; }
            QLineEdit, QComboBox { background: white; border: 1px solid #0EA5E9; padding: 6px; border-radius: 4px; color: #111827; }
            QPushButton { background-color: #0EA5E9; color: white; padding: 8px; border-radius: 6px; }
            QPushButton#parentsBtn { background: transparent; color: #0EA5E9; border: none; padding: 4px; }
        """)
        self.form = QFormLayout()

        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(["Enrolled", "Pending", "Cancelled"])

        self.form.addRow("First Name", self.first_name)
        self.form.addRow("Middle Name", self.middle_name)
        self.form.addRow("Last Name", self.last_name)
        self.form.addRow("Email", self.email)
        self.form.addRow("Phone", self.phone)
        self.form.addRow("Address", self.address)
        self.form.addRow("Status", self.status)

        layout.addLayout(self.form)

        # Buttons
        self.parents_btn = QPushButton("Manage Parents / Guardian")
        self.parents_btn.setObjectName("parentsBtn")
        self.parents_btn.clicked.connect(self.open_parents)
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setProperty('class', 'primary')
        self.save_btn.clicked.connect(self.save_changes)

        layout.addWidget(self.parents_btn)
        layout.addWidget(self.save_btn)

    def load_student(self):
        s = self.student_controller.get_student_by_id(self.student_id)
        if not s or not isinstance(s, dict):
            QMessageBox.critical(self, "Error", "Student not found")
            self.reject()
            return

        self.personal_info_id = s.get("personal_info_id")
        if self.personal_info_id is None:
            QMessageBox.critical(self, "Error", "Invalid student data")
            self.reject()
            return

        self.first_name.setText(s.get("first_name", ""))
        self.middle_name.setText(s.get("middle_name") or "")
        self.last_name.setText(s.get("last_name", ""))
        self.email.setText(s.get("email", ""))
        self.phone.setText(s.get("phone_number") or "")
        self.address.setText(s.get("address") or "")

        # Set dropdown to current status
        status_text = s.get("status", "Active").capitalize()
        index = self.status.findText(status_text)
        if index != -1:
            self.status.setCurrentIndex(index)

    def save_changes(self):
        if self.personal_info_id is None:
            QMessageBox.critical(self, "Error", "Cannot save. Invalid student data.")
            return

        data = {
            "first_name": self.first_name.text(),
            "middle_name": self.middle_name.text(),
            "last_name": self.last_name.text(),
            "email": self.email.text(),
            "phone_number": self.phone.text(),
            "address": self.address.text(),
            "status": self.status.currentText().lower()
        }

        try:
            ok = self.student_controller.update_student(self.student_id, data)
            if ok:
                QMessageBox.information(self, "Saved", "Student updated")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update student")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Update failed: {str(e)}")
            print(self, "Error", f"Update failed: {str(e)}")

    def open_parents(self):
        try:
            from views.Students.add_parents import ParentForm
            parents = self.student_controller.get_parents_by_student(self.student_id)

            if parents:
                parent = parents[0]
                ParentForm(
                    self.student_controller,
                    self.student_id,
                    parent_id=parent["parent_id"],
                    student_parent_id=parent["student_parent_id"]  # <--- get it from the dict
                ).exec()
            else:
                ParentForm(self.student_controller, self.student_id).exec()

        except Exception as e:
            print(self, "Error", f"Cannot open Parents form: {str(e)}")
            QMessageBox.critical(self, "Error", f"Cannot open Parents form: {str(e)}")


