# scripts/create_jwt.py

import os
import jwt
from datetime import datetime, timedelta

# Replace with a strong secret in production
SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"

def create_jwt(user_id: str):
    payload = {
        "user_id": user_id,
        # "exp": datetime.utcnow() + timedelta(hours=1),
        # "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_jwt.py <user_id>")
    else:
        print(create_jwt(sys.argv[1]))
