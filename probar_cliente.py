from modelos.cliente import Cliente
from repositorios.cliente_repositorio import ClienteRepositorio

repo = ClienteRepositorio()

# Crear cliente y buscarlo
cliente = Cliente("Ana Prueba", "ana.prueba@mail.com", "+56911111111")
cliente.establecer_contrasena("clave123")
print("ID creado:", repo.crear(cliente))

encontrado = repo.buscar_por_correo("ana.prueba@mail.com")
if encontrado is None:
    print("No se encontró el cliente")
else:
    print("Encontrado:", encontrado)
    print("Login con clave correcta:", encontrado.iniciar_sesion("clave123"))
    print("Login con clave incorrecta:", encontrado.iniciar_sesion("otra_clave"))