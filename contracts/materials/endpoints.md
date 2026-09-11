# Contrato — materials-service

**Responsable:** Estudiante B  
**Componente:** `materials-service`  
**Datos propios:** colección MongoDB `material_listings`  
**Ruta base pública:** `/api/v1/materials`  
**Autenticación:** Firebase ID Token (`Authorization: Bearer <token>`)

## Matriz de endpoints

| Método y ruta | Propósito | Auth | Solicitud | Respuestas |
|---|---|---|---|---|
| `GET /api/v1/health/` | Salud del servicio | No | — | `200` `{status, service}` |
| `GET /api/v1/materials/` | Listar materiales del usuario | Sí | — | `200` array, `401` |
| `POST /api/v1/materials/` | Crear publicación | Sí | JSON body | `201`, `400`, `401` |
| `GET /api/v1/materials/{id}/` | Obtener una publicación | Sí | — | `200`, `401`, `404` |
| `PUT /api/v1/materials/{id}/` | Actualizar una publicación | Sí | JSON body | `200`, `400`, `401`, `404` |
| `DELETE /api/v1/materials/{id}/` | Eliminar una publicación | Sí | — | `200`, `401`, `404` |

Especificación OpenAPI 3.0.3: `openapi.yaml`.

## Atributos

| Ubicación | Atributo | Tipo | Obligatorio | Regla |
|---|---|---|---|---|
| Request/Response | company_id | String | Sí | ObjectId válido (referencia externa) |
| Request/Response | material_type | String | Sí | No vacío |
| Request/Response | quantity | Number | Sí | > 0 |
| Request/Response | unit | String | No | Default `kg` |
| Request/Response | location | String | No | Puede omitirse |
| Request/Response | descripcion | String | No | Puede omitirse |
| Request/Response | precio | Number | Sí | >= 0 |
| Request/Response | status | String | No | Default `available` |
| Response | id | String | Sí | Generado |
| Response | published_by | String | Sí | uid Firebase |
| Response | created_at | String (ISO) | Sí | Generado |

## Desacoplamiento

Este servicio **no** consulta la colección `companies`. Solo guarda `company_id` como referencia y filtra por `published_by`.

Ver ejemplos en `examples/`.
