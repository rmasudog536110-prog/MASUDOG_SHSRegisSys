from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QLineEdit, QPushButton, QMessageBox
)


class ParentForm(QDialog):
    def __init__(self, student_controller, student_id):
        super().__init__()
        self.student_controller = student_controller
        self.student_id = student_id

        self.setWindowTitle("Add Parent / Guardian")
        self.resize(400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.relationship = QComboBox()
        self.relationship.addItems(["father", "mother", "guardian"])

        self.personal_info_id = QLineEdit()
        self.occupation = QLineEdit()

        form.addRow("Relationship", self.relationship)
        form.addRow("Personal Info ID", self.personal_info_id)
        form.addRow("Occupation", self.occupation)

        layout.addLayout(form)

        btn = QPushButton("Save")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        data = {
            "personal_info_id": int(self.personal_info_id.text()),
            "relationship": self.relationship.currentText(),
            "occupation": self.occupation.text(),
            "is_primary": True
        }

        if self.student_controller.add_parent(self.student_id, data):
            QMessageBox.information(self, "Saved", "Parent added")
            self.accept()
