\# 🍽️ EcoTech Solutions - Sistema de Gestión de Reservas de Restaurante



\*\*Asignatura:\*\* Programación Orientada a Objetos Segura (TI3021)  


\*\*Unidad 2:\*\* Implementación de Software Orientado a Objetos en Python  



\---



\## 📌 Descripción del Proyecto

Este proyecto corresponde a la implementación en Python del prototipo estructural para la \*\*"Optimización del Sistema de Gestión Interna en EcoTech Solutions"\*\*. Soluciona la administración de reservas de restaurante traduciendo un diagrama UML validado a código fuente orientado a objetos, integrado con una base de datos MySQL relacional y aplicando estándares de seguridad mediante encriptación \*\*Bcrypt\*\*.



\---



\## 🚀 Características y Principios POO Aplicados



1\. \*\*Traducción Fiel del Modelo UML (Criterio 2.1.1):\*\*

&#x20;  - Implementación completa de las 8 clases de dominio: `Usuario`, `Cliente`, `Empleado`, `Restaurant`, `Zona`, `Mesa`, `Reserva` y `Disponibilidad`.

&#x20;  - Representación estricta de relaciones:

&#x20;    - \*\*Herencia:\*\* `Cliente` y `Empleado` heredan de la clase abstracta `Usuario`.

&#x20;    - \*\*Composición / Asociación:\*\* `Restaurant` ➔ `Zona` ➔ `Mesa` ➔ `Disponibilidad` / `Cliente` ➔ `Reserva` ➔ `Disponibilidad`.



2\. \*\*Encapsulamiento y Reutilización de Código (Criterio 2.1.2):\*\*

&#x20;  - \*\*Encapsulamiento:\*\* Ocultamiento de atributos privados (`\_atributo`) con acceso controlado mediante propiedades (`@property` y `@setter`) y validaciones en tiempo de asignación.

&#x20;  - \*\*Reutilización:\*\* Uso de `BaseRepositorio` para abstraer operaciones SQL redundantes y evitar la duplicación de código.



3\. \*\*Conexión Segura a BD y Persistencia (Criterio 2.1.3):\*\*

&#x20;  - Conexión a MySQL utilizando la librería oficial \*\*`mysql-connector-python`\*\*.

&#x20;  - Manejo de variables de entorno mediante `python-decouple` (`.env`) para resguardar credenciales de BD.



4\. \*\*Seguridad y Encriptación (Requerimiento Especial):\*\*

&#x20;  - Incorporación de la librería \*\*`bcrypt`\*\* para la protección de credenciales.

&#x20;  - Las contraseñas en MySQL soportan valores `VARCHAR(72) NULL`, permitiendo que el usuario se cree sin contraseña y la defina/encripte posteriormente.

&#x20;  - Verificación de credenciales mediante `bcrypt.checkpw` sin almacenar jamás texto plano.



\---



\## 📁 Estructura del Proyecto



```text

ecotech\_reservas/

│

├── config/

│   └── configuracion.py       # Lectura centralizada de variables de entorno (.env)

├── conexion/

│   └── conexion\_bd.py         # Conexión oficial a MySQL (mysql-connector)

├── modelos/                   # Clases de Dominio (POO pura)

│   ├── usuario.py             # Clase base abstracta con lógica Bcrypt

│   ├── cliente.py             # Subclase Cliente

│   ├── empleado.py            # Subclase Empleado

│   ├── restaurant.py          # Entidad Restaurant

│   ├── zona.py                # Entidad Zona

│   ├── mesa.py                # Entidad Mesa

│   ├── reserva.py             # Entidad Reserva

│   └── disponibilidad.py     # Entidad Disponibilidad

├── repositorios/              # Capa de Persistencia (Patrón Repository)

│   ├── base\_repositorio.py    # Repositorio base con manejo de SQL a prueba de fallos

│   ├── usuario\_repositorio.py

│   ├── cliente\_repositorio.py

│   └── empleado\_repositorio.py

├── .env                       # Credenciales privadas de base de datos

├── .gitignore                 # Archivos excluidos del control de versiones

├── main.py                    # Punto de entrada y script de prueba estructural

├── requirements.txt           # Dependencias del proyecto

└── schema.sql                 # Script DDL de la base de datos MySQL

