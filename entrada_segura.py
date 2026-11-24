import getpass

try:
    import maskpass
except ImportError:
    maskpass = None


def solicitar_contrasena(
    prompt: str = "Ingrese contraseña: ",
    mask: str = "*",
    confirmar: bool = False,
) -> str:
    """Solicita una contraseña ocultando los caracteres en consola."""
    while True:
        if maskpass is not None:
            try:
                clave = maskpass.askpass(prompt=prompt, mask=mask)
            except Exception:
                clave = getpass.getpass(prompt)
        else:
            clave = getpass.getpass(prompt)

        if not clave:
            print("[AVISO] La contraseña no puede estar vacía. Intenta nuevamente.")
            continue

        if not confirmar:
            return clave

        if maskpass is not None:
            try:
                clave_confirmacion = maskpass.askpass(
                    prompt="Confirme contraseña: ", mask=mask
                )
            except Exception:
                clave_confirmacion = getpass.getpass("Confirme contraseña: ")
        else:
            clave_confirmacion = getpass.getpass("Confirme contraseña: ")

        if clave == clave_confirmacion:
            return clave

        print("[AVISO] Las contraseñas no coinciden. Intenta nuevamente.")