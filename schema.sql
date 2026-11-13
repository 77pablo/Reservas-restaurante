CREATE DATABASE IF NOT EXISTS ecotech_reservas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecotech_reservas;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre_completo VARCHAR(150) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    genero VARCHAR(30) NOT NULL,
    contrasena VARCHAR(72) NULL COMMENT 'Hash bcrypt o NULL'
) ENGINE = InnoDB;

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    preferencias TEXT,
    puntos_fidelidad INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    cargo VARCHAR(50) NOT NULL,
    turno VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE restaurant (
    id_restaurant INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    horario_apertura TIME NOT NULL,
    horario_cierre TIME NOT NULL
) ENGINE = InnoDB;

CREATE TABLE zona (
    id_zona INT AUTO_INCREMENT PRIMARY KEY,
    id_restaurant INT NOT NULL,
    nombre_zona VARCHAR(50) NOT NULL,
    permite_fumadores BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_restaurant) REFERENCES restaurant(id_restaurant) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE mesa (
    id_mesa INT AUTO_INCREMENT PRIMARY KEY,
    id_zona INT NOT NULL,
    numero_mesa INT NOT NULL,
    capacidad INT NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_zona) REFERENCES zona(id_zona) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    cant_personas INT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE disponibilidad (
    id_disponibilidad INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa INT NOT NULL,
    id_reserva INT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado_franja VARCHAR(20) NOT NULL DEFAULT 'Disponible',
    FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa) ON DELETE CASCADE,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva) ON DELETE SET NULL
) ENGINE = InnoDB;
