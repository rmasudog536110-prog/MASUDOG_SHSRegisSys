from PyQt6.QtWidgets import QMainWindow, QApplication
import sys

class StaffDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Staff Dashboard Test")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffDashboard()
    window.show()
    sys.exit(app.exec())
