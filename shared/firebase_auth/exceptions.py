"""Fuerza 401 en fallos de autenticación Firebase (nunca 403)."""

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response


def _unauthenticated_payload(exc):
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict) and detail.get("code"):
        return {
            "code": detail.get("code", "UNAUTHENTICATED"),
            "message": detail.get("message", "Token inválido o vencido"),
        }
    return {
        "code": "UNAUTHENTICATED",
        "message": "Token inválido o vencido",
    }


def firebase_exception_handler(exc, context):
    """
    DRF, si authenticate_header no aplica, muta AuthenticationFailed a 403.
    La rúbrica exige 401 para token ausente, inválido o vencido.
    403 queda solo para PermissionDenied (token válido sin permiso).
    """
    # Import diferido: rest_framework.views importa settings que cargan este paquete.
    from rest_framework.views import exception_handler

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        exc.status_code = status.HTTP_401_UNAUTHORIZED

    response = exception_handler(exc, context)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        payload = _unauthenticated_payload(exc)
        if response is None:
            response = Response(payload, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = payload
        response["WWW-Authenticate"] = "Bearer"

    return response
