"""Autenticación Firebase compartida entre microservicios."""

import logging
import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

logger = logging.getLogger(__name__)
_initialized = False


def ensure_firebase_initialized() -> None:
    """Inicializa Firebase Admin una sola vez por proceso (lazy)."""
    global _initialized
    if _initialized or firebase_admin._apps:
        _initialized = True
        return

    load_dotenv(Path.cwd() / ".env")
    load_dotenv(Path.cwd().parent / ".env")

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not cred_path:
        raise RuntimeError("FIREBASE_CREDENTIALS_PATH no está definido")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    _initialized = True
    logger.info("Firebase Admin inicializado correctamente")


class FirebaseUser:
    """Usuario mínimo compatible con IsAuthenticated de DRF."""

    def __init__(self, uid, email=None):
        self.uid = uid
        self.email = email
        self.is_authenticated = True

    def __str__(self):
        return self.email or self.uid


class FirebaseAuthentication(BaseAuthentication):
    """Valida Authorization: Bearer <Firebase ID Token>."""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            raise exceptions.AuthenticationFailed(
                {
                    "code": "UNAUTHENTICATED",
                    "message": "Token mal formado",
                }
            )

        id_token = auth_header.split("Bearer ", 1)[1].strip()
        if not id_token:
            raise exceptions.AuthenticationFailed(
                {
                    "code": "UNAUTHENTICATED",
                    "message": "Token vacío",
                }
            )

        try:
            ensure_firebase_initialized()
            decoded_token = auth.verify_id_token(id_token)
        except exceptions.AuthenticationFailed:
            raise
        except Exception:
            logger.warning("Token de Firebase inválido o vencido")
            raise exceptions.AuthenticationFailed(
                {
                    "code": "UNAUTHENTICATED",
                    "message": "Token inválido o vencido",
                }
            )

        request.firebase_user = decoded_token
        user = FirebaseUser(
            uid=decoded_token.get("uid"),
            email=decoded_token.get("email"),
        )
        return (user, id_token)

    def authenticate_header(self, request):
        return "Bearer"
