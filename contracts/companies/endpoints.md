# Contrato — companies-service

**Responsable:** Estudiante A  
**Componente:** `companies-service`  
**Datos propios:** colección MongoDB `companies`  
**Ruta base pública:** `/api/v1/companies`  
**Autenticación:** Firebase ID Token (`Authorization: Bearer <token>`)

## Matriz de endpoints

| Método y ruta | Propósito | Auth | Solicitud | Respuestas |
|---|---|---|---|---|
| `GET /api/v1/health/` | Salud del servicio | No | — | `200` `{status, service}` |
| `GET /api/v1/companies/` | Listar empresas del usuario | Sí | — | `200` array, `401` |
| `POST /api/v1/companies/` | Crear empresa | Sí | JSON body | `201`, `400`, `401` |
| `GET /api/v1/companies/{id}/` | Obtener una empresa | Sí | — | `200`, `401`, `404` |
| `PUT /api/v1/companies/{id}/` | Actualizar una empresa | Sí | JSON body | `200`, `400`, `401`, `404` |
| `DELETE /api/v1/companies/{id}/` | Eliminar una empresa | Sí | — | `200`, `401`, `404` |

Especificación OpenAPI 3.0.3: `openapi.yaml`.

## Atributos

| Ubicación | Atributo | Tipo | Obligatorio | Regla |
|---|---|---|---|---|
| Request/Response | name | String | Sí | 3–100 caracteres |
| Request/Response | nit | String | Sí | Único |
| Request/Response | city | String | No | Puede omitirse |
| Request/Response | sector | String | No | Puede omitirse |
| Request/Response | descripcion | String | No | Puede omitirse |
| Request/Response | comunidad | String | No | Puede omitirse |
| Response | id | String | Sí | Generado por el backend |
| Response | owner_uid | String | Sí | uid Firebase |
| Response | created_at | String (ISO) | Sí | Generado |

## Errores estándar

- `401` `{"code":"UNAUTHENTICATED","message":"Token inválido o vencido"}`
- `400` `{"code":"INVALID_DATA","message":"...","errors":{...}}`

Ver ejemplos en `examples/`.
