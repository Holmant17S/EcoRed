# Diagrama de microservicios — EcoRed Circular

```text
                    ┌─────────────────────┐
                    │   Cliente (Browser) │
                    └──────────┬──────────┘
                               │  http://localhost:8080
                               ▼
                    ┌─────────────────────┐
                    │  proxy (Nginx)      │
                    └──┬────┬─────┬────┬──┘
                       │    │     │    │
         /             │    │     │    │
         ▼             │    │     │    │
┌──────────────┐       │    │     │    │
│   frontend   │       │    │     │    │
└──────────────┘       │    │     │    │
                       │    │     │    │
      /api/v1/companies/    │     │    /api/v1/requests/
                       ▼    │     ▼    ▼
            ┌──────────────┐│┌──────────────┐┌──────────────┐
            │ companies    │││ materials    ││ requests     │
            │ -service     │││ -service     ││ -service     │
            │ companies    │││ listings     ││ material_    │
            └──────┬───────┘│└──────┬───────┘│ requests     │
                   │        │       │        └──────┬───────┘
                   └────────┴───────┴───────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │   MongoDB Atlas     │
                         └─────────────────────┘

Auth: Firebase ID Token. Cada microservicio lo valida con Admin SDK.
```

## Matriz de componentes

| Componente | Responsabilidad | Datos propios | Ruta base | Imagen |
|---|---|---|---|---|
| companies-service | CRUD empresas | `companies` | `/api/v1/companies` | `companies-service:v1.0.0` |
| materials-service | Publicaciones | `material_listings` | `/api/v1/materials` | `materials-service:v1.0.0` |
| requests-service | Solicitudes | `material_requests` | `/api/v1/requests` | `requests-service:v1.0.0` |
| frontend + proxy | UI y enrutamiento | — | `/` | `frontend:v1.0.0` |
