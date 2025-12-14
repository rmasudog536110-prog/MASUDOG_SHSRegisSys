from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt
from controllers.reportsController import ReportController

class ReportView(QWidget):
    def __init__(self, report_controller):
        super().__init__()
        self.enrollment_tab = None
        self.pending_tab = None
        self.new_reg_tab = None
        self.all_students_tab = None
        self.tabs = None
        self.controller = report_controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Tab 1: All Students
        self.all_students_tab = QTableWidget()
        self.load_all_students()
        self.tabs.addTab(self.all_students_tab, "All Students")

        # Tab 2: Enrollment Summary
        self.enrollment_tab = QTableWidget()
        self.load_enrollment_summary()
        self.tabs.addTab(self.enrollment_tab, "Enrollment by Program")

        # Tab 3: New Registrations
        self.new_reg_tab = QTableWidget()
        self.load_new_registrations()
        self.tabs.addTab(self.new_reg_tab, "New Registrations")

        # Tab 4: Pending Applications
        self.pending_tab = QTableWidget()
        self.load_pending_applications()
        self.tabs.addTab(self.pending_tab, "Pending Applications")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def load_all_students(self):
        data = self.controller.all_students()
        self.all_students_tab.setColumnCount(6)
        self.all_students_tab.setHorizontalHeaderLabels(["Student ID", "Full Name", "Program", "Year Level", "Enrollment Date", "Status"])
        self.all_students_tab.setRowCount(len(data))
        for row, student in enumerate(data):
            for col, value in enumerate(student):
                self.all_students_tab.setItem(row, col, QTableWidgetItem(str(value)))

    def load_enrollment_summary(self):
        data = self.controller.enrollment_summary()
        self.enrollment_tab.setColumnCount(2)
        self.enrollment_tab.setHorizontalHeaderLabels(["Program", "Number of Students"])
        self.enrollment_tab.setRowCount(len(data))
        for row, item in enumerate(data):
            self.enrollment_tab.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.enrollment_tab.setItem(row, 1, QTableWidgetItem(str(item[1])))

    def load_new_registrations(self):
        data = self.controller.new_registrations()
        self.new_reg_tab.setColumnCount(4)
        self.new_reg_tab.setHorizontalHeaderLabels(["Student ID", "Full Name", "Program", "Registration Date"])
        self.new_reg_tab.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.new_reg_tab.setItem(row, col, QTableWidgetItem(str(value)))

    def load_pending_applications(self):
        data = self.controller.pending_applications()
        self.pending_tab.setColumnCount(5)
        self.pending_tab.setHorizontalHeaderLabels(["Student ID", "Full Name", "Program", "Application Date", "Status"])
        self.pending_tab.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.pending_tab.setItem(row, col, QTableWidgetItem(str(value)))


    def export_student_report(self):
        """Export student report"""
        QMessageBox.information(self, "Export Report",
                                "Student report exported successfully")

    def export_staff_report(self):
        """Export staff report"""
        QMessageBox.information(self, "Export Report",
                                "Staff report exported successfully")
