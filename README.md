# Reservas-restaurante



\# Sistema de Reservas de Restaurante



Aplicación web para gestionar reservas de mesas en un restaurante, desarrollada en Python con Flask, Peewee y MySQL.



\## 1. Descripción del proyecto



El sistema permite registrar reservas, consultar las reservas existentes y gestionar sus estados. También mantiene información sobre clientes, mesas, horarios y disponibilidad.



Este proyecto se desarrolla para la asignatura de Programación Orientada a Objetos Seguro y busca aplicar principios de programación orientada a objetos, separación de responsabilidades, persistencia de datos y validación de información.



\## 2. Objetivos



\- Registrar reservas indicando cliente, fecha, horario y cantidad de personas.

\- Consultar las reservas y sus datos asociados.

\- Gestionar los estados de una reserva.

\- Verificar la disponibilidad y la capacidad de las mesas.

\- Mantener los datos históricos de las reservas.

\- Organizar el código mediante capas y clases reutilizables.

\- Comprobar el funcionamiento mediante pruebas automatizadas.



\## 3. Tecnologías utilizadas



\- \*\*Python:\*\* lenguaje principal.

\- \*\*Flask:\*\* framework para la aplicación web.

\- \*\*Peewee:\*\* ORM para interactuar con la base de datos.

\- \*\*MySQL:\*\* sistema de gestión de base de datos.

\- \*\*python-decouple:\*\* lectura de parámetros de configuración.

\- \*\*unittest:\*\* ejecución de pruebas automatizadas.



\## 4. Arquitectura del proyecto



El sistema separa las responsabilidades en distintas capas.



\### Presentación



Ubicación: `presentacion/`



Contiene la aplicación Flask y las plantillas HTML que permiten al usuario interactuar con el sistema.



Archivos principales:



\- `presentacion/app.py`

\- `presentacion/templates/index.html`

\- `presentacion/templates/reservar.html`

\- `presentacion/templates/reservas.html`



\### Negocio



Ubicación: `negocio/servicios/`



Contiene los servicios que coordinan las operaciones del sistema.



Archivo principal:



\- `negocio/servicios/reserva\_servicio.py`



\### Acceso a datos



Ubicación: `datos/`



Contiene la configuración de conexión a MySQL, los modelos de persistencia y los repositorios.



Archivos principales:



\- `datos/conexion.py`

\- `datos/modelos/models.py`

\- `datos/repositorio/cliente\_repositorio.py`

\- `datos/repositorio/reserva\_repositorio.py`



\### Pruebas



Ubicación: `pruebas/`



Contiene las pruebas automatizadas del proyecto.



\- `pruebas/test\_conexion.py`

\- `pruebas/test\_reserva\_repositorio.py`



\## 5. Modelos y entidades principales



\### Usuario



Representa la información común de los usuarios, como nombre, correo electrónico, contraseña y teléfono.



\### Cliente



Hereda de `Usuario` y añade preferencias alimentarias y puntos de fidelidad.



\### Empleado



Hereda de `Usuario` e incorpora información laboral, como cargo y fecha de contratación.



\### Restaurant



Representa el restaurante, su dirección, nombre, teléfono y horarios de apertura y cierre.



\### Zona



Representa una zona del restaurante y se relaciona con el restaurante correspondiente.



\### Mesa



Representa una mesa, su número, capacidad de comensales y estado de actividad.



\### Reserva



Representa una reserva realizada por un cliente. Incluye cantidad de personas, estado, observaciones y datos históricos de fecha, horario y mesa.



\### Disponibilidad



Representa las franjas horarias asociadas a las mesas y permite registrar si una franja está disponible o reservada.



\### EmpleadoRestaurant



Representa la asociación entre empleados y restaurantes, incluyendo el turno correspondiente.



Los modelos de dominio y los modelos de persistencia se encuentran diferenciados en `datos/modelos/models.py`.



\## 6. Estados de las reservas



El sistema contempla los siguientes estados:



\- `Pendiente`

\- `Confirmada`

\- `Cancelada`

\- `Completada`



Las transiciones permitidas se controlan en `ReservaRepositorio`.



Una reserva pendiente puede confirmarse o cancelarse. Una reserva confirmada puede cancelarse o completarse. Las reservas canceladas o completadas no admiten nuevas transiciones según las reglas actuales.



Al cancelar una reserva, el sistema libera la franja de disponibilidad asociada y conserva los datos históricos guardados en la reserva.



\## 7. Base de datos



Nombre de la base de datos: `reserva-restaurante`



La conexión se configura en `datos/conexion.py` utilizando Peewee y parámetros externos.



Entre las tablas principales se encuentran:



\- `usuario`

\- `cliente`

\- `empleado`

\- `restaurant`

\- `zona`

\- `mesa`

\- `reserva`

\- `disponibilidad`

\- `empleado\_restaurant`



La estructura debe existir previamente en MySQL y ser compatible con los modelos definidos en el proyecto.



\## 8. Configuración del entorno



\### Requisitos previos



\- Python instalado.

\- MySQL Server en ejecución.

\- Una base de datos compatible llamada `reserva-restaurante`.

\- Las dependencias de Python instaladas.



\### Configurar las credenciales



El archivo `datos/conexion.py` obtiene la configuración mediante `python-decouple`.



Los parámetros utilizados para la conexión son:



\- `database`

\- `host`

\- `port`

\- `user`

\- `password`



Configura estos valores en el archivo de entorno que utiliza el proyecto. No publiques contraseñas ni credenciales reales en el repositorio.



También configura la clave secreta de Flask según el nombre que utilice `presentacion/app.py`.



\### Instalar dependencias



Activa tu entorno virtual, si utilizas uno, e instala las dependencias del proyecto.



Las dependencias deben corresponder a los módulos que importa la aplicación y a tu controlador MySQL. Puedes revisar los imports de los archivos antes de instalar paquetes adicionales.



\## 9. Ejecutar la aplicación



Desde la carpeta raíz del proyecto, ejecuta:



```powershell

python -m presentacion.app

```



Después abre en el navegador la dirección local configurada por Flask:



`http://127.0.0.1:5055/`



Las rutas principales son:



\- `/`: página de inicio.

\- `/reservar`: formulario de creación de reservas.

\- `/reservas`: administración de reservas.

\- `/reservas/<id\_reserva>/estado`: gestión del estado de una reserva.

\- `/salud`: ruta de comprobación de la aplicación.



\## 10. Ejecutar las pruebas



Desde la raíz del proyecto, ejecuta:



```powershell

python -m unittest discover -s pruebas -v

```



Las pruebas actuales comprueban la conexión a MySQL, la existencia de las tablas principales, la conversión y validación de fechas y horas, y las reglas permitidas para las transiciones de estado.



La salida `OK` indica que las pruebas descubiertas se ejecutaron sin fallos. Esto no significa que todas las funcionalidades estén cubiertas por pruebas automatizadas.



\## 11. Validaciones y comportamiento



El repositorio de reservas comprueba, entre otras reglas:



\- Que la cantidad de personas sea válida.

\- Que la fecha no esté en el pasado.

\- Que la hora de inicio sea anterior a la hora de término.

\- Que exista un cliente registrado.

\- Que la franja horaria esté disponible.

\- Que la mesa esté activa y tenga capacidad suficiente.

\- Que los cambios de estado respeten las transiciones permitidas.



La creación de una reserva y el bloqueo de su franja se realizan dentro de una transacción de base de datos.



\## 12. Seguridad y buenas prácticas



\- Mantener las credenciales fuera del código fuente.

\- No publicar archivos de entorno con contraseñas.

\- Validar los datos enviados mediante formularios.

\- Utilizar consultas del ORM en lugar de construir consultas SQL con valores concatenados.

\- Mantener la protección CSRF habilitada en los formularios que modifican información.

\- Verificar las reglas de autorización antes de permitir acciones administrativas.

\- Ejecutar las pruebas antes de entregar cambios.

\- Mantener copias de seguridad antes de modificar la estructura o los datos de la base de datos.



\## 13. Limitaciones y mejoras futuras



Las siguientes mejoras pueden incorporarse a medida que avance el proyecto:



\- Completar las pruebas funcionales de creación, confirmación y cancelación de reservas.

\- Añadir pruebas de integración para la disponibilidad y asignación de mesas.

\- Documentar el diagrama UML y sus relaciones.

\- Mejorar el encapsulamiento de las clases donde corresponda.

\- Implementar autenticación y autorización para las funciones administrativas.

\- Incorporar documentación de instalación y dependencias verificadas.

\- Completar los datos históricos de reservas antiguas únicamente cuando exista evidencia fiable.



\## 14. Estado de las pruebas



Durante el desarrollo se ejecutaron 14 pruebas automatizadas con resultado satisfactorio.



También se comprobó manualmente el registro de una reserva y su cancelación, verificando que sus datos históricos se conservaran y que la franja asociada volviera a estar disponible.



Estas comprobaciones son evidencia parcial del funcionamiento y deben complementarse con las pruebas que exija la evaluación académica.



\## 15. Autoría



Proyecto académico: Sistema de Reservas de Restaurante.



Asignatura: Programación Orientada a Objetos Seguro.



