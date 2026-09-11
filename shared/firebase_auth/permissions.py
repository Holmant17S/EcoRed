"""Permiso que, con authenticate_header de Firebase, responde 401 si falta el token."""

from rest_framework import permissions


class FirebaseIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request.user, "is_authenticated", False))
