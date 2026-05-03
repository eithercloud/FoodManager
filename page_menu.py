import tkinter as tk
from tkinter import ttk, messagebox
import os
from utils import campo, make_form, make_page, make_scrollable_page
from datetime import datetime


class PageMenu:
    def __init__(self, body, db):
        self._dirty = True       # Si True, recarga platillos desde Firebase al navegar
        self.db = db
        self._reload_cb = None   # Callback que avisa a otras páginas cuando se elimina un platillo

        self.platillos_data = {} # Diccionario {nombre: {datos + id}} cargado desde Firebase
        self.combo_var = tk.StringVar()

        # Frame principal sin scroll (la imagen ocupa toda la pantalla)
        self.frame = tk.Frame(body, bg="#0F0092")
        self.frame.place(relwidth=1, relheight=1)

        self._build()

    def set_reload_cb(self, cb):
        """Registra el callback que se ejecuta al eliminar un platillo."""
        self._reload_cb = cb

    def _build(self):
        """Construye el selector de platillo y el área de detalle."""

        self.contenedor = tk.Frame(self.frame, bg="#0F0092")
        self.contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.contenedor, text="Selecciona un platillo",
                 font=("Arial", 12, "bold"),
                 bg="#0F0092", fg="white").pack(anchor="w", pady=(0, 10))

        # Combo para elegir el platillo a visualizar
        self.combo = ttk.Combobox(
            self.contenedor,
            textvariable=self.combo_var,
            state="readonly",
            font=("Arial", 12),
            style="Custom.TCombobox"
        )
        self.combo.pack(fill="x", pady=(0, 20))
        # Al seleccionar un platillo, muestra su detalle
        self.combo.bind("<<ComboboxSelected>>", self._mostrar_detalle)

        # Frame donde se renderiza el detalle del platillo seleccionado
        self.detalle_frame = tk.Frame(self.contenedor, bg="#D3D4D3")
        self.detalle_frame.pack(fill="both", expand=True)

    def cargar_platillos(self):
        """
        Carga todos los platillos desde Firebase y llena el combo.
        Solo consulta Firebase si _dirty es True.
        Muestra automáticamente el primero de la lista.
        """
        if not self._dirty:
            return
        self._dirty = False
        self.platillos_data.clear()
        nombres = []

        for doc in self.db.collection("platillos").stream():
            d = doc.to_dict()
            nombre = d.get("nombre", "")
            # Guarda los datos junto con el id del documento
            self.platillos_data[nombre] = {**d, "id": doc.id}
            nombres.append(nombre)

        self.combo["values"] = nombres

        # Muestra el primer platillo automáticamente si hay datos
        if nombres:
            self.combo.current(0)
            self._mostrar_detalle(None)

    def _eliminar(self, nombre):
        """
        Pide confirmación y elimina el platillo de Firebase.
        Luego marca como sucias las páginas dependientes y recarga.
        """
        confirmar = messagebox.askyesno(
            "Eliminar platillo",
            f"¿Seguro que quieres eliminar '{nombre}'?"
        )
        if not confirmar:
            return

        # Obtiene el id del documento desde el caché
        doc_id = self.platillos_data[nombre].get("id")

        # Si por algún motivo no está cacheado, lo busca en Firebase
        if not doc_id:
            for doc in self.db.collection("platillos").stream():
                if doc.to_dict().get("nombre") == nombre:
                    doc_id = doc.id
                    break

        if doc_id:
            self.db.collection("platillos").document(doc_id).delete()

        # Marca para forzar recarga y avisa a otras páginas
        self._dirty = True
        if self._reload_cb:
            self._reload_cb()
        self.cargar_platillos()

    def _mostrar_detalle(self, event):
        """
        Renderiza el detalle completo del platillo seleccionado:
        imagen, nombre, precio, ingredientes, fechas y botón de eliminar.
        """
        # Limpia el detalle anterior
        for w in self.detalle_frame.winfo_children():
            w.destroy()

        nombre = self.combo_var.get()
        if nombre not in self.platillos_data:
            return

        d = self.platillos_data[nombre]

        precio       = d.get("precio", 0)
        ingredientes = d.get("ingredientes", [])
        imagen       = d.get("imagen", "")
        fc           = d.get("fecha_creacion", "")
        fm           = d.get("fecha_modificacion", "")

        # Formatea las fechas si están en formato ISO
        try:
            fc = datetime.fromisoformat(fc).strftime("%d/%m/%Y %H:%M")
            fm = datetime.fromisoformat(fm).strftime("%d/%m/%Y %H:%M")
        except:
            pass

        cont = tk.Frame(self.detalle_frame, bg="#ffffff")
        cont.pack(fill="both", expand=True, padx=20, pady=20)

        # ── IZQUIERDA: imagen del platillo ────────────
        frame_img = tk.Frame(cont, bg="#000000")
        frame_img.pack(side="left", fill="both", expand=True)

        if imagen and os.path.exists(imagen):
            try:
                from PIL import Image, ImageTk
                img    = Image.open(imagen)
                img    = img.resize((600, 600))
                img_tk = ImageTk.PhotoImage(img)

                lbl = tk.Label(frame_img, image=img_tk, bg="#ffffff")
                lbl.image = img_tk  # Evita que el GC elimine la imagen
                lbl.pack(expand=True)
            except:
                tk.Label(frame_img, text="Error imagen", bg="#ffffff").pack()

        # ── DERECHA: información del platillo ─────────
        frame_info = tk.Frame(cont, bg="#FFFFFF")
        frame_info.pack(side="left", fill="both", expand=True, padx=30, pady=30)

        # Nombre y precio
        tk.Label(frame_info, text=nombre,
                 font=("Arial", 20, "bold"), bg="#ffffff").pack(anchor="w")

        tk.Label(frame_info, text=f"$ {precio}",
                 font=("Arial", 16), fg="#055B0A", bg="#ffffff").pack(anchor="w", pady=(5, 15))

        # Lista de ingredientes
        tk.Label(frame_info, text="Ingredientes:",
                 font=("Arial", 16, "bold"), bg="#ffffff").pack(anchor="w")

        for ing in ingredientes:
            tk.Label(frame_info, text=f"• {ing}",
                     font=("Arial", 12), bg="#ffffff").pack(anchor="w")

        # Fechas de creación y modificación
        tk.Label(frame_info, text=f"Creado: {fc}",
                 font=("Arial", 12), fg="gray", bg="#ffffff").pack(anchor="w", pady=(20, 0))

        tk.Label(frame_info, text=f"Modificado: {fm}",
                 font=("Arial", 12), fg="gray", bg="#ffffff").pack(anchor="w")

        # Botón para eliminar el platillo actual
        tk.Button(frame_info, text="🗑 Eliminar platillo",
                  bg="#e84118", fg="white", bd=0,
                  font=("Arial", 13, "bold"), padx=20, pady=6,
                  command=lambda n=nombre: self._eliminar(n)
                  ).pack(anchor="w", pady=(10, 0))