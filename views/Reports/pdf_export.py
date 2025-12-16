import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTableWidget
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize, QPdfWriter
from PyQt6.QtCore import QMarginsF
from datetime import datetime


class PDFExport:
    """Reusable PDF export helper for table and full reports."""

    def __init__(self, parent, controller=None):
        self.parent = parent
        self.controller = controller
        # default directory for exports -> the Reports directory containing this file
        self.reports_dir = os.path.dirname(__file__)

    def export_current_tab(self, table: QTableWidget, title: str = "Report"):
        """Export the currently displayed QTableWidget to PDF."""
        path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export PDF", os.path.join(self.reports_dir, f"{title}.pdf"), "PDF Files (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        # Build headers
        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]

        # Build rows
        rows_html = []
        for row in range(table.rowCount()):
            cells = [f"<td>{table.item(row, col).text() if table.item(row, col) else ''}</td>"
                     for col in range(table.columnCount())]
            rows_html.append("<tr>" + "".join(cells) + "</tr>")

        html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #111827; }}
                    h1 {{ text-align: center; color: #2c3e50; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th {{ background-color: #f3f4f6; color: #1f2937; padding: 6px; border: 1px solid #d1d5db; font-weight: bold; }}
                    td {{ padding: 6px; border: 1px solid #e5e7eb; }}
                    tr:nth-child(even) {{ background-color: #f9fafb; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <table>
                    <thead>
                        <tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </body>
            </html>
            """

        try:
            doc = QTextDocument()
            doc.setHtml(html)

            pdf = QPdfWriter(path)
            pdf.setResolution(96)
            pdf.setPageLayout(QPageLayout(QPageSize(QPageSize.PageSizeId.A4),
                                          QPageLayout.Orientation.Portrait,
                                          QMarginsF(1, 1, 1, 1)))

            doc.print(pdf)
            QMessageBox.information(self.parent, "Export", "PDF exported successfully!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", str(e))

    def export_full_report_staff(self):
        """Export full report from the controller to PDF."""
        if not self.controller:
            QMessageBox.critical(self.parent, "Error", "No controller available for full report.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export Full Report", os.path.join(self.reports_dir, "Full_Staff_Report.pdf"), "PDF Files (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        # fetch staff data and headers (kept outside the .pdf extension branch)
        data = self.controller.get_all_staff()
        title = "Full Staff Report"
        headers = ["User ID", "First", "Middle", "Last", "Username", "Email", "Department", "Role", "Status",
                   "Created At"]
        # Build rows
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{item}</td>" for item in row) + "</tr>"
            for row in data
        )

        html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #111827; }}
                    h1 {{ text-align: center; color: #2c3e50; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th {{ background-color: #34495e; color: white; padding: 6px; border: 1px solid #2c3e50; text-transform: uppercase; }}
                    td {{ padding: 6px; border: 1px solid #dee2e6; }}
                    tr:nth-child(even) {{ background-color: #f8f9fa; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <table>
                    <thead>
                        <tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </body>
            </html>
            """

        try:
            doc = QTextDocument()
            doc.setHtml(html)
            pdf = QPdfWriter(path)
            pdf.setResolution(96)
            pdf.setPageLayout(QPageLayout(QPageSize(QPageSize.PageSizeId.A4),
                                          QPageLayout.Orientation.Portrait,
                                          QMarginsF(1, 1, 1, 1)))
            doc.print(pdf)
            QMessageBox.information(self.parent, "Export", f"{title} exported successfully!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", str(e))

    def export_full_report_students(self):
        """Export the student report using the exact same columns as the GUI table."""
        if not self.controller:
            QMessageBox.critical(self.parent, "Error", "No controller available for full report.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export Full Student Report", "Full_Student_Report.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        # 1. Use get_all_students() to match the GUI columns exactly
        data = self.controller.get_all_students()

        if not data:
            QMessageBox.warning(self.parent, "No Data", "No student data available to export.")
            return

        # 2. Hardcode the headers to match your View Reports tab
        headers = ["Student ID", "Full Name", "Program", "Year Level", "Enrollment Date", "Status"]

        # 3. Build Rows
        # We assume 'data' is a list of tuples/lists matching the header count
        rows_html = ""
        for row in data:
            cells = ""
            # If row is a dictionary, we fetch specific keys to match headers
            if isinstance(row, dict):
                # Adjust these keys based on your actual DB dictionary keys
                cells += f"<td>{row.get('student_id', '')}</td>"
                cells += f"<td>{row.get('full_name', '')}</td>"
                cells += f"<td>{row.get('program_code', '')}</td>"
                cells += f"<td>{row.get('year_level', '')}</td>"
                cells += f"<td>{row.get('enrollment_date', '')}</td>"
                cells += f"<td>{row.get('status', '')}</td>"

            # If row is a tuple/list (Standard for get_all_students), just iterate
            else:
                for item in row:
                    cells += f"<td>{item}</td>"

            rows_html += f"<tr>{cells}</tr>"

        title = "Full Student Report"

        # 4. Standard Professional Styling
        html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 10pt; color: #111827; }}
                    h1 {{ text-align: center; color: #2c3e50; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th {{ background-color: #34495e; color: white; padding: 8px; border: 1px solid #2c3e50; text-transform: uppercase; font-size: 9pt; }}
                    td {{ padding: 6px; border: 1px solid #dee2e6; font-size: 9pt; }}
                    tr:nth-child(even) {{ background-color: #f8f9fa; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <table>
                    <thead>
                        <tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </body>
            </html>
        """

        try:
            doc = QTextDocument()
            doc.setHtml(html)
            pdf = QPdfWriter(path)
            pdf.setResolution(96)

            # Use Portrait since we only have 6 columns
            pdf.setPageLayout(
                QPageLayout(
                    QPageSize(QPageSize.PageSizeId.A4),
                    QPageLayout.Orientation.Portrait,
                    QMarginsF(15, 15, 15, 15)
                )
            )
            doc.print(pdf)
            QMessageBox.information(self.parent, "Export", f"{title} exported successfully!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", str(e))