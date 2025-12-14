from models.db import Database
from datetime import datetime

class ReportController:
    def __init__(self, db: Database):
        self.db = db

    # 1. All Students Listing
    def get_all_students(self):
        query = """
        SELECT student_id, CONCAT(first_name, ' ', last_name) AS full_name,
               program, year_level, enrollment_date, status
        FROM students
        """
        return self.db.fetch_all(query)

    # 2. Enrollment by Course/Program (Count)
    def get_enrollment_summary(self):
        query = """
        SELECT program, COUNT(*) AS student_count
        FROM students
        GROUP BY program
        """
        return self.db.fetch_all(query)

    # 3. Student Profile (Individual)
    def get_student_profile(self, student_id):
        profile_query = f"""
        SELECT student_id, first_name, last_name, dob, contact, address, program, year_level, status
        FROM students
        WHERE student_id = '{student_id}'
        """
        courses_query = f"""
        SELECT c.course_code, c.course_name, e.section
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.student_id = '{student_id}'
        """
        profile = self.db.fetch_one(profile_query)
        courses = self.db.fetch_all(courses_query)
        return {"profile": profile, "courses": courses}

    # 4. New Registrations Report
    def get_new_registrations(self, start_date=None, end_date=None):
        query = "SELECT student_id, CONCAT(first_name, ' ', last_name) AS full_name, program, enrollment_date FROM students WHERE 1=1"
        if start_date:
            query += f" AND enrollment_date >= '{start_date}'"
        if end_date:
            query += f" AND enrollment_date <= '{end_date}'"
        return self.db.fetch_all(query)

    # 5. Pending Applications Report
    def get_pending_applications(self):
        query = """
        SELECT student_id, CONCAT(first_name, ' ', last_name) AS full_name, program, application_date, status
        FROM students
        WHERE status = 'Pending'
        """
        return self.db.fetch_all(query)
