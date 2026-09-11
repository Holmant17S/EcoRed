# shared/firebase-auth

Módulo compartido para validar el ID Token de Firebase en cada microservicio.

- El frontend envía `Authorization: Bearer <ID_TOKEN>`.
- Cada servicio monta este paquete en `PYTHONPATH` (Compose/Dockerfile).
- Token ausente, inválido o vencido → HTTP **401** (`UNAUTHENTICATED`). El **403** solo aplica si el token es válido y falta permiso.
- No es un microservicio de autenticación: se reutiliza el proyecto Firebase de EcoRed.
