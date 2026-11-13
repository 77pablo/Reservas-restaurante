import re

def validar_rut(rut):
    if not rut or not isinstance(rut, str):
        return "", "RUT Inválido"
    
    rut_limpio = rut.strip()
    
    patron = r'^(\d{1,3}(?:\.\d{3}){2}-[\dkK]|\d{7,8}-[\dkK])$'
    if not re.match(patron, rut_limpio):
        return "", "RUT Inválido"
    
    cuerpo, dv = rut_limpio.replace(".", "").split("-")
    dv = dv.upper()
    
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


def validar_genero(genero):
    if not genero or not isinstance(genero, str):
        return "", "Género Inválido"
        
    genero_limpio = genero.strip()
    
    if genero_limpio not in ['1', '2', '3']:
        mensaje = 'Género Inválido'
        genero = ''
    else:
        mensaje = 'Género Válido'
        
    return genero, mensaje