"""Convierte 403+UNAUTHENTICATED en 401 a la salida HTTP."""


class UnauthenticatedStatusMiddleware:
    """
    DRF puede mutar AuthenticationFailed a 403 antes de enviar la respuesta.
    Este middleware garantiza el contrato del taller: token ausente/inválido = 401.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 403:
            return response

        content = getattr(response, "content", b"") or b""
        if b"UNAUTHENTICATED" not in content:
            return response

        response.status_code = 401
        response.reason_phrase = "Unauthorized"
        response["WWW-Authenticate"] = "Bearer"
        return response
