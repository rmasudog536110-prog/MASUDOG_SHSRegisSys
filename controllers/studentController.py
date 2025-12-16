from models.db import Database
from mysql.connector import Error
import os
import shutil


class StudentController:
    def __init__(self, db: Database):
        self.db = db

    def get_all_students(self, order="DESC"):
        """Fetch all students with related info and order by ID"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                # sanitize order direction
                if not isinstance(order, str) or order.upper() not in ("ASC", "DESC"):
                    order = "DESC"

                query = (
                    "SELECT "
                    "s.id, "
                    "pi.first_name, pi.middle_name, pi.last_name, pi.suffix, pi.sex, pi.nationality, pi.place_of_birth, pi.email, "
                    "pi.phone_number AS phone, pi.date_of_birth, pi.address, "
                    "st.strand_name AS strand, gl.level AS grade, s.student_type AS enrollment, s.status, s.registered_at AS created_at, u.username AS created_by "
                    "FROM students s "
                    "LEFT JOIN personal_information pi ON pi.id = s.personal_info_id "
                    "LEFT JOIN strands st ON st.id = s.strand_id "
                    "LEFT JOIN grade_levels gl ON gl.id = s.grade_level_id "
                    "LEFT JOIN users u ON u.id = s.created_by "
                    f"ORDER BY s.id {order}"
                )
                cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            print(f"Error getting students: {e}")
            return []

    def get_student_by_id(self, student_id):
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT 
                        s.id,
                        pi.first_name, pi.middle_name, pi.last_name,
                        pi.email, pi.phone_number, pi.address,
                        st.strand_name AS strand,
                        gl.level AS grade,
                        s.student_type,
                        s.status,
                        pi.id AS personal_info_id
                    FROM students s
                    JOIN personal_information pi ON pi.id = s.personal_info_id
                    LEFT JOIN strands st ON st.id = s.strand_id
                    LEFT JOIN grade_levels gl ON gl.id = s.grade_level_id
                    WHERE s.id = %s
                """, (student_id,))
                return cursor.fetchone()
        except Error as e:
            print("Fetch student error:", e)
            return None

    def create_student(self, student_data, created_by, document_files=None):
        """
        Create student with full personal information matching database schema

        student_data: dict with keys matching personal_information table + academic info
        document_files: dict with document type -> file path
        """
        try:
            with self.db.connection.cursor() as cursor:
                # 1️⃣ Insert personal information (all fields from form)
                cursor.execute("""
                    INSERT INTO personal_information (
                        first_name, middle_name, last_name, suffix, sex, 
                        nationality, place_of_birth, email, phone_number, 
                        date_of_birth, address
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    student_data['first_name'],
                    student_data.get('middle_name', ''),
                    student_data['last_name'],
                    student_data.get('suffix', ''),
                    student_data.get('sex', ''),
                    student_data.get('nationality', ''),
                    student_data.get('place_of_birth', ''),
                    student_data['email'],
                    student_data.get('phone_number', ''),
                    student_data.get('date_of_birth'),
                    student_data.get('address', '')
                ))
                personal_info_id = cursor.lastrowid

                # 2️⃣ Get strand_id from strand_name
                strand_id = None
                if 'strand' in student_data:
                    cursor.execute("SELECT id FROM strands WHERE strand_name = %s",
                                   (student_data['strand'],))
                    res = cursor.fetchone()
                    strand_id = res[0] if res else None

                # 3️⃣ Get grade_level_id from level
                grade_level_id = None
                if 'grade_level' in student_data:
                    cursor.execute("SELECT id FROM grade_levels WHERE level = %s",
                                   (student_data['grade_level'],))
                    res = cursor.fetchone()
                    grade_level_id = res[0] if res else None

                # 4️⃣ Insert student record
                cursor.execute("""
                    INSERT INTO students (
                        personal_info_id, strand_id, grade_level_id, 
                        student_type, status, created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    personal_info_id,
                    strand_id,
                    grade_level_id,
                    student_data.get('student_type', 'new'),
                    "pending",
                    created_by
                ))
                student_id = cursor.lastrowid

                # 5️⃣ Handle document uploads (matching database ENUM values)
                if document_files:
                    upload_dir = "uploaded_documents"
                    os.makedirs(upload_dir, exist_ok=True)

                    # Map form document names to database ENUM values
                    doc_type_mapping = {
                        "PSA Birth Certificate": "PSA_BIRTH",
                        "Certificate of Good Moral Character": "GOOD_MORAL",
                        "2x2 ID Pictures": "ID_PICTURE",
                        # Add more mappings as needed
                    }

                    for doc_name, file_path in document_files.items():
                        if file_path:  # file selected
                            # Get database doc_type
                            db_doc_type = doc_type_mapping.get(doc_name, "OTHERS")

                            filename = f"{student_id}_{db_doc_type}_{os.path.basename(file_path)}"
                            dest_path = os.path.join(upload_dir, filename)
                            shutil.copy(file_path, dest_path)

                            # Insert into documents table
                            cursor.execute("""
                                INSERT INTO documents (student_id, doc_type, file_path, uploaded_by)
                                VALUES (%s, %s, %s, %s)
                            """, (
                                student_id, db_doc_type, dest_path, created_by
                            ))

                self.db.connection.commit()
                return student_id

        except Error as e:
            self.db.connection.rollback()
            print(f"Error creating student: {e}")
            return None

    def update_student(self, student_id, data):
        """
        Update a student's personal info and status.
        `data` should be a dict with keys:
        first_name, middle_name, last_name, email, phone_number, address, status
        """
        try:
            with self.db.connection.cursor() as cursor:
                # Update personal_information table
                cursor.execute("""
                    UPDATE personal_information pi
                    JOIN students s ON s.personal_info_id = pi.id
                    SET pi.first_name=%s,
                        pi.middle_name=%s,
                        pi.last_name=%s,
                        pi.email=%s,
                        pi.phone_number=%s,
                        pi.address=%s,
                        s.status=%s
                    WHERE s.id=%s
                """, (
                    data.get("first_name", ""),
                    data.get("middle_name", ""),
                    data.get("last_name", ""),
                    data.get("email", ""),
                    data.get("phone_number", ""),
                    data.get("address", ""),
                    data.get("status", "pending"),
                    student_id
                ))
                self.db.connection.commit()
                return True
        except Error as e:
            self.db.connection.rollback()
            print("Error updating student:", e)
            return False

    def delete_student(self, id):
        """Delete a student by ID"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("DELETE FROM students WHERE id = %s", (id,))
                self.db.connection.commit()
                return True
        except Error as e:
            print(f"Error deleting student: {e}")
            return False

    def get_student_count(self):
        """Get total number of students"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM students")
                count = cursor.fetchone()[0]
                return count
        except Error as e:
            print(f"Error getting student count: {e}")
            return 0

    def get_enrolled_students(self):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'enrolled'")
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting enrolled students: {e}")
            return 0

    def get_pending_student_count(self):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'pending'")
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting pending students: {e}")
            return 0

    def check_student_id_exists(self, id):
        """Check if student ID already exists"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM students WHERE id = %s",
                    (id,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Error as e:
            print(f"Error checking student ID: {e}")
            return True

    def get_parents_by_student(self, student_id):
        """Return all parents/guardians of a student"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT sp.id AS student_parent_id, p.id AS parent_id, p.relationship, 
                           p.occupation, pi.first_name, pi.middle_name, pi.last_name, pi.email, pi.phone_number
                    FROM student_parents sp
                    JOIN parents p ON sp.parents_id = p.id
                    JOIN personal_information pi ON pi.id = p.personal_info_id
                    WHERE sp.student_id = %s
                """, (student_id,))
                return cursor.fetchall()
        except Error as e:
            print("Error fetching parents:", e)
            return []

    def get_parent(self, parent_id):
        """Return a single parent by parent ID"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT p.id AS parent_id, p.relationship, p.occupation,
                           pi.first_name, pi.middle_name, pi.last_name,
                           pi.email, pi.phone_number, pi.address
                    FROM parents p
                    JOIN personal_information pi ON pi.id = p.personal_info_id
                    WHERE p.id = %s
                """, (parent_id,))
                return cursor.fetchone()
        except Error as e:
            print("Error fetching parent:", e)
            return None

    def add_parent(self, student_id, parent_data):
        try:
            with self.db.connection.cursor() as cursor:
                # 1. Insert personal information
                cursor.execute("""
                    INSERT INTO personal_information
                        (first_name, middle_name, last_name, email, phone_number, address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    parent_data["first_name"],
                    parent_data.get("middle_name", ""),
                    parent_data["last_name"],
                    parent_data.get("email", ""),
                    parent_data.get("phone_number", ""),
                    parent_data.get("address", "")
                ))
                personal_info_id = cursor.lastrowid

                # 2. Insert into parents table
                cursor.execute("""
                    INSERT INTO parents (personal_info_id, relationship, occupation)
                    VALUES (%s, %s, %s)
                """, (
                    personal_info_id,
                    parent_data["relationship"],
                    parent_data.get("occupation", "")
                ))
                parent_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO student_parents (student_id, parents_id, is_primary)
                    VALUES (%s, %s, %s)
                """, (
                    student_id,
                    parent_id,
                    parent_data.get("is_primary", 0)
                ))
                self.db.connection.commit()
                return True

        except Exception as e:
            self.db.connection.rollback()
            print("Add parent error:", e)
            return False

    def update_parent(self, parent_id, parent_data):
        """Update a parent's personal info or relationship"""
        try:
            with self.db.connection.cursor() as cursor:
                # Update personal info
                cursor.execute("""
                    UPDATE personal_information pi
                    JOIN parents p ON pi.id = p.personal_info_id
                    SET pi.first_name=%s, pi.middle_name=%s, pi.last_name=%s,
                        pi.email=%s, pi.phone_number=%s, pi.address=%s,
                        p.relationship=%s, p.occupation=%s
                    WHERE p.id=%s
                """, (
                    parent_data["first_name"],
                    parent_data.get("middle_name", ""),
                    parent_data["last_name"],
                    parent_data.get("email", ""),
                    parent_data.get("phone_number", ""),
                    parent_data.get("address", ""),
                    parent_data["relationship"],
                    parent_data["occupation"],
                    parent_id
                ))
                self.db.connection.commit()
                return True
        except Error as e:
            self.db.connection.rollback()
            print("Error updating parent:", e)
            return False

    def delete_parent(self, student_parent_id):
        """Remove parent-student link and parent if no other student references"""
        try:
            with self.db.connection.cursor() as cursor:
                # Get parent_id
                cursor.execute("SELECT parents_id FROM student_parents WHERE id=%s", (student_parent_id,))
                res = cursor.fetchone()
                if not res:
                    return False
                parent_id = res[0]

                # Delete link
                cursor.execute("DELETE FROM student_parents WHERE id=%s", (student_parent_id,))

                # Check if parent linked to other students
                cursor.execute("SELECT COUNT(*) FROM student_parents WHERE parents_id=%s", (parent_id,))
                count = cursor.fetchone()[0]
                if count == 0:
                    cursor.execute("DELETE FROM parents WHERE id=%s", (parent_id,))

                self.db.connection.commit()
                return True
        except Error as e:
            self.db.connection.rollback()
            print("Error deleting parent:", e)
            return False
