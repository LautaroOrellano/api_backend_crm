# main.py
from models.cliente import Cliente
from services.cliente_service import agregar_cliente, obtener_clientes

# Crear un cliente
nuevo = Cliente("Lautaro", "lautaro@gmail.com", "2236052979", "Cliente VIP")
agregar_cliente(nuevo)

# Mostrar todos los clientes
clientes = obtener_clientes()
for c in clientes:
    print(c)