#!/usr/bin/env bash
# Publica las imágenes de EcoRed Circular en OCIR con etiquetado semántico.
# Ejecutar desde la raíz del proyecto (Git Bash / WSL):
#   bash scripts/publish-ocir.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export OCIR_ENDPOINT="${OCIR_ENDPOINT:-gru.ocir.io}"
export TENANCY_NAMESPACE="${TENANCY_NAMESPACE:-gr8wnrtapwvy}"
export VERSION="${VERSION:-v1.0.0}"
export REPOSITORIO="${REPOSITORIO:-ecored}"
export COMPONENTE="${COMPONENTE:-ALL}"

if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "VERSION debe ser semántica (ej. v1.0.0), recibido: $VERSION" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no está en PATH." >&2
  exit 1
fi

COMPONENTES=("frontend" "services/companies" "services/materials" "services/requests" "proxy")

image_name_for() {
  case "$1" in
    frontend) echo "frontend" ;;
    services/companies) echo "companies-service" ;;
    services/materials) echo "materials-service" ;;
    services/requests) echo "requests-service" ;;
    proxy) echo "proxy" ;;
    *) echo "$(basename "$1")" ;;
  esac
}

dockerfile_for() {
  case "$1" in
    frontend) echo "frontend/Dockerfile" ;;
    services/companies) echo "services/companies/Dockerfile" ;;
    services/materials) echo "services/materials/Dockerfile" ;;
    services/requests) echo "services/requests/Dockerfile" ;;
    proxy) echo "proxy/Dockerfile" ;;
    *) echo "$1/Dockerfile" ;;
  esac
}

echo "=== 1. Login en OCIR (${OCIR_ENDPOINT}) ==="
echo "Usuario típico: ${TENANCY_NAMESPACE}/oracleidentitycloudservice/<correo>"
echo "Password: Auth Token de OCI (no la contraseña de la cuenta)."
if [[ -n "${OCIR_AUTH_TOKEN:-}" && -n "${OCIR_USERNAME:-}" ]]; then
  printf '%s' "$OCIR_AUTH_TOKEN" | docker login "$OCIR_ENDPOINT" --username "$OCIR_USERNAME" --password-stdin
else
  docker login "$OCIR_ENDPOINT"
fi

published=()

for COMP in "${COMPONENTES[@]}"; do
  NOMBRE_SERVICIO="$(image_name_for "$COMP")"
  if [[ "$COMPONENTE" != "ALL" && "$COMPONENTE" != "$NOMBRE_SERVICIO" && "$COMPONENTE" != "$COMP" && "$COMPONENTE" != "$(basename "$COMP")" ]]; then
    continue
  fi

  DOCKERFILE="$(dockerfile_for "$COMP")"
  REPO="${REPOSITORIO}/${NOMBRE_SERVICIO}"
  IMAGE_TAG="${OCIR_ENDPOINT}/${TENANCY_NAMESPACE}/${REPO}:${VERSION}"

  echo
  echo "=== Procesando: ${NOMBRE_SERVICIO} (${VERSION}) ==="
  # Contexto = raíz del repo: los Dockerfiles copian shared/, services/ y mocks/.
  docker build --platform linux/amd64 -f "$DOCKERFILE" -t "${NOMBRE_SERVICIO}:${VERSION}" .
  docker tag "${NOMBRE_SERVICIO}:${VERSION}" "$IMAGE_TAG"
  docker push "$IMAGE_TAG"

  echo "=== Verificando imagen en OCIR ==="
  docker pull "$IMAGE_TAG"
  docker image inspect "$IMAGE_TAG" --format='{{.Id}} - {{.RepoTags}}'
  published+=("$IMAGE_TAG")
done

if [[ ${#published[@]} -eq 0 ]]; then
  echo "Ningún componente coincidió con COMPONENTE=${COMPONENTE}" >&2
  exit 1
fi

echo
echo "Publicación lista (solo tags semánticos, no latest):"
printf '  %s\n' "${published[@]}"
