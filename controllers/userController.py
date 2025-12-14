from models.db import Database
from mysql.connector import Error

class UserController:
    def __init__(self, db: Database):
        self.db = db

    def create_user(self, username, password, role, personal_info_id):
        try:
            with self.db.connection.cursor() as cursor:
                hashed_password = self.db.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password, role, personal_info_id) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, role, personal_info_id)
                )
                self.db.connection.commit()
                user_id = cursor.lastrowid
                return user_id
        except Error as e:
            print(f"Error creating user: {e}")
            return None

    def delete_user(self, user_id):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                self.db.connection.commit()
                return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False

    def verify_login(self, username, password):
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                hashed_password = self.db.hash_password(password)
                cursor.execute(
                    "SELECT id, username, role FROM users WHERE username = %s AND password = %s",
                    (username, hashed_password)
                )
                user = cursor.fetchone()
                return user
        except Error as e:
            print(f"Error verifying login: {e}")
            return None

    def get_all_users(self):
        """Return all users with personal info and department for staff"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                cursor.execute('''
                    SELECT
                        u.id, u.username, u.role, u.status, u.created_at AS created,
                        p.first_name, p.middle_name, p.last_name, p.email, d.name AS department
                    FROM users u
                    LEFT JOIN personal_information p ON u.personal_info_id = p.id
                    LEFT JOIN departments d ON d.id = u.department_id
                    ORDER BY u.created_at DESC
                ''')
                users = cursor.fetchall()
                return users
        except Error as e:
            print(f"Error getting users: {e}")
            return []

    def get_user_count(self):
        """Get total number of users"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                return count
        except Error as e:
            print(f"Error getting user count: {e}")
            return 0

    def check_username_exists(self, username):
        """Check if username already exists"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
                count = cursor.fetchone()[0]
                return count > 0
        except Error as e:
            print(f"Error checking username: {e}")
            return True

    def get_staff_count(self):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'staff'")
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting staff count: {e}")
            return 0

    def get_active_staff_count(self):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role='staff' AND status='active'"
                )
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting active staff: {e}")
            return 0

    def get_inactive_staff_count(self):
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role='staff' AND status!='active'"
                )
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting inactive staff: {e}")
            return 0


