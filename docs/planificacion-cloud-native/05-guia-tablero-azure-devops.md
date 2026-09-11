# Guía — Proyecto y tablero en Azure DevOps (o Jira)

El enunciado pide **proyecto en Azure o Jira**, lista de producto editable, tablero del producto, Sprint 1 y evidencia (capturas).

Esta guía usa **Azure DevOps Boards**. Los menús de Azure suelen estar en inglés; entre paréntesis va el significado.

---

## A. Crear el proyecto

1. Entra a [https://dev.azure.com](https://dev.azure.com) con la cuenta institucional o de Microsoft.  
2. **New organization** (nueva organización), si no tienen una → nombre, por ejemplo `ecored-circular`.  
3. **New project** (nuevo proyecto)
   - **Name** (nombre): `EcoRed Circular`
   - **Visibility** (visibilidad): Private (privado)
   - **Work item process** (proceso): **Agile** o **Basic**. Agile permite Épica → Funcionalidad → Historia de usuario (en inglés: Epic → Feature → User Story).
4. Entra a **Boards → Work items** (Tableros → Elementos de trabajo).

Captura 1: página del proyecto creado (nombre + menú Boards).

---

## B. Configurar el Sprint 1

1. **Boards → Sprints** (o **Project settings → Teams → Iterations**: configuración del proyecto → equipos → iteraciones).  
2. Crea la iteración:
   - `Sprint 1` — fechas de las 2 semanas del equipo.  
   - Opcional: Sprint 2 a Sprint 5 con la misma duración.  
3. Asigna **Sprint 1** al equipo por defecto.

Captura 2: iteraciones con Sprint 1 seleccionado.

---

## C. Crear la jerarquía (copiar títulos)

### Épicas (6)

| Título |
|---|
| E1 — Identidad y acceso |
| E2 — Gestión de empresas |
| E3 — Publicaciones de materiales |
| E4 — Mercado circular |
| E5 — Plataforma nativa de la nube |
| E6 — Observabilidad y operaciones |

### Funcionalidades (12)

Crea cada funcionalidad y asígnala como hija de la épica:

| Título | Padre |
|---|---|
| F1 — Autenticación de usuarios | E1 |
| F2 — Autorización y tenencia | E1 |
| F3 — Registro y consulta de empresas | E2 |
| F4 — Administración de empresas | E2 |
| F5 — Publicación de materiales | E3 |
| F6 — Ciclo de vida de materiales | E3 |
| F7 — Catálogo público y búsqueda | E4 |
| F8 — Solicitudes de intercambio | E4 |
| F9 — Configuración y secretos | E5 |
| F10 — Contenerización y orquestación | E5 |
| F11 — Contratos API y puerta de enlace | E5 |
| F12 — Telemetría, registros y salud | E6 |

### Historias de usuario (30)

Importa `product-backlog.csv` o créalas a mano. Para cada una:

- Tipo: **User Story** (historia de usuario) al importar a Azure; en el CSV el tipo ya está en español (**Historia de usuario**). Al importar, mapea: Épica → Epic, Funcionalidad → Feature, Historia de usuario → User Story.
- Esfuerzo = puntos de la columna Puntos de historia
- Prioridad = 1 / 2 / 3
- Iteración = `Sprint 1` solo para US-01 a US-07; el resto queda en la lista de producto
- Padre = funcionalidad indicada
- Etiquetas: microservicio y factores, por ejemplo `servicio-empresas; factor-15; factor-8`

Textos de historia y criterios: copiar de `ENTREGABLE-PLANIFICACION.md` y `02-historias-sprint-1.md`.

---

## D. Importar el CSV (recomendado)

1. Abre `product-backlog.csv` en Excel y **guarda como CSV UTF-8**.  
2. En Azure DevOps: **Boards → Queries → Import work items** (Tableros → Consultas → Importar elementos de trabajo).  
3. Mapea columnas:
   - Tipo de elemento → Work Item Type (con la conversión de tipos indicada arriba)
   - Título → Title
   - Descripción → Description
   - Criterios de aceptación → Acceptance Criteria (en proceso Agile)
   - Prioridad → Priority
   - Puntos de historia → Effort
   - Etiquetas → Tags
4. Después de importar, arrastra US-01 a US-07 al **Sprint 1**.

Si el proceso **Basic** no tiene funcionalidades (Feature), usa solo épicas e historias, o guarda F1 a F12 como etiquetas.

---

## E. Tablero de producto y tablero del Sprint 1

### Lista de producto

**Boards → Backlogs** (Tableros → Listas) → vista **Épicas** o **Historias**.  
Debe verse la lista ordenada por prioridad.

Captura 3: lista de producto con épicas, funcionalidades e historias (US-01 a US-30 o el CSV importado).

### Sprint 1

**Boards → Sprints → Sprint 1** → tablero Kanban. Columnas típicas en inglés: **New / Active / Resolved / Closed** (Nuevo / Activo / Resuelto / Cerrado) o **To Do / Doing / Done** (Por hacer / En curso / Terminado).

Las 7 tarjetas:

- US-01 Iniciar sesión con correo y contraseña  
- US-02 Validar token y aislar datos en la API  
- US-03 Registrar empresa  
- US-04 Consultar mis empresas  
- US-05 Publicar material reciclable  
- US-06 Consultar mis publicaciones de materiales  
- US-07 Configuración externa, contenedores y salud  

Captura 4: tablero Sprint 1 con las 7 historias.  
Captura 5: detalle de una historia (por ejemplo US-03) mostrando “Como… quiero… para…” y criterios Dado que / Cuando / Entonces.

---

## F. Alternativa Jira Cloud

1. [https://www.atlassian.com](https://www.atlassian.com) → crear sitio → proyecto **Scrum**.  
2. Crea las épicas E1 a E6.  
3. Crea las historias con enlace a la épica, puntos y Sprint = Sprint 1 para US-01 a US-07.  
4. Importa el CSV: **Issues → Import issues from CSV** (Incidencias → Importar desde CSV).  
5. Capturas: lista de producto, tablero del sprint y detalle de una historia.

Al importar, mapea: Tipo de elemento → Issue Type, Título → Summary, Descripción → Description.

---

## G. Qué entregar como evidencia

Suban un PDF o una carpeta con:

1. URL del proyecto Azure o Jira (si el profesor puede entrar, inviten su correo).  
2. Capturas A a E de esta guía.  
3. Este paquete de `docs/planificacion-cloud-native/` (lista de producto editable).

No hace falta que el tablero esté en Terminado: para la entrega de planificación basta el Sprint 1 cargado y la lista de producto visible.
