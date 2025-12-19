from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QLabel, QHBoxLayout, QPushButton, QHeaderView
)
from views.Reports.pdf_export import PDFExport

class StaffReportView(QWidget):
    def __init__(self, parent, user_controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = user_controller
        self.pdf_exporter = PDFExport(self, controller=self.controller)
        self.init_ui()

    def init_ui(self):

        self.setStyleSheet("""
                    QMessageBox QLabel {
                        color: black;
                    }
                    QMessageBox QPushButton {
                        background-color: #0EA5E9;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 4px;
                    }
                """)

        main_layout = QVBoxLayout(self)

        # ---------- HEADER ----------
        header = QHBoxLayout()
        title = QLabel("Staff Reports")
        title.setStyleSheet("font-size:16pt; font-weight:bold; color:black;")
        header.addWidget(title)
        header.addStretch()

        self.export_btn = QPushButton("Export Full Staff Report")
        self.export_btn.setStyleSheet(
            "background-color:#0EA5E9; color:white; padding:8px; border-radius:6px;"
        )
        # Call PDFExport for full report
        self.export_btn.clicked.connect(lambda: self.pdf_exporter.export_full_report_staff())
        header.addWidget(self.export_btn)

        main_layout.addLayout(header)

        # ---------- TABS ----------
        self.tabs = QTabWidget()

        table_style = """
            QTableWidget {
                background-color: white;
                color: #1f2937;
                gridline-color: #e5e7eb;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                color: #374151; /* Darker font for headers */
                padding: 4px;
                border: 1px solid #d1d5db;
                font-weight: bold;
            }
        """

        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #f3f4f6;
                color: #4b5563; /* Gray font for inactive tabs */
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #d1d5db;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #0EA5E9; /* Blue font for the active tab */
                font-weight: bold;
                border-bottom-color: white; /* Makes it look connected to the pane */
            }
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                top: -1px;
            }
        """)

        self.all_staff_tab = QTableWidget()
        self.all_staff_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.all_staff_tab, "All Staff")

        self.active_staff_tab = QTableWidget()
        self.active_staff_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.active_staff_tab, "Active Staff")

        self.inactive_staff_tab = QTableWidget()
        self.inactive_staff_tab.setStyleSheet(table_style)
        self.tabs.addTab(self.inactive_staff_tab, "Inactive Staff")

        main_layout.addWidget(self.tabs)

        # ---------- FOOTER ----------
        footer = QHBoxLayout()
        footer.addStretch()

        self.export_tab_btn = QPushButton("Export Current Tab")
        self.export_tab_btn.setStyleSheet(
            "background-color:#0EA5E9; color:white; padding:8px 16px; border-radius:6px; font-weight:bold;"
        )
        self.export_tab_btn.clicked.connect(
            lambda: self.pdf_exporter.export_current_tab(self.tabs.currentWidget(),
                                                         title=self.tabs.tabText(self.tabs.currentIndex()))
        )
        footer.addWidget(self.export_tab_btn)
        main_layout.addLayout(footer)

        self.load_all()

    # -------------------------------------------------
    # DATA LOADERS
    # -------------------------------------------------

    def load_all(self):
        self.load_all_staff()
        self.load_active_staff()
        self.load_inactive_staff()

    def _headers(self):
        return [
            "User ID", "First Name", "Middle Name", "Last Name",
            "Username", "Email", "Department", "Role", "Status", "Created At"
        ]

    def load_all_staff(self):
        data = self.controller.get_all_staff()
        self._fill_table(self.all_staff_tab, self._headers(), data)

    def load_active_staff(self):
        data = [s for s in self.controller.get_all_staff() if s[8] == "active"]
        self._fill_table(self.active_staff_tab, self._headers(), data)

    def load_inactive_staff(self):
        data = [s for s in self.controller.get_all_staff() if s[8] == "inactive"]
        self._fill_table(self.inactive_staff_tab, self._headers(), data)

    def _fill_table(self, table, headers, data):
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))

        header = table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for row, record in enumerate(data):
            for col, value in enumerate(record):
                table.setItem(row, col, QTableWidgetItem(str(value)))


