# shared/firebase-auth

Módulo compartido para validar el ID Token de Firebase en cada microservicio.

- El frontend envía `Authorization: Bearer <ID_TOKEN>`.
- Cada servicio monta este paquete en `PYTHONPATH` (Compose/Dockerfile).
- No es un microservicio de autenticación: se reutiliza el proyecto Firebase de EcoRed.
