from conexion.conexion_bd import ConexionBD
from modelos.empleado import Empleado
from repositorios.empleado_repositorio import EmpleadoRepositorio

def main():
    print("=" * 60)
    print(" EcoTech Solutions - Seguridad y Encriptación (Bcrypt)")
    print("=" * 60)

    if not ConexionBD().probar_conexion():
        print("Revisa tu XAMPP y el archivo .env")
        return

    empleado_repo = EmpleadoRepositorio()

    # 1. Crear sin contraseña (NULL en DB)
    print("\n--- 1. Creando usuario SIN contraseña (NULO) ---")
    nuevo_empleado = Empleado(
        nombre_completo="Carlos Administrador",
        correo="carlos.admin@ecotech.cl",
        telefono="+56912345678",
        cargo="Administrador",
        turno="Mañana"
    )
    empleado_repo.crear(nuevo_empleado)
    print(f"[OK] Empleado creado: {nuevo_empleado}")

    # 2. Intento de login sin clave
    print("\n--- 2. Intentando Login sin contraseña ---")
    if not nuevo_empleado.iniciar_sesion("cualquier_clave"):
         print("[OK] Sistema rechazó el login. La clave es NULA.")

    # 3. Establecer contraseña con bcrypt
    print("\n--- 3. Usuario establece su contraseña ---")
    nuevo_empleado.establecer_contrasena("MiSuperClaveSegura2026")
    empleado_repo.actualizar(nuevo_empleado)
    print(f"[OK] Contraseña encriptada y guardada en BD.")
    print(f"[HASH BCRYPT GENERADO]: {nuevo_empleado.contrasena}")

    # 4. Pruebas de Login
    print("\n--- 4. Pruebas de Login ---")
    print("Intento con clave incorrecta: '123456'")
    if not nuevo_empleado.iniciar_sesion("123456"):
        print("[OK] Login fallido. Acceso denegado.")

    print("Intento con clave correcta: 'MiSuperClaveSegura2026'")
    if nuevo_empleado.iniciar_sesion("MiSuperClaveSegura2026"):
        print("[OK] Login exitoso. ¡Bienvenido Carlos!")

if __name__ == "__main__":
    main()
