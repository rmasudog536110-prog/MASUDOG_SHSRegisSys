from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)

class ParentForm(QDialog):
    def __init__(self, student_controller, student_id, parent_id=None, student_parent_id=None):
        super().__init__()
        self.student_controller = student_controller
        self.student_id = student_id
        self.parent_id = parent_id
        self.student_parent_id = student_parent_id

        self.setWindowTitle("Parent / Guardian Form")
        self.resize(400, 400)
        self.init_ui()
        if self.parent_id:
            self.load_parent_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QDialog { background-color: #F3F6F8; }
            QLabel { color: #111827; }
            QLineEdit, QComboBox { background: white; border: 1px solid #0EA5E9; padding: 6px; border-radius: 4px; color: #111827; }
            QPushButton { background-color: #0EA5E9; color: white; padding: 8px; border-radius: 6px; }
            QPushButton#deleteBtn { background-color: #DC3545; }
        """)

        form = QFormLayout()

        self.relationship = QComboBox()
        self.relationship.addItems(["father", "mother", "guardian"])

        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone_number = QLineEdit()
        self.address = QLineEdit()
        self.occupation = QLineEdit()

        form.addRow("Relationship", self.relationship)
        form.addRow("First Name", self.first_name)
        form.addRow("Middle Name", self.middle_name)
        form.addRow("Last Name", self.last_name)
        form.addRow("Email", self.email)
        form.addRow("Phone Number", self.phone_number)
        form.addRow("Address", self.address)
        form.addRow("Occupation", self.occupation)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Add")
        self.save_btn.clicked.connect(self.save)
        btn_layout.addWidget(self.save_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.clicked.connect(self.delete)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        if not self.parent_id:
            self.update_btn.hide()
            self.delete_btn.hide()

    def load_parent_data(self):
        parent = self.student_controller.get_parent(self.parent_id)
        if not parent:
            print(self, "Error", "Parent data not found")
            QMessageBox.critical(self, "Error", "Parent data not found")
            self.reject()
            return

        self.first_name.setText(parent.get("first_name", ""))
        self.middle_name.setText(parent.get("middle_name", ""))
        self.last_name.setText(parent.get("last_name", ""))
        self.email.setText(parent.get("email", ""))
        self.phone_number.setText(parent.get("phone_number", ""))
        self.address.setText(parent.get("address", ""))
        self.occupation.setText(parent.get("occupation", ""))
        self.relationship.setCurrentText(parent.get("relationship", "father"))

        self.save_btn.hide()
        self.update_btn.show()
        self.delete_btn.show()

    def save(self):
        data = self._collect_data()
        if self.student_controller.add_parent(self.student_id, data):
            QMessageBox.information(self, "Success", "Parent added successfully")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add parent")

    def update(self):
        data = self._collect_data()
        if self.student_controller.update_parent(self.parent_id, data):
            QMessageBox.information(self, "Success", "Parent updated successfully")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update parent")

    def delete(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this parent?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if self.student_controller.delete_parent(self.student_parent_id):
                QMessageBox.information(self, "Deleted", "Parent deleted successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete parent")

    def _collect_data(self):
        return {
            "relationship": self.relationship.currentText(),
            "first_name": self.first_name.text().strip(),
            "middle_name": self.middle_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "email": self.email.text().strip(),
            "phone_number": self.phone_number.text().strip(),
            "address": self.address.text().strip(),
            "occupation": self.occupation.text().strip(),
            "is_primary": True
        }
