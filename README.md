# Proyecto Customer Manager API - Documentación Técnica

## Visión General
Este proyecto es una API Backend robusta y escalable construida con **FastAPI**, diseñada para la gestión de clientes y usuarios. Implementa una **arquitectura por capas** (Layered Architecture) que separa claramente las responsabilidades, facilitando el mantenimiento y la escalabilidad del software.

## Tecnologías y Librerías Principales

A continuación se detalla el stack tecnológico y la función de cada librería:

*   **⚡ FastAPI**: El framework principal. Elegido por su altísimo rendimiento (asíncrono), generación automática de documentación (Swagger UI) y facilidad de uso.
*   **🗄️ SQLAlchemy**: El ORM (Object-Relational Mapper) utilizado para interactuar con la base de datos. Permite trabajar con modelos de Python en lugar de escribir SQL crudo.
*   **🐬 mysql-connector-python**: El driver que permite a SQLAlchemy conectarse a una base de datos MySQL.
*   **🛡️ Pydantic**: Se utiliza para la **validación de datos**. Define los esquemas (Schemas) de entrada y salida, asegurando que los datos sean correctos antes de procesarlos.
*   **📦 Alembic**: Herramienta de **migraciones**. Permite versionar la estructura de la base de datos (crear tablas, alterar columnas) de manera controlada.
*   **🔑 Python-Jose & Passlib**: Proporcionan la seguridad. `python-jose` se usa para generar y validar tokens **JWT (JSON Web Tokens)** para autenticación, y `passlib` para el hasheo seguro de contraseñas.

---

## Estructura del Proyecto y Arquitectura

El código fuente principal se encuentra en la carpeta `app/`. La arquitectura sigue un flujo de datos unidireccional y separación de conceptos:

### 1. `app/api/` (Capa de Presentación / Routers)
*   Son los puntos de entrada de la aplicación (Endpoints).
*   Se encargan de recibir las peticiones HTTP (`GET`, `POST`, `PUT`, `DELETE`).
*   Analizan los datos de entrada usando **Schemas** y delegan la lógica a la capa de **Servicios**.

### 2. `app/schemas/` (Data Transfer Objects - DTOs)
*   Definen la *forma* de los datos.
*   Ejemplo: Un `CustomerCreateSchema` define qué campos son obligatorios para crear un cliente.
*   Sirven de contrato entre el Frontend y el Backend.

### 3. `app/services/` (Capa de Negocio)
*   Aquí reside el **corazón** de la aplicación.
*   Contiene la lógica de negocio y reglas de validación (ej: "No se puede crear un cliente con un email duplicado").
*   Orquesta las operaciones llamando a la capa de **Repositorios**.

### 4. `app/repositories/` (Capa de Acceso a Datos)
*   Abstrae la base de datos.
*   Contiene las consultas directas (Queries) usando SQLAlchemy (ej: `db.query(User).filter(...)`).
*   Su única responsabilidad es guardar, leer, actualizar o borrar datos.

### 5. `app/models/` (Entidades de BD)
*   Son las clases de Python que representan las tablas de la base de datos (ej: `class User(Base): ...`).

### 6. `app/core/` y `app/config/`
*   Manejan la configuración global, variables de entorno (`.env`) y seguridad.

---

## Flujo de Ejecución (Ejemplo)

Cuando el Frontend solicita "Crear un Cliente":

1.  **Router**: Recibe el JSON, lo valida con el `Schema`.
2.  **Service**: Verifica que el usuario tenga permisos ó que el cliente no exista.
3.  **Repository**: Prepara la sentencia SQL `INSERT` y la ejecuta en la BD.
4.  **Database**: Guarda el registro.
5.  **Respuesta**: El dato guardado sube por las capas y se devuelve como JSON al Frontend.

## Cómo Iniciar (Resumen)

El archivo `main.py` es el punto de entrada. Típicamente se ejecuta con un servidor ASGI como **Uvicorn**:

```bash
uvicorn main:app --reload
```
