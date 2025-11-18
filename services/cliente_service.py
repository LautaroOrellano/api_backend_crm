# services/cliente_service.py
from db.connection import get_connection
from mysql.connector import Error
from models.cliente import Cliente

def agregar_cliente(cliente: Cliente):
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        sql = "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)"
        valores = (cliente.nombre, cliente.email, cliente.telefono)
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid # id del nuevo registro
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise # o loguealo y devolvé None / False segun tu diseño
    finally:
        if cursor:
            cursor.close()
        if conexion:
             conexion.close()

def obtener_clientes():
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        # cursor(dictionary=True) devuelve filas como dicts: {"id":1, "nombre":"..."}
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes")
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()