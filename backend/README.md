# Esta carpeta solo guarda configuración local de los microservicios.
# No contiene código de aplicación (el código vive en services/).
#
# Archivos esperados (NO subir a Git):
# - .env                      → MONGODB_URI, DJANGO_SECRET_KEY, etc.
# - firebase-service-account.json
#
# docker-compose.yaml monta estos archivos en companies-service y materials-service.
