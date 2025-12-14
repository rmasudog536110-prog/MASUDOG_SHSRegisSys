from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QHBoxLayout,
    QLabel
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


class StudentTabs(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 🔹 Table label
        title = QLabel("Student Table")
        title.setStyleSheet("font-size:16pt; font-weight:bold; color:black; text-align:center;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Strand", "Grade",
            "Enrollment", "Status", "Action"
        ])

        # 🔹 Inline table styling (simple)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                background-color: white;
                gridline-color: black;
                font-size: 12pt;
            }

            QHeaderView::section {
                background-color: #E5E7EB;
                color: black;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }

            QTableWidget::item:selected {
                background-color: #D1D5DB;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)

    def load_data(self):
        students = self.parent.student_controller.get_all_students()
        self.table.setRowCount(len(students))

        for row, s in enumerate(students):
            student_id = s["id"]

            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            self.table.setItem(row, 0, create_centered_item(str(student_id)))

            full_name = " ".join(filter(None, [
                s.get("first_name"),
                s.get("middle_name"),
                s.get("last_name")
            ]))
            self.table.setItem(row, 1, create_centered_item(full_name))

            self.table.setItem(row, 2, create_centered_item(s.get("email", "N/A")))
            self.table.setItem(row, 3, create_centered_item(s.get("strand", "")))
            self.table.setItem(row, 4, create_centered_item(str(s.get("grade", ""))))
            self.table.setItem(row, 5, create_centered_item(s.get("enrollment", "")))

            status = s.get("status", "")
            status_item = create_centered_item(status)
            status_item.setForeground(
                QColor("green") if status.lower() == "enrolled" else QColor("red")
            )
            self.table.setItem(row, 6, status_item)

            # Action buttons
            actions = QWidget()
            action_layout = QHBoxLayout(actions)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, sid=student_id: self.edit_student(sid))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, sid=student_id: self.delete_student(sid))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 7, actions)

    def edit_student(self, student_id):
        from views.Students.edit_student import EditStudentForm
        dialog = EditStudentForm(self.parent.student_controller, student_id)
        if dialog.exec():
            self.load_data()

    def delete_student(self, student_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this student?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success = self.parent.student_controller.delete_student(student_id)
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete student.")


class StaffTabs(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 🔹 Table label
        title = QLabel("Staff Table")
        title.setStyleSheet("font-size:16pt; font-weight:bold; color:black;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Department",
            "Created", "Status", "Action"
        ])

        # 🔹 Inline table styling (simple)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                color: black;
                background-color: white;
                gridline-color: black;
                font-size: 11pt;
            }

            QHeaderView::section {
                background-color: #E5E7EB;
                color: black;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }

            QTableWidget::item:selected {
                background-color: #D1D5DB;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)


    def load_data(self):
        users = self.parent.user_controller.get_all_users()
        staff = [u for u in users if u.get("role") == "staff"]

        self.table.setRowCount(len(staff))

        for row, s in enumerate(staff):
            user_id = s["id"]

            # Helper function to create and center a QTableWidgetItem
            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            # Column 0: ID (Centered)
            self.table.setItem(row, 0, create_centered_item(user_id))

            # Column 1: Full Name (Usually Left-aligned, but centering it here if requested)
            full_name = " ".join(filter(None, [s.get("first_name"), s.get("last_name")])) or s.get("username", "")
            self.table.setItem(row, 1, create_centered_item(full_name))

            # Column 2: Email (Usually Left-aligned)
            self.table.setItem(row, 2, QTableWidgetItem(s.get("email", "N/A")))

            # Column 3: Department (Centered)
            self.table.setItem(row, 3, create_centered_item(s.get("department", "")))

            # Column 4: Created At (Centered)
            self.table.setItem(row, 4, create_centered_item(s.get("created", "")))

            # Column 5: Status (Centered)
            self.table.setItem(row, 5, create_centered_item(s.get("status", "")))

            # Action buttons
            actions = QWidget()
            action_layout = QHBoxLayout(actions)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, sid=user_id: self.edit_staff(sid))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, sid=user_id: self.delete_staff(sid))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 6, actions)

    def edit_staff(self, user_id):
        if hasattr(self.parent, "edit_staff"):
            self.parent.edit_staff(user_id)

    def delete_staff(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this staff account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success = self.parent.user_controller.delete_user(user_id)
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete staff.")
