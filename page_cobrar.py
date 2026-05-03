import tkinter as tk
from tkinter import ttk, messagebox
from utils import campo, make_scrollable_page
from utils import numero_con_limite
from datetime import datetime

class PageCobrar:
    def __init__(self, body, db):
        self._reload_ventas_cb = None
        self._dirty = True
        self.db = db
        self.platillos_data = {}
        self.pedido_lista = []

        self.frame, self.form = make_scrollable_page(body)
        self._build()

    def _build(self):
        form = self.form
    
        # ── Platillo ──────────────────────────
        tk.Label(form, text="Platillo", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 2))

        self.combo_var = tk.StringVar()
        self.combo_platillos = ttk.Combobox(form, textvariable=self.combo_var,
                                             font=("Arial", 16), state="readonly",
                                             style="Custom.TCombobox")
        self.combo_platillos.grid(row=1, column=0, padx=20, pady=(2, 4), sticky="ew", ipady=8)

        self.lbl_precio_sel = tk.Label(form, text="", bg="#D4D3D3", fg="#055B0A",
                                        font=("Arial", 13, "bold"))
        self.lbl_precio_sel.grid(row=2, column=0, sticky="w", padx=22)

        # ── Cantidad ──────────────────────────
        tk.Label(form, text="Cantidad", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=3, column=0, sticky="w", padx=20, pady=(15, 2))

        frame_cantidad = tk.Frame(form, bg="#D4D3D3")
        frame_cantidad.grid(row=4, column=0, sticky="w", padx=20, pady=(2, 10))

        self.cantidad_var = tk.IntVar(value=1)

        tk.Button(frame_cantidad, text=" − ", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 16, "bold"), padx=12, pady=6,
                  command=lambda: self._cambiar_cantidad(-1)).pack(side="left")
        tk.Label(frame_cantidad, textvariable=self.cantidad_var,
                 bg="#ffffff", fg="black", font=("Arial", 16),
                 width=4, anchor="center", pady=6).pack(side="left")
        tk.Button(frame_cantidad, text=" + ", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 16, "bold"), padx=12, pady=6,
                  command=lambda: self._cambiar_cantidad(1)).pack(side="left")

        tk.Button(form, text="+ Agregar al pedido", bg="#1e272e", fg="white", bd=0,
                  font=("Arial", 14, "bold"), padx=20, pady=8,
                  command=self._agregar_al_pedido
                  ).grid(row=5, column=0, sticky="w", padx=20, pady=(5, 15))

        # ── Tabla pedido ──────────────────────
        tk.Label(form, text="Pedido actual", bg="#D4D3D3", fg="black",
                 font=("Arial", 16)).grid(row=6, column=0, sticky="w", padx=20, pady=(5, 2))

        self.frame_tabla = tk.Frame(form, bg="#ffffff")
        self.frame_tabla.grid(row=7, column=0, sticky="ew", padx=20, pady=(2, 10))
        self.frame_tabla.grid_columnconfigure(0, weight=3)
        self.frame_tabla.grid_columnconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(2, weight=1)
        self.frame_tabla.grid_columnconfigure(3, weight=1)

        for col, txt in enumerate(["Platillo", "Cantidad", "P. Unit.", "Subtotal", ""]):
            tk.Label(self.frame_tabla, text=txt, bg="#1e272e", fg="white",
                     font=("Arial", 13, "bold"), anchor="center",
                     padx=10, pady=6).grid(row=0, column=col, sticky="ew", padx=1, pady=1)

        self.lbl_total = tk.Label(form, text="Total: $0.00", bg="#D4D3D3",
                                   fg="#055B0A", font=("Arial", 16, "bold"))
        self.lbl_total.grid(row=8, column=0, sticky="e", padx=25, pady=(5, 2))
        
        # ── Pago y cambio ─────────────────────
        self.pago   = campo(form, "Pago con", 9)
        vcmd_pago = (self.frame.register(numero_con_limite(20)), "%P")

        self.pago.config(
            validate="key",
            validatecommand=vcmd_pago
        )
        self.cambio = campo(form, "Cambio",   11)
        self.pago.bind("<KeyRelease>", self._calcular_cambio_auto)
        self.cambio.config(state="readonly")

        tk.Button(form, text="Procesar Cobro", bg="#055B0A", fg="white", bd=0,
                  font=("Arial", 16, "bold"), width=30,
                  activebackground="#055B0A", padx=40, pady=4,
                  command=self._procesar_cobro
                  ).grid(row=13, column=0, pady=15)

        self.combo_platillos.bind("<<ComboboxSelected>>",
                                   lambda e: (self.cantidad_var.set(1), self._actualizar_precio_label()))

    # ── Métodos ───────────────────────────────
    def set_reload_ventas_cb(self, cb):
        self._reload_ventas_cb = cb
    def _cambiar_cantidad(self, delta):
        nuevo = max(1, self.cantidad_var.get() + delta)
        self.cantidad_var.set(nuevo)
        self._actualizar_precio_label()

    def _actualizar_precio_label(self):
        sel = self.combo_var.get()
        if sel in self.platillos_data:
            p = self.platillos_data[sel].get("precio", 0)
            total = float(p) * self.cantidad_var.get()
            self.lbl_precio_sel.config(text=f"  ${p} c/u  →  subtotal ${total:.2f}")
        else:
            self.lbl_precio_sel.config(text="")

    def _agregar_al_pedido(self):
        sel = self.combo_var.get()
        if not sel:
            messagebox.showwarning("Sin platillo", "Selecciona un platillo")
            return
        cantidad    = self.cantidad_var.get()
        precio_unit = float(self.platillos_data.get(sel, {}).get("precio", 0))
        subtotal    = precio_unit * cantidad

        for item in self.pedido_lista:
            if item["nombre"] == sel:
                item["cantidad"] += cantidad
                item["subtotal"] += subtotal
                self._refrescar_tabla()
                self.cantidad_var.set(1)
                self._actualizar_precio_label()
                return

        self.pedido_lista.append({"nombre": sel, "cantidad": cantidad,
                                   "precio_unit": precio_unit, "subtotal": subtotal})
        self._refrescar_tabla()
        self.cantidad_var.set(1)
        self._actualizar_precio_label()

    def _refrescar_tabla(self):
        for w in self.frame_tabla.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        total = 0
        for i, item in enumerate(self.pedido_lista):
            bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
            tk.Label(self.frame_tabla, text=item["nombre"], bg=bg, fg="black",
                     font=("Arial", 13), anchor="w", padx=10, pady=5
                     ).grid(row=i+1, column=0, sticky="ew", padx=1, pady=1)
            tk.Label(self.frame_tabla, text=str(item["cantidad"]), bg=bg, fg="black",
                     font=("Arial", 13), anchor="center"
                     ).grid(row=i+1, column=1, sticky="ew", padx=1, pady=1)
            tk.Label(self.frame_tabla, text=f"${item['precio_unit']:.2f}", bg=bg, fg="black",
                     font=("Arial", 13), anchor="center"
                     ).grid(row=i+1, column=2, sticky="ew", padx=1, pady=1)
            tk.Label(self.frame_tabla, text=f"${item['subtotal']:.2f}", bg=bg, fg="black",
                     font=("Arial", 13), anchor="center"
                     ).grid(row=i+1, column=3, sticky="ew", padx=1, pady=1)
            tk.Button(self.frame_tabla, text="✕", bg="#e84118", fg="white", bd=0,
                      font=("Arial", 12, "bold"), padx=8, pady=3,
                      command=lambda ix=i: self._eliminar_fila(ix)
                      ).grid(row=i+1, column=4, padx=4, pady=1)
            total += item["subtotal"]
        self.lbl_total.config(text=f"Total: ${total:.2f}")
        self._calcular_cambio_auto()
    
    def _eliminar_fila(self, idx):
        del self.pedido_lista[idx]
        self._refrescar_tabla()

    def _calcular_cambio_auto(self, event=None):
        try:
            total    = sum(i["subtotal"] for i in self.pedido_lista)
            pago_val = float(self.pago.get())
            cambio_val = pago_val - total
            self.cambio.config(state="normal")
            self.cambio.delete(0, tk.END)
            self.cambio.insert(0, f"{cambio_val:.2f}")
            self.cambio.config(fg="#055B0A" if cambio_val >= 0 else "#e84118")
        except ValueError:
            self.cambio.config(state="normal")
            self.cambio.delete(0, tk.END)

    def cargar_combo_platillos(self):
        if not self._dirty:
            return
        self._dirty = False
        self.platillos_data = {}
        for doc in self.db.collection("platillos").stream():
            d = doc.to_dict()
            self.platillos_data[d["nombre"]] = {**d, "id": doc.id}
        self.combo_platillos["values"] = list(self.platillos_data.keys())
        self.lbl_precio_sel.config(text="")
        self.cantidad_var.set(1)
    
    def _procesar_cobro(self):
        if not self.pedido_lista:
            messagebox.showwarning("Pedido vacío", "Agrega al menos un platillo")
            return
        if not self.pago.get():
            messagebox.showwarning("Campos vacíos", "Ingresa el monto de pago")
            return
        total = sum(i["subtotal"] for i in self.pedido_lista)

        try:
            pago_val = float(self.pago.get())
        except ValueError:
            messagebox.showerror("Error", "Pago inválido")
            return

        # VALIDACIÓN 
        if pago_val < total:
            messagebox.showerror("Pago insuficiente", "El pago no puede ser menor al total")
            return

        cambio_val = pago_val - total

        

        for item in self.pedido_lista:
            self.db.collection("cobros").add({
                "platillo":        item["nombre"],
                "precio_unitario": item["precio_unit"],
                "cantidad":        item["cantidad"],
                "total":           item["subtotal"],
                "pago":            pago_val,
                "cambio":          cambio_val,
                "fecha": datetime.now().isoformat()
            })
        
        if self._reload_ventas_cb:
            self._reload_ventas_cb()
        
        detalle = "\n".join([f"  {i['nombre']} x{i['cantidad']} = ${i['subtotal']:.2f}"
                             for i in self.pedido_lista])
        
        messagebox.showinfo("✅ Cobro registrado",
                            f"{detalle}\n\nTotal: ${total:.2f}\nCambio: ${cambio_val:.2f}")
        
        self.pedido_lista.clear()
        self._refrescar_tabla()
        self.pago.delete(0, tk.END)
        self.cambio.config(state="normal")
        self.cambio.delete(0, tk.END)
        self._dirty = True

    