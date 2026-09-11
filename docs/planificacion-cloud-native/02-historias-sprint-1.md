# Sprint 1 — Historias de usuario y criterios de aceptación

**Producto:** EcoRed Circular  
**Sprint:** 1  
**Duración sugerida:** 2 semanas  
**Historias:** US-01 a US-07 (7, dentro del rango 5–8)  
**Puntos:** 34

---

## Objetivo del sprint

Entregar un incremento funcional completo, ejecutable en local (Docker + variables de entorno), en el que un empresario autenticado registra empresas, publica materiales y consulta ambos módulos contra APIs REST persistidas en MongoDB Atlas.

Al cierre del sprint debe poder demostrarse:

1. Inicio de sesión con Firebase.  
2. Cliente web hablando con el backend por REST.  
3. Persistencia en MongoDB Atlas.  
4. Dos módulos de negocio: empresas y materiales.  
5. Alta y consulta en ambos.  
6. Configuración por variables de entorno.  
7. Comprobación de salud y arranque contenerizado o equivalente local verificable.

---

## US-01 — Iniciar sesión con correo y contraseña

**Épica:** E1 Identidad y acceso  
**Funcionalidad:** F1 Autenticación de usuarios  
**Prioridad:** 1  
**Puntos:** 5  
**Microservicio:** servicio-identidad, cliente-web  
**Factores:** 5 Configuración · 15 Autenticación y autorización

Como empresario, quiero iniciar sesión con correo y contraseña, para acceder de forma segura a mis empresas y materiales.

### Escenario exitoso

Dado que existe un usuario Firebase con correo y contraseña válidos  
Cuando ingreso esas credenciales en `/login` y envío el formulario  
Entonces Firebase autentica la sesión, soy redirigido a `/home` y el layout muestra navegación a Empresas y Materiales.

### Validaciones

Dado que estoy en `/login`  
Cuando envío el formulario con correo vacío, contraseña vacía o un correo con formato inválido  
Entonces no se llama a Firebase y el formulario indica los campos obligatorios / formato de correo.

### Manejo de errores

Dado que el correo no existe o la contraseña es incorrecta  
Cuando intento iniciar sesión  
Entonces permanezco en `/login` y veo un mensaje claro (credenciales inválidas), sin pantalla en blanco.

Dado que no hay red o Firebase no responde  
Cuando intento iniciar sesión  
Entonces veo un mensaje de error recuperable y puedo reintentar.

### Autenticación / autorización

Dado que no hay sesión activa  
Cuando intento abrir `/home`, `/companies` o `/materials`  
Entonces soy redirigido a `/login`.

Dado que ya hay sesión activa  
Cuando abro `/login`  
Entonces soy redirigido a `/home`.

### Reglas de negocio

- La identidad la emite autenticación de Firebase (servicio de respaldo); la app no almacena contraseñas.
- Las claves de Firebase se leen de variables `VITE_FIREBASE_*`, no van hardcodeadas en componentes.
- La sesión se restaura con `onAuthStateChanged` al recargar el navegador.

---

## US-02 — Validar token y aislar datos en la API

**Épica:** E1 Identidad y acceso  
**Funcionalidad:** F2 Autorización y tenencia  
**Prioridad:** 1  
**Puntos:** 5  
**Microservicio:** servicio-identidad (capa intermedia), servicio-empresas, servicio-materiales  
**Factores:** 2 API primero · 12 Procesos sin estado · 15 Autenticación y autorización

Como empresario, quiero que la API valide mi token y aísle mis datos, para que nadie más consulte o modifique mi información.

### Escenario exitoso

Dado que tengo una sesión Firebase vigente  
Cuando el cliente web llama a `GET /api/companies/` o `GET /api/materials/` con `Authorization: Bearer <idToken>`  
Entonces la API verifica el token con Firebase Admin, extrae el `uid` y responde 200 solo con recursos de ese usuario.

### Validaciones

Dado que una petición a un recurso protegido llega sin encabezado `Authorization` o con un token que no es Bearer  
Cuando el backend procesa la petición  
Entonces responde 401 y no consulta MongoDB con un `uid` vacío.

### Manejo de errores

Dado que el token está expirado, malformado o revocado  
Cuando llamo a un endpoint protegido  
Entonces recibo 401 y el cliente web muestra un mensaje de sesión inválida / pide un nuevo inicio de sesión.

Dado que Firebase Admin no puede validar (configuración incompleta)  
Cuando llega una petición autenticada  
Entonces el backend registra el error y responde 401 o 500 de forma controlada, sin mostrar un volcado técnico en HTML.

### Autenticación / autorización

Dado que `GET /api/health/` es público  
Cuando lo consulto sin token  
Entonces responde 200 `{"status":"ok"}`.

Dado que `/api/companies/` y `/api/materials/` son privados  
Cuando los consulto sin token  
Entonces responden 401.

### Reglas de negocio

- El backend no guarda estado: no guarda sesión de servidor; cada petición se autoriza con el token.
- El `uid` del token es la única clave de tenencia (`owner_uid` / `published_by`).
- Un usuario A jamás recibe documentos cuyo dueño sea el usuario B.

---

## US-03 — Registrar empresa

**Épica:** E2 Gestión de empresas  
**Funcionalidad:** F3 Registro y consulta de empresas  
**Prioridad:** 1  
**Puntos:** 5  
**Microservicio:** servicio-empresas, cliente-web  
**Factores:** 2 API primero · 5 Configuración · 8 Servicios de respaldo · 15 AuthN/AuthZ

Como empresario, quiero registrar mi empresa (nombre, NIT, ciudad, sector, descripción y comunidad), para asociar publicaciones de materiales a un actor formal.

### Escenario exitoso

Dado que estoy autenticado y en `/companies`  
Cuando completo nombre, NIT, ciudad, sector, descripción y comunidad y envío el formulario  
Entonces el cliente web hace `POST /api/companies/` con el Bearer token, el backend persiste en MongoDB Atlas y responde 201 con `id`, y la empresa queda disponible para publicar materiales.

### Validaciones

Dado que estoy en el formulario de empresa  
Cuando dejo vacío el nombre, el NIT o la ciudad, o el NIT no es numérico  
Entonces el formulario no envía la petición y marca los campos requeridos.

Dado que el backend recibe `name` o `nit` vacíos  
Cuando procesa `POST /api/companies/`  
Entonces responde 400 y no inserta el documento.

### Manejo de errores

Dado que MongoDB Atlas no está disponible  
Cuando envío una empresa válida  
Entonces el backend responde 503/500 y el cliente web muestra un error de persistencia, sin perder el resto de la sesión.

Dado que la API responde 401  
Cuando intento registrar  
Entonces se informa que la sesión expiró y se redirige a login.

### Autenticación / autorización

Dado que no hay token válido  
Cuando se llama `POST /api/companies/`  
Entonces la API responde 401 y no crea el registro.

Dado que estoy autenticado  
Cuando creo una empresa  
Entonces no puedo enviar un `owner_uid` distinto: el servidor ignora cualquier dueño del body y usa el `uid` del token.

### Reglas de negocio

- Campos de negocio: `name`, `nit`, `city`, `sector`, `descripcion`, `comunidad`.
- `owner_uid` = `uid` de Firebase.
- `created_at` se genera en servidor (UTC).
- La empresa queda persistida en la colección `companies` de MongoDB Atlas.

---

## US-04 — Consultar mis empresas

**Épica:** E2 Gestión de empresas  
**Funcionalidad:** F3 Registro y consulta de empresas  
**Prioridad:** 1  
**Puntos:** 3  
**Microservicio:** servicio-empresas, cliente-web  
**Factores:** 2 API primero · 8 Servicios de respaldo · 15 AuthN/AuthZ

Como empresario, quiero consultar las empresas que yo registré, para verificar y reutilizar esos datos al publicar materiales.

### Escenario exitoso

Dado que estoy autenticado y tengo al menos una empresa  
Cuando abro `/companies`  
Entonces se ejecuta `GET /api/companies/` y veo nombre, NIT, ciudad y sector de **solo mis** empresas.

### Validaciones

Dado que estoy autenticado y no tengo empresas  
Cuando abro `/companies`  
Entonces veo un estado vacío y el formulario de registro, no un error.

### Manejo de errores

Dado que la API falla o hay error de red  
Cuando cargo `/companies`  
Entonces veo un mensaje de error y puedo reintentar, sin pantalla en blanco.

### Autenticación / autorización

Dado que no hay sesión  
Cuando navego a `/companies`  
Entonces el cliente web me envía a `/login` y no llama a la API.

Dado que el usuario B tiene empresas  
Cuando el usuario A lista empresas  
Entonces A no ve las de B.

### Reglas de negocio

- Filtro obligatorio: `owner_uid = uid` del token.
- El `_id` de Mongo se serializa como `id` string en JSON.
- El combo de empresa en materiales se alimenta de este listado.

---

## US-05 — Publicar material reciclable

**Épica:** E3 Publicaciones de materiales  
**Funcionalidad:** F5 Publicación de materiales  
**Prioridad:** 1  
**Puntos:** 5  
**Microservicio:** servicio-materiales, cliente-web  
**Factores:** 2 API primero · 8 Servicios de respaldo · 15 AuthN/AuthZ

Como empresario, quiero publicar un material reciclable asociado a una de mis empresas, para ofrecer excedente a la red circular.

### Escenario exitoso

Dado que estoy autenticado y tengo al menos una empresa  
Cuando en `/materials` elijo empresa, tipo, cantidad, unidad, ubicación, descripción, precio y envío  
Entonces el cliente web hace `POST /api/materials/`, MongoDB Atlas guarda el documento y la API responde 201 con `id`. La publicación aparece en mi listado.

### Validaciones

Dado que no tengo empresas  
Cuando abro el formulario de materiales  
Entonces el envío está deshabilitado y se indica que debo registrar una empresa primero.

Dado que cantidad no es un número mayor que 0, el precio es negativo, o faltan tipo / empresa / ubicación  
Cuando envío el formulario o la API recibe el body  
Entonces no se persiste el material (validación de UI y 400 en API).

### Manejo de errores

Dado que `company_id` no es un ObjectId válido o no existe  
Cuando llamo `POST /api/materials/`  
Entonces la API responde 400 y no crea el documento.

Dado que hay error de red o 500  
Cuando publico  
Entonces veo un mensaje de error y el formulario conserva o permite reintentar.

### Autenticación / autorización

Dado que no hay token  
Cuando se llama `POST /api/materials/`  
Entonces responde 401.

Dado que `company_id` pertenece a otro usuario  
Cuando intento publicar  
Entonces la API responde 403 o 400 y no crea la publicación.

### Reglas de negocio

- Campos: `company_id`, `material_type`, `quantity`, `unit` (por defecto `kg`), `location`, `descripcion`, `precio`, `status`.
- `status` inicial = `available` si no se envía otro valor permitido.
- `published_by` = `uid` del token (no se toma del cliente).
- `quantity` y `precio` se persisten como número.
- Un material solo puede asociarse a una empresa del usuario autenticado.

---

## US-06 — Consultar mis publicaciones de materiales

**Épica:** E3 Publicaciones de materiales  
**Funcionalidad:** F6 Ciclo de vida de materiales  
**Prioridad:** 1  
**Puntos:** 3  
**Microservicio:** servicio-materiales, cliente-web  
**Factores:** 2 API primero · 8 Servicios de respaldo · 15 AuthN/AuthZ

Como empresario, quiero ver las publicaciones de materiales de mis empresas, para conocer el inventario que tengo en la plataforma.

### Escenario exitoso

Dado que estoy autenticado y he publicado materiales  
Cuando abro `/materials`  
Entonces `GET /api/materials/` devuelve esas publicaciones (tipo, cantidad, unidad, ubicación, precio, estado) y el cliente web las renderiza.

### Validaciones

Dado que no tengo publicaciones  
Cuando abro `/materials`  
Entonces veo un listado vacío (no un error) y el formulario de alta si ya tengo empresa.

### Manejo de errores

Dado que la API responde 401, 500 o hay fallo de red  
Cuando cargo materiales  
Entonces se muestra un mensaje entendible y no se listan datos parciales de otro usuario.

### Autenticación / autorización

Dado que no hay sesión  
Cuando voy a `/materials`  
Entonces soy redirigido a `/login`.

Dado que el usuario B publicó materiales  
Cuando A lista materiales  
Entonces A no ve los de B.

### Reglas de negocio

- El listado se construye así: empresas donde `owner_uid = uid` → materiales cuyo `company_id` está en ese conjunto.
- Identificadores Mongo se exponen como strings.
- En Sprint 1 el catálogo es **privado** (solo propio). El catálogo público es US-16 (Sprint 3).

---

## US-07 — Configuración externa, contenedores y salud

**Épica:** E5 Plataforma nativa de la nube / E6 Observabilidad  
**Funcionalidad:** F9 Configuración y secretos · F10 Contenerización · F12 Telemetría  
**Prioridad:** 1  
**Puntos:** 8  
**Microservicio:** plataforma (Compose), cliente-web, backend  
**Factores:** 3 Gestión de dependencias · 4 Diseño, compilación, publicación y ejecución · 5 Configuración · 7 Desechabilidad · 8 Servicios de respaldo · 9 Paridad de entornos · 11 Enlace de puertos · 14 Telemetría

Como operador, quiero configurar la aplicación con variables de entorno, ejecutarla en contenedores y verificar su salud, para correr el mismo incremento en local sin secretos en el código.

### Escenario exitoso

Dado que existen `.env` de cliente web y backend (no versionados) con MongoDB Atlas, Firebase y `DJANGO_*`  
Cuando ejecuto `docker compose up --build` y/o levanto cliente web y backend  
Entonces el backend escucha en el puerto publicado, `GET /api/health/` responde 200 `{"status":"ok"}` y el cliente web usa `VITE_API_URL` para hablar con la API.

### Validaciones

Dado que falta una variable obligatoria del cliente web (`VITE_API_URL` o `VITE_FIREBASE_*`)  
Cuando arranca la aplicación  
Entonces se muestra un diagnóstico de variables faltantes en lugar de una pantalla blanca.

Dado que falta `MONGODB_URI`, `DJANGO_SECRET_KEY` o la cuenta de servicio de Firebase en el backend  
Cuando arranca o se atiende una petición que los requiere  
Entonces el fallo es explícito en los registros o en una respuesta controlada, no un comportamiento silencioso.

### Manejo de errores

Dado que MongoDB Atlas rechaza la URI  
Cuando el backend intenta persistir  
Entonces el error se registra en el log de consola (salida estándar del contenedor) y la API no finge un 201.

Dado que el contenedor se detiene  
Cuando vuelvo a levantarlo  
Entonces arranca de nuevo (`restart: unless-stopped` o equivalente) sin estado local irrecuperable: los datos siguen en Atlas.

### Autenticación / autorización

Dado que las credenciales de Firebase Admin y la URI de Mongo viven en entorno / archivos montados como secretos  
Cuando se inspecciona el código fuente  
Entonces no hay claves de API ni cadenas de conexión reales en el repositorio.

Dado que `/api/health/` es de sondeo  
Cuando un orquestador o un compañero lo consulta sin token  
Entonces responde 200 sin exigir inicio de sesión.

### Reglas de negocio / plataforma

- Código distinto de configuración: `SECRET_KEY`, `MONGODB_URI`, `CORS_ALLOWED_ORIGINS` y claves Firebase salen del entorno.
- Servicios de respaldo intercambiables por URL: Atlas y Firebase no están “dentro” del contenedor de la aplicación.
- El proceso publica un puerto (enlace de puertos); no depende de un servidor web externo embebido de forma no declarativa.
- La imagen (`ecored-circular:v1.0` o similar) es el artefacto de **compilación**; la **ejecución** solo inyecta variables y secretos.
- La comprobación de salud es la telemetría mínima del Sprint 1; métricas y trazas completas son US-22.

---

## Demostración sugerida (incremento)

1. Mostrar `.env.example` (sin secretos) y variables reales solo en local.  
2. `docker compose up` o arranque local, luego `GET /api/health/`.  
3. Inicio de sesión con usuario Firebase.  
4. Crear empresa → aparece en el listado.  
5. Crear material de esa empresa → aparece en el listado.  
6. Intentar `GET /api/companies/` sin token → 401.  
7. Entrar con otro usuario → no ve los datos del primero.

---

## Tablero Sprint 1

| Historia | Por hacer | En curso | Terminado |
|---|---|---|---|
| US-01 Inicio de sesión correo/contraseña | | | |
| US-02 Token y tenencia en API | | | |
| US-03 Registrar empresa | | | |
| US-04 Consultar empresas | | | |
| US-05 Publicar material | | | |
| US-06 Consultar materiales | | | |
| US-07 Configuración, Docker y salud | | | |

Mover a **Terminado** solo con la Definición de terminado del entregable principal.
