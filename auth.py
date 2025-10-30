# auth.py
import hashlib
import json
import os
from datetime import datetime

class Authentication:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.load_users()
    
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Default admin user
            self.users = {
                'admin': {
                    'password': self.hash_password('admin123'),
                    'role': 'admin',
                    'name': 'System Administrator',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            self.save_users()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        if username in self.users:
            if self.users[username]['password'] == self.hash_password(password):
                self.current_user = {
                    'username': username,
                    'role': self.users[username]['role'],
                    'name': self.users[username]['name']
                }
                return self.current_user
        return None
    
    def register(self, username, password, name, role='user'):
        if username not in self.users:
            self.users[username] = {
                'password': self.hash_password(password),
                'role': role,
                'name': name,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_users()
            return True
        return False
    
    def get_current_user(self):
        return self.current_user
    
    def logout(self):
        self.current_user = None
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)