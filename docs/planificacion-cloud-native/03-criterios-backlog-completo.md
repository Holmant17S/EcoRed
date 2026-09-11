# Criterios de aceptación — historias US-08 a US-30

Las historias del Sprint 1 están en `02-historias-sprint-1.md`.  
Este archivo completa el Product Backlog: cada historia restante tiene criterios verificables en formato Given / When / Then.

---

## Sprint 2

### US-08 — Crear cuenta

Como visitante, quiero crear una cuenta con correo y contraseña, para usar la plataforma sin depender de un usuario preexistente.

Dado que estoy en la pantalla de registro y el correo no existe en Firebase  
Cuando envío correo válido y contraseña de al menos 6 caracteres  
Entonces se crea el usuario, queda autenticado y entro a `/home`.

Dado que el correo ya está registrado o la contraseña es menor a 6 caracteres  
Cuando envío el formulario  
Entonces veo un error y no se abre sesión.

Dado que no hay sesión  
Cuando intento `/companies`  
Entonces voy a login/registro.

---

### US-09 — Iniciar sesión con Google

Como empresario, quiero iniciar sesión con Google, para autenticarme más rápido.

Dado que el proveedor Google está habilitado en Firebase  
Cuando pulso “Continuar con Google” y autorizo la cuenta  
Entonces se crea o reutiliza el usuario y entro a `/home`.

Dado que cancelo el popup o Google falla  
Cuando intento el inicio de sesión  
Entonces permanezco en `/login` con un mensaje de error.

---

### US-10 — Editar empresa

Como empresario, quiero editar los datos de una empresa mía, para mantener la información actualizada.

Dado que soy dueño de la empresa `id`  
Cuando envío `PUT /api/companies/{id}` con nombre y ciudad válidos  
Entonces se actualiza el documento y GET posterior refleja los cambios.

Dado que la empresa es de otro `uid`  
Cuando llamo PUT  
Entonces recibo 403/404 y el documento no cambia.

Dado que el nombre queda vacío  
Cuando envío PUT  
Entonces recibo 400.

---

### US-11 — Eliminar empresa

Como empresario, quiero eliminar una empresa mía, para retirar actores que ya no participan.

Dado que soy dueño de la empresa y no tiene materiales, o se define cascada  
Cuando envío `DELETE /api/companies/{id}`  
Entonces responde 204 y deja de aparecer en el listado.

Dado que la empresa tiene materiales publicados  
Cuando intento borrar  
Entonces o bien se bloquea con 409, o se eliminan/archivan los materiales (regla documentada en el sprint).

Dado que no soy el dueño  
Cuando llamo DELETE  
Entonces 403/404.

---

### US-12 — Editar material

Como empresario, quiero editar una publicación de material mía, para corregir cantidad, precio o ubicación.

Dado que el material pertenece a una empresa mía  
Cuando envío `PUT /api/materials/{id}` con cantidad > 0  
Entonces se persisten los cambios.

Dado que cantidad ≤ 0 o precio < 0  
Cuando envío PUT  
Entonces 400.

Dado que el material es de otra empresa  
Cuando envío PUT  
Entonces 403/404.

---

### US-13 — Cambiar estado del material

Como empresario, quiero cambiar el estado de un material (available, reserved, exchanged), para reflejar su ciclo de vida.

Dado que soy el publicador y el estado actual es `available`  
Cuando cambio a `reserved`  
Entonces el catálogo (cuando exista) deja de ofrecerlo como libre y GET muestra `reserved`.

Dado que envío un estado fuera de `{available, reserved, exchanged}`  
Cuando llamo al endpoint  
Entonces 400.

Dado que un interesado no es el dueño  
Cuando intenta cambiar el estado directo  
Entonces 403 (el cambio de estado por solicitud es US-19/US-20).

---

### US-14 — Detalle de empresa y material

Como empresario, quiero ver el detalle de una empresa y de un material, para revisar la información completa antes de operar.

Dado que el recurso me pertenece (o es público en catálogo, Sprint 3)  
Cuando abro `/companies/:id` o `/materials/:id`  
Entonces veo todos los campos persistidos.

Dado que el id no existe  
Cuando abro el detalle  
Entonces 404 y mensaje en UI.

Dado que el detalle privado no es mío  
Cuando lo pido  
Entonces 403/404.

---

### US-15 — Validaciones de negocio en API

Como empresario, quiero que la API rechace datos inválidos y acciones sobre recursos ajenos, para no corromper el negocio ni cruzar tenencias.

Dado que NIT duplicado para el mismo `uid` (regla: único por usuario)  
Cuando creo una segunda empresa con el mismo NIT  
Entonces 409.

Dado que `company_id` no es mío  
Cuando publico material  
Entonces 403 y cero inserts.

Dado un body con campos extra no permitidos  
Cuando POST/PUT  
Entonces se ignoran o se rechazan; nunca se usa `owner_uid` del cliente.

---

## Sprint 3

### US-16 — Catálogo público

Como interesado, quiero ver un catálogo de materiales disponibles de otras empresas, para encontrar recursos reutilizables.

Dado que estoy autenticado  
Cuando abro el catálogo  
Entonces veo materiales con `status=available` de **otras** empresas, no los míos mezclados como “ajenos”.

Dado que no hay token  
Cuando llamo al catálogo  
Entonces 401 (el marketplace es para usuarios de la red).

Dado que un material está `reserved` o `exchanged`  
Cuando cargo el catálogo  
Entonces no aparece.

---

### US-17 — Filtros del catálogo

Como interesado, quiero filtrar el catálogo por tipo, ciudad y rango de precio, para acotar resultados útiles.

Dado que hay materiales de distintos tipos y ciudades  
Cuando filtro `material_type=plastico` y `city=Bogota`  
Entonces solo se listan coincidencias.

Dado un rango `precio_min > precio_max`  
Cuando aplico filtros  
Entonces 400 o la UI lo impide.

Dado que ningún material cumple  
Cuando filtro  
Entonces listado vacío, no error.

---

### US-18 — Solicitar un material

Como interesado, quiero solicitar un material disponible, para iniciar un intercambio con su publicador.

Dado que el material está `available` y no es mío  
Cuando envío `POST /api/requests` con `material_id`  
Entonces se crea la solicitud `pending` y el dueño podrá verla.

Dado que el material es mío o no está `available`  
Cuando solicito  
Entonces 409/400.

Dado que ya tengo una solicitud `pending` sobre el mismo material  
Cuando vuelvo a solicitar  
Entonces 409.

---

### US-19 — Aceptar o rechazar solicitudes

Como empresario, quiero aceptar o rechazar solicitudes sobre mis materiales, para controlar con quién intercambio.

Dado que soy dueño del material y hay una solicitud `pending`  
Cuando acepto  
Entonces esa solicitud pasa a `accepted`, las demás `pending` del mismo material se rechazan o se bloquean, y el material pasa a `reserved`.

Dado que no soy el dueño  
Cuando acepto  
Entonces 403.

Dado que la solicitud ya no está `pending`  
Cuando acepto o rechazo  
Entonces 409.

---

### US-20 — Cerrar intercambio

Como empresario, quiero marcar un intercambio como cerrado, para retirar el material del catálogo y dejar trazabilidad.

Dado que hay una solicitud `accepted` sobre mi material  
Cuando confirmo cierre  
Entonces el material queda `exchanged`, la solicitud `completed` y desaparece del catálogo.

Dado que el material no está `reserved`  
Cuando intento cerrar  
Entonces 409.

Dado un usuario que no es dueño ni solicitante aceptado  
Cuando cierra  
Entonces 403.

---

## Sprint 4

### US-21 — Logs estructurados

Como operador, quiero registros estructurados en la salida estándar de cada servicio, para diagnosticar sin entrar al contenedor.

Dado que el servicio atiende un POST de empresa  
Cuando termina la petición  
Entonces emite una línea JSON o clave-valor a la salida estándar (método, ruta, status, `uid` si aplica), sin escribir archivos locales obligatorios.

Dado un 401 o 500  
Cuando ocurre  
Entonces el log incluye nivel ERROR/WARN y no imprime el token ni secretos.

---

### US-22 — Métricas y trazas

Como operador, quiero métricas y trazas de las APIs (latencia, errores, correlación), para observar el sistema en la nube.

Dado que Application Insights / OpenTelemetry está configurado por entorno  
Cuando hay tráfico  
Entonces existen métricas de peticiones, latencia p95 y tasa de error, y un `identificador de traza` correlacionable.

Dado que la telemetría no está configurada en local  
Cuando arranca el servicio  
Entonces la app sigue funcionando (telemetría degradable, no bloqueante).

---

### US-23 — Separar microservicios companies y materials

Como operador, quiero separar companies y materials en microservicios contenerizados, para desplegarlos y escalarlos de forma independiente.

Dado el repositorio  
Cuando construyo las imágenes `servicio-empresas` y `servicio-materiales`  
Entonces cada una expone su API y su health en un puerto propio.

Dado que detengo solo `servicio-materiales`  
Cuando listo empresas  
Entonces `servicio-empresas` sigue respondiendo.

Dado que ambos persisten en Atlas  
Cuando creo empresa y material  
Entonces `servicio-materiales` valida la empresa vía API interna o contrato compartido, no vía import de código del otro servicio.

---

### US-24 — puerta de enlace de API

Como cliente web, quiero consumir los servicios a través de una puerta de enlace de API, para unificar autenticación, enrutamiento y CORS.

Dado que la puerta de enlace está en marcha  
Cuando el cliente web llama `https://gateway/api/companies`  
Entonces la puerta de enlace valida el token Bearer (o lo reenvía) y enruta al servicio de empresas.

Dado una ruta inexistente  
Cuando llamo a la puerta de enlace  
Entonces responde 404.

Dado un origen no permitido  
Cuando hay una petición preliminar CORS  
Entonces la puerta de enlace la rechaza.

---

### US-25 — Pipeline build-release-run

Como operador, quiero un pipeline diseño-compilación-publicación-ejecución, para publicar artefactos inmutables con la misma receta en local y nube.

Dado un commit en la rama principal  
Cuando corre el canal de integración  
Entonces construye imágenes, etiqueta la versión y no usa `latest` como único identificador de release.

Dado un release publicado  
Cuando se despliega  
Entonces solo se inyectan variables/secretos; no se recompila en el ambiente de run.

---

### US-26 — Actividad y preparación

Como operador, quiero sondas de actividad y de preparación, para que el orquestador reinicie o retire instancias no saludables.

Dado que el proceso vive pero Mongo no acepta conexiones  
Cuando se consulta la preparación  
Entonces falla (no recibe tráfico) mientras la actividad puede seguir OK si el proceso no está trabado.

Dado que el proceso está congelado  
Cuando falla la actividad  
Entonces la política de restart lo recrea.

---

## Sprint 5

### US-27 — Matching sugerido

Como interesado, quiero recibir sugerencias de materiales según ciudad y tipo, para descubrir intercambios viables más rápido.

Dado que publiqué o busqué tipo `metal` en `Medellín`  
Cuando pido sugerencias  
Entonces recibo materiales `available` ajenos de esa ciudad/tipo, ordenados por recencia o precio.

Dado que no hay coincidencias  
Cuando pido sugerencias  
Entonces lista vacía, no error.

---

### US-28 — Notificaciones

Como empresario, quiero recibir notificaciones de nuevas solicitudes, para responder sin vigilar el tablero.

Dado que alguien solicita mi material  
Cuando se crea la solicitud  
Entonces queda una notificación in-app (y/o log de evento) para mi `uid`.

Dado que no estoy autenticado  
Cuando listo notificaciones  
Entonces 401.

---

### US-29 — Impacto ambiental

Como empresario, quiero ver el impacto estimado (kg reutilizados) de mis intercambios, para evidenciar el valor circular.

Dado que cerré intercambios con cantidades en kg  
Cuando abro mi panel de impacto  
Entonces veo la suma de `quantity` de materiales `exchanged` de mis empresas.

Dado que no hay intercambios cerrados  
Cuando abro el panel  
Entonces el impacto es 0, no error.

---

### US-30 — Seed administrativo

Como operador, quiero ejecutar un proceso administrativo de carga inicial sin acoplarlo al proceso web en ejecución, para cargar datos de demo de forma repetible.

Dado un comando one-off (`manage.py seed_demo` o job de contenedor)  
Cuando lo ejecuto con las mismas variables de entorno  
Entonces inserta datos de demo en Atlas y termina; el proceso HTTP no queda bloqueado.

Dado que la carga inicial corre dos veces  
Cuando se ejecuta  
Entonces es idempotente o documenta que duplica de forma controlada.
