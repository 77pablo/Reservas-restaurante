from conexion.conexion_bd import ConexionBD
from modelos.empleado import Empleado
from repositorios.empleado_repositorio import EmpleadoRepositorio
from entrada_segura import solicitar_contrasena


def main():
    print("=" * 60)
    print(" EcoTech Solutions - Seguridad y Encriptación (Bcrypt)")
    print("=" * 60)

    if not ConexionBD().probar_conexion():
        print("Revisa tu wamp y el archivo .env")
        return

    empleado_repo = EmpleadoRepositorio()

    # Limpia registro previo de prueba si existe para permitir reejecuciones
    empleado_repo._ejecutar_consulta(
        "DELETE FROM empleado WHERE id_usuario IN (SELECT id_usuario FROM usuario WHERE rut = %s)",
        ("12.345.678-5",),
    )
    empleado_repo._ejecutar_consulta(
        "DELETE FROM usuario WHERE rut = %s",
        ("12.345.678-5",),
    )

    # 1. Crear sin contraseña (NULL en DB)
    print("\n--- 1. Creando usuario SIN contraseña (NULO) ---")

    nuevo_empleado = Empleado(
        nombre_completo="Carlos Administrador",
        rut="12.345.678-5",
        correo="carlos.admin@ecotech.cl",
        telefono="+56912345678",
        genero="1",
        contrasena=None,
        cargo="Administrador",
        turno="Mañana",
    )

    try:
        id_creado = empleado_repo.crear(nuevo_empleado)
        if not id_creado:
            print("[ERROR] No se pudo crear el empleado en la base de datos.")
            return
        print(f"[OK] Empleado creado (ID usuario: {nuevo_empleado.id_usuario}, ID empleado: {nuevo_empleado.id_empleado})")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el empleado: {e}")
        return

    # 2. Intento de login sin clave
    print("\n--- 2. Intentando Login sin contraseña ---")
    if not nuevo_empleado.iniciar_sesion("cualquier_clave"):
        print("[OK] Sistema rechazó el login. La clave es NULA.")

    # 3. Establecer contraseña con maskpass + bcrypt
    print("\n--- 3. Usuario establece su contraseña ---")
    nueva_clave = solicitar_contrasena(
        prompt="Define la contraseña del empleado: ",
        mask="*",
        confirmar=True,
    )
    nuevo_empleado.establecer_contrasena(nueva_clave)
    empleado_repo.actualizar(nuevo_empleado)
    print("[OK] Contraseña encriptada y guardada en BD.")
    print(f"[HASH BCRYPT GENERADO]: {nuevo_empleado.contrasena}")

    # 4. Pruebas de Login con ingreso oculto
    print("\n--- 4. Pruebas de Login ---")
    clave_prueba = solicitar_contrasena(
        prompt="Ingresa la contraseña para iniciar sesión: ",
        mask="*",
        confirmar=False,
    )
    if nuevo_empleado.iniciar_sesion(clave_prueba):
        print("[OK] Login exitoso. ¡Bienvenido Carlos!")
    else:
        print("[OK] Login fallido. Acceso denegado.")


if __name__ == "__main__":
    main()