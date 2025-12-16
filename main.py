import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from controllers.userController import UserController
# Models
from models.db import Database

# Controllers
from controllers.authController import AuthController
from controllers.studentController import StudentController

# Views
from views.login import LoginWindow

if __name__ == "__main__":
    # Initialize database
    db = Database()
    db.create_database_if_not_exists()
    db.connect()
    db.migrations()
    db.create_default_admin()
    db.create_default_staff()

    # Initialize controllers
    auth_ctrl = AuthController(db)
    user_ctrl = UserController(db)
    student_ctrl = StudentController(db)

    # Initialize PyQt application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(r"C:\Users\Machcreator\PycharmProjects\StudentRegisSys\images\LOGO (1).png"))

    # Pass controllers to the LoginWindow
    window = LoginWindow(auth_ctrl, student_ctrl)  # <-- updated
    window.resize(500, 600)
    window.show()

    def open_dashboard(user):
        role = user.get("role")
        user_id = user.get("id")
        username = user.get("username")

        if role.lower() == "admin":
            from views.Admin.admin_dashboard import AdminDashboard
            window.dashboard = AdminDashboard(auth_ctrl, user_ctrl, student_ctrl, user_id, username)
        else:
            from views.Staff.staff_dashboard import StaffDashboard
            window.dashboard = StaffDashboard(auth_ctrl, student_ctrl, user_id, username)

        window.dashboard.show()
        window.hide()  # close login window

    window.login_successful.connect(open_dashboard)

    sys.exit(app.exec())
