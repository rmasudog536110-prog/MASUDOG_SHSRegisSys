import sys
from models.db import Database
from controllers.userController import UserController
from controllers.studentController import StudentController
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame, QStatusBar
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from views.Admin.stats import DashboardStats
from views.Admin.tabs import StudentTabs, StaffTabs
from views.Admin.staff import CreateStaffForm
from views.Students.student_form import StudentCreationForm


class AdminDashboard(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, userController, studentController, user_id, username):
        super().__init__()

        self.user_controller = userController
        self.student_controller = studentController
        self.db = userController.db
        self.current_user_id = user_id

        self.user_id = user_id
        self.username = username

        self.init_ui()
        self.load_data()
        self.load_statistics()


    def init_ui(self):
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(1400, 800)

        central = QWidget()
        central.setStyleSheet("background-color: #D9D9D9;")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._create_header(layout)

        self.tab_widget = QTabWidget()
        self.dashboard_tab = DashboardStats(self)
        self.students_tab = StudentTabs(self)
        self.staff_tab = StaffTabs(self)

        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.students_tab, "Students")
        self.tab_widget.addTab(self.staff_tab, "Staff")

        layout.addWidget(self.tab_widget)
        self.setCentralWidget(central)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _create_header(self, parent):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background:#0EA5E9")

        layout = QHBoxLayout(header)
        title = QLabel("SHS Management System")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color:#F6EBEB")

        user = QLabel(f"Admin: {self.username}")
        user.setStyleSheet("color:#F6EBEB")

        logout = QPushButton("Logout")
        logout.clicked.connect(self.logout)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user)
        layout.addWidget(logout)

        parent.addWidget(header)

    def load_data(self):
        # Safely call load_data on tabs if they exist
        if hasattr(self.students_tab, "load_data"):
            self.students_tab.load_data()
        if hasattr(self.staff_tab, "load_data"):
            self.staff_tab.load_data()
        # Commented out statistics to avoid undefined labels
        self.load_statistics()

    def load_statistics(self):
        # Students
        total_students = self.student_controller.get_student_count()
        enrolled_students = self.student_controller.get_enrolled_students()
        pending_students = self.student_controller.get_pending_student_count()

        self.total_students_label.setText(str(total_students))
        self.active_students_label.setText(str(enrolled_students))
        self.pending_reviews_label.setText(str(pending_students))

        # Staff
        total_staff = self.user_controller.get_staff_count()
        active_staff = self.user_controller.get_active_staff_count()
        inactive_staff = self.user_controller.get_inactive_staff_count()

        self.total_staff_label.setText(str(total_staff))
        self.active_staff_label.setText(str(active_staff))
        self.staff_pending_label.setText(str(inactive_staff))

    # ---------------- Fixed student creation ----------------
    def create_student_account(self):
        # Pass the correct parameters: db and current_user_id
        dialog = StudentCreationForm(self.db, self.current_user_id)
        if dialog.exec():  # This opens the modal form
            self.load_data()  # Refresh the student tab

    # ---------------- Staff creation ----------------
    def create_staff_account(self):
        dialog = CreateStaffForm(self.user_controller)
        if dialog.exec():
            self.load_data()

    def logout(self):
        self.logout_requested.emit()
        self.close()


if __name__ == "__main__":
    db = Database()
    db.create_database_if_not_exists()
    db.connect()
    db.migrations()
    db.create_default_admin()
    db.create_default_staff()

    user_ctrl = UserController(db)
    student_ctrl = StudentController(db)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(r"C:\Users\Machcreator\Downloads\LOGO (1).png"))

    dashboard = AdminDashboard(
        userController=user_ctrl,
        studentController=student_ctrl,
        user_id=101,
        username="admin"
    )

    dashboard.show()
    sys.exit(app.exec())


