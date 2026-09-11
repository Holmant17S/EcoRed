# Criterios de aceptación — US-01 a US-20

Formato de cada criterio:

Dado que [condición inicial]  
Cuando [acción]  
Entonces [resultado esperado]

---

## US-01 — Iniciar sesión con correo y contraseña

Como empresario, quiero iniciar sesión con correo y contraseña, para acceder de forma segura a mis empresas y materiales.

Dado que existe un usuario de Firebase con correo y contraseña válidos  
Cuando ingreso esas credenciales en `/login` y envío el formulario  
Entonces se autentica la sesión, soy redirigido a `/home` y veo la navegación a Empresas y Materiales.

Dado que estoy en `/login`  
Cuando envío el formulario con correo vacío, contraseña vacía o un correo con formato inválido  
Entonces no se llama a Firebase y el formulario indica los campos obligatorios.

Dado que el correo no existe o la contraseña es incorrecta  
Cuando intento iniciar sesión  
Entonces permanezco en `/login` y veo un mensaje de credenciales inválidas.

Dado que no hay sesión activa  
Cuando intento abrir `/home`, `/companies` o `/materials`  
Entonces soy redirigido a `/login`.

Dado que la autenticación la emite Firebase  
Cuando un usuario inicia sesión  
Entonces la aplicación no almacena la contraseña y usa el token emitido por Firebase.

---

## US-02 — Validar token y aislar datos en la API

Como empresario, quiero que la API valide mi token y aísle mis datos, para que nadie más consulte o modifique mi información.

Dado que tengo una sesión de Firebase vigente  
Cuando el cliente web llama a `GET /api/companies/` o `GET /api/materials/` con `Authorization: Bearer <token>`  
Entonces la API verifica el token, extrae el `uid` y responde 200 solo con recursos de ese usuario.

Dado que una petición a un recurso protegido llega sin encabezado `Authorization`  
Cuando el backend procesa la petición  
Entonces responde 401 y no consulta MongoDB.

Dado que el token está expirado o es inválido  
Cuando llamo a un endpoint protegido  
Entonces recibo 401 y el cliente web pide un nuevo inicio de sesión.

Dado que `GET /api/health/` es público  
Cuando lo consulto sin token  
Entonces responde 200 con `{"status":"ok"}`.

Dado que el usuario A y el usuario B están autenticados  
Cuando A lista empresas o materiales  
Entonces no recibe documentos cuyo dueño sea B.

---

## US-03 — Registrar empresa

Como empresario, quiero registrar mi empresa (nombre, NIT, ciudad, sector, descripción y comunidad), para asociar publicaciones de materiales a un actor formal.

Dado que estoy autenticado y en `/companies`  
Cuando completo nombre, NIT, ciudad, sector, descripción y comunidad y envío el formulario  
Entonces el backend persiste la empresa en MongoDB Atlas y responde 201 con un `id`.

Dado que estoy en el formulario de empresa  
Cuando dejo vacío el nombre, el NIT o la ciudad  
Entonces el formulario no envía la petición y marca los campos requeridos.

Dado que MongoDB Atlas no está disponible  
Cuando envío una empresa válida  
Entonces el backend responde error y el cliente web muestra un mensaje de persistencia.

Dado que no hay token válido  
Cuando se llama `POST /api/companies/`  
Entonces la API responde 401 y no crea el registro.

Dado que estoy autenticado  
Cuando creo una empresa  
Entonces el servidor asigna `owner_uid` con el `uid` del token e ignora cualquier dueño enviado en el cuerpo.

---

## US-04 — Consultar mis empresas

Como empresario, quiero consultar las empresas que yo registré, para verificar y reutilizar esos datos al publicar materiales.

Dado que estoy autenticado y tengo al menos una empresa  
Cuando abro `/companies`  
Entonces veo nombre, NIT, ciudad y sector de solo mis empresas.

Dado que estoy autenticado y no tengo empresas  
Cuando abro `/companies`  
Entonces veo un estado vacío y el formulario de registro, no un error.

Dado que la API falla o hay error de red  
Cuando cargo `/companies`  
Entonces veo un mensaje de error y puedo reintentar.

Dado que no hay sesión  
Cuando navego a `/companies`  
Entonces el cliente web me envía a `/login`.

Dado que el usuario B tiene empresas  
Cuando el usuario A lista empresas  
Entonces A no ve las empresas de B.

---

## US-05 — Publicar material reciclable

Como empresario, quiero publicar un material reciclable asociado a una de mis empresas, para ofrecer excedente a la red circular.

Dado que estoy autenticado y tengo al menos una empresa  
Cuando en `/materials` elijo empresa, tipo, cantidad, unidad, ubicación, descripción y precio y envío  
Entonces la API responde 201, el material queda en MongoDB Atlas y aparece en mi listado.

Dado que no tengo empresas  
Cuando abro el formulario de materiales  
Entonces el envío está deshabilitado y se indica que debo registrar una empresa primero.

Dado que la cantidad no es mayor que 0, el precio es negativo o faltan tipo, empresa o ubicación  
Cuando envío el formulario o la API recibe el cuerpo  
Entonces no se persiste el material.

Dado que no hay token  
Cuando se llama `POST /api/materials/`  
Entonces responde 401.

Dado que `company_id` pertenece a otro usuario  
Cuando intento publicar  
Entonces la API responde 403 o 400 y no crea la publicación.

---

## US-06 — Consultar mis publicaciones de materiales

Como empresario, quiero ver las publicaciones de materiales de mis empresas, para conocer el inventario que tengo en la plataforma.

Dado que estoy autenticado y he publicado materiales  
Cuando abro `/materials`  
Entonces veo tipo, cantidad, unidad, ubicación, precio y estado de esas publicaciones.

Dado que no tengo publicaciones  
Cuando abro `/materials`  
Entonces veo un listado vacío, no un error.

Dado que la API responde 401 o 500 o hay fallo de red  
Cuando cargo materiales  
Entonces se muestra un mensaje entendible.

Dado que no hay sesión  
Cuando voy a `/materials`  
Entonces soy redirigido a `/login`.

Dado que el usuario B publicó materiales  
Cuando A lista materiales  
Entonces A no ve los materiales de B.

---

## US-07 — Configuración externa, contenedores y salud

Como operador, quiero configurar la aplicación con variables de entorno, ejecutarla en contenedores y verificar su salud, para correr el mismo incremento en local sin secretos en el código.

Dado que existen archivos `.env` (no versionados) con MongoDB Atlas, Firebase y variables `DJANGO_*`  
Cuando ejecuto `docker compose up --build` o levanto cliente web y backend  
Entonces el backend escucha en el puerto publicado y `GET /api/health/` responde 200.

Dado que falta una variable obligatoria del cliente web  
Cuando arranca la aplicación  
Entonces se muestra un diagnóstico de variables faltantes en lugar de una pantalla blanca.

Dado que MongoDB Atlas rechaza la URI  
Cuando el backend intenta persistir  
Entonces el error se registra en la salida estándar y la API no finge un 201.

Dado que las credenciales viven en el entorno  
Cuando se inspecciona el código fuente  
Entonces no hay claves ni cadenas de conexión reales en el repositorio.

Dado que `/api/health/` es de sondeo  
Cuando se consulta sin token  
Entonces responde 200 sin exigir inicio de sesión.

---

## US-08 — Crear cuenta con correo y contraseña

Como visitante, quiero crear una cuenta con correo y contraseña, para usar la plataforma sin depender de un usuario preexistente.

Dado que estoy en la pantalla de registro y el correo no existe en Firebase  
Cuando envío un correo válido y una contraseña de al menos 6 caracteres  
Entonces se crea el usuario, queda autenticado y entro a `/home`.

Dado que el correo ya está registrado o la contraseña tiene menos de 6 caracteres  
Cuando envío el formulario  
Entonces veo un error y no se abre sesión.

Dado que no hay sesión  
Cuando intento abrir `/companies`  
Entonces soy enviado a inicio de sesión o registro.

---

## US-09 — Iniciar sesión con Google

Como empresario, quiero iniciar sesión con Google, para autenticarme más rápido.

Dado que el proveedor Google está habilitado en Firebase  
Cuando pulso “Continuar con Google” y autorizo la cuenta  
Entonces se crea o reutiliza el usuario y entro a `/home`.

Dado que cancelo la ventana o Google falla  
Cuando intento el inicio de sesión  
Entonces permanezco en `/login` con un mensaje de error.

Dado que no hay sesión  
Cuando intento abrir una ruta protegida  
Entonces soy redirigido a `/login`.

---

## US-10 — Editar empresa propia

Como empresario, quiero editar los datos de una empresa mía, para mantener la información actualizada.

Dado que soy dueño de la empresa  
Cuando envío `PUT /api/companies/{id}` con nombre y ciudad válidos  
Entonces se actualiza el documento y una consulta posterior refleja los cambios.

Dado que el nombre queda vacío  
Cuando envío la actualización  
Entonces recibo 400 y el documento no cambia.

Dado que la empresa pertenece a otro usuario  
Cuando llamo a `PUT /api/companies/{id}`  
Entonces recibo 403 o 404 y el documento no cambia.

---

## US-11 — Eliminar empresa propia

Como empresario, quiero eliminar una empresa mía, para retirar actores que ya no participan.

Dado que soy dueño de la empresa  
Cuando envío `DELETE /api/companies/{id}`  
Entonces responde 204 y deja de aparecer en el listado.

Dado que la empresa tiene materiales publicados  
Cuando intento borrar  
Entonces se bloquea con 409 o se archivan los materiales según la regla documentada.

Dado que no soy el dueño  
Cuando llamo a `DELETE`  
Entonces recibo 403 o 404.

---

## US-12 — Editar publicación de material

Como empresario, quiero editar una publicación de material mía, para corregir cantidad, precio o ubicación.

Dado que el material pertenece a una empresa mía  
Cuando envío `PUT /api/materials/{id}` con cantidad mayor que 0  
Entonces se persisten los cambios.

Dado que la cantidad es menor o igual a 0 o el precio es negativo  
Cuando envío la actualización  
Entonces recibo 400.

Dado que el material es de otra empresa  
Cuando envío `PUT`  
Entonces recibo 403 o 404.

---

## US-13 — Cambiar estado del material

Como empresario, quiero cambiar el estado de un material (disponible, reservado, intercambiado), para reflejar su ciclo de vida.

Dado que soy el publicador y el estado actual es disponible  
Cuando cambio el estado a reservado  
Entonces una consulta posterior muestra reservado y deja de ofrecerse como libre.

Dado que envío un estado distinto de disponible, reservado o intercambiado  
Cuando llamo al endpoint  
Entonces recibo 400.

Dado que un interesado no es el dueño  
Cuando intenta cambiar el estado de forma directa  
Entonces recibe 403.

---

## US-14 — Ver detalle de empresa y material

Como empresario, quiero ver el detalle de una empresa y de un material, para revisar la información completa antes de operar.

Dado que el recurso me pertenece  
Cuando abro `/companies/:id` o `/materials/:id`  
Entonces veo todos los campos persistidos.

Dado que el identificador no existe  
Cuando abro el detalle  
Entonces recibo 404 y un mensaje en la interfaz.

Dado que el detalle privado no es mío  
Cuando lo pido  
Entonces recibo 403 o 404.

---

## US-15 — Validaciones de negocio en la API

Como empresario, quiero que la API rechace datos inválidos y acciones sobre recursos ajenos, para no corromper el negocio ni cruzar tenencias.

Dado que ya registré un NIT para mi usuario  
Cuando creo una segunda empresa con el mismo NIT  
Entonces recibo 409.

Dado que `company_id` no es mío  
Cuando publico un material  
Entonces recibo 403 y no se inserta el documento.

Dado que el cuerpo incluye `owner_uid` enviado por el cliente  
Cuando hago `POST` o `PUT`  
Entonces el servidor ignora ese campo y usa el `uid` del token.

---

## US-16 — Catálogo público de materiales disponibles

Como interesado, quiero ver un catálogo de materiales disponibles de otras empresas, para encontrar recursos reutilizables.

Dado que estoy autenticado  
Cuando abro el catálogo  
Entonces veo materiales disponibles de otras empresas.

Dado que no hay token  
Cuando llamo al catálogo  
Entonces recibo 401.

Dado que un material está reservado o intercambiado  
Cuando cargo el catálogo  
Entonces ese material no aparece.

---

## US-17 — Filtrar catálogo por tipo, ciudad y precio

Como interesado, quiero filtrar el catálogo por tipo, ciudad y rango de precio, para acotar resultados útiles.

Dado que hay materiales de distintos tipos y ciudades  
Cuando filtro por tipo plástico y ciudad Bogotá  
Entonces solo se listan coincidencias.

Dado un rango en el que el precio mínimo es mayor que el máximo  
Cuando aplico filtros  
Entonces recibo 400 o la interfaz lo impide.

Dado que ningún material cumple los filtros  
Cuando filtro  
Entonces veo un listado vacío, no un error.

---

## US-18 — Solicitar un material disponible

Como interesado, quiero solicitar un material disponible, para iniciar un intercambio con su publicador.

Dado que el material está disponible y no es mío  
Cuando envío `POST /api/requests` con el identificador del material  
Entonces se crea la solicitud en estado pendiente y el dueño podrá verla.

Dado que el material es mío o no está disponible  
Cuando solicito  
Entonces recibo 409 o 400.

Dado que ya tengo una solicitud pendiente sobre el mismo material  
Cuando vuelvo a solicitar  
Entonces recibo 409.

---

## US-19 — Aceptar o rechazar solicitudes

Como empresario, quiero aceptar o rechazar solicitudes sobre mis materiales, para controlar con quién intercambio.

Dado que soy dueño del material y hay una solicitud pendiente  
Cuando acepto  
Entonces esa solicitud pasa a aceptada, el material pasa a reservado y las demás solicitudes pendientes se rechazan o se bloquean.

Dado que no soy el dueño  
Cuando acepto  
Entonces recibo 403.

Dado que la solicitud ya no está pendiente  
Cuando acepto o rechazo  
Entonces recibo 409.

---

## US-20 — Cerrar intercambio

Como empresario, quiero marcar un intercambio como cerrado, para retirar el material del catálogo y dejar trazabilidad.

Dado que hay una solicitud aceptada sobre mi material  
Cuando confirmo el cierre  
Entonces el material queda intercambiado, la solicitud queda completada y desaparece del catálogo.

Dado que el material no está reservado  
Cuando intento cerrar  
Entonces recibo 409.

Dado un usuario que no es dueño ni solicitante aceptado  
Cuando intenta cerrar  
Entonces recibe 403.
