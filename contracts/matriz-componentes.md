# Matriz de componentes — equipo de 3

| Estudiante | Componente | Responsabilidad | Datos propios | Ruta base | Imagen OCIR |
|---|---|---|---|---|---|
| A | companies-service | Empresas del usuario autenticado | Mongo `companies` | `/api/v1/companies` | `ecored/companies-service:v1.0.0` |
| B | materials-service | Publicaciones de materiales | Mongo `material_listings` | `/api/v1/materials` | `ecored/materials-service:v1.0.0` |
| C | frontend + proxy | UI, mocks, enrutamiento Nginx | — | `/` | `ecored/frontend:v1.0.0` |

Auth compartida: Firebase (no es microservicio).
