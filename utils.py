import tkinter as tk
import tkinter as tk

def campo(parent, texto, fila, bg="#D4D3D3"):
    """Crea un label + entry apilados en el form. Devuelve el Entry."""
    tk.Label(parent, text=texto, bg=bg, fg="black", anchor="w",
             font=("Arial", 16)).grid(row=fila, column=0, columnspan=2,
                                      sticky="w", padx=20, pady=(15, 2))
    entry = tk.Entry(parent, bd=0, bg="#ffffff", font=("Arial", 16),
                     relief="flat", highlightthickness=0)
    entry.grid(row=fila+1, column=0, columnspan=2,
               padx=20, pady=(2, 10), ipady=8, sticky="ew")
    return entry

def make_page(body, bg="#0F0092"):
    """Crea un frame que cubre todo el body. Se usa como base de cada pestaña."""
    f = tk.Frame(body, bg=bg)
    f.place(relx=0, rely=0, relwidth=1, relheight=1)
    return f

def make_form(parent, width=1300, bg="#D4D3D3"):
    """Crea un formulario centrado horizontalmente dentro del parent."""
    f = tk.Frame(parent, bg=bg, width=width)
    f.place(relx=0.5, rely=0, anchor="n", width=width)
    f.grid_columnconfigure(0, weight=1)
    f.grid_columnconfigure(1, weight=1)
    return f

def make_scrollable_page(body, bg_page="#0F0092", form_width=1300, bg_form="#D4D3D3"):
    """
    Crea una página completa con scroll vertical.
    Devuelve (pagina, form): pagina es el frame raíz, form es donde van los widgets.
    """
    # Frame raíz de la página
    pagina = tk.Frame(body, bg=bg_page)
    pagina.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Canvas que permite el scroll
    canvas = tk.Canvas(pagina, bg=bg_page, highlightthickness=0)
    sb = tk.Scrollbar(pagina, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)

    # Scroll con rueda del mouse
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # Form centrado dentro del canvas
    form = tk.Frame(canvas, bg=bg_form, width=form_width)
    win = canvas.create_window((0, 10), window=form, anchor="n")

    # Recalcula el área de scroll cuando cambia el tamaño del form
    form.bind("<Configure>", lambda e: (
        canvas.configure(scrollregion=canvas.bbox("all")),
        canvas.coords(win, canvas.winfo_width() // 2, 10)
    ))

    # Recentra el form cuando cambia el tamaño del canvas
    canvas.bind("<Configure>", lambda e: canvas.coords(win, e.width // 2, 10))

    form.grid_columnconfigure(0, weight=1)
    form.grid_columnconfigure(1, weight=1)

    return pagina, form

# ── VALIDACIONES REUTILIZABLES ─────────────────────

def texto_con_limite(max_len):
    """
    Valida que el texto no supere max_len caracteres
    y que solo contenga letras y espacios.
    """
    def validador(nuevo_valor):
        if len(nuevo_valor) > max_len:
            return False
        if nuevo_valor == "":
            return True
        return all(c.isalpha() or c.isspace() for c in nuevo_valor)
    return validador

def numero_con_limite(max_len):
    """
    Valida que el valor sea un número positivo
    y no supere max_len caracteres.
    """
    def validador(nuevo_valor):
        if len(nuevo_valor) > max_len:
            return False
        if nuevo_valor == "":
            return True
        try:
            return float(nuevo_valor) >= 0
        except:
            return False
    return validador

def limitar_longitud(max_len):
    """Valida que el texto no supere max_len caracteres. Sin restricción de tipo."""
    def validador(nuevo_valor):
        return len(nuevo_valor) <= max_len
    return validador