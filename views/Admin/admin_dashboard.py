import sys

from controllers.authController import AuthController
from models.db import Database
from controllers.userController import UserController
from controllers.studentController import StudentController

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStatusBar
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from views.Students.student_view import AdminStudentDashboard
from views.Admin.staff_view import AdminStaffDashboard
from views.Admin.staff import CreateStaffForm
from views.Students.create_student import StudentCreationForm


class AdminDashboard(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, authController,userController, studentController, user_id, username):
        super().__init__()

        self.auth_controller = authController
        self.user_controller = userController
        self.student_controller = studentController
        self.db = userController.db
        self.current_user_id = user_id
        self.username = username

        self.init_ui()
        self.show_student_dashboard()
        self.load_statistics()

        # Refresh statistics periodically so stat cards reflect live changes
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self.load_statistics)
        self._stats_timer.start(2000)  # refresh every 2 seconds

    def init_ui(self):
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(1200, 700)

        central = QWidget()
        central.setStyleSheet("background-color: #D9D9D9;")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._create_header(layout)
        self.student_dashboard = AdminStudentDashboard(self)
        self.staff_dashboard = AdminStaffDashboard(self)
        self.staff_dashboard.hide()

        layout.addWidget(self.student_dashboard)
        layout.addWidget(self.staff_dashboard)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _create_header(self, parent):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background:#0EA5E9")

        layout = QHBoxLayout(header)

        header_icon = QPixmap(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\LOGO (1).png")
        header_label = QLabel()

        new_width = 60
        new_height = 60
        scaled_icon = header_icon.scaled(new_width, new_height)
        header_label.setPixmap(scaled_icon)

        title = QLabel("SHS Student Registration System")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color:#F6EBEB")

        user = QLabel(self.username.upper())
        user.setStyleSheet("color:white; font-weight:bold ")

        logout = QPushButton("Logout")
        logout.clicked.connect(self.logout)

        layout.addWidget(header_label)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user)
        layout.addWidget(logout)

        parent.addWidget(header)

    # ================= DASHBOARD SWITCHING =================

    def show_student_dashboard(self):
        self.staff_dashboard.hide()
        self.student_dashboard.show()
        self.student_dashboard.load_data()
        self.load_statistics()

    def show_staff_dashboard(self):
        self.student_dashboard.hide()
        self.staff_dashboard.show()
        self.staff_dashboard.load_data()
        self.load_statistics()

    # ================= STATISTICS =================

    def load_statistics(self):
        self.total_students_label.setText(
            str(self.student_controller.get_student_count())
        )
        self.active_students_label.setText(
            str(self.student_controller.get_enrolled_students())
        )
        self.pending_reviews_label.setText(
            str(self.student_controller.get_pending_student_count())
        )

        self.total_staff_label.setText(
            str(self.user_controller.get_staff_count())
        )
        self.active_staff_label.setText(
            str(self.user_controller.get_active_staff_count())
        )
        self.staff_pending_label.setText(
            str(self.user_controller.get_inactive_staff_count())
        )

    # ================= ACTIONS =================

    def create_student_account(self):
        dialog = StudentCreationForm(self.db, self.current_user_id)
        if dialog.exec():
            self.student_dashboard.load_data()
            self.load_statistics()

    def create_staff_account(self):
        dialog = CreateStaffForm(self.user_controller)
        if dialog.exec():
            self.staff_dashboard.load_data()
            self.load_statistics()

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

    auth_ctrl = AuthController(db)
    user_ctrl = UserController(db)
    student_ctrl = StudentController(db)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\LOGO (1).png"))

    dashboard = AdminDashboard(
        authController=auth_ctrl,
        userController=user_ctrl,
        studentController=student_ctrl,
        user_id=101,
        username="admin"
    )

    dashboard.show()
    sys.exit(app.exec())


