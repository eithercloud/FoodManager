# FoodManager

Sistema de gestión para restaurantes desarrollado en Python con Tkinter y Firebase.

## Descripción

FoodManager es una aplicación de escritorio que permite administrar un restaurante de forma completa: desde el registro de platillos e ingredientes hasta el cobro a clientes y el historial de ventas.

## Funcionalidades

- **Cobrar** — Arma pedidos con múltiples platillos, calcula el total, el cambio automáticamente y genera un ticket PDF al procesar el cobro
- **Añadir Platillo** — Registra nuevos platillos con nombre, precio, ingredientes e imagen
- **Modificar Platillo** — Edita o elimina platillos existentes
- **Añadir Ingrediente** — Agrega ingredientes disponibles para asignar a los platillos
- **Platillos** — Visualiza el menú completo con imagen, precio e ingredientes de cada platillo
- **Ventas** — Historial de cobros con filtros por fecha y ordenamiento

## Tecnologías

- Python 3.13
- Tkinter (interfaz gráfica)
- Firebase Firestore (base de datos en la nube)
- Pillow (visualización de imágenes)

## ⚙️ Instalación

1. Clonar el repositorio:
git clone https://github.com/eithercloud/FoodManager.git

2. Instalar las dependencias:
pip install firebase-admin reportlab pillow openpyxl

3. Agregar el archivo de credenciales de Firebase en la raíz del proyecto
nombre-del-proyecto-firebase-adminsdk.json

4. Actualizar el nombre del archivo en `firebase_config.py`

5. Ejecutar la aplicación:
python main.py

## 📁 Estructura del proyecto
FoodManager/
├── main.py                  # Punto de entrada y navegación
├── firebase_config.py       # Conexión a Firebase
├── utils.py                 # Componentes y validaciones reutilizables
├── page_cobrar.py           # Página de cobro y generación de tickets
├── page_platillo.py         # Página para añadir platillos
├── page_modificar.py        # Página para modificar o eliminar platillos
├── page_ingrediente.py      # Página para añadir ingredientes
├── page_menu.py             # Página de visualización del menú
├── page_venta.py            # Página de historial de ventas
└── imagenes_platillos/      # Carpeta de imágenes (no incluida en el repo)

## ⚠️ Notas

- El archivo `.json` de credenciales de Firebase **no está incluido** por seguridad. Se debe generar uno propio desde la consola de Firebase.
- Las carpetas `imagenes_platillos/` se crea automáticamente al ejecutar la app.

## 👤 Autor

Desarrollado por [eithercloud](https://github.com/eithercloud)
