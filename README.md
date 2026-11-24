# 🍽️ EcoTech Solutions - Sistema de Gestión de Reservas de Restaurante

**Asignatura:** Programación Orientada a Objetos Segura (TI3021)  
**Unidad 2:** Implementación de Software Orientado a Objetos en Python  

---

## 📌 Descripción del Proyecto

Este proyecto corresponde a la implementación en Python del prototipo estructural para la **"Optimización del Sistema de Gestión Interna en EcoTech Solutions"**. Aborda la administración de reservas de restaurante traduciendo un modelo UML validado a código fuente orientado a objetos, integrado con una base de datos MySQL relacional y aplicando prácticas de seguridad mediante hashing de contraseñas con **Bcrypt** e ingreso enmascarado con **Maskpass**.

---

## 🚀 Características y Principios POO Aplicados

1. **Traducción Fiel del Modelo UML:**
   - Implementación de las clases de dominio: `Usuario`, `Cliente`, `Empleado`, `Restaurant`, `Zona`, `Mesa`, `Reserva` y `Disponibilidad`.
   - **Herencia:** `Cliente` y `Empleado` heredan de la clase base `Usuario`.
   - **Composición / Asociación:** `Restaurant` ➔ `Zona` ➔ `Mesa` ➔ `Disponibilidad` y `Cliente` ➔ `Reserva` ➔ `Disponibilidad`.

2. **Encapsulamiento, Validación y Reutilización:**
   - **Encapsulamiento:** Atributos internos (`_atributo`) expuestos mediante `@property` y `@setter` con validaciones de dominio (como RUT, género, cantidad de personas y estados de reserva).
   - **Validaciones centralizadas:** Reglas de formato y consistencia agrupadas en `validaciones.py`.
   - **Patrón Repository:** `BaseRepositorio` centraliza el acceso a MySQL para evitar duplicación de lógica de conexión y ejecución SQL.

3. **Conexión Segura a BD y Persistencia:**
   - Conexión a MySQL mediante **`mysql-connector-python`** con codificación `utf8mb4`.
   - Gestión de credenciales a través de variables de entorno con **`python-decouple`** y archivo `.env` (excluido de Git vía `.gitignore`).

4. **Seguridad, Encriptación e Ingreso Oculto:**
   - Encriptación de contraseñas con **`bcrypt`** (`bcrypt.gensalt()`, `bcrypt.hashpw()` y `bcrypt.checkpw()`).
   - Ingreso oculto de contraseñas en consola mediante **`maskpass`** (con respaldo automático a `getpass` si el entorno lo requiere) a través de `entrada_segura.py`.
   - Soporte para usuarios creados inicialmente sin contraseña (`NULL` en base de datos), rechazando inicios de sesión hasta que se establezca un hash válido.

---

## 📁 Estructura del Proyecto

```text
Reservas-restaurante/
├── config/
│   └── configuracion.py        # Lectura centralizada de variables de entorno (.env)
├── conexion/
│   └── conexion_bd.py          # Gestión y prueba de conexión a MySQL
├── modelos/                    # Clases de dominio
│   ├── usuario.py
│   ├── cliente.py
│   ├── empleado.py
│   ├── restaurant.py
│   ├── zona.py
│   ├── mesa.py
│   ├── reserva.py
│   └── disponibilidad.py
├── repositorios/               # Capa de persistencia (Patrón Repository)
│   ├── base_repositorio.py
│   ├── usuario_repositorio.py
│   ├── empleado_repositorio.py
│   └── ...
├── entrada_segura.py           # Solicitud oculta de contraseñas (maskpass + getpass)
├── validaciones.py             # Validaciones de negocio (RUT, género, etc.)
├── main.py                     # Script de prueba del flujo, Bcrypt y Maskpass
├── requirements.txt            # Dependencias del proyecto
├── schema.sql                  # Script DDL de la base de datos MySQL
└── .gitignore                  # Archivos excluidos del control de versiones