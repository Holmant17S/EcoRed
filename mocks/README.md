# Mocks — EcoRed Circular

Datos simulados para desarrollar el frontend **sin levantar** los microservicios. Están alineados a `contracts/`.

| Archivo | GET | POST |
|---|---|---|
| `companies.json` | Lista de empresas | Recurso creado |
| `materials.json` | Lista de materiales | Recurso creado |
| `requests.json` | Lista de solicitudes | Recurso creado |

## Opción A — Vite (`VITE_USE_MOCKS=true`)

En `frontend/.env`:

```env
VITE_USE_MOCKS=true
```

Los clientes `companyService.js`, `materialService.js` y `requestService.js` leen estos JSON (alias `@mocks`) y no llaman a `/api/v1`.

## Opción B — json-server (API falsa en el puerto 3001)

Desde la raíz del proyecto:

```bash
npx json-server --port 3001 mocks/companies.json
```

Para materiales, usa `mocks/materials.json` en otro puerto o fusiona ambos recursos en un `db.json` con las claves `get`/`post`.

Luego apunta el frontend a esa URL:

```env
VITE_API_URL=http://localhost:3001
VITE_USE_MOCKS=false
```

## Opción C — Import directo

```js
import companiesMock from "@mocks/companies.json";

const empresas = companiesMock.get;
const alta = companiesMock.post;
```

Los JSON de `frontend/src/mocks/` se mantienen como copia de trabajo del GET para no romper imports antiguos.
