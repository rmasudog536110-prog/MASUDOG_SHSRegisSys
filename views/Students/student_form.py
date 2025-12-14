import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QTextEdit, QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt
from models.db import Database


class StudentCreationForm(QDialog):
    def __init__(self, db, created_by):
        super().__init__()
        self.db = db
        self.creator_user_id = created_by
        self.documents = {}
        self.setWindowTitle("Student Registration Form")
        self.resize(1200, 800)  # initial size
        self.setMinimumSize(1000, 700)
        self.setMaximumSize(1600, 1000)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        dashboard_btn = QPushButton("<- Back to Dashboard")
        dashboard_btn.clicked.connect(self.close)  # closes dialog
        main_layout.addWidget(dashboard_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setSpacing(10)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)


        # ---------------- Personal Information ----------------
        self.layout.addWidget(QLabel("<b>Student Personal Information</b>"))

        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.last_name = QLineEdit()
        self.suffix = QLineEdit()
        self.sex = QComboBox()
        self.sex.addItems(["M", "F", "Other"])
        self.nationality = QLineEdit()
        self.place_of_birth = QLineEdit()
        self.email = QLineEdit()
        self.phone_number = QLineEdit()
        self.date_of_birth = QLineEdit()
        self.address = QTextEdit()
        self.address.setFixedHeight(50)

        personal_fields = [
            ("First Name:", self.first_name),
            ("Middle Name:", self.middle_name),
            ("Last Name:", self.last_name),
            ("Suffix:", self.suffix),
            ("Sex:", self.sex),
            ("Nationality:", self.nationality),
            ("Place of Birth:", self.place_of_birth),
            ("Email:", self.email),
            ("Phone Number:", self.phone_number),
            ("Date of Birth (YYYY-MM-DD):", self.date_of_birth),
            ("Address:", self.address),
        ]

        grid_personal = QGridLayout()
        grid_personal.setHorizontalSpacing(10)
        grid_personal.setVerticalSpacing(15)
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

        # ---------------- Academic Information ----------------
        self.layout.addWidget(QLabel("<b>Academic Information</b>"))
        self.strand_combo = QComboBox()
        self.grade_level_combo = QComboBox()
        self.student_type_combo = QComboBox()
        self.student_type_combo.addItems(["new", "returning", "als", "pept", "transferee"])
        self.student_type_combo.currentTextChanged.connect(self.update_document_list)

        # Load strands and grade levels
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT id, strand_name FROM strands")
        self.strands = cursor.fetchall()
        self.strand_combo.addItems([s[1] for s in self.strands])
        cursor.execute("SELECT id, level FROM grade_levels")
        self.grade_levels = cursor.fetchall()
        self.grade_level_combo.addItems([g[1] for g in self.grade_levels])
        cursor.close()

        grid_academic = QGridLayout()
        grid_academic.setHorizontalSpacing(20)
        grid_academic.setVerticalSpacing(10)
        grid_academic.addWidget(QLabel("Strand:"), 0, 0)
        grid_academic.addWidget(self.strand_combo, 0, 1)
        grid_academic.addWidget(QLabel("Grade Level:"), 1, 0)
        grid_academic.addWidget(self.grade_level_combo, 1, 1)
        grid_academic.addWidget(QLabel("Student Type:"), 2, 0)
        grid_academic.addWidget(self.student_type_combo, 2, 1)
        self.layout.addLayout(grid_academic)

        # ---------------- Document Selection ----------------
        self.layout.addWidget(QLabel("<b>Required Documents</b>"))

        self.documents_master = {
            "Core": [
                "Original Report Card (Form 138)",
                "Certificate of Good Moral Character",
                "PSA Birth Certificate",
                "2x2 ID Pictures",
                "Enrollment Form"
            ],
            "Private": [
                "ESC/QVR Certificate (Private School only)"
            ],
            "Transferee": [
                "Transcript of Records (TOR) (Transferees only)",
                "List of Subjects Taken (Transferees only)",
                "Duly Signed Processing Form (Transferees only)"
            ]
        }

        self.docs_layout = QGridLayout()
        self.docs_layout.setHorizontalSpacing(20)
        self.docs_layout.setVerticalSpacing(15)
        self.layout.addLayout(self.docs_layout)

        self.update_document_list(self.student_type_combo.currentText())

        submit_button = QPushButton("Create Student")
        submit_button.clicked.connect(self.submit_form)
        main_layout.addWidget(submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def update_document_list(self, student_type=None):
        # Clear previous widgets
        while self.docs_layout.count():
            item = self.docs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.documents.clear()  # stores status of each document

        # Show all documents (Core + Private + Transferee)
        docs_to_show = (
                self.documents_master["Core"] +
                self.documents_master["Private"] +
                self.documents_master["Transferee"]
        )

        row, col = 0, 0
        for doc_name in docs_to_show:
            self.documents[doc_name] = "Not Provided"

            vbox = QVBoxLayout()
            label = QLabel(doc_name)
            dropdown = QComboBox()
            dropdown.addItems(["Provided", "Not Provided"])
            dropdown.currentTextChanged.connect(lambda text, d=doc_name: self.update_document_status(d, text))

            vbox.addWidget(label)
            vbox.addWidget(dropdown)

            self.docs_layout.addLayout(vbox, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def update_document_status(self, doc_name, status):
        self.documents[doc_name] = status

    def submit_form(self):
        student_data = {
            "first_name": self.first_name.text(),
            "middle_name": self.middle_name.text(),
            "last_name": self.last_name.text(),
            "suffix": self.suffix.text(),
            "sex": self.sex.currentText(),
            "nationality": self.nationality.text(),
            "place_of_birth": self.place_of_birth.text(),
            "email": self.email.text(),
            "phone_number": self.phone_number.text(),
            "date_of_birth": self.date_of_birth.text(),
            "address": self.address.toPlainText(),
            "strand_id": self.strands[self.strand_combo.currentIndex()][0],
            "grade_level_id": self.grade_levels[self.grade_level_combo.currentIndex()][0],
            "student_type": self.student_type_combo.currentText(),
            "documents_status": self.documents  # include dropdown selections
        }

        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO personal_information (
                    first_name, middle_name, last_name, suffix, sex, nationality,
                    place_of_birth, email, phone_number, date_of_birth, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_data["first_name"], student_data["middle_name"], student_data["last_name"],
                student_data["suffix"], student_data["sex"], student_data["nationality"],
                student_data["place_of_birth"], student_data["email"], student_data["phone_number"],
                student_data["date_of_birth"], student_data["address"]
            ))
            personal_info_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO students (personal_info_id, strand_id, grade_level_id, student_type, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                personal_info_id, student_data["strand_id"], student_data["grade_level_id"],
                student_data["student_type"], "pending", self.creator_user_id
            ))

            self.db.connection.commit()
            cursor.close()
            print(f"Student {student_data['first_name']} {student_data['middle_name']} {student_data['last_name']} created successfully!")
            self.accept()

        except Exception as e:
            self.db.connection.rollback()
            print(self.creator_user_id)
            print(f"Error: {e}")
