from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel,
    QHBoxLayout, QPushButton, QHeaderView
)
from controllers.reportsController import ReportController
from views.Reports.pdf_export import PDFExport  # Import the PDFExport class


class StudentReportView(QWidget):
    def __init__(self, parent, report_controller: ReportController):
        super().__init__(parent)
        self.parent = parent
        self.controller = report_controller
        self.pdf_exporter = PDFExport(self, controller=self.controller)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        table_style = """
            QTableWidget {
                background-color: white;
                color: #1f2937;
                gridline-color: #e5e7eb;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                color: #374151;
                padding: 4px;
                border: 1px solid #d1d5db;
                font-weight: bold;
            }
        """

        # ---------- HEADER ----------
        header = QHBoxLayout()
        title = QLabel("View Reports")
        title.setStyleSheet("font-size:16pt; font-weight:bold; color: black;")
        header.addWidget(title)
        header.addStretch()

        self.back_btn = QPushButton("Back to Dashboard")
        self.back_btn.setStyleSheet(
            "background-color:#0EA5E9; border-radius:6px; padding:8px; color: white;"
        )
        self.back_btn.clicked.connect(
            lambda: (self.parent.close() if getattr(self, 'parent', None) else self.close())
        )
        header.addWidget(self.back_btn)

        self.export_btn = QPushButton("Export Full Report to PDF")
        self.export_btn.setStyleSheet(
            "background-color:#0EA5E9; color:white; padding:8px; border-radius:6px;"
        )
        # Call the correct PDFExport method (plural) — avoid AttributeError crash
        self.export_btn.clicked.connect(
            lambda: self.pdf_exporter.export_full_report_students()
        )
        header.addWidget(self.export_btn)

        main_layout.addLayout(header)

        # ---------- TABS ----------
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #f3f4f6;
                color: #4b5563;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #d1d5db;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #0EA5E9;
                font-weight: bold;
                border-bottom-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                top: -1px;
            }
        """)

        # Tab 1: All Students
        self.all_students_tab = QTableWidget()
        self.all_students_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.all_students_tab, "All Students")

        # Tab 2: Enrollment Summary
        self.enrollment_tab = QTableWidget()
        self.enrollment_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.enrollment_tab, "Enrollment by Program")

        # Tab 3: New Registrations
        self.new_reg_tab = QTableWidget()
        self.new_reg_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.new_reg_tab, "New Registrations")

        # Tab 4: Pending Applications
        self.pending_tab = QTableWidget()
        self.pending_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.pending_tab, "Pending Applications")

        main_layout.addWidget(self.tabs)

        # ---------- FOOTER ----------
        footer = QHBoxLayout()
        footer.addStretch()

        self.export_tab_btn = QPushButton("Export Current Tab")
        self.export_tab_btn.setStyleSheet(
            "background-color:#0EA5E9; color:white; padding:8px 16px; border-radius:6px; font-weight:bold;"
        )
        self.export_tab_btn.clicked.connect(
            lambda: self.pdf_exporter.export_current_tab(
                self.tabs.currentWidget(), self.tabs.tabText(self.tabs.currentIndex())
            )
        )
        footer.addWidget(self.export_tab_btn)

        main_layout.addLayout(footer)
        self.setLayout(main_layout)

        # Load data into tabs
        self.reload_all()

    # ------------------- LOAD DATA -------------------
    def reload_all(self):
        self.load_all_students()
        self.load_enrollment_summary()
        self.load_new_registrations()
        self.load_pending_applications()

    def load_all_students(self):
        data = self.controller.get_all_students()
        headers = ["Student ID", "Full Name", "Program", "Year Level", "Enrollment Date", "Status"]
        self._fill_table(self.all_students_tab, headers, data)

    def load_enrollment_summary(self):
        data = self.controller.get_enrollment_summary()
        headers = ["Program", "Number of Students"]
        self._fill_table(self.enrollment_tab, headers, data)

    def load_new_registrations(self):
        data = self.controller.get_new_registrations()
        headers = ["Student ID", "Full Name", "Program", "Registration Date"]
        self._fill_table(self.new_reg_tab, headers, data)

    def load_pending_applications(self):
        data = self.controller.get_pending_applications()
        headers = ["Student ID", "Full Name", "Program", "Application Date", "Status"]
        self._fill_table(self.pending_tab, headers, data)

    # ------------------- HELPER -------------------
    def _fill_table(self, table, headers, data):
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))

        header = table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
