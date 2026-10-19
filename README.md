# Sistema de Reservas de Restaurante

Aplicacion para gestionar reservas de mesas en un restaurante, desarrollada en Python aplicando
programacion orientada a objetos, con interfaz de consola y una interfaz web (Flask), usando
Peewee como ORM y MySQL (administrado via phpMyAdmin) como motor de base de datos.

## 1. Descripcion del proyecto

El sistema permite registrar clientes y empleados, administrar restaurantes, zonas y mesas,
gestionar la disponibilidad horaria y registrar reservas con asignacion automatica de mesa
segun capacidad y horario solicitado.

Este proyecto se desarrolla para la asignatura de Programacion Orientada a Objetos Seguro y
aplica los cuatro pilares de la POO (abstraccion, encapsulamiento, herencia y polimorfismo),
ademas de una arquitectura en capas (presentacion, negocio y datos) conectada a una base de
datos relacional real.

## 2. Objetivos

- Registrar clientes y empleados con sus datos basicos.
- Administrar restaurantes, zonas y mesas.
- Registrar franjas de disponibilidad por mesa, fecha y horario.
- Registrar reservas indicando cliente, cantidad de personas y horario, con asignacion
  automatica de mesa disponible.
- Gestionar los estados de una reserva (Pendiente, Confirmada, Cancelada, Completada).
- Separar el codigo en capas (presentacion, negocio, datos) con clases reutilizables.
- Verificar el funcionamiento mediante pruebas automatizadas.

## 3. Tecnologias utilizadas

- **Python 3.12**: lenguaje principal.
- **Peewee**: ORM para interactuar con MySQL.
- **PyMySQL**: driver de conexion a MySQL.
- **Flask**: framework para la interfaz web.
- **python-decouple**: lectura de variables de entorno (.env).
- **unittest**: pruebas automatizadas (libreria estandar de Python).
- **MySQL / phpMyAdmin**: motor y administracion de la base de datos.

### Nota sobre la libreria de conexion a la base de datos

Para conectar la aplicacion a MySQL se utiliza **PyMySQL** como driver de bajo nivel,
en conjunto con **Peewee** como ORM. PyMySQL es una libreria escrita en Python puro,
ampliamente adoptada por la comunidad y compatible con el protocolo de MySQL, sin
depender de bibliotecas nativas en C. Es una alternativa estandar a
`mysql-connector-python` (la libreria oficial de Oracle) y es recomendada oficialmente
en la documentacion de varios frameworks y ORMs de Python (incluido Peewee) cuando se
busca una conexion ligera, multiplataforma y facil de instalar en entornos Windows,
como es el caso de este proyecto.

Esta decision permite que toda la capa de acceso a datos (`datos/conexion`,
`datos/modelos`, `datos/repositorio`) use una API consistente de Python para ejecutar
consultas SQL de forma segura (parametrizada), evitando inyeccion SQL y facilitando las
pruebas automatizadas de conexion incluidas en `pruebas/test_conexion.py`.

## 4. Arquitectura del proyecto

El sistema separa responsabilidades en tres capas principales: presentacion, negocio y datos.

### Dominio

Ubicacion: `dominio/`

Contiene las clases de negocio puras (sin dependencias de base de datos ni de interfaz),
que representan el modelo UML del sistema:

- `dominio/usuario.py` (clase base)
- `dominio/cliente.py` (hereda de Usuario)
- `dominio/empleado.py` (hereda de Usuario)
- `dominio/restaurant.py`
- `dominio/zona.py`
- `dominio/mesa.py`
- `dominio/reserva.py`
- `dominio/disponibilidad.py`

### Presentacion

Ubicacion: `presentacion/` y `web/`

El proyecto ofrece dos interfaces de usuario que comparten la misma capa de negocio:

- **Consola**: `presentacion/menu.py`, iniciada desde `main.py`. Menu navegable de 15
  opciones para gestionar clientes, empleados, restaurantes, zonas, mesas, disponibilidad
  y reservas.
- **Web**: `web/app.py`, interfaz Flask con plantillas en `web/templates/`. Incluye una
  vista publica de reserva (`/reservar`) con asignacion automatica de mesa, y vistas de
  administracion (CRUD) para cada entidad.

### Negocio

Ubicacion: `negocio/servicios/`

Contiene los servicios que coordinan las reglas de negocio y son usados tanto por la
consola como por la interfaz web, evitando duplicar logica:

- `negocio/servicios/reserva_servicio.py`: creacion de reservas (transaccional) y cambios
  de estado.
- `negocio/servicios/disponibilidad_servicio.py`: busqueda de franjas horarias disponibles.

### Acceso a datos

Ubicacion: `datos/` y `repositorios/`

- `datos/conexion.py`: configuracion de la conexion a MySQL mediante Peewee.
- `datos/modelos/orm_models.py`: modelos ORM (persistencia) de las 8 entidades.
- `repositorios/`: un repositorio por entidad (`ClienteRepositorio`, `EmpleadoRepositorio`,
  `RestaurantRepositorio`, `ZonaRepositorio`, `MesaRepositorio`, `DisponibilidadRepositorio`,
  `ReservaRepositorio`), todos heredando operaciones comunes de `BaseRepositorio`.

### Pruebas

Ubicacion: `pruebas/`

Pruebas automatizadas con `unittest`:

- `pruebas/test_conexion.py`: verifica la conexion a MySQL y la existencia de las tablas.
- `pruebas/test_reserva_servicio.py`: verifica reglas de negocio (validaciones de cantidad
  de personas, cliente inexistente, mesa inexistente, horarios invalidos).

## 5. Modelos y entidades principales

### Usuario

Clase base con nombre, correo, contrasena y telefono. Define metodos polimorficos
`obtener_rol()` y `realizar_accion_principal()`.

### Cliente (hereda de Usuario)

Anade preferencias alimentarias y puntos de fidelidad. Sobrescribe los metodos
polimorficos de Usuario.

### Empleado (hereda de Usuario)

Anade cargo y turno laboral. Sobrescribe los metodos polimorficos de Usuario.

### Restaurant

Nombre, direccion, telefono y horarios de apertura y cierre.

### Zona

Pertenece a un Restaurant. Indica si permite fumadores.

### Mesa

Pertenece a una Zona. Numero, capacidad de comensales y estado activo/inactivo.

### Disponibilidad

Franja horaria asociada a una Mesa, con fecha, hora de inicio, hora de fin y estado
(Disponible / Ocupado), y opcionalmente asociada a una Reserva.

### Reserva

Realizada por un Cliente. Incluye cantidad de personas, estado, observaciones y fecha
de creacion.

> Nota: el diagrama UML de este proyecto no incluye una relacion directa entre Empleado
> y Restaurant; la asignacion de personal no forma parte del alcance actual.

## 6. Estados de las reservas

- Pendiente
- Confirmada
- Cancelada
- Completada

Las transiciones permitidas se controlan en `dominio/reserva.py` y se aplican en
`ReservaServicio.cambiar_estado`. Una reserva pendiente puede confirmarse o cancelarse.
Una reserva confirmada puede cancelarse o completarse. Las reservas canceladas o
completadas no admiten nuevas transiciones.

Al cancelar una reserva, el sistema libera la franja de disponibilidad asociada.

## 7. Base de datos

Nombre de la base de datos: `reserva-restaurante`

Administrada mediante MySQL y visualizada/gestionada con phpMyAdmin. La conexion se
configura en `datos/conexion.py` utilizando Peewee y PyMySQL, con parametros leidos
desde variables de entorno.

Tablas principales: `usuario`, `cliente`, `empleado`, `restaurant`, `zona`, `mesa`,
`reserva`, `disponibilidad`.

## 8. Configuracion del entorno

### Requisitos previos

- Python 3.12 instalado.
- MySQL Server en ejecucion (gestionado con phpMyAdmin).
- Base de datos `reserva-restaurante` creada.
- Dependencias de `requirements.txt` instaladas.

### Variables de entorno

Crea un archivo `.env` en la raiz (puedes basarte en `.env.example`) con:DB_HOST=localhost
DB_PORT=3306
DB_NAME=reserva-restaurante
DB_USER=root
DB_PASS=tu_password
SECRET_KEY=una_clave_secreta 

El archivo `.env` no debe subirse al repositorio.

### Instalar dependencias
pip install -r requirements.txt
## 9. Ejecutar la aplicacion

### Interfaz de consola

Desde la raiz del proyecto:
python main.py

Muestra un menu navegable con 15 opciones para gestionar clientes, empleados,
restaurantes, zonas, mesas, disponibilidad y reservas.

### Interfaz web

Desde la raiz del proyecto:
python -m web.app

Luego abre en el navegador:http://127.0.0.1:5000/

Rutas principales:

- `/`: panel con conteos generales.
- `/reservar`: formulario publico de reserva con asignacion automatica de mesa.
- `/clientes`, `/empleados`, `/restaurantes`, `/disponibilidad`, `/reservas`: administracion
  CRUD de cada entidad.
- `/usuarios`: demostracion de polimorfismo entre Cliente y Empleado.

## 10. Ejecutar las pruebas

Desde la raiz del proyecto:python -m unittest discover -s pruebas -v

Actualmente se ejecutan 15 pruebas automatizadas que verifican la conexion a MySQL, la
existencia de las tablas principales y las reglas de negocio de creacion de reservas y
busqueda de disponibilidad.

## 11. Validaciones y comportamiento

El servicio de reservas (`ReservaServicio`) valida, entre otras reglas:

- Que la cantidad de personas sea un entero positivo.
- Que el cliente exista.
- Que la franja de disponibilidad exista y este libre.
- Que la mesa este activa y tenga capacidad suficiente.
- Que los cambios de estado respeten las transiciones permitidas.

La creacion de una reserva y la ocupacion de su franja se realizan dentro de una
transaccion de base de datos (`db.atomic()`), evitando condiciones de carrera.

## 12. Seguridad y buenas practicas

- Las credenciales se mantienen fuera del codigo fuente, en `.env` (ignorado por git).
- Se usan consultas del ORM (Peewee) en lugar de SQL concatenado.
- Las operaciones de escritura relevantes se ejecutan dentro de transacciones.
- Se mantiene un archivo `.gitignore` para evitar subir archivos temporales, cache de
  Python y credenciales.

## 13. Diagrama UML

El diagrama de clases del sistema se encuentra en la raiz del repositorio:

- `diagrama_uml.mmd`: codigo fuente del diagrama (formato Mermaid).
- `diagrama_uml.png`: imagen exportada del diagrama.

## 14. Limitaciones y mejoras futuras

- Completar pruebas funcionales end-to-end de la interfaz web.
- Anadir servicios de negocio para clientes, empleados, restaurantes, zonas y mesas
  (actualmente solo reservas y disponibilidad pasan explicitamente por la capa de negocio).
- Implementar autenticacion y autorizacion para las funciones administrativas.
- Reorganizar `datos/` con subcarpetas internas (repositorio, sql, auxiliares) segun la
  estructura objetivo de la asignatura.

## 15. Autoria

Proyecto academico: Sistema de Reservas de Restaurante.

Asignatura: Programacion Orientada a Objetos Seguro.