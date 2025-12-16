from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QFrame, QDialog
)
from PyQt6.QtCore import Qt
from controllers.reportsController import ReportController
from views.Reports.student_report import StudentReportView
from views.Reports.staff_report import StaffReportView


class DashboardStats(QWidget):
    def __init__(self, parent, mode="students"):
        super().__init__()
        self.parent = parent
        self.mode = mode
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Conditional stat cards
        if self.mode == "students":
            layout.addWidget(self._quick_actions_student())
            layout.addLayout(self._stats_row_students())
        else:
            layout.addWidget(self._quick_actions_staff())
            layout.addLayout(self._stats_row_staff())


    def _stat_card(self, title_text, color_hex, callback=None):
        # Title label
        title_label = QLabel(title_text)
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Value label
        value_label = QLabel("0")  # Initialize with 0
        value_label.setObjectName("ValueLabel")
        value_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Horizontal layout for the card
        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 0)
        card_layout.setSpacing(10)
        card_layout.addWidget(title_label)
        card_layout.addStretch()
        card_layout.addWidget(value_label)

        # Card widget (clickable if callback provided)
        card_widget = QFrame()
        card_widget.setLayout(card_layout)
        if callback:
            def mousePressEvent(ev):
                try:
                    callback()
                except Exception:
                    pass
            card_widget.mousePressEvent = mousePressEvent

        card_widget.setFixedSize(300, 100)  # Adjust size as needed
        card_widget.setFrameShape(QFrame.Shape.StyledPanel)
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 2px solid {color_hex};
                border-radius: 5px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QLabel#TitleLabel {{
                font-size: 12pt;
                font-weight: 600;
                color: {color_hex};
                text-transform: uppercase;
            }}
            QLabel#ValueLabel {{
                font-size: 28pt;
                font-weight: bold;
                color: #333333;
                margin-right: 5px
            }}
            
            QLabel#TitleLabel, QLabel#ValueLabel {{
                background: transparent;
                border: none;
            }}

        """)

        return card_widget, value_label

    def _stats_row_students(self):
        row = QHBoxLayout()


        # Card 1: Total Students
        card_total, self.parent.total_students_label = self._stat_card(
            "Total Students",
            "#3498db",  # Blue
            callback=lambda: self._open_report_view(mode="students", select_tab=0)
        )
        row.addWidget(card_total)

        # Card 2: Active Students
        card_active, self.parent.active_students_label = self._stat_card(
            "Enrolled Students",
            "#2ecc71",  # Green
            callback=lambda: self._open_report_view(mode="students", select_tab=1)
        )
        row.addWidget(card_active)

        # Card 3: Pending Reviews
        card_pending, self.parent.pending_reviews_label = self._stat_card(
            "Pending Reviews",
            "#f39c12",
            callback=lambda: self._open_report_view(mode="students", select_tab=3)
        )
        row.addWidget(card_pending)


        return row

    def _stats_row_staff(self):
        row = QHBoxLayout()

        card, self.parent.total_staff_label = self._stat_card("Total Staff", "#9b59b6")
        row.addWidget(card)

        card, self.parent.active_staff_label = self._stat_card("Active Staff", "#1abc9c")
        row.addWidget(card)

        card, self.parent.staff_pending_label = self._stat_card("Inactive Staff", "#e74c3c")
        row.addWidget(card)

        return row

    def _quick_actions_student(self):
        group = QGroupBox("Quick Actions")
        group.setStyleSheet("color: black; font-weight: bold; font-size: 12pt;")
        layout = QGridLayout(group)

        layout.addWidget(self._action_btn(
            "Create Student Account", "#0EA5E9", self.parent.create_student_account
        ), 0, 0)

        layout.addWidget(self._action_btn(
            "Sort Table", "#2ecc71", lambda: getattr(self.parent, 'student_dashboard', None) and getattr(self.parent.student_dashboard, 'table', None) and self.parent.student_dashboard.table.refresh_table()
        ), 0, 1)

        if getattr(self.parent, 'username', '').lower() == 'admin':
            layout.addWidget(self._action_btn(
                "View Staff Table", "#2ecc71", self.parent.show_staff_dashboard
            ), 0, 2)

        layout.addWidget(self._action_btn(
            "View Report", "#0EA5E9", lambda: self._open_report_view_students(mode="students")
        ), 0, 3)

        return group

    def _quick_actions_staff(self):
        group = QGroupBox("Quick Actions")
        group.setStyleSheet("color: black; font-weight: bold; font-size: 12pt;")
        layout = QGridLayout(group)

        layout.addWidget(self._action_btn(
            "Create Staff Account", "#0EA5E9", self.parent.create_staff_account
        ), 0, 0)

        layout.addWidget(self._action_btn(
            "Sort Table", "#2ecc71", lambda: getattr(self.parent, 'staff_dashboard', None) and getattr(self.parent.staff_dashboard, 'table', None) and self.parent.staff_dashboard.table.refresh_table()
        ), 0, 1)

        layout.addWidget(self._action_btn(
            "View Student Table", "#2ecc71", self.parent.show_student_dashboard
        ), 0, 2)

        layout.addWidget(self._action_btn(
            "Export Report", "#0EA5E9", lambda: self._open_report_view_staff(mode="staff")
        ), 0, 3)

        return group

    def _open_report_view_students(self, mode="students"):
        """Open a dialog showing `ReportView` so the user can preview and export manually."""
        try:
            controller = ReportController(getattr(self.parent, 'db', None) or getattr(self.parent, 'user_controller', None).db)
        except Exception:
            controller = ReportController(getattr(self.parent, 'db', None))

        dialog = QDialog(self)
        dialog.setWindowTitle("Reports")
        dialog.resize(900, 700)
        layout = QVBoxLayout(dialog)

        report_view = StudentReportView(dialog, controller)
        layout.addWidget(report_view)

        dialog.exec()

    def _open_report_view_staff(self, mode="staff"):
        """Open a dialog showing `ReportView` so the user can preview and export manually."""
        try:
            controller = ReportController(getattr(self.parent, 'db', None) or getattr(self.parent, 'user_controller', None).db)
        except Exception:
            controller = ReportController(getattr(self.parent, 'db', None))

        dialog = QDialog(self)
        dialog.setWindowTitle("Reports")
        dialog.resize(900, 700)
        layout = QVBoxLayout(dialog)

        report_view = StaffReportView(dialog, controller)
        layout.addWidget(report_view)

        dialog.exec()

    def _action_btn(self, text, color, callback):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{color};
                color:white;
                padding:15px;
                font-weight:bold;
                border-radius:6px;
            }}
        """)
        btn.clicked.connect(callback)
        return btn
