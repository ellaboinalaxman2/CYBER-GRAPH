from datetime import datetime
from ..models.user import UserRole
from ..repositories.user_repository import UserRepository

def seed_users():
    """Seed users collection with initial data"""
    
    user_repo = UserRepository()
    
    # Clear existing users
    user_repo.delete_many({})
    
    users = [
        {
            "user_id": "USR-001",
            "username": "admin",
            "email": "admin@cybergraph.com",
            "password_hash": "$2b$12$hashed_password_here",  # In real app, use proper hashing
            "role": UserRole.ADMIN,
            "full_name": "System Administrator",
            "department": "IT Security",
            "is_active": True,
            "permissions": ["ALL"],
            "preferences": {"theme": "dark", "notifications": True}
        },
        {
            "user_id": "USR-002",
            "username": "analyst1",
            "email": "analyst1@cybergraph.com",
            "password_hash": "$2b$12$hashed_password_here",
            "role": UserRole.ANALYST,
            "full_name": "Security Analyst",
            "department": "Security Operations",
            "is_active": True,
            "permissions": ["VIEW_ALERTS", "INVESTIGATE_ALERTS"],
            "preferences": {"theme": "light", "notifications": True}
        },
        {
            "user_id": "USR-003",
            "username": "viewer1",
            "email": "viewer1@cybergraph.com",
            "password_hash": "$2b$12$hashed_password_here",
            "role": UserRole.VIEWER,
            "full_name": "Security Viewer",
            "department": "Management",
            "is_active": True,
            "permissions": ["VIEW_DASHBOARD"],
            "preferences": {"theme": "light", "notifications": False}
        }
    ]
    
    for user in users:
        user_repo.create_user(user)
        print(f"Created user: {user['username']}")
    
    print(f"Seeded {len(users)} users")

if __name__ == "__main__":
    seed_users()