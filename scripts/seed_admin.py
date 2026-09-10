# One-off helper: python scripts/seed_admin.py <username> <password>
# Creates the admin user if it doesn't exist, or updates its password if it does.
# Never commit the plaintext password.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt

from database import Base, SessionLocal, engine
import models

def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python scripts/seed_admin.py <username> <password>", file=sys.stderr)
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
        if admin:
            admin.password_hash = password_hash
            print(f"Updated password for admin user '{username}'.")
        else:
            db.add(models.AdminUser(username=username, password_hash=password_hash))
            print(f"Created admin user '{username}'.")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
