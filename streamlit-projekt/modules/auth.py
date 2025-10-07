"""
Authentication module for the Streamlit application
Implements login functionality with user management and session handling
"""
import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime
from modules import hashing

class AuthManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_user_table()
        self.create_default_admin()
    
    def ensure_user_table(self):
        """Ensure the Benutzer table exists and has correct structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Benutzer (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_on TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        if not self.user_exists('admin'):
            self.create_user('admin', 'admin123', is_admin=True)
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Benutzer WHERE username = ?', (username,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Create a new user"""
        try:
            if self.user_exists(username):
                return False
            
            created_on = datetime.now().isoformat()
            password_hash, _ = hashing.PasswordHasher.hash_password(password, created_on)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Benutzer (username, password_hash, is_admin, created_on)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, 1 if is_admin else 0, created_on))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Benutzers: {e}")
            return False
    
    def verify_login(self, username: str, password: str) -> tuple[bool, dict]:
        """Verify user login credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ID, username, password_hash, is_admin, created_on 
            FROM Benutzer WHERE username = ?
        ''', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return False, {}
        
        user_id, username, stored_hash, is_admin, created_on = user_data
        
        if hashing.PasswordHasher.verify_password(stored_hash, password, created_on):
            return True, {
                'id': user_id,
                'username': username,
                'is_admin': bool(is_admin),
                'created_on': created_on
            }
        return False, {}
    
    def get_all_users(self) -> list:
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT ID, username, is_admin, created_on FROM Benutzer')
        users = cursor.fetchall()
        conn.close()
        return users

def login_required(func):
    """Decorator to require login for certain pages"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    """Decorator to require admin privileges"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
            st.stop()
        if not st.session_state.get('user_data', {}).get('is_admin', False):
            st.error("Sie benötigen Administrator-Rechte für diese Seite.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def show_login_form(auth_manager: AuthManager):
    """Display login form"""
    st.title("🔐 Anmelden")
    
    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Anmelden")
        
        if submitted:
            if username and password:
                success, user_data = auth_manager.verify_login(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data
                    st.success(f"Willkommen, {user_data['username']}!")
                    st.rerun()
                else:
                    st.error("Ungültige Anmeldedaten!")
            else:
                st.error("Bitte geben Sie Benutzername und Passwort ein!")
    
    # Default credentials info
    st.info("Standard-Anmeldedaten: Benutzername: `admin`, Passwort: `admin123`")

def logout():
    """Logout user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}