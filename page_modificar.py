import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, shutil
from utils import campo, make_form, make_page, make_scrollable_page
from datetime import datetime
from utils import numero_con_limite, texto_con_limite

# Carpeta donde se almacenan las imágenes de los platillos
CARPETA_IMAGENES = "imagenes_platillos"


class PageModificar:
    def __init__(self, body, db):
        self._dirty = True           # Si True, recarga datos desde Firebase al navegar
        self.db = db
        self._reload_cb = None       # Callback que avisa a otras páginas del cambio
        self.platillos_data = {}     # Diccionario {nombre: {datos + id}} cargado desde Firebase
        self.mod_ing_vars = {}       # Diccionario {nombre_ingrediente: BooleanVar}
        self.mod_imagen_original = tk.StringVar(value="")
        self.mod_imagen_nombre   = tk.StringVar(value="Sin imagen seleccionada")

        self.frame, self.form = make_scrollable_page(body)
        self._build()

    def set_reload_cb(self, cb):
        """Registra el callback que se ejecuta después de guardar o eliminar un platillo."""
        self._reload_cb = cb

    def _build(self):
        """Construye todos los widgets del formulario de modificación."""
        form = self.form

        # Selector de platillo a editar
        tk.Label(form, text="Selecciona el platillo a editar", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=0, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))

        self.mod_combo_var = tk.StringVar()
        self.mod_combo = ttk.Combobox(form, textvariable=self.mod_combo_var,
                                       font=("Arial", 16), state="readonly",
                                       style="Custom.TCombobox")
        self.mod_combo.grid(row=1, column=0, columnspan=2, padx=20, pady=(2, 10),
                            sticky="ew", ipady=8)
        # Al seleccionar un platillo, rellena los campos automáticamente
        self.mod_combo.bind("<<ComboboxSelected>>", self._on_seleccionado)

        # Campo de nombre (máx. 30 letras)
        self.mod_nombre = campo(form, "Nombre del platillo", 2)
        vcmd = (self.frame.register(texto_con_limite(30)), "%P")
        self.mod_nombre.config(validate="key", validatecommand=vcmd)

        # Campo de precio (máx. 20 dígitos, solo números positivos)
        self.mod_precio = campo(form, "Precio", 4)
        vcmd_pago = (self.frame.register(numero_con_limite(20)), "%P")
        self.mod_precio.config(validate="key", validatecommand=vcmd_pago)

        # Sección de checkboxes de ingredientes (se llena dinámicamente en _on_seleccionado)
        tk.Label(form, text="Ingredientes", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=6, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))
        self.frame_checks = tk.Frame(form, bg="#D4D3D3")
        self.frame_checks.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        # Sección de imagen
        tk.Label(form, text="Imagen del platillo", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=8, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))
        frame_img = tk.Frame(form, bg="#D4D3D3")
        frame_img.grid(row=9, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        tk.Button(frame_img, text="📁  Cambiar imagen", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 14), padx=20, pady=6,
                  command=self._seleccionar_imagen).pack(side="left")

        # Label que muestra el nombre del archivo de imagen seleccionado
        self.lbl_imagen = tk.Label(frame_img, textvariable=self.mod_imagen_nombre,
                                    bg="#D4D3D3", fg="gray", font=("Arial", 13, "italic"))
        self.lbl_imagen.pack(side="left", padx=15)

        # Botón para guardar los cambios en Firebase
        tk.Button(form, text="Guardar Cambios", bg="#055B0A", fg="white", bd=0,
                  font=("Arial", 16, "bold"), width=30,
                  activebackground="#055B0A", padx=40, pady=4,
                  command=self._guardar).grid(row=10, column=0, columnspan=2, pady=15)

    def cargar_platillos(self):
        """
        Carga todos los platillos desde Firebase y llena el combo selector.
        Solo consulta Firebase si _dirty es True.
        También cachea los ingredientes para evitar otra consulta al seleccionar platillo.
        """
        if not self._dirty:
            return
        self._dirty = False

        # Carga platillos incluyendo su id de documento
        self.platillos_data = {}
        for doc in self.db.collection("platillos").stream():
            d = doc.to_dict()
            self.platillos_data[d["nombre"]] = {**d, "id": doc.id}

        self.mod_combo["values"] = list(self.platillos_data.keys())

        # Limpia los campos del formulario
        self.mod_nombre.delete(0, tk.END)
        self.mod_precio.delete(0, tk.END)
        self.mod_imagen_nombre.set("Sin imagen seleccionada")
        self.mod_imagen_original.set("")
        self.lbl_imagen.config(fg="gray")

        # Cachea ingredientes para usarlos sin otra consulta en _on_seleccionado
        self._cache_ingredientes = [
            doc.to_dict().get("nombre", "")
            for doc in self.db.collection("ingredientes").stream()
        ]

    def _on_seleccionado(self, event):
        """
        Se ejecuta al elegir un platillo del combo.
        Rellena nombre, precio, imagen y checkboxes con los datos del platillo seleccionado.
        """
        sel = self.mod_combo_var.get()
        if sel not in self.platillos_data:
            return
        datos = self.platillos_data[sel]

        # Rellena nombre y precio
        self.mod_nombre.delete(0, tk.END)
        self.mod_nombre.insert(0, datos.get("nombre", ""))
        self.mod_precio.delete(0, tk.END)
        self.mod_precio.insert(0, str(datos.get("precio", "")))

        # Muestra la imagen actual si existe
        ruta = datos.get("imagen", "")
        if ruta:
            self.mod_imagen_nombre.set(os.path.basename(ruta))
            self.mod_imagen_original.set(ruta)
            self.lbl_imagen.config(fg="#055B0A")
        else:
            self.mod_imagen_nombre.set("Sin imagen seleccionada")
            self.mod_imagen_original.set("")
            self.lbl_imagen.config(fg="gray")

        # Reconstruye checkboxes usando el caché (sin nueva consulta a Firebase)
        for w in self.frame_checks.winfo_children():
            w.destroy()
        self.mod_ing_vars.clear()

        todos    = getattr(self, "_cache_ingredientes", [])
        actuales = datos.get("ingredientes", [])

        # Marca como seleccionados los ingredientes que ya tenía el platillo
        for i, ing in enumerate(todos):
            var = tk.BooleanVar(value=(ing in actuales))
            self.mod_ing_vars[ing] = var
            tk.Checkbutton(self.frame_checks, text=ing, variable=var,
                           bg="#D4D3D3", fg="black", font=("Arial", 14),
                           activebackground="#D4D3D3",
                           selectcolor="#ffffff").grid(row=i // 5, column=i % 5,
                                                       sticky="w", padx=10, pady=4)

    def _seleccionar_imagen(self):
        """Abre un diálogo para elegir una nueva imagen y guarda su ruta."""
        path = filedialog.askopenfilename(
            title="Seleccionar nueva imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")]
        )
        if path:
            self.mod_imagen_original.set(path)
            self.mod_imagen_nombre.set(os.path.basename(path))
            self.lbl_imagen.config(fg="#055B0A")

    def _guardar(self):
        """
        Valida los campos, copia la imagen si cambió
        y actualiza el documento del platillo en Firebase.
        """
        sel = self.mod_combo_var.get()
        if not sel or sel not in self.platillos_data:
            messagebox.showwarning("Sin selección", "Selecciona un platillo primero")
            return
        if not self.mod_nombre.get() or not self.mod_precio.get():
            messagebox.showwarning("Campos vacíos", "Nombre y precio son obligatorios")
            return

        doc_id = self.platillos_data[sel]["id"]
        ruta   = self.platillos_data[sel].get("imagen", "")
        src    = self.mod_imagen_original.get()

        # Si se eligió una imagen nueva y diferente, la copia a la carpeta del proyecto
        if src and os.path.isfile(src) and src != ruta:
            ext     = os.path.splitext(src)[1]
            nombre  = self.mod_nombre.get().strip().replace(" ", "_") + ext
            destino = os.path.join(CARPETA_IMAGENES, nombre)
            shutil.copy2(src, destino)
            ruta = destino

        seleccionados = [ing for ing, v in self.mod_ing_vars.items() if v.get()]

        # Actualiza el documento en Firebase
        self.db.collection("platillos").document(doc_id).update({
            "nombre":             self.mod_nombre.get().strip(),
            "precio":             float(self.mod_precio.get()),
            "ingredientes":       seleccionados,
            "imagen":             ruta,
            "fecha_modificacion": datetime.now().isoformat()
        })

        messagebox.showinfo("✅ Actualizado", f"'{self.mod_nombre.get()}' actualizado correctamente")

        # Recarga el combo y marca otras páginas 
        self.cargar_platillos()
        self._dirty = True
        if self._reload_cb:
            self._reload_cb()