import mysql.connector
from mysql.connector import Error
import hashlib

class Database:
    def __init__(self, host="localhost", user="root", password="", database="student_regis_sys"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def create_database_if_not_exists(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` DEFAULT CHARACTER SET 'utf8mb4'")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Database `{self.database}` has been created.")
        except mysql.connector.Error as err:
            print(f"Error creating database: {err}")
            raise

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if self.connection.is_connected():
                print(f"Connected to {self.database} database")
        except mysql.connector.Error as e:
            print(f"Connection error: {e}")
            raise

    def migrations(self):
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("Call create_database_if_not_exists() and connect() first.")

        cursor = self.connection.cursor()
        try:

            # PERSONAL INFORMATION TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal_information (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                middle_name VARCHAR(100),
                last_name VARCHAR(100) NOT NULL,
                suffix VARCHAR(20),
                sex ENUM('M','F','Other'),
                nationality VARCHAR(100),
                place_of_birth VARCHAR(255),
                email VARCHAR(150),
                phone_number VARCHAR(12),
                date_of_birth DATE,
                address TEXT,
                profile_picture_path VARCHAR(255), -- recommended: store path/URL, not blob
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                INDEX idx_fullname (last_name, first_name)
            )
            """)

            # DEPARTMENTS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name ENUM('Administration', 'Registrar'),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # USERS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                personal_info_id INT NULL,
                department_id INT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL, -- store hash
                role ENUM('admin','staff') NOT NULL DEFAULT 'staff',
                status ENUM('active', 'inactive') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_username (username),
                
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
                FOREIGN KEY (personal_info_id) REFERENCES personal_information(id) ON DELETE SET NULL
            ) AUTO_INCREMENT = 101
            """)

            # STRANDS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS strands (
                id INT AUTO_INCREMENT PRIMARY KEY,
                strand_name VARCHAR(50) UNIQUE NOT NULL, -- e.g. STEM, ABM, HUMSS
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # GRADE LEVELS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_levels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                level VARCHAR(10) UNIQUE NOT NULL, -- '11', '12'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # STUDENTS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                personal_info_id INT NOT NULL,
                strand_id INT,
                grade_level_id INT,
                student_type ENUM('new','returnee','als','pept','transferee') DEFAULT 'new',
                status ENUM('enrolled', 'pending', 'cancelled') DEFAULT 'pending',
                created_by INT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_student_personal (personal_info_id),
                
                FOREIGN KEY (personal_info_id) REFERENCES personal_information(id) ON DELETE CASCADE,
                FOREIGN KEY (strand_id) REFERENCES strands(id) ON DELETE SET NULL,
                FOREIGN KEY (grade_level_id) REFERENCES grade_levels(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )AUTO_INCREMENT=101001;
            """)

            # PARENTS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS parents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                personal_info_id INT NOT NULL,
                relationship ENUM('father', 'mother', 'guardian') NOT NULL,
                occupation VARCHAR(150),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_guardian_personal (personal_info_id),
                
                FOREIGN KEY (personal_info_id) REFERENCES personal_information(id) ON DELETE CASCADE
            ) AUTO_INCREMENT=1001;
            """)

            # STUDENT-PARENTS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_parents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                parents_id INT NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                
                INDEX idx_sg_student (student_id),
                INDEX idx_sg_guardian (parents_id),
                
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (parents_id) REFERENCES parents(id) ON DELETE CASCADE
            )
            """)

            # ACADEMIC RECORDS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                record_type ENUM('Form137','Form138','NCAE','A&E','PEPT','Other') NOT NULL,
                school_name VARCHAR(255) NOT NULL,
                school_year BIGINT NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                uploaded_by INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                
                INDEX idx_ac_student (student_id),
                INDEX idx_ac_type (record_type),
                
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """)

            # DOCUMENTS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                doc_type ENUM('PSA_BIRTH','GOOD_MORAL','ID_PICTURE','OTHERS') NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                uploaded_by INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
                
                INDEX idx_docs_student (student_id),
                INDEX idx_docs_type (doc_type)
            )
            """)

            # REGISTRATIONS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                school_year VARCHAR(20),
                required_documents TEXT, 
                is_complete BOOLEAN DEFAULT FALSE,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registered_by INT,
                
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (registered_by) REFERENCES users(id) ON DELETE SET NULL,
                
                INDEX idx_reg_student (student_id)
            )
            """)

            # AUDIT LOGS TABLE
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(255),
                object_type VARCHAR(100),
                object_id INT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_audit_user (user_id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_type VARCHAR(50),
                generated_by INT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY(generated_by) REFERENCES users(id) ON DELETE SET NULL
                )
                """)

            # Seed basic strands, grade levels, and departments if empty
            # Check departments
            cursor.execute("SELECT COUNT(*) FROM departments")
            count = cursor.fetchone()[0]

            if count == 0:
                departments = ['Administration', 'Registrar']
                dept_tuples = [(d,) for d in departments]
                cursor.executemany(
                    "INSERT INTO departments (name) VALUES (%s)",
                    dept_tuples
                )

            # Check strands
            cursor.execute("SELECT COUNT(*) FROM strands")
            count = cursor.fetchone()[0]  # fetchone() returns a tuple like (count,)

            if count == 0:
                strand = ['STEM', 'HUMSS', 'ABM', 'TVL', 'GAS']
                strands= [(s,) for s in strand]  # convert to list of tuples
                cursor.executemany(
                    "INSERT INTO strands (strand_name) VALUES (%s)",
                    strands
                )

            # Check grade levels
            cursor.execute("SELECT COUNT(*) FROM grade_levels")
            count = cursor.fetchone()[0]

            if count == 0:
                levels = ['11', '12']
                grade_levels = [(g,) for g in levels]
                cursor.executemany(
                    "INSERT INTO grade_levels (level) VALUES (%s)",
                    grade_levels
                )

            self.connection.commit()
            print("Migrations completed successfully.")
        except mysql.connector.Error as err:
            self.connection.rollback()
            print(f"Migration error: {err}")
            raise
        finally:
            cursor.close()

    def create_default_admin(self):
        """Create default admin user if not exists"""
        try:
            cursor = self.connection.cursor()
            # Check if admin exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            result = cursor.fetchone()

            if result[0] == 0:
                # Default password: admin123
                username = 'admin'
                hashed_password = self.hash_password("admin123")
                role = 'admin'
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed_password, role)
                )
                self.connection.commit()
                print("Default admin user created")

            cursor.close()
        except Error as e:
            print(f"Error creating default admin: {e}")

    def create_default_staff(self):
        """Create default staff with personal info and department if not exists"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'staff'")
            result = cursor.fetchone()

            if result[0] == 0:
                # 1️⃣ Create default personal information
                first_name = "First"
                middle_name = "Middle"
                last_name = "Staff"
                email = "staff@school.com"
                phone_number = "09123456789"

                cursor.execute("""
                    INSERT INTO personal_information (first_name,middle_name, last_name, email, phone_number)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, middle_name, last_name, email, phone_number))

                personal_info_id = cursor.lastrowid  # get the generated id

                department_name = "Administration"
                cursor.execute("SELECT id FROM departments WHERE name = %s", (department_name,))
                dep = cursor.fetchone()
                if dep:
                    department_id = dep[0]
                else:
                    cursor.execute("INSERT INTO departments (name) VALUES (%s)", (department_name,))
                    department_id = cursor.lastrowid

                username = 'staff'
                hashed_password = self.hash_password("staff123")
                role = 'staff'
                cursor.execute("""
                    INSERT INTO users (username, password, role, personal_info_id, department_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, hashed_password, role, personal_info_id, department_id))

                self.connection.commit()
                print("Default staff user created")

            cursor.close()

        except Error as e:
            print(f"Error creating default staff: {e}")

    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def fetch_all(self, query, params=None):
        """Helper to execute a query and return all rows."""
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """Helper to execute a query and return a single row."""
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        finally:
            cursor.close()


if __name__ == '__main__':
    db = Database()
    db.connect()
    db.migrations()
    db.create_default_admin()
    db.create_default_staff()