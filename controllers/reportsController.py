from models.db import Database
from datetime import datetime

class ReportController:
    def __init__(self, db: Database):
        self.db = db

    # 1. All Students Listing
    def get_all_students(self):
        query = """
        SELECT
            s.id AS student_id,
            CONCAT(pi.first_name, ' ', COALESCE(pi.last_name, '')) AS full_name,
            st.strand_name AS program,
            gl.level AS year_level,
            s.registered_at AS enrollment_date,
            s.status
        FROM students s
        LEFT JOIN personal_information pi ON s.personal_info_id = pi.id
        LEFT JOIN strands st ON s.strand_id = st.id
        LEFT JOIN grade_levels gl ON s.grade_level_id = gl.id
        """
        return self.db.fetch_all(query)

    # 2. Enrollment by Course/Program (Count)
    def get_enrollment_summary(self):
        query = """
        SELECT st.strand_name AS program, COUNT(*) AS student_count
        FROM students s
        LEFT JOIN strands st ON s.strand_id = st.id
        GROUP BY st.strand_name
        """
        return self.db.fetch_all(query)

    # 3. Student Profile (Individual)
    def get_student_profile(self, student_id):
        profile_query = f"""
        SELECT s.id AS student_id, pi.first_name, pi.last_name, pi.date_of_birth AS dob,
               pi.phone_number AS contact, pi.address, st.strand_name AS program, gl.level AS year_level, s.status
        FROM students s
        LEFT JOIN personal_information pi ON s.personal_info_id = pi.id
        LEFT JOIN strands st ON s.strand_id = st.id
        LEFT JOIN grade_levels gl ON s.grade_level_id = gl.id
        WHERE s.id = %s
        """
        profile = self.db.fetch_one(profile_query, (student_id,))
        # courses/enrollments may not be present in this schema; return empty list for courses
        courses = []
        return {"profile": profile, "courses": courses}

    # 4. New Registrations Report
    def get_new_registrations(self, start_date=None, end_date=None):
        query = "SELECT s.id AS student_id, CONCAT(pi.first_name, ' ', COALESCE(pi.last_name, '')) AS full_name, st.strand_name AS program, s.registered_at AS enrollment_date FROM students s LEFT JOIN personal_information pi ON s.personal_info_id = pi.id LEFT JOIN strands st ON s.strand_id = st.id WHERE 1=1"
        params = []
        if start_date:
            query += " AND s.registered_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND s.registered_at <= %s"
            params.append(end_date)
        return self.db.fetch_all(query, tuple(params) if params else None)

    # 5. Pending Applications Report
    def get_pending_applications(self):
        query = """
        SELECT s.id AS student_id, CONCAT(pi.first_name, ' ', COALESCE(pi.last_name, '')) AS full_name,
               st.strand_name AS program, s.registered_at AS application_date, s.status
        FROM students s
        LEFT JOIN personal_information pi ON s.personal_info_id = pi.id
        LEFT JOIN strands st ON s.strand_id = st.id
        WHERE s.status = 'pending'
        """
        return self.db.fetch_all(query)

    def get_all_students_detailed(self):
        """Return detailed student info useful for full reports."""
        query = """
        SELECT
            s.id AS student_id,
            pi.first_name, pi.middle_name, pi.last_name, pi.date_of_birth,
            pi.phone_number, pi.address,
            st.strand_name AS program, gl.level AS year_level,
            s.registered_at AS registered_at, s.status, u.username AS created_by
        FROM students s
        LEFT JOIN personal_information pi ON s.personal_info_id = pi.id
        LEFT JOIN strands st ON s.strand_id = st.id
        LEFT JOIN grade_levels gl ON s.grade_level_id = gl.id
        LEFT JOIN users u ON s.created_by = u.id
        """
        return self.db.fetch_all(query)

    def get_all_staff(self):
        """Return staff listing with personal info and department."""
        query = """
        SELECT
            u.id AS user_id,
            pi.first_name, pi.middle_name, pi.last_name,
            u.username, pi.email, d.name AS department,
            u.role, u.status, u.created_at
        FROM users u
        LEFT JOIN personal_information pi ON u.personal_info_id = pi.id
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.role = 'staff'
        """
        return self.db.fetch_all(query)
