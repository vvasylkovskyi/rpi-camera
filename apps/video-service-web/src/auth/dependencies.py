import base64
import os

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from shared.logger.logger import Logger

app = FastAPI()
security = HTTPBearer()
logger = Logger("authentication")

# Clerk settings
CLERK_JWKS_URL = os.environ["CLERK_JWKS_URL"]
# CLERK_AUDIENCE = "<your-audience>"  # Found in Clerk JWT template settings
# CLERK_ISSUER = f"https://<your-clerk-domain>"

# Cache JWKS to avoid fetching on every request
_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        resp = requests.get(CLERK_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def jwk_to_pem(jwk):
    """Convert a single JWK entry to PEM format"""
    n = int.from_bytes(base64.urlsafe_b64decode(jwk["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(jwk["e"] + "=="), "big")
    public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem


def get_public_key_for_kid(kid):
    jwks = get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwk_to_pem(key)
    raise HTTPException(status_code=401, detail="Public key not found")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        public_key = get_public_key_for_kid(unverified_header["kid"])

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            # audience=CLERK_AUDIENCE,
            # issuer=CLERK_ISSUER
        )
        return payload["sub"]  # Clerk stores user ID in `sub`
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error occurred while decoding token: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
