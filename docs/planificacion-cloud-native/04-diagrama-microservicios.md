# Diagrama de microservicios — EcoRed Circular (equipo de 3)

```text
                    ┌─────────────────────┐
                    │   Cliente (Browser) │
                    └──────────┬──────────┘
                               │  http://localhost:8080
                               ▼
                    ┌─────────────────────┐
                    │  proxy (Nginx)      │
                    │  rutas estables     │
                    └──┬───────┬───────┬──┘
                       │       │       │
         /             │       │       │
         ▼             │       │       │
┌──────────────┐       │       │       │
│   frontend   │       │       │       │
│  React SPA   │       │       │       │
└──────────────┘       │       │       │
                       │       │       │
        /api/v1/companies/     │   /api/v1/materials/
                       ▼       │       ▼
            ┌──────────────────┐   ┌──────────────────┐
            │ companies-service│   │ materials-service│
            │  Django + DRF    │   │  Django + DRF    │
            │  colección:      │   │  colección:      │
            │  companies       │   │  material_       │
            └────────┬─────────┘   │  listings        │
                     │             └────────┬─────────┘
                     │                      │
                     └──────────┬───────────┘
                                ▼
                     ┌─────────────────────┐
                     │   MongoDB Atlas     │
                     └─────────────────────┘

Auth: Firebase (frontend obtiene ID Token; cada MS lo valida con Admin SDK)
```

## Matriz de responsables

| Estudiante | Componente | Responsabilidad | Datos propios | Ruta base | Imagen OCIR |
|---|---|---|---|---|---|
| A | companies-service | CRUD empresas | `companies` | `/api/v1/companies` | `companies-service:v1.0.0` |
| B | materials-service | Publicaciones | `material_listings` | `/api/v1/materials` | `materials-service:v1.0.0` |
| C | frontend + proxy | UI, mocks, enrutamiento | — | `/` | `frontend:v1.0.0` |
