-- ============================================
-- Usar la base de datos
-- ============================================
USE `reserva-restaurante`;

-- ============================================
-- PASO 1: Eliminar TODAS las tablas existentes
-- (orden inverso a las dependencias de FK)
-- ============================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS disponibilidad;
DROP TABLE IF EXISTS reserva;
DROP TABLE IF EXISTS empleado_restaurant;
DROP TABLE IF EXISTS mesa;
DROP TABLE IF EXISTS zona;
DROP TABLE IF EXISTS restaurant;
DROP TABLE IF EXISTS empleado;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS usuario;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- PASO 2: Crear tablas en orden correcto
-- ============================================

-- Tabla padre (clase Usuario del UML)
CREATE TABLE usuario (
    id_usuario       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo  VARCHAR(150) NOT NULL,
    correo           VARCHAR(100) NOT NULL UNIQUE,
    telefono         VARCHAR(20),
    contrasena       VARCHAR(255) NOT NULL
) ENGINE=InnoDB COMMENT='Datos base de cualquier usuario del sistema';

-- Cliente hereda de Usuario (relacion 1:1)
CREATE TABLE cliente (
    id_cliente        INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario        INT NOT NULL UNIQUE,
    preferencias      TEXT,
    puntos_fidelidad  INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Perfil de cliente (hereda de Usuario)';

-- Empleado hereda de Usuario (relacion 1:1)
CREATE TABLE empleado (
    id_empleado   INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario    INT NOT NULL UNIQUE,
    cargo         VARCHAR(50) NOT NULL,
    turno         VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Perfil de empleado (hereda de Usuario)';

CREATE TABLE restaurant (
    id_restaurant     INT AUTO_INCREMENT PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    direccion         VARCHAR(200) NOT NULL,
    telefono          VARCHAR(20),
    horario_apertura  TIME NOT NULL,
    horario_cierre    TIME NOT NULL
) ENGINE=InnoDB COMMENT='Establecimientos EcoTech Solutions';

-- Restaurant 1 -- * Zona
CREATE TABLE zona (
    id_zona            INT AUTO_INCREMENT PRIMARY KEY,
    id_restaurant      INT NOT NULL,
    nombre_zona        VARCHAR(50) NOT NULL,
    permite_fumadores  BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_restaurant) REFERENCES restaurant(id_restaurant) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Zonas o ambientes dentro de un restaurant';

-- Zona 1 -- * Mesa
CREATE TABLE mesa (
    id_mesa        INT AUTO_INCREMENT PRIMARY KEY,
    id_zona        INT NOT NULL,
    numero_mesa    INT NOT NULL,
    capacidad      INT NOT NULL,
    activa         BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_zona) REFERENCES zona(id_zona) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Mesas fisicas dentro de una zona';

-- Cliente 1 -- * Reserva
CREATE TABLE reserva (
    id_reserva       INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente       INT NOT NULL,
    fecha_creacion   DATETIME DEFAULT CURRENT_TIMESTAMP,
    cant_personas    INT NOT NULL,
    estado           VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    observaciones    TEXT,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Reservas realizadas por clientes';

-- Mesa 1 -- * Disponibilidad  /  Reserva 1 -- 1..* Disponibilidad
CREATE TABLE disponibilidad (
    id_disponibilidad  INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa            INT NOT NULL,
    id_reserva         INT NULL,
    fecha              DATE NOT NULL,
    hora_inicio        TIME NOT NULL,
    hora_fin           TIME NOT NULL,
    estado_franja      VARCHAR(20) NOT NULL DEFAULT 'Disponible',
    FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa) ON DELETE CASCADE,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Franjas horarias de disponibilidad por mesa';
-- ============================================
-- PASO 3: Datos de ejemplo (datos reales del proyecto)
-- ============================================
SET FOREIGN_KEY_CHECKS = 0;
INSERT INTO `usuario` (`id_usuario`, `nombre_completo`, `correo`, `telefono`, `contrasena`) VALUES ('1', 'Pablo Espinoza', 'pablo.espinoza@correo.cl', '+56912345678', 'password123');
INSERT INTO `usuario` (`id_usuario`, `nombre_completo`, `correo`, `telefono`, `contrasena`) VALUES ('2', 'Ana Torres', 'ana.torres@ecotech.cl', '+56987654321', 'clave12345');
INSERT INTO `cliente` (`id_cliente`, `id_usuario`, `preferencias`, `puntos_fidelidad`) VALUES ('1', '1', 'Sin restricciones', '100');
INSERT INTO `empleado` (`id_empleado`, `id_usuario`, `cargo`, `turno`) VALUES ('1', '2', 'Jefe de comedor', 'Tarde');
INSERT INTO `restaurant` (`id_restaurant`, `nombre`, `direccion`, `telefono`, `horario_apertura`, `horario_cierre`) VALUES ('1', 'EcoTech Bistro', 'Av. Siempre Verde 123, Temuco', '+56912345000', '12:00:00', '23:00:00');
INSERT INTO `restaurant` (`id_restaurant`, `nombre`, `direccion`, `telefono`, `horario_apertura`, `horario_cierre`) VALUES ('2', 'EcoTech Bistro', 'Av. Siempre Verde 123, Temuco', '+56912345000', '12:00:00', '23:00:00');
INSERT INTO `restaurant` (`id_restaurant`, `nombre`, `direccion`, `telefono`, `horario_apertura`, `horario_cierre`) VALUES ('3', 'EcoTech Bistro', 'Av. Siempre Verde 123, Temuco', '+56912345000', '12:00:00', '23:00:00');
INSERT INTO `restaurant` (`id_restaurant`, `nombre`, `direccion`, `telefono`, `horario_apertura`, `horario_cierre`) VALUES ('4', 'EcoTech Bistro', 'Av. Siempre Verde 123, Temuco', '+56912345000', '12:00:00', '23:00:00');
INSERT INTO `restaurant` (`id_restaurant`, `nombre`, `direccion`, `telefono`, `horario_apertura`, `horario_cierre`) VALUES ('5', 'AP', 'los alerces', '+569832323', '10:00:00', '02:00:00');
INSERT INTO `zona` (`id_zona`, `id_restaurant`, `nombre_zona`, `permite_fumadores`) VALUES ('1', '1', 'Terraza', '0');
INSERT INTO `zona` (`id_zona`, `id_restaurant`, `nombre_zona`, `permite_fumadores`) VALUES ('2', '2', 'Terraza', '0');
INSERT INTO `zona` (`id_zona`, `id_restaurant`, `nombre_zona`, `permite_fumadores`) VALUES ('3', '3', 'Terraza', '0');
INSERT INTO `zona` (`id_zona`, `id_restaurant`, `nombre_zona`, `permite_fumadores`) VALUES ('4', '4', 'Terraza', '0');
INSERT INTO `mesa` (`id_mesa`, `id_zona`, `numero_mesa`, `capacidad`, `activa`) VALUES ('1', '1', '1', '4', '1');
INSERT INTO `mesa` (`id_mesa`, `id_zona`, `numero_mesa`, `capacidad`, `activa`) VALUES ('2', '2', '1', '4', '1');
INSERT INTO `mesa` (`id_mesa`, `id_zona`, `numero_mesa`, `capacidad`, `activa`) VALUES ('3', '3', '1', '4', '1');
INSERT INTO `mesa` (`id_mesa`, `id_zona`, `numero_mesa`, `capacidad`, `activa`) VALUES ('4', '4', '1', '4', '1');
INSERT INTO `reserva` (`id_reserva`, `id_cliente`, `fecha_creacion`, `cant_personas`, `estado`, `observaciones`) VALUES ('1', '1', '2026-10-18 23:38:57', '4', 'Confirmada', 'Celebracion de cumpleanos');
INSERT INTO `reserva` (`id_reserva`, `id_cliente`, `fecha_creacion`, `cant_personas`, `estado`, `observaciones`) VALUES ('2', '1', '2026-10-19 14:24:04', '4', 'Confirmada', 'Celebracion de cumpleanos');
INSERT INTO `disponibilidad` (`id_disponibilidad`, `id_mesa`, `id_reserva`, `fecha`, `hora_inicio`, `hora_fin`, `estado_franja`) VALUES ('1', '1', '1', '2026-10-18', '19:00:00', '21:00:00', 'Ocupado');
INSERT INTO `disponibilidad` (`id_disponibilidad`, `id_mesa`, `id_reserva`, `fecha`, `hora_inicio`, `hora_fin`, `estado_franja`) VALUES ('2', '2', NULL, '2026-10-19', '19:00:00', '21:00:00', 'Disponible');
INSERT INTO `disponibilidad` (`id_disponibilidad`, `id_mesa`, `id_reserva`, `fecha`, `hora_inicio`, `hora_fin`, `estado_franja`) VALUES ('3', '3', NULL, '2026-10-19', '19:00:00', '21:00:00', 'Disponible');
INSERT INTO `disponibilidad` (`id_disponibilidad`, `id_mesa`, `id_reserva`, `fecha`, `hora_inicio`, `hora_fin`, `estado_franja`) VALUES ('4', '4', '2', '2026-10-19', '19:00:00', '21:00:00', 'Ocupado');
INSERT INTO `disponibilidad` (`id_disponibilidad`, `id_mesa`, `id_reserva`, `fecha`, `hora_inicio`, `hora_fin`, `estado_franja`) VALUES ('5', '1', NULL, '2026-10-19', '19:00:00', '21:00:00', 'Disponible');
SET FOREIGN_KEY_CHECKS = 1;
