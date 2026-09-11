# EcoRed Circular — Microservicios, Docker y OCIR

Proyecto descompuesto en **3 microservicios + 1 frontend**, contenerizado con Docker Compose y publicado en **Oracle Cloud Infrastructure Registry (OCIR)**.

## Arquitectura

```text
Browser → proxy (Nginx :8080)
            ├─ /                  → frontend
            ├─ /api/v1/companies  → companies-service
            ├─ /api/v1/materials  → materials-service
            └─ /api/v1/requests   → requests-service
                                      ↓
                              MongoDB Atlas + Firebase Auth
```

| Responsable | Componente | Imagen local | Imagen en OCIR |
|---|---|---|---|
| Estudiante A | Empresas | `companies-service:v1.0.0` | `gru.ocir.io/gr8wnrtapwvy/ecored/companies-service:v1.0.0` |
| Estudiante B | Materiales | `materials-service:v1.0.0` | `gru.ocir.io/gr8wnrtapwvy/ecored/materials-service:v1.0.0` |
| — | Solicitudes | `requests-service:v1.0.0` | `gru.ocir.io/gr8wnrtapwvy/ecored/requests-service:v1.0.0` |
| Estudiante C | UI + proxy | `frontend:v1.0.0` | `gru.ocir.io/gr8wnrtapwvy/ecored/frontend:v1.0.0` |

Auth: Firebase ID Token (no hay microservicio de autenticación).  
Contratos y mocks: `contracts/` (fichas + OpenAPI 3.0.3) y `mocks/` (JSON + json-server).

## Estructura del repositorio

```text
services/companies/     # Microservicio empresas
services/materials/     # Microservicio materiales
services/requests/      # Microservicio solicitudes
frontend/               # React (Vite) + Dockerfile
proxy/                  # Nginx gateway
shared/firebase_auth/   # Validación de token compartida
contracts/              # endpoints.md, examples JSON y openapi.yaml
mocks/                  # JSON simulados + README (Vite / json-server)
scripts/publish-ocir.sh # Build, tag semántico v1.0.0, push y verify en OCIR
http/ecored-api.http    # Colección REST Client (sin secretos)
backend/                # Solo secretos locales (no se suben)
docker-compose.yaml     # Integración local
docs/                   # Planificación del curso
```

## Requisitos previos

- Docker Desktop
- Archivo `backend/.env` (MongoDB Atlas, `DJANGO_SECRET_KEY`, etc.)
- Archivo `backend/firebase-service-account.json`
- Archivo `.env` en la raíz con las variables `VITE_FIREBASE_*` (para el build del frontend)
- Cuenta OCI con acceso a OCIR (para publicar)

Plantillas: `.env.example` y `frontend/.env.example`.  
Pruebas HTTP: `http/ecored-api.http` (REST Client).

---

## Docker Compose (integración local)

### 1. Configurar entorno

1. Copia `frontend/.env.example` → `frontend/.env` y completa Firebase.
2. Copia las mismas `VITE_FIREBASE_*` a `.env` en la raíz del proyecto (Compose las usa en el build).
3. Asegura `backend/.env` y `backend/firebase-service-account.json`.

### 2. Construir y levantar

```powershell
cd ecored-circular
docker compose -f docker-compose.yaml build
docker compose -f docker-compose.yaml up -d
docker compose -f docker-compose.yaml ps
```

### 3. Verificar

- App: http://localhost:8080
- Health empresas: http://localhost:8080/api/v1/health/companies
- Health materiales: http://localhost:8080/api/v1/health/materials
- Health solicitudes: http://localhost:8080/api/v1/health/requests

```powershell
docker compose -f docker-compose.yaml logs --tail=100
```

### 4. Detener

```powershell
docker compose -f docker-compose.yaml down
```

**Nota:** Si el puerto 8080 está ocupado, detén el contenedor viejo (`docker ps` → `docker stop <nombre>`).

---

## OCIR — qué se hizo

Se crearon imágenes versionadas (`v1.0.0`, no solo `latest`) y se publicaron en la tenancy del equipo. El microservicio `requests-service` se añade al mismo esquema.

### Datos de publicación usados

| Variable | Valor |
|---|---|
| Región / endpoint | `gru.ocir.io` |
| Tenancy namespace | `gr8wnrtapwvy` |
| Prefijo de repo | `ecored/` |
| Versión | `v1.0.0` |

### Rutas publicadas (evidencia)

```text
gru.ocir.io/gr8wnrtapwvy/ecored/companies-service:v1.0.0
gru.ocir.io/gr8wnrtapwvy/ecored/materials-service:v1.0.0
gru.ocir.io/gr8wnrtapwvy/ecored/requests-service:v1.0.0
gru.ocir.io/gr8wnrtapwvy/ecored/frontend:v1.0.0
```

### Cómo se publicó (script)

Desde la raíz, en Git Bash o WSL:

```bash
bash scripts/publish-ocir.sh
```

El script hace `docker login`, construye cada componente con tag semántico `v1.0.0` (nunca solo `latest`), empuja a OCIR y verifica con `docker pull` + `docker image inspect`.

Comandos equivalentes (PowerShell):

```powershell
$OCIR = "gru.ocir.io"
$NS   = "gr8wnrtapwvy"
$VER  = "v1.0.0"

# Login (usuario: namespace/oracleidentitycloudservice/correo  |  password: Auth Token OCI)
docker login $OCIR

# Tag + push por componente
docker tag companies-service:$VER $OCIR/$NS/ecored/companies-service:$VER
docker push  $OCIR/$NS/ecored/companies-service:$VER

docker tag materials-service:$VER $OCIR/$NS/ecored/materials-service:$VER
docker push  $OCIR/$NS/ecored/materials-service:$VER

docker tag frontend:$VER $OCIR/$NS/ecored/frontend:$VER
docker push  $OCIR/$NS/ecored/frontend:$VER
```

### Verificación individual (pedida por el taller)

```powershell
$VERIFY = "gru.ocir.io/gr8wnrtapwvy/ecored/companies-service:v1.0.0"
docker pull $VERIFY
docker image inspect $VERIFY
```

Repetir cambiando el nombre del componente (`materials-service`, `frontend`).

### Qué no se subió a OCIR ni al repo

- Auth Token de OCI  
- `.env` / secretos Django  
- `firebase-service-account.json`  
- `venv` / `node_modules`

---

## Pruebas de cada microservicio

```powershell
# companies
cd services\companies
$env:PYTHONPATH = "..\..\shared;$PWD"
python manage.py test tests

# materials
cd ..\materials
$env:PYTHONPATH = "..\..\shared;$PWD"
python manage.py test tests

# requests
cd ..\requests
$env:PYTHONPATH = "..\..\shared;$PWD"
python manage.py test tests

# frontend
cd ..\..\frontend
npm test
```

---

## Entrega Moodle

Archivo sugerido: `GrupoXX_Microservicios_OCIR.zip`

Git Bash / WSL (desde `ecored-circular/`):

```bash
zip -r GrupoXX_Microservicios_OCIR.zip . \
  -x "*.git*" \
  -x "*node_modules*" \
  -x "*__pycache__*" \
  -x "*.venv*" \
  -x "**/.env*" \
  -x "**/*firebase-service-account*.json" \
  -x "*.zip"
```

PowerShell:

```powershell
Compress-Archive -Path `
  README.md, docker-compose.yaml, .gitignore, .dockerignore, `
  services, frontend, proxy, contracts, mocks, shared, scripts, docs, backend `
  -DestinationPath GrupoXX_Microservicios_OCIR.zip -Force
```

(El `Compress-Archive` de Windows no excluye tan fino como `zip`; revisa que no entren `.env` ni el JSON de Firebase.)

Incluir:

1. Informe PDF (enlace al repo + rutas OCIR)  
2. Contratos (`contracts/`) y mocks (`mocks/`)  
3. `docker-compose.yaml`  
4. Evidencias OCIR (consola + `pull` / `inspect`)

No incluir dependencias generadas ni credenciales.

---

## Criterios del avance cubiertos

| Criterio | Evidencia |
|---|---|
| Arquitectura y responsabilidades | Diagrama + matriz en `contracts/` y `docs/` |
| Contratos y mocks | `contracts/` (OpenAPI 3.0.3 + JSON), `mocks/` |
| Desarrollo por componente | `services/*`, `frontend/` |
| Pruebas | `services/*/tests/` (200/201, 400, 401, 404) y `frontend` (Vitest) |
| Contenerización e integración | Dockerfiles + `docker-compose.yaml` |
| Publicación OCIR | Imágenes `v1.0.0` en `gru.ocir.io/.../ecored/` |
