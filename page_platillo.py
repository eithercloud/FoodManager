import tkinter as tk
from tkinter import filedialog, messagebox
import os, shutil
from utils import campo, make_form, make_page, make_scrollable_page
from datetime import datetime
from utils import numero_con_limite, texto_con_limite

# Carpeta donde se guardan las imágenes de los platillos
CARPETA_IMAGENES = "imagenes_platillos"
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


class PagePlatillo:
    def __init__(self, body, db):
        self._dirty = True        # Indica si hay que recargar ingredientes desde Firebase
        self.db = db
        self._reload_cb = None    # Callback que se llama al guardar un platillo nuevo
        self.ingredientes_vars = {}  # Diccionario {nombre_ingrediente: BooleanVar}
        self.imagen_path = tk.StringVar(value="")
        self.imagen_nombre = tk.StringVar(value="Sin imagen seleccionada")

        self.frame, self.form = make_scrollable_page(body)
        self._build()

    def set_reload_cb(self, cb):
        """Registra el callback que se ejecuta después de guardar un platillo."""
        self._reload_cb = cb

    def _build(self):
        """Construye todos los widgets del formulario."""
        form = self.form

        # Campo de texto para el nombre del platillo (máx. 30 letras)
        self.nombre_p = campo(form, "Nombre del platillo", 0)
        vcmd = (self.frame.register(texto_con_limite(30)), "%P")
        self.nombre_p.config(validate="key", validatecommand=vcmd)

        # Campo numérico para el precio (máx. 20 dígitos, solo números positivos)
        self.precio_p = campo(form, "Precio", 2)
        vcmd_pago = (self.frame.register(numero_con_limite(20)), "%P")
        self.precio_p.config(validate="key", validatecommand=vcmd_pago)

        # Sección de checkboxes de ingredientes
        tk.Label(form, text="Ingredientes", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=4, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))
        self.frame_checks = tk.Frame(form, bg="#D4D3D3")
        self.frame_checks.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        # Sección de imagen
        tk.Label(form, text="Imagen del platillo", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=6, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))
        frame_img = tk.Frame(form, bg="#D4D3D3")
        frame_img.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        tk.Button(frame_img, text="📁  Buscar imagen", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 14), padx=20, pady=6,
                  command=self._seleccionar_imagen).pack(side="left")

        # Label que muestra el nombre del archivo de imagen seleccionado
        self.lbl_imagen = tk.Label(frame_img, textvariable=self.imagen_nombre,
                                    bg="#D4D3D3", fg="gray", font=("Arial", 13, "italic"))
        self.lbl_imagen.pack(side="left", padx=15)

        # Botón para guardar el platillo en Firebase
        tk.Button(form, text="Guardar Platillo", bg="#055B0A", fg="white", bd=0,
                  font=("Arial", 16, "bold"), width=30,
                  activebackground="#055B0A", padx=40, pady=4,
                  command=self._guardar).grid(row=8, column=0, columnspan=2, pady=15)

    def cargar_checks_ingredientes(self):
        """
        Carga los ingredientes desde Firebase y genera un checkbox por cada uno.
        Solo consulta Firebase si _dirty es True.
        """
        if not self._dirty:
            return
        self._dirty = False

        # Limpia los checkboxes anteriores
        for w in self.frame_checks.winfo_children():
            w.destroy()
        self.ingredientes_vars.clear()

        # Trae ingredientes de Firebase
        lista = [doc.to_dict().get("nombre", "") for doc in self.db.collection("ingredientes").stream()]

        if not lista:
            tk.Label(self.frame_checks,
                     text="No hay ingredientes. Añade en 'Añadir Ingrediente'.",
                     bg="#D4D3D3", fg="gray", font=("Arial", 13, "italic")).grid(row=0, column=0)
            return

        # Crea un checkbox por cada ingrediente (5 por fila)
        for i, ing in enumerate(lista):
            var = tk.BooleanVar()
            self.ingredientes_vars[ing] = var
            tk.Checkbutton(self.frame_checks, text=ing, variable=var,
                           bg="#D4D3D3", fg="black", font=("Arial", 14),
                           activebackground="#3EA805",
                           selectcolor="#ffffff").grid(row=i // 5, column=i % 5,
                                                       sticky="w", padx=10, pady=4)

    def _seleccionar_imagen(self):
        """Abre un diálogo para elegir una imagen y guarda su ruta."""
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")]
        )
        if path:
            self.imagen_path.set(path)
            self.imagen_nombre.set(os.path.basename(path))
            self.lbl_imagen.config(fg="#055B0A")
        else:
            self.imagen_path.set("")
            self.imagen_nombre.set("Sin imagen seleccionada")
            self.lbl_imagen.config(fg="gray")

    def _guardar(self):
        """
        Valida los campos, copia la imagen a la carpeta del proyecto
        y guarda el platillo en Firebase.
        """
        if not self.nombre_p.get() or not self.precio_p.get():
            messagebox.showwarning("Campos vacíos", "Nombre y precio son obligatorios")
            return

        # Copia la imagen seleccionada a la carpeta imagenes_platillos/
        ruta = ""
        if self.imagen_path.get():
            ext     = os.path.splitext(self.imagen_path.get())[1]
            nombre  = self.nombre_p.get().strip().replace(" ", "_") + ext
            destino = os.path.join(CARPETA_IMAGENES, nombre)
            shutil.copy2(self.imagen_path.get(), destino)
            ruta = destino

        ahora = datetime.now().isoformat()
        seleccionados = [ing for ing, v in self.ingredientes_vars.items() if v.get()]

        # Guarda el platillo en la colección "platillos" de Firebase
        self.db.collection("platillos").add({
            "nombre":             self.nombre_p.get().strip(),
            "precio":             float(self.precio_p.get()),
            "ingredientes":       seleccionados,
            "imagen":             ruta,
            "fecha_creacion":     ahora,
            "fecha_modificacion": ahora
        })

        messagebox.showinfo("✅ Guardado", f"'{self.nombre_p.get()}' guardado correctamente")

        # Limpia el formulario tras guardar
        self.nombre_p.delete(0, tk.END)
        self.precio_p.delete(0, tk.END)
        for v in self.ingredientes_vars.values():
            v.set(False)
        self.imagen_path.set("")
        self.imagen_nombre.set("Sin imagen seleccionada")
        self.lbl_imagen.config(fg="gray")

        # Marca para que otras páginas recarguen datos
        self._dirty = True
        if self._reload_cb:
            self._reload_cb()