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
        self.sort_order = "DESC"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Table label
        title = QLabel("Student Table")
        title.setStyleSheet(
            "font-size:16pt; font-weight:bold; color:black; text-align:center;"
        )
        layout.addWidget(title)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Strand", "Grade",
            "Enrollment", "Status", "Action"
        ])

        # Table style
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                color: black;
                background-color: white;
                gridline-color: black;
                font-size: 10pt;
            }

            QHeaderView::section {
                background-color: #E5E7EB;
                color: black;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }

            QTableWidget::item:selected {
                background-color: #BEE7FA;
            }

            QPushButton {
                background-color: #0EA5E9;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }

            QPushButton#deleteBtn {
                background-color: #e74c3c;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)

    def load_data(self):
        students = self.parent.student_controller.get_all_students(self.sort_order)
        self.table.setRowCount(len(students))

        for row, s in enumerate(students):
            student_id = s["id"]

            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            self.table.setItem(row, 0, create_centered_item(student_id))

            full_name = " ".join(filter(None, [
                s.get("first_name"), s.get("middle_name"), s.get("last_name")
            ]))
            self.table.setItem(row, 1, create_centered_item(full_name))
            self.table.setItem(row, 2, create_centered_item(s.get("email", "N/A")))
            self.table.setItem(row, 3, create_centered_item(s.get("strand", "")))
            self.table.setItem(row, 4, create_centered_item(s.get("grade", "")))
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
            delete_btn.setObjectName("deleteBtn")
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

    def refresh_table(self):
        self.sort_order = "ASC" if self.sort_order == "DESC" else "DESC"
        self.load_data()


class StaffTabs(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.sort_order = "DESC"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("Staff Table")
        title.setStyleSheet("font-size:16pt; font-weight:bold; color:black;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Department",
            "Created", "Status", "Action"
        ])

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                color: black;
                background-color: white;
                gridline-color: black;
                font-size: 10pt;
            }

            QHeaderView::section {
                background-color: #E5E7EB;
                color: black;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }

            QTableWidget::item:selected {
                background-color: #BEE7FA;
            }

            QPushButton {
                background-color: #0EA5E9;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }

            QPushButton#deleteBtn {
                background-color: #e74c3c;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)

    def load_data(self):
        users = self.parent.user_controller.get_all_users(self.sort_order)
        staff = [u for u in users if u.get("role") == "staff"]

        self.table.setRowCount(len(staff))

        for row, s in enumerate(staff):
            user_id = s["id"]

            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            self.table.setItem(row, 0, create_centered_item(user_id))
            full_name = " ".join(filter(None, [s.get("first_name"), s.get("last_name")])) or s.get("username", "")
            self.table.setItem(row, 1, create_centered_item(full_name))
            self.table.setItem(row, 2, create_centered_item(s.get("email", "N/A")))
            self.table.setItem(row, 3, create_centered_item(s.get("department", "")))
            self.table.setItem(row, 4, create_centered_item(s.get("created", "")))
            self.table.setItem(row, 5, create_centered_item(s.get("status", "")))

            actions = QWidget()
            action_layout = QHBoxLayout(actions)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, sid=user_id: self.edit_staff(sid))

            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("deleteBtn")
            delete_btn.clicked.connect(lambda _, sid=user_id: self.delete_staff(sid))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 6, actions)

    def refresh_table(self):
        self.sort_order = "ASC" if self.sort_order == "DESC" else "DESC"
        self.load_data()

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
