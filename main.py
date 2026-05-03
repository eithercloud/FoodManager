import tkinter as tk
from tkinter import ttk
import ctypes
from firebase_config import init_firebase
from page_cobrar import PageCobrar
from page_platillo import PagePlatillo
from page_modificar import PageModificar
from page_ingrediente import PageIngrediente
from page_menu import PageMenu
from page_venta import PageVenta

# ── DPI FIX ───────────────────────────────────
# Mejora la nitidez en pantallas de alta resolución (4K, HiDPI)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# Conexión a Firebase
db = init_firebase()

# ── Ventana principal ──────────────────────────
root = tk.Tk()
root.title("Restaurante")
root.state("zoomed")  # Inicia maximizado
root.configure(bg="#0F0092")

# ── Estilo global para todos los Combobox ──────
style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.TCombobox",
    fieldbackground="#1e272e", background="#1e272e",
    foreground="#ffffff", font=("Arial", 16, "bold"),
    padding=8, relief="flat"
)
style.map("Custom.TCombobox",
    fieldbackground=[("readonly", "#1e272e")],
    selectbackground=[("readonly", "#1e272e")],
    selectforeground=[("readonly", "#ffffff")]
)
# Estilo del dropdown del Combobox
root.option_add("*TCombobox*Listbox.background", "#1e272e")
root.option_add("*TCombobox*Listbox.foreground", "#ffffff")
root.option_add("*TCombobox*Listbox.font", "Arial 10")
root.option_add("*TCombobox*Listbox.selectBackground", "#055B0A")
root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

# ── Header con botones de navegación ──────────
header = tk.Frame(root, bg="#0f1419", height=80)
header.pack(fill="x")
header.pack_propagate(False)

# ── Body donde viven todas las páginas ────────
body = tk.Frame(root, bg="#0F0092")
body.pack(fill="both", expand=True)

def mostrar(pagina, callback=None):
    """Trae al frente la página indicada y ejecuta su callback de carga."""
    pagina.tkraise()
    if callback:
        callback()

# ── Instancia de cada página ──────────────────
p_cobrar      = PageCobrar(body, db)
p_platillo    = PagePlatillo(body, db)
p_modificar   = PageModificar(body, db)
p_ingrediente = PageIngrediente(body, db)
p_menu        = PageMenu(body, db)
p_venta       = PageVenta(body, db)

# ── Referencias cruzadas entre páginas ────────

def recargar_cobrar():
    """
    Marca como sucias las páginas que dependen de la lista de platillos
    y fuerza la recarga del combo en Cobrar.
    Se llama cuando se guarda o elimina un platillo.
    """
    p_cobrar._dirty    = True
    p_menu._dirty      = True
    p_modificar._dirty = True
    p_cobrar.cargar_combo_platillos()

# Cuando se guarda un platillo nuevo o se modifica/elimina uno existente
p_platillo.set_reload_cb(recargar_cobrar)
p_modificar.set_reload_cb(recargar_cobrar)
p_menu.set_reload_cb(recargar_cobrar)
p_venta.set_reload_cb(recargar_cobrar)

def recargar_checks():
    """
    Fuerza que la página Añadir Platillo recargue
    los checkboxes de ingredientes.
    Se llama cuando se agrega un ingrediente nuevo.
    """
    p_platillo._dirty = True
    p_platillo.cargar_checks_ingredientes()

p_ingrediente.set_reload_checks_cb(recargar_checks)

def actualizar_ventas():
    """Recarga la tabla de ventas al procesar un cobro."""
    p_venta.recargar_datos()

p_cobrar.set_reload_ventas_cb(actualizar_ventas)

# ── Botones del header ────────────────────────
btn_cfg = dict(bg="#1e272e", fg="white", bd=0, width=15, font=("Arial", 12))

# ── Boton "Cobrar Platillo" ────────
tk.Button(header, text="Cobrar", **btn_cfg,
    command=lambda: mostrar(p_cobrar.frame, p_cobrar.cargar_combo_platillos)
).pack(side="left", padx=10, pady=15)

# ── Boton "Añadir Platillo" ────────
tk.Button(header, text="Añadir Platillo", **btn_cfg,
    command=lambda: mostrar(p_platillo.frame, p_platillo.cargar_checks_ingredientes)
).pack(side="left", padx=10, pady=15)

# ── Boton "Modificar Platillo" ────────
tk.Button(header, text="Modificar Platillo", **btn_cfg,
    command=lambda: mostrar(p_modificar.frame, p_modificar.cargar_platillos)
).pack(side="left", padx=10, pady=15)

# ── Boton "Añadir Ingredientes" ────────
tk.Button(header, text="Añadir Ingrediente", **btn_cfg,
    command=lambda: mostrar(p_ingrediente.frame, p_ingrediente.actualizar_lista)
).pack(side="left", padx=10, pady=15)

# ── Boton "Platillos" ────────
tk.Button(header, text="Platillos", **btn_cfg,
    command=lambda: mostrar(p_menu.frame, p_menu.cargar_platillos)
).pack(side="left", padx=10, pady=15)

# ── Boton "Ventas" ────────
tk.Button(header, text="Ventas", **btn_cfg,
    command=lambda: mostrar(p_venta.frame, p_venta.cargar_platillos)
).pack(side="left", padx=10, pady=15)

# ── Boton "Salir" ────────
tk.Button(header, text="Salir", bg="#e84118", fg="white", bd=0,
    width=15, font=("Arial", 12), command=root.quit
).pack(side="right", padx=10, pady=15)

# ── Mostrar página inicial ────────────────────
mostrar(p_cobrar.frame, p_cobrar.cargar_combo_platillos)
root.mainloop()