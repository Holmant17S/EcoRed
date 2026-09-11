# Contrato — requests-service

**Componente:** `requests-service`  
**Datos propios:** colección MongoDB `material_requests`  
**Ruta base pública:** `/api/v1/requests`  
**Autenticación:** Firebase ID Token (`Authorization: Bearer <token>`)

## Matriz de endpoints

| Método y ruta | Propósito | Auth | Solicitud | Respuestas |
|---|---|---|---|---|
| `GET /api/v1/health/` | Salud del servicio | No | — | `200` `{status, service}` |
| `GET /api/v1/requests/` | Listar solicitudes del usuario | Sí | — | `200` array, `401` |
| `POST /api/v1/requests/` | Crear solicitud | Sí | JSON body | `201`, `400`, `401` |
| `GET /api/v1/requests/{id}/` | Obtener una solicitud | Sí | — | `200`, `401`, `404` |
| `PUT /api/v1/requests/{id}/` | Actualizar una solicitud | Sí | JSON body | `200`, `400`, `401`, `404` |
| `DELETE /api/v1/requests/{id}/` | Eliminar una solicitud | Sí | — | `200`, `401`, `404` |

Especificación OpenAPI 3.0.3: `openapi.yaml`.

## Atributos

| Ubicación | Atributo | Tipo | Obligatorio | Regla |
|---|---|---|---|---|
| Request/Response | material_id | String | Sí | ObjectId válido (referencia externa) |
| Request/Response | company_id | String | Sí | ObjectId válido (referencia externa) |
| Request/Response | quantity | Number | Sí | > 0 |
| Request/Response | message | String | No | Puede omitirse |
| Request/Response | status | String | No | `pending` (alta), `accepted`, `rejected` |
| Response | id | String | Sí | Generado |
| Response | requested_by | String | Sí | uid Firebase |
| Response | created_at | String (ISO) | Sí | Generado |

## Desacoplamiento

Este servicio **no** consulta las colecciones `companies` ni `material_listings`. Solo guarda IDs de referencia y filtra por `requested_by`.
