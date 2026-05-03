import tkinter as tk
from tkinter import messagebox
from utils import make_form, make_page, make_scrollable_page
from utils import limitar_longitud


class PageIngrediente:
    def __init__(self, body, db):
        self._dirty = True              # Si True, recarga la lista desde Firebase al navegar
        self.db = db
        self._reload_checks_cb = None   # Callback que avisa a PagePlatillo de nuevos ingredientes
        self.entradas_nuevas = []       # Lista de Entry widgets para capturar ingredientes

        self.frame, self.form = make_scrollable_page(body)
        self._build()

    def set_reload_checks_cb(self, cb):
        """Registra el callback que recarga los checkboxes en PagePlatillo."""
        self._reload_checks_cb = cb

    def _build(self):
        """Construye el formulario para añadir ingredientes."""
        form = self.form

        tk.Label(form, text="Añadir nuevos ingredientes", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=2, column=0, columnspan=2,
                                           sticky="w", padx=20, pady=(15, 2))

        # Frame donde se apilan los campos de texto dinámicamente
        self.frame_nuevos = tk.Frame(form, bg="#D4D3D3")
        self.frame_nuevos.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))
        self.frame_nuevos.grid_columnconfigure(0, weight=1)

        # Crea el primer campo vacío al iniciar
        self._agregar_campo()

        # Botón para añadir más campos (máx. 10)
        tk.Button(form, text="+ Agregar otro campo", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 13), padx=20, pady=6,
                  command=self._agregar_campo).grid(row=4, column=0, sticky="w",
                                                     padx=20, pady=(5, 10))

        # Botón para guardar todos los ingredientes escritos en Firebase
        tk.Button(form, text="Guardar Ingredientes", bg="#055B0A", fg="white", bd=0,
                  font=("Arial", 16, "bold"), width=30,
                  activebackground="#055B0A", padx=40, pady=4,
                  command=self._guardar).grid(row=5, column=0, columnspan=2, pady=15)

    def actualizar_lista(self):
        """
        Recarga y muestra la lista de ingredientes guardados en Firebase.
        Solo consulta Firebase si _dirty es True.
        Requiere que frame_lista exista en el formulario.
        """
        if not self._dirty:
            return
        self._dirty = False

        if not hasattr(self, "frame_lista"):
            return

        # Limpia la lista anterior
        for w in self.frame_lista.winfo_children():
            w.destroy()

        lista = [doc.to_dict().get("nombre", "") for doc in self.db.collection("ingredientes").stream()]

        if not lista:
            tk.Label(self.frame_lista, text="  Aún no hay ingredientes guardados",
                     bg="#ffffff", fg="gray", font=("Arial", 13, "italic")).pack(anchor="w", pady=6)
            return

        # Muestra cada ingrediente con fondo alternado para mejor legibilidad
        for i, ing in enumerate(lista):
            bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
            tk.Label(self.frame_lista, text=f"  • {ing}", bg=bg, fg="black",
                     font=("Arial", 14), anchor="w").pack(fill="x", pady=1)

    def _agregar_campo(self):
        """
        Agrega un nuevo campo de texto para escribir un ingrediente.
        Limita a 10 campos por vez y 40 caracteres por campo.
        """
        if len(self.entradas_nuevas) >= 10:
            messagebox.showwarning("Límite alcanzado", "Máximo 10 ingredientes por vez")
            return

        fila  = len(self.entradas_nuevas)
        entry = tk.Entry(self.frame_nuevos, bd=0, bg="#ffffff", font=("Arial", 16))
        entry.grid(row=fila, column=0, sticky="ew", pady=4, ipady=5)

        # Validación: máximo 40 caracteres por ingrediente
        vcmd = (self.frame.register(limitar_longitud(40)), "%P")
        entry.config(validate="key", validatecommand=vcmd)

        self.entradas_nuevas.append(entry)

    def _guardar(self):
        """
        Lee todos los campos, guarda en Firebase los que no estén vacíos
        y limpia el formulario para el siguiente uso.
        """
        guardados = 0

        for entry in self.entradas_nuevas:
            nombre = entry.get().strip()
            if nombre:
                self.db.collection("ingredientes").add({"nombre": nombre})
                guardados += 1

        if guardados == 0:
            messagebox.showwarning("Sin datos", "Escribe al menos un ingrediente")
            return

        messagebox.showinfo("✅ Guardado", f"{guardados} ingrediente(s) guardado(s)")

        # Destruye los campos usados y crea uno nuevo vacío
        for e in self.entradas_nuevas:
            e.destroy()
        self.entradas_nuevas.clear()
        self._agregar_campo()

        # Marca como sucio para forzar recarga y avisa a PagePlatillo
        self._dirty = True
        self.actualizar_lista()
        if self._reload_checks_cb:
            self._reload_checks_cb()