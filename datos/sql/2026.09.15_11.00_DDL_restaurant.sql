-- TABLA BASE: USUARIO
CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador único de cada usuario en el sistema',
    nombre_completo VARCHAR(150) NOT NULL COMMENT 'Nombre real del usuario',
    correo_electronico VARCHAR(100) UNIQUE NOT NULL COMMENT 'Correo para inicio de sesión y notificaciones',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto',
    contrasena VARCHAR(255) NOT NULL COMMENT 'Contraseña encriptada para autenticación'
) COMMENT = 'Tabla padre que almacena credenciales y datos base de cualquier persona';

-- TABLA: CLIENTE (Independiente con FK a Usuario)
CREATE TABLE Cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT COMMENT 'PK propia del perfil de cliente',
    id_usuario INT UNIQUE NOT NULL COMMENT 'FK al usuario base. UNIQUE asegura la relación 1:1',
    preferencias_alimentarias TEXT COMMENT 'Ej: Vegano, celíaco, alergias',
    puntos_fidelidad INT DEFAULT 0 COMMENT 'Sistema de puntos para recompensas',
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) COMMENT = 'Perfil transaccional para clientes del restaurante';

-- TABLA: EMPLEADO (Independiente con FK a Usuario)
CREATE TABLE Empleado (
    id_empleado INT PRIMARY KEY AUTO_INCREMENT COMMENT 'PK propia del perfil de empleado',
    id_usuario INT UNIQUE NOT NULL COMMENT 'FK al usuario base. UNIQUE asegura la relación 1:1',
    cargo VARCHAR(50) NOT NULL COMMENT 'Rol general: Recepcionista, Jefe de comedor, Chef, Administrador',
    fecha_contratacion DATE COMMENT 'Fecha de ingreso a la empresa',
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
) COMMENT = 'Perfil administrativo/operativo para el personal';

-- TABLA: RESTAURANT
CREATE TABLE Restaurant (
    id_restaurant INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador único del establecimiento',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre comercial del restaurante',
    direccion VARCHAR(200) NOT NULL COMMENT 'Ubicación física',
    telefono_contacto VARCHAR(20) COMMENT 'Teléfono central del local',
    horario_apertura TIME NOT NULL COMMENT 'Hora de inicio de operaciones',
    horario_cierre TIME NOT NULL COMMENT 'Hora de fin de operaciones'
) COMMENT = 'Almacena la información física y operativa del establecimiento';

-- TABLA AUXILIAR N:M: EMPLEADO_RESTAURANT
CREATE TABLE Empleado_Restaurant (
    id_empleado INT NOT NULL COMMENT 'FK del empleado asignado',
    id_restaurant INT NOT NULL COMMENT 'FK del restaurante donde trabaja',
    turno VARCHAR(50) NOT NULL COMMENT 'Ej: Mañana, Tarde, Fines de semana en ESTE local',
    PRIMARY KEY (id_empleado, id_restaurant) COMMENT 'Clave primaria compuesta',
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) ON DELETE CASCADE,
    FOREIGN KEY (id_restaurant) REFERENCES Restaurant(id_restaurant) ON DELETE CASCADE
) COMMENT = 'Tabla puente para que un empleado trabaje en múltiples restaurantes y viceversa';

-- TABLA: ZONA 
CREATE TABLE Zona (
    id_zona INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador único de la zona o ambiente',
    id_restaurant INT NOT NULL COMMENT 'FK al restaurante al que pertenece',
    nombre_zona VARCHAR(50) NOT NULL COMMENT 'Ej: Terraza, Salón Principal, VIP',
    permite_fumadores BOOLEAN DEFAULT FALSE COMMENT 'Indica si rige ley de tabaco en esta área',
    FOREIGN KEY (id_restaurant) REFERENCES Restaurant(id_restaurant) ON DELETE CASCADE
) COMMENT = 'Divisiones físicas del restaurante donde se agrupan las mesas';

-- TABLA: MESA 
CREATE TABLE Mesa (
    id_mesa INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador único de la mesa física',
    id_zona INT NOT NULL COMMENT 'FK a la zona donde está ubicada',
    numero_mesa INT NOT NULL COMMENT 'Número visible para clientes y personal',
    capacidad_comensales INT NOT NULL COMMENT 'Cantidad máxima de personas que caben',
    activa BOOLEAN DEFAULT TRUE COMMENT 'Indica si la mesa está habilitada para uso',
    FOREIGN KEY (id_zona) REFERENCES Zona(id_zona) ON DELETE CASCADE
) COMMENT = 'Mesas físicas disponibles dentro de cada zona del restaurante';

-- TABLA: RESERVA 
CREATE TABLE Reserva (
    id_reserva INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador único de la transacción',
    id_cliente INT NOT NULL COMMENT 'FK del cliente que solicita la reserva',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Cuándo se registró la solicitud en sistema',
    cantidad_personas INT NOT NULL COMMENT 'Número de asistentes esperados',
    estado VARCHAR(20) NOT NULL COMMENT 'Pendiente, Confirmada, Cancelada, Completada',
    observaciones_especiales TEXT COMMENT 'Anotaciones extra (ej: Silla de bebé, Cumpleaños)',
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
) COMMENT = 'Cabecera de la transacción de reserva solicitada por un cliente';

-- TABLA: DISPONIBILIDAD 
CREATE TABLE Disponibilidad (
    id_disponibilidad INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador de la franja de tiempo',
    id_mesa INT NOT NULL COMMENT 'FK de la mesa a la que aplica este horario',
    id_reserva INT COMMENT 'FK de la reserva asignada (NULL si está libre)',
    fecha DATE NOT NULL COMMENT 'Día calendario de esta disponibilidad',
    hora_inicio TIME NOT NULL COMMENT 'Hora exacta en la que empieza la franja',
    hora_fin TIME NOT NULL COMMENT 'Hora exacta en la que termina la franja',
    estado_franja VARCHAR(20) NOT NULL COMMENT 'Libre, Ocupado, Bloqueado (ej: por limpieza)',
    FOREIGN KEY (id_mesa) REFERENCES Mesa(id_mesa) ON DELETE CASCADE,
    FOREIGN KEY (id_reserva) REFERENCES Reserva(id_reserva) ON DELETE SET NULL
) COMMENT = 'Gestión del tiempo y estado de cada mesa en el restaurante';