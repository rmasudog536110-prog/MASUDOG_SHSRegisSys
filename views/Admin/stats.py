from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class DashboardStats(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # reference to AdminDashboard
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Stats rows
        layout.addWidget(self._quick_actions())
        layout.addLayout(self._stats_row_students())
        layout.addLayout(self._stats_row_staff())

        layout.addStretch()

    def _stat_card(self, title_text, color_hex):
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
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)
        card_layout.addWidget(title_label)
        card_layout.addStretch()
        card_layout.addWidget(value_label)

        # Card widget
        card_widget = QFrame()
        card_widget.setLayout(card_layout)

        card_widget.setFixedSize(350, 100)  # Adjust size as needed
        card_widget.setFrameShape(QFrame.Shape.StyledPanel)
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 2px solid {color_hex};
                border-radius: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QLabel#TitleLabel {{
                font-size: 12pt;
                font-weight: 600;
                color: #666666;
                text-transform: uppercase;
            }}
            QLabel#ValueLabel {{
                font-size: 28pt;
                font-weight: bold;
                color: #333333;
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
            "#3498db"  # Blue
        )
        row.addWidget(card_total)

        # Card 2: Active Students
        card_active, self.parent.active_students_label = self._stat_card(
            "Enrolled Students",
            "#2ecc71"  # Green
        )
        row.addWidget(card_active)

        # Card 3: Pending Reviews
        card_pending, self.parent.pending_reviews_label = self._stat_card(
            "Pending Reviews",
            "#f39c12"  # Orange/Yellow
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

    def _quick_actions(self):
        group = QGroupBox("Quick Actions")
        layout = QGridLayout(group)

        layout.addWidget(self._action_btn(
            "Create Student Account", "#0EA5E9", self.parent.create_student_account
        ), 0, 0)

        layout.addWidget(self._action_btn(
            "View Students Table", "#2ecc71", lambda: self.parent.tab_widget.setCurrentIndex(1)
        ), 0, 1)

        layout.addWidget(self._action_btn(
            "Create Staff Account", "#0EA5E9", self.parent.create_staff_account
        ), 0, 2)

        layout.addWidget(self._action_btn(
            "View Staff Table", "#2ecc71", lambda: self.parent.tab_widget.setCurrentIndex(2)
        ), 0, 3)

        return group

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
