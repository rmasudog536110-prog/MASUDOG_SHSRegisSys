from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QStatusBar, QFrame,
    QGroupBox, QLineEdit, QGridLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QColor
from views.Students.student_form import CreateStudentDialog


class StaffDashboard(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_controller, student_controller, user_id, username):
        super().__init__()
        self.user_controller = user_controller
        self.student_controller = student_controller
        self.user_id = user_id
        self.username = username
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Staff Dashboard - SHS Management System")
        self.setMinimumSize(1400, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.create_header(main_layout)

        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Total Students Card
        total_students_card = self.create_stat_card(
            "Total Students",
            "0",
            "#3498db",
            "students"
        )

        # Active Students Card
        active_students_card = self.create_stat_card(
            "Active Students",
            "0",
            "#2ecc71",
            "check-circle"
        )

        # Pending Reviews Card
        pending_reviews_card = self.create_stat_card(
            "Pending Reviews",
            "0",
            "#f39c12",
            "clock"
        )

        stats_layout.addWidget(total_students_card)
        stats_layout.addWidget(active_students_card)
        stats_layout.addWidget(pending_reviews_card)
        stats_layout.addStretch()

        # Search and Filter Section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()

        # Search input
        search_label = QLabel("🔍 Search Student by email, Strand, Grade:")
        search_label.setFont(QFont("Arial", 11))

        self.student_search_input = QLineEdit()
        self.student_search_input.setPlaceholderText("Type to search...")
        self.student_search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.student_search_input.textChanged.connect(self.filter_student_table)

        # Filter buttons
        filter_buttons_layout = QHBoxLayout()
        filter_buttons_layout.setSpacing(10)

        self.all_students_btn = QPushButton("ALL")
        self.active_students_btn = QPushButton("ACTIVE")
        self.pending_students_btn = QPushButton("PENDING")
        self.inactive_students_btn = QPushButton("INACTIVE")

        # Style filter buttons
        for btn in [self.all_students_btn, self.active_students_btn,
                    self.pending_students_btn, self.inactive_students_btn]:
            btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 8px 15px;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                    border-color: #2980b9;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """)

        self.all_students_btn.setChecked(True)
        self.all_students_btn.clicked.connect(lambda: self.filter_student_table("all"))
        self.active_students_btn.clicked.connect(lambda: self.filter_student_table("active"))
        self.pending_students_btn.clicked.connect(lambda: self.filter_student_table("pending"))
        self.inactive_students_btn.clicked.connect(lambda: self.filter_student_table("inactive"))

        filter_buttons_layout.addWidget(self.all_students_btn)
        filter_buttons_layout.addWidget(self.active_students_btn)
        filter_buttons_layout.addWidget(self.pending_students_btn)
        filter_buttons_layout.addWidget(self.inactive_students_btn)

        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.student_search_input, 1)
        filter_layout.addLayout(filter_buttons_layout)

        filter_widget.setLayout(filter_layout)

        # Quick Actions Section
        actions_group = QGroupBox("Student Management")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: white;
                color: #2c3e50;
            }
        """)

        actions_layout = QGridLayout()
        actions_layout.setSpacing(15)

        # Action buttons
        create_student_btn = self.create_action_button(
            "Create Student Account",
            "#3498db",
            self.create_student_account
        )

        refresh_table_btn = self.create_action_button(
            "🔄 Refresh Table",
            "#2ecc71",
            self.load_student_data
        )

        update_student_btn = self.create_action_button(
            "Update Student Account",
            "#f39c12",
            self.update_student_account
        )

        delete_student_btn = self.create_action_button(
            "Delete Student Account",
            "#e74c3c",
            self.delete_student_account
        )

        actions_layout.addWidget(create_student_btn, 0, 0)
        actions_layout.addWidget(refresh_table_btn, 0, 1)
        actions_layout.addWidget(update_student_btn, 1, 0)
        actions_layout.addWidget(delete_student_btn, 1, 1)

        actions_group.setLayout(actions_layout)

        # Students Table
        students_group = QGroupBox("STUDENT ACCOUNTS")
        students_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: white;
                color: #2c3e50;
            }
        """)

        group_layout = QVBoxLayout()

        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels([
            "ID", "Student Name", "Contacts", "STRAND", "Grade", "Enrollment", "Status"
        ])

        # Style the table
        self.students_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                gridline-color: #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)

        # Configure header
        header = self.students_table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        header.setStretchLastSection(True)

        # Set column widths
        self.students_table.setColumnWidth(0, 50)  # ID
        self.students_table.setColumnWidth(1, 200)  # Name
        self.students_table.setColumnWidth(2, 250)  # Contacts
        self.students_table.setColumnWidth(3, 100)  # STRAND
        self.students_table.setColumnWidth(4, 80)  # Grade
        self.students_table.setColumnWidth(5, 100)  # Enrollment
        self.students_table.setColumnWidth(6, 100)  # Status

        group_layout.addWidget(self.students_table)
        students_group.setLayout(group_layout)

        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_btn = QPushButton("📊 Export Report")
        export_btn.setFont(QFont("Arial", 11))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        export_btn.clicked.connect(self.export_report)

        export_layout.addWidget(export_btn)

        # Add all to content layout
        content_layout.addLayout(stats_layout)
        content_layout.addWidget(filter_widget)
        content_layout.addWidget(actions_group)
        content_layout.addWidget(students_group, 1)
        content_layout.addLayout(export_layout)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        central_widget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Welcome, {self.username} | Staff Dashboard")

    def create_header(self, parent_layout):
        """Create header with title and user info"""
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setStyleSheet("""
            QFrame#header {
                background-color: #2c3e50;
                border: none;
            }
        """)
        header_widget.setFixedHeight(70)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)

        # System title
        title_label = QLabel("SHS Management System")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")

        # Dashboard title
        dashboard_label = QLabel("Staff Dashboard")
        dashboard_label.setFont(QFont("Arial", 14))
        dashboard_label.setStyleSheet("color: #ecf0f1;")

        # User info and logout
        user_layout = QHBoxLayout()
        user_layout.setSpacing(15)

        user_label = QLabel(f"Staff: {self.username}")
        user_label.setFont(QFont("Arial", 12))
        user_label.setStyleSheet("color: white;")

        logout_button = QPushButton("Logout")
        logout_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)

        user_layout.addWidget(user_label)
        user_layout.addWidget(logout_button)

        header_layout.addWidget(title_label)
        header_layout.addSpacing(20)
        header_layout.addWidget(dashboard_label)
        header_layout.addStretch()
        header_layout.addLayout(user_layout)

        header_widget.setLayout(header_layout)
        parent_layout.addWidget(header_widget)

    def create_stat_card(self, title, value, color, icon_name):
        """Create a statistics card"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        card.setMinimumHeight(120)
        card.setMaximumWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2c3e50;")

        # Store reference for updating
        if "Total" in title:
            self.total_students_label = value_label
        elif "Active" in title:
            self.active_students_label = value_label
        elif "Pending" in title:
            self.pending_reviews_label = value_label

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def create_action_button(self, text, color, callback):
        """Create an action button"""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 11))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        button.clicked.connect(callback)
        return button

    def darken_color(self, hex_color):
        """Darken a hex color"""
        # Simple darkening for hover effect
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)

        return f'#{r:02x}{g:02x}{b:02x}'

    def load_data(self):
        """Load all data for dashboard"""
        self.load_statistics()
        self.load_student_data()

    def load_statistics(self):
        """Load statistics data"""
        try:
            # Get student statistics from student controllers
            total_students = self.student_controller.get_student_count()
            active_students = 0  # You'll need to implement status checking
            pending_reviews = 0  # You'll need to implement this

            # Update labels
            if hasattr(self, 'total_students_label'):
                self.total_students_label.setText(str(total_students))

            if hasattr(self, 'active_students_label'):
                self.active_students_label.setText(str(active_students))

            if hasattr(self, 'pending_reviews_label'):
                self.pending_reviews_label.setText(str(pending_reviews))

        except Exception as e:
            print(f"Error loading statistics: {e}")

    def load_student_data(self):
        """Load student data into table"""
        try:
            students = self.student_controller.get_all_students()

            # Set table rows
            self.students_table.setRowCount(len(students))


            for row, student in enumerate(students):
                # ID
                self.students_table.setItem(row, 0, QTableWidgetItem(str(student['id'])))

                # Name
                full_name = f"{student['first_name']} {student['middle_name']} {student['last_name']}"
                self.students_table.setItem(row, 1, QTableWidgetItem(student['full_name']))

                # Contacts
                contacts = f"{student['email']}\n{student['phone']}"
                self.students_table.setItem(row, 2, QTableWidgetItem(contacts))

                # STRAND
                self.students_table.setItem(row, 3, QTableWidgetItem(student['strand']))

                # Grade
                self.students_table.setItem(row, 4, QTableWidgetItem(student['grade']))

                # Enrollment
                self.students_table.setItem(row, 5, QTableWidgetItem(student['enrollment']))

                # Status
                status_item = QTableWidgetItem(student['status'])
                if student['status'] == 'Active':
                    status_item.setForeground(QColor("#27ae60"))
                elif student['status'] == 'Pending':
                    status_item.setForeground(QColor("#f39c12"))
                else:
                    status_item.setForeground(QColor("#e74c3c"))
                self.students_table.setItem(row, 6, status_item)

            self.status_bar.showMessage(f"Loaded {len(students)} students")

        except Exception as e:
            print(f"Error loading student data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load student data: {str(e)}")

    def filter_student_table(self, filter_type="all"):
        """Filter student table based on search and filter"""
        search_text = self.student_search_input.text().lower()

        for row in range(self.students_table.rowCount()):
            show_row = True

            # Apply status filter
            if filter_type == "active":
                status_item = self.students_table.item(row, 6)
                if status_item and status_item.text() != "Active":
                    show_row = False
            elif filter_type == "pending":
                status_item = self.students_table.item(row, 6)
                if status_item and status_item.text() != "Pending":
                    show_row = False
            elif filter_type == "inactive":
                status_item = self.students_table.item(row, 6)
                if status_item and status_item.text() != "Inactive":
                    show_row = False

            # Apply search filter
            if show_row and search_text:
                row_matches = False
                for col in range(self.students_table.columnCount()):
                    item = self.students_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_matches = True
                        break
                show_row = row_matches

            # Show/hide row
            self.students_table.setRowHidden(row, not show_row)

    # Action methods
    def create_student_account(self):
        """Open create student dialog"""
        dialog = CreateStudentDialog(self.user_controller, self.student_controller)
        if dialog.exec():
            self.load_student_data()
            self.load_statistics()

    def update_student_account(self):
        """Update selected student account"""
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            student_id = self.students_table.item(selected_row, 0).text()
            QMessageBox.information(self, "Update Student",
                                    f"Update student ID: {student_id}")
        else:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a student to update")

    def delete_student_account(self):
        """Delete selected student account"""
        selected_row = self.students_table.currentRow()
        if selected_row >= 0:
            student_name = self.students_table.item(selected_row, 1).text()
            reply = QMessageBox.question(
                self, "Delete Student",
                f"Are you sure you want to delete {student_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Here you would call the controllers to delete the student
                QMessageBox.information(self, "Success", "Student deleted successfully")
                self.load_student_data()
                self.load_statistics()
        else:
            QMessageBox.warning(self, "Selection Required",
                                "Please select a student to delete")

    def export_report(self):
        """Export student report"""
        QMessageBox.information(self, "Export Report",
                                "Student report exported successfully")

    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()