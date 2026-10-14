# FinanControl — CRUD inicial

Aplicación web básica para registrar, consultar, editar y eliminar gastos personales. Está desarrollada con Python, Flask, SQLite, HTML y CSS, de acuerdo con la propuesta del proyecto.

## Requisitos
- Python 3.10 o superior
- pip

## Cómo ejecutar en Windows
1. Descomprime la carpeta.
2. Abre una terminal dentro de la carpeta `FinanControl_CRUD_Inicial`.
3. Crea un entorno virtual (recomendado):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Instala Flask:

   ```powershell
   pip install -r requirements.txt
   ```

5. Inicia la aplicación:

   ```powershell
   python app.py
   ```

6. Abre en el navegador la dirección que muestra la terminal, normalmente `http://127.0.0.1:5000`.

La base de datos `financontrol.db` se crea automáticamente al iniciar la aplicación. También se crean un usuario de prueba y categorías iniciales.

## Funciones incluidas
- Crear un gasto con descripción, valor, fecha y categoría.
- Consultar el listado de gastos y un resumen en la pantalla inicial.
- Editar un gasto existente.
- Eliminar un gasto con confirmación.
- Validar campos obligatorios y que el valor sea mayor que cero.
- Guardar los datos en SQLite.

## Modelo de datos
- `usuario`: datos básicos del usuario.
- `categoria`: categorías de gastos.
- `gasto`: descripción, valor, fecha y claves foráneas de usuario y categoría.

## Importante para el proyecto académico
Este repositorio es un punto de partida, no evidencia de que el grupo ya haya realizado o probado cada operación. Ejecuten el programa, prueben las cuatro operaciones, revisen el código y modifiquen lo que puedan explicar. Registren en la bitácora únicamente el uso real de IA y las pruebas que efectivamente hicieron. Antes de publicar, cambien `app.secret_key` por una clave apropiada para su entorno.
