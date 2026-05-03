import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
from openpyxl import Workbook
from datetime import datetime

class PageVenta:
    def __init__(self, body, db):
        self.db = db

        self.page = 0
        self.page_size = 30

        self.data_cache = []     
        self.data_filtrada = []

        self.frame = tk.Frame(body, bg="#0F0092")
        self.frame.place(relwidth=1, relheight=1)

        self._build()

    def set_reload_cb(self, cb):
        self._reload_cb = cb

    def _build(self):

        # ── FILTROS ─────────────────────────
        filtros = tk.Frame(self.frame, bg=self.frame["bg"])
        filtros.pack(fill="x", padx=40, pady=10)

        def crear_fecha_selector(parent, row, col, texto):
            tk.Label(parent, text=texto, bg=self.frame["bg"], fg="white",
                     font=("Arial", 12, "bold")).grid(row=row, column=col, padx=5)

            frame = tk.Frame(parent, bg="#D4D3D3")
            frame.grid(row=row, column=col+1, padx=5)

            dia = tk.Spinbox(frame, from_=1, to=31, width=3, bd=0, relief="flat")
            mes = tk.Spinbox(frame, from_=1, to=12, width=3, bd=0, relief="flat")
            anio = tk.Spinbox(frame, from_=2020, to=2050, width=5, bd=0, relief="flat")

            dia.pack(side="left")
            tk.Label(frame, text="/").pack(side="left")
            mes.pack(side="left")
            tk.Label(frame, text="/").pack(side="left")
            anio.pack(side="left")

            return dia, mes, anio

        # Fechas
        self.dia_ini, self.mes_ini, self.anio_ini = crear_fecha_selector(filtros, 0, 0, "Desde")
        self.dia_fin, self.mes_fin, self.anio_fin = crear_fecha_selector(filtros, 0, 2, "Hasta")

        # Tipo filtro
        tk.Label(filtros, text="Filtro fecha", bg=self.frame["bg"], fg="white", 
                 font=("Arial", 12, "bold")).grid(row=0, column=4, padx=10)

        self.filtro_fecha_var = tk.StringVar(value="Desde siempre")

        ttk.Combobox(
            filtros,
            textvariable=self.filtro_fecha_var,
            values=["Desde siempre", "Rango"],
            state="readonly",
            width=15,
            style="Custom.TCombobox"
        ).grid(row=0, column=5)

        # Orden
        tk.Label(filtros, text="Ordenar", bg=self.frame["bg"], fg="white",
                 font=("Arial", 12, "bold")).grid(row=0, column=6, padx=10)

        self.orden_var = tk.StringVar(value="Fecha (Mas Nuevo)")

        ttk.Combobox(
            filtros,
            textvariable=self.orden_var,
            values=[
                "Fecha (Mas Nuevo)",
                "Fecha (Mas Antiguo)",
                "Cantidad (De Mayor)",
                "Cantidad (De Menor)"
            ],
            state="readonly",
            width=28,
            style="Custom.TCombobox"
        ).grid(row=0, column=7)

        tk.Button(filtros, text="Filtrar",
                  bg="#055B0A", fg="white",
                  font=("Arial", 12, "bold"),
                    bd=0,                
                    relief="flat",
                  command=self.cargar_platillos
        ).grid(row=0, column=8, padx=10)

        tk.Button(
            filtros,
            text="Exportar Excel",
            bg="#055B0A",
            fg="white",
            font=("Arial", 12, "bold"),
            bd=0,
            relief="flat",
            command=self.exportar_excel
        ).grid(row=0, column=9, padx=10)

        # ── TABLA ─────────────────────────
        cont = tk.Frame(self.frame, bg="#D4D3D3")
        cont.pack(fill="both", expand=True, padx=40, pady=10)

        columnas = ("Platillo", "Cantidad", "Total", "Pago", "Cambio", "Fecha")

        self.tree = ttk.Treeview(cont, columns=columnas, show="headings")

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=130)

        self.tree.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(cont, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # FILAS INTERCALADAS
        self.tree.tag_configure("par", background="#ffffff")
        self.tree.tag_configure("impar", background="#dcdada")

        # ── PAGINACIÓN ─────────────────────────
        nav = tk.Frame(self.frame, bg="#0F0092")
        nav.pack(pady=10)

        tk.Button(nav, text="⟨ Anterior",
    command=self.prev_page,
    bd=0,
    relief="flat",
    bg="#1e272e",
    fg="white",
    activebackground="#1e272e"
).pack(side="left", padx=10)
        self.lbl_page = tk.Label(nav, text="Página 1", bg="#0F0092", fg="white")
        self.lbl_page.pack(side="left")
        tk.Button(nav, text="Siguiente ⟩",
    command=self.next_page,
    bd=0,
    relief="flat",
    bg="#1e272e",
    fg="white",
    activebackground="#1e272e"
).pack(side="left", padx=10)
        

    # ───────────────────────────────
    # CARGA
    # ───────────────────────────────
    def recargar_datos(self):
        self.data_cache.clear()   
        self.cargar_platillos()   

    def exportar_excel(self):

        if not self.data_filtrada:
            print("No hay datos para exportar")
            return

        # Crear carpeta si no existe
        carpeta = "exportaciones"
        os.makedirs(carpeta, exist_ok=True)

        # Nombre archivo con fecha
        nombre_archivo = f"ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(carpeta, nombre_archivo)

        # Crear Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Ventas"

        # Encabezados
        headers = ["Platillo", "Cantidad", "Total", "Pago", "Cambio", "Fecha"]
        ws.append(headers)

        # Datos
        for d in self.data_filtrada:
            fecha = d.get("fecha_obj")
            fecha = fecha.strftime("%d/%m/%Y %H:%M") if fecha else ""

            ws.append([
                d.get("platillo", ""),
                d.get("cantidad", ""),
                float(d.get("total", 0)),
                float(d.get("pago", 0)),
                float(d.get("cambio", 0)),
                fecha
            ])

        wb.save(ruta)

        print(f"Archivo exportado en: {ruta}")
    def cargar_platillos(self):

        # SOLO CONSULTA UNA VEZ
        if not self.data_cache:
            ventas = self.db.collection("cobros").stream()

            for doc in ventas:
                d = doc.to_dict()

                try:
                    d["fecha_obj"] = datetime.fromisoformat(d.get("fecha", ""))
                except:
                    d["fecha_obj"] = None

                self.data_cache.append(d)

        self._aplicar_filtros()

    # ───────────────────────────────
    def _aplicar_filtros(self):
        self.page = 0
        self.data_filtrada = []

        inicio = self._get_fecha(self.dia_ini, self.mes_ini, self.anio_ini)
        fin = self._get_fecha(self.dia_fin, self.mes_fin, self.anio_fin)

        usar_rango = self.filtro_fecha_var.get() == "Rango"

        for d in self.data_cache:
            fecha = d.get("fecha_obj")

            # FILTRO DE FECHA CORREGIDO
            if usar_rango:
                if not fecha:
                    continue

                if inicio and fecha < inicio:
                    continue

                if fin and fecha > fin:
                    continue

            self.data_filtrada.append(d)

        self._ordenar()
        self._mostrar_pagina()
        

    # ───────────────────────────────
    def _ordenar(self):
        orden = self.orden_var.get()

        if "Fecha" in orden:
            reverse = "nuevo" in orden
            self.data_filtrada.sort(
                key=lambda x: x.get("fecha_obj") or datetime.min,
                reverse=reverse
            )
        else:
            reverse = "mayor" in orden
            self.data_filtrada.sort(
                key=lambda x: x.get("cantidad", 0),
                reverse=reverse
            )
    
    # ───────────────────────────────
    def _mostrar_pagina(self):
        self.tree.delete(*self.tree.get_children())  # 🔥 más rápido

        inicio = self.page * self.page_size
        fin = inicio + self.page_size
        datos = self.data_filtrada[inicio:fin]

        for i, d in enumerate(datos):
            fecha = d.get("fecha_obj")
            fecha = fecha.strftime("%d/%m/%Y %H:%M") if fecha else ""

            tag = "par" if i % 2 == 0 else "impar"

            self.tree.insert("", "end", values=(
                d.get("platillo", ""),
                d.get("cantidad", ""),
                f"${d.get('total', 0):.2f}",
                f"${d.get('pago', 0):.2f}",
                f"${d.get('cambio', 0):.2f}",
                fecha
            ), tags=(tag,))

        self.lbl_page.config(text=f"Página {self.page + 1}")

    # ───────────────────────────────
    def next_page(self):
        if (self.page + 1) * self.page_size < len(self.data_filtrada):
            self.page += 1
            self._mostrar_pagina()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._mostrar_pagina()

    # ───────────────────────────────
    def _get_fecha(self, dia, mes, anio):
        try:
            return datetime(
                int(anio.get()),
                int(mes.get()),
                int(dia.get())
            )
        except:
            return None