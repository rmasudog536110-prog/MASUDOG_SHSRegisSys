from PyQt6.QtWidgets import QWidget, QVBoxLayout
from views.Dashboard.stat_cards import DashboardStats
from views.Dashboard.dashboard_tabs import StaffTabs

class AdminStaffDashboard(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout(self)

        self.stats = DashboardStats(parent, mode="staff")
        self.table = StaffTabs(parent)

        layout.addWidget(self.stats)
        layout.addWidget(self.table)

    def load_data(self):
        self.table.load_data()
