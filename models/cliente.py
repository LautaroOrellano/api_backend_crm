# models/cliente.py

class Cliente:

    # Constructor
    def __init__(self, nombre, email, telefono, notas=None):
        #this
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.notas = notas

    # toString
    def __str__(self):
        return f"{self.nombre} | {self.email} | {self.telefono} | {self.notas}"