from models.db import Database
from mysql.connector import Error
from controllers.authController import AuthController


class UserController:
    def __init__(self, db: Database):
        self.db = db

    def delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                self.db.connection.commit()
                return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False

    def get_all_users(self, order="DESC"):
        """Fetch all users with related info"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                if not isinstance(order, str) or order.upper() not in ("ASC", "DESC"):
                    order = "DESC"

                query = (
                    "SELECT "
                    "u.id, u.username, u.role, u.status, u.created_at AS created, "
                    "p.first_name, p.middle_name, p.last_name, p.email, d.name AS department "
                    "FROM users u "
                    "LEFT JOIN personal_information p ON u.personal_info_id = p.id "
                    "LEFT JOIN departments d ON d.id = u.department_id "
                    f"ORDER BY u.created_at {order}"
                )
                cursor.execute(query)
                return cursor.fetchall()
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

    def get_staff_count(self):
        """Get total number of staff users"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'staff'")
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting staff count: {e}")
            return 0

    def get_active_staff_count(self):
        """Get number of active staff users"""
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
        """Get number of inactive staff users"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role='staff' AND status!='active'"
                )
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Error getting inactive staff: {e}")
            return 0

    def get_user_by_id(self, user_id: int):
        """Fetch user information by ID with personal info and department"""
        try:
            with self.db.connection.cursor(dictionary=True) as cursor:
                query = (
                    "SELECT u.id, u.username, u.role, u.status, u.personal_info_id, u.department_id, "
                    "p.first_name, p.middle_name, p.last_name, p.suffix, p.email, "
                    "p.phone_number, p.address, d.name as department "
                    "FROM users u "
                    "LEFT JOIN personal_information p ON u.personal_info_id = p.id "
                    "LEFT JOIN departments d ON u.department_id = d.id "
                    "WHERE u.id = %s"
                )
                cursor.execute(query, (user_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Error fetching user: {e}")
            return None

    def update_user(self, user_id: int, username: str = None, role: str = None, status: str = None, password: str = None, department_id: int = None):
        """Update user account information (username, role, status, password, department_id)"""
        try:
            # Update basic user info
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = %s")
                params.append(username)
            if role is not None:
                updates.append("role = %s")
                params.append(role)
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if department_id is not None:
                updates.append("department_id = %s")
                params.append(department_id)
               
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    self.db.connection.commit()
            
            # Update password separately if provided
            if password:
                auth_controller = AuthController(self.db)
                auth_controller.update_password(user_id, password)
            
            return True
        except Error as e:
            print(f"Error updating user: {e}")
            return False

    def update_personal_info(self, personal_info_id: int, first_name: str = None, 
                            middle_name: str = None, last_name: str = None, 
                            suffix: str = None, email: str = None, 
                            phone_number: str = None, address: str = None):
        """Update personal information"""
        try:
            updates = []
            params = []
            
            if first_name is not None:
                updates.append("first_name = %s")
                params.append(first_name)
            if middle_name is not None:
                updates.append("middle_name = %s")
                params.append(middle_name)
            if last_name is not None:
                updates.append("last_name = %s")
                params.append(last_name)
            if suffix is not None:
                updates.append("suffix = %s")
                params.append(suffix)
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            if phone_number is not None:
                updates.append("phone_number = %s")
                params.append(phone_number)
            if address is not None:
                updates.append("address = %s")
                params.append(address)
            
            if not updates:
                return True
            
            params.append(personal_info_id)
            query = f"UPDATE personal_information SET {', '.join(updates)} WHERE id = %s"
            
            with self.db.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.db.connection.commit()
                return True
        except Error as e:
            print(f"Error updating personal info: {e}")
            return False

    def check_username_exists(self, username: str, exclude_user_id: int = None) -> bool:
        """Check if username is already taken (optionally exclude a specific user)"""
        try:
            with self.db.connection.cursor() as cursor:
                if exclude_user_id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM users WHERE username = %s AND id != %s",
                        (username, exclude_user_id)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
                return cursor.fetchone()[0] > 0
        except Error as e:
            print(f"Error checking username: {e}")
            return False

    def create_personal_info(self, first_name: str, middle_name: str = None, 
                            last_name: str = None, suffix: str = None, 
                            email: str = None, phone_number: str = None, 
                            address: str = None) -> int:
        """Create a personal information record and return its ID"""
        try:
            with self.db.connection.cursor() as cursor:
                query = """
                    INSERT INTO personal_information 
                    (first_name, middle_name, last_name, suffix, email, phone_number, address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (first_name, middle_name, last_name, suffix, email, phone_number, address))
                self.db.connection.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Error creating personal info: {e}")
            return None

    def get_department_id(self, department_name: str) -> int:
        """Get department ID from department name"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM departments WHERE name = %s", (department_name,))
                result = cursor.fetchone()
                dept_id = result[0] if result else None
                return dept_id
        except Error as e:
            print(f"Error getting department: {e}")
            return None

    def create_user(self, username: str, password: str, role: str = "staff", personal_info_id: int = None, department_id: int = None) -> int:
        """Create a new user account using AuthController"""
        try:
            auth_controller = AuthController(self.db)
            user_id = auth_controller.create_user(username, password, role, personal_info_id, department_id)
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
