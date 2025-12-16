from models.db import Database
from mysql.connector import Error
import hashlib

class AuthController:
    def __init__(self, db: Database):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username: str, password: str):
        """Verify user login and return user info if valid"""
        try:
            hashed = self.hash_password(password)
            query = """
                SELECT u.id, u.username, u.role, u.status,
                       u.department_id, u.personal_info_id
                FROM users u
                WHERE u.username = %s AND u.password = %s
            """
            row = self.db.fetch_one(query, (username, hashed))
            if row:
                user = {
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "status": row[3],
                    "department_id": row[4],
                    "personal_info_id": row[5]
                }
                if user["status"] != "active":
                    print("User is not active.")
                    return None
                return user
            return None
        except Error as e:
            print(f"Login error: {e}")
            return None

    def create_user(self, username: str, password: str, role: str = "staff", personal_info_id=None, department_id=None):
        """Create a new user"""
        try:
            hashed = self.hash_password(password)
            query = """
                INSERT INTO users (username, password, role, personal_info_id, department_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query, (username, hashed, role, personal_info_id, department_id))
            self.db.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Error as e:
            print(f"Error creating user: {e}")
            return None

    def update_password(self, user_id: int, new_password: str):
        """Update password for a user"""
        try:
            hashed = self.hash_password(new_password)
            query = "UPDATE users SET password = %s WHERE id = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(query, (hashed, user_id))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error updating password: {e}")
            return False

    def get_user_by_id(self, user_id: int):
        """Fetch user information by ID"""
        try:
            query = """
                SELECT u.id, u.username, u.role, u.status,
                       u.department_id, u.personal_info_id
                FROM users u
                WHERE u.id = %s
            """
            row = self.db.fetch_one(query, (user_id,))
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "status": row[3],
                    "department_id": row[4],
                    "personal_info_id": row[5]
                }
            return None
        except Error as e:
            print(f"Error fetching user: {e}")
            return None

    def check_username_exists(self, username: str) -> bool:
        """Check if username is already taken"""
        try:
            query = "SELECT COUNT(*) FROM users WHERE username = %s"
            row = self.db.fetch_one(query, (username,))
            return row[0] > 0
        except Error as e:
            print(f"Error checking username: {e}")
            return True

    def deactivate_user(self, user_id: int):
        """Set user status to inactive"""
        try:
            query = "UPDATE users SET status = 'inactive' WHERE id = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(query, (user_id,))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error deactivating user: {e}")
            return False

    def activate_user(self, user_id: int):
        """Set user status to active"""
        try:
            query = "UPDATE users SET status = 'active' WHERE id = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(query, (user_id,))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error activating user: {e}")
            return False

    def list_users(self, role=None):
        """List all users optionally filtered by role"""
        try:
            if role:
                query = "SELECT id, username, role, status FROM users WHERE role = %s ORDER BY created_at DESC"
                rows = self.db.fetch_all(query, (role,))
            else:
                query = "SELECT id, username, role, status FROM users ORDER BY created_at DESC"
                rows = self.db.fetch_all(query)
            users = []
            for row in rows:
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "status": row[3]
                })
            return users
        except Error as e:
            print(f"Error listing users: {e}")
            return []
