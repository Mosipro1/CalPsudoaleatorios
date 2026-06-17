import tkinter as tk
from tkinter import ttk, messagebox
from modulos import multiplicador_constante, productos_medios, cuadrados_medios


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Números Pseudoaleatorios")
        self.root.geometry("800x600")

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self._crear_tab_mult_const(notebook)
        self._crear_tab_prod_medios(notebook)
        self._crear_tab_cuad_medios(notebook)

    def _crear_input(self, parent, texto, row, default=""):
        ttk.Label(parent, text=texto).grid(row=row, column=0, sticky='e', padx=5, pady=3)
        var = tk.StringVar(value=default)
        entry = ttk.Entry(parent, textvariable=var, width=28)
        entry.grid(row=row, column=1, sticky='w', padx=5, pady=3)
        return var

    def _crear_tabla(self, parent):
        columns = ("iteracion", "xn", "ri")
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=16)
        tree.heading("iteracion", text="#")
        tree.heading("xn", text="Xn")
        tree.heading("ri", text="ri")
        tree.column("iteracion", width=60, anchor='center')
        tree.column("xn", width=200, anchor='center')
        tree.column("ri", width=200, anchor='center')

        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        return tree

    def _validar_positivos(self, *valores):
        for v in valores:
            if v <= 0:
                raise ValueError("Todos los valores deben ser enteros positivos")

    # ── Módulo 1: Multiplicador Constante ──

    def _crear_tab_mult_const(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Multiplicador Constante")

        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))

        self.mc_constante = self._crear_input(input_frame, "Constante (a):", 0, "5")
        self.mc_valor_ini = self._crear_input(input_frame, "Valor Inicial (X₀):", 1, "1234")
        self.mc_iteraciones = self._crear_input(input_frame, "Iteraciones:", 2, "10")
        self.mc_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 3, "4")
        self.mc_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.mc_periodo_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._mc_generar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._mc_limpiar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._mc_verificar_periodo).pack(side='left', padx=5)

        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill='both', expand=True, pady=(10, 0))

        self.mc_tree = self._crear_tabla(table_frame)

    def _mc_generar(self):
        try:
            constante = int(self.mc_constante.get())
            valor_ini = int(self.mc_valor_ini.get())
            iteraciones = int(self.mc_iteraciones.get())
            digitos = int(self.mc_digitos.get())
            self._validar_positivos(constante, valor_ini, iteraciones, digitos)
            resultados = multiplicador_constante.generar(constante, valor_ini, iteraciones, digitos)
            self._mc_limpiar()
            for it, xn, ri in resultados:
                self.mc_tree.insert('', 'end', values=(it, xn, f"{ri:.{digitos}f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _mc_limpiar(self):
        for item in self.mc_tree.get_children():
            self.mc_tree.delete(item)

    def _mc_verificar_periodo(self):
        try:
            constante = int(self.mc_constante.get())
            valor_ini = int(self.mc_valor_ini.get())
            digitos = int(self.mc_digitos.get())
            self._validar_positivos(constante, valor_ini, digitos)
            periodo = multiplicador_constante.calcular_periodo(constante, valor_ini, digitos)
            if periodo is None:
                self.mc_periodo_label.config(text="No se encontró repetición en el límite establecido", fg="#dc2626")
            else:
                self.mc_periodo_label.config(
                    text=f"✓ Período: {periodo['unicos']} números únicos (ciclo de {periodo['longitud_ciclo']}, repite {periodo['valor_repetido']} en iteración {periodo['iteracion_repetida']})",
                    fg="#2563eb"
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Módulo 2: Productos Medios ──

    def _crear_tab_prod_medios(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Productos Medios")

        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))

        self.pm_semilla1 = self._crear_input(input_frame, "Semilla 1:", 0, "1234")
        self.pm_semilla2 = self._crear_input(input_frame, "Semilla 2:", 1, "5678")
        self.pm_iteraciones = self._crear_input(input_frame, "Iteraciones:", 2, "10")
        self.pm_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 3, "4")
        self.pm_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.pm_periodo_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._pm_generar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._pm_limpiar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._pm_verificar_periodo).pack(side='left', padx=5)

        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill='both', expand=True, pady=(10, 0))

        self.pm_tree = self._crear_tabla(table_frame)

    def _pm_generar(self):
        try:
            s1 = int(self.pm_semilla1.get())
            s2 = int(self.pm_semilla2.get())
            iteraciones = int(self.pm_iteraciones.get())
            digitos = int(self.pm_digitos.get())
            self._validar_positivos(s1, s2, iteraciones, digitos)
            resultados = productos_medios.generar(s1, s2, iteraciones, digitos)
            self._pm_limpiar()
            for it, xn, ri in resultados:
                self.pm_tree.insert('', 'end', values=(it, xn, f"{ri:.{digitos}f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _pm_limpiar(self):
        for item in self.pm_tree.get_children():
            self.pm_tree.delete(item)

    def _pm_verificar_periodo(self):
        try:
            s1 = int(self.pm_semilla1.get())
            s2 = int(self.pm_semilla2.get())
            digitos = int(self.pm_digitos.get())
            self._validar_positivos(s1, s2, digitos)
            periodo = productos_medios.calcular_periodo(s1, s2, digitos)
            if periodo is None:
                self.pm_periodo_label.config(text="No se encontró repetición en el límite establecido", fg="#dc2626")
            else:
                self.pm_periodo_label.config(
                    text=f"✓ Período: {periodo['unicos']} números únicos (ciclo de {periodo['longitud_ciclo']}, repite {periodo['valor_repetido']} en iteración {periodo['iteracion_repetida']})",
                    fg="#2563eb"
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Módulo 3: Cuadrados Medios ──

    def _crear_tab_cuad_medios(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Cuadrados Medios")

        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))

        self.cm_semilla = self._crear_input(input_frame, "Semilla:", 0, "1234")
        self.cm_iteraciones = self._crear_input(input_frame, "Iteraciones:", 1, "10")
        self.cm_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 2, "4")
        self.cm_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.cm_periodo_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._cm_generar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._cm_limpiar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._cm_verificar_periodo).pack(side='left', padx=5)

        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill='both', expand=True, pady=(10, 0))

        self.cm_tree = self._crear_tabla(table_frame)

    def _cm_generar(self):
        try:
            semilla = int(self.cm_semilla.get())
            iteraciones = int(self.cm_iteraciones.get())
            digitos = int(self.cm_digitos.get())
            self._validar_positivos(semilla, iteraciones, digitos)
            resultados = cuadrados_medios.generar(semilla, iteraciones, digitos)
            self._cm_limpiar()
            for it, xn, ri in resultados:
                self.cm_tree.insert('', 'end', values=(it, xn, f"{ri:.{digitos}f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cm_limpiar(self):
        for item in self.cm_tree.get_children():
            self.cm_tree.delete(item)

    def _cm_verificar_periodo(self):
        try:
            semilla = int(self.cm_semilla.get())
            digitos = int(self.cm_digitos.get())
            self._validar_positivos(semilla, digitos)
            periodo = cuadrados_medios.calcular_periodo(semilla, digitos)
            if periodo is None:
                self.cm_periodo_label.config(text="No se encontró repetición en el límite establecido", fg="#dc2626")
            else:
                self.cm_periodo_label.config(
                    text=f"✓ Período: {periodo['unicos']} números únicos (ciclo de {periodo['longitud_ciclo']}, repite {periodo['valor_repetido']} en iteración {periodo['iteracion_repetida']})",
                    fg="#2563eb"
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
