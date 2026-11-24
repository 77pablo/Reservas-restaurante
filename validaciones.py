import re
from typing import Any, Tuple


def validar_rut(rut: Any) -> Tuple[str, str]:
    if not rut or not isinstance(rut, str):
        return "", "RUT Inválido"

    rut_limpio = re.sub(r"\s+", "", rut).upper()

    patron = r"^(\d{1,3}(?:\.\d{3}){2}-[\dK]|\d{7,8}-[\dK])$"
    if not re.match(patron, rut_limpio):
        return "", "RUT Inválido"

    cuerpo, dv = rut_limpio.replace(".", "").split("-")

    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    resultado = 11 - resto

    if resultado == 11:
        dv_esperado = "0"
    elif resultado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resultado)

    if dv != dv_esperado:
        return "", "RUT Inválido"

    return rut_limpio, "RUT Válido"


def validar_genero(genero: Any) -> Tuple[str, str]:
    if genero is None or isinstance(genero, bool):
        return "", "Género Inválido"

    if not isinstance(genero, (str, int)):
        return "", "Género Inválido"

    genero_limpio = str(genero).strip()

    if genero_limpio not in {"1", "2", "3"}:
        return "", "Género Inválido"

    return genero_limpio, "Género Válido"