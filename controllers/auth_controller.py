import sqlite3
import hashlib

class AuthController:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._init_db()
        self.current_user = None

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        # Create default admin if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            self.register_user("admin", "admin123", role="admin")
        
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role="user"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            hashed_pw = self._hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, hashed_pw, role))
            conn.commit()
            conn.close()
            return True, "Usuario registrado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, str(e)

    def login_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        hashed_pw = self._hash_password(password)
        cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", 
                       (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = {"id": user[0], "username": user[1], "role": user[2]}
            return True, "Inicio de sesión exitoso"
        else:
            return False, "Usuario o contraseña inválidos"

    def logout(self):
        self.current_user = None

    def update_user(self, user_id, new_username=None, new_password=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if new_username:
                cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
                if self.current_user and self.current_user["id"] == user_id:
                    self.current_user["username"] = new_username
            if new_password:
                hashed_pw = self._hash_password(new_password)
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
            conn.commit()
            return True, "Perfil actualizado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

# Singleton instance
auth_controller = AuthController()
