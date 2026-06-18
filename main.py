import tkinter as tk
from tkinter import ttk, messagebox
from modulos import (
    multiplicador_constante,
    productos_medios,
    cuadrados_medios,
    congruencial_lineal,
    congruencial_multiplicativo,
    mersenne_twister,
    lotka_volterra,
    pruebas_estadisticas,
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Simulación")
        self.root.geometry("960x760")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._crear_tab_mult_const(self.notebook)
        self._crear_tab_prod_medios(self.notebook)
        self._crear_tab_cuad_medios(self.notebook)
        self._crear_tab_congruencial_lineal(self.notebook)
        self._crear_tab_congruencial_multiplicativo(self.notebook)
        self._crear_tab_mersenne_twister(self.notebook)
        self._crear_tab_lotka_volterra(self.notebook)
        self._crear_tab_pruebas(self.notebook)

    def _crear_input(self, parent, texto, row, default=""):
        ttk.Label(parent, text=texto).grid(row=row, column=0, sticky="e", padx=5, pady=3)
        var = tk.StringVar(value=default)
        entry = ttk.Entry(parent, textvariable=var, width=28)
        entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        return var

    def _crear_tabla(self, parent, columns=("iteracion", "xn", "ri"), col_widths=(60, 200, 200)):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=16)
        for col, w in zip(columns, col_widths):
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=w, anchor="center")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def _validar_positivos(self, *valores):
        for v in valores:
            if v <= 0:
                raise ValueError("Todos los valores deben ser enteros positivos")

    def _enviar_a_pruebas(self, tree, columna_ri=2):
        ris = []
        for item in tree.get_children():
            vals = tree.item(item, "values")
            if len(vals) > columna_ri:
                ris.append(vals[columna_ri])
        if not ris:
            messagebox.showinfo("Sin datos", "Primero genere números con este método.")
            return
        self.pe_texto.delete("1.0", "end")
        self.pe_texto.insert("1.0", ", ".join(ris))
        self.notebook.select(self.notebook.index("end") - 1)

    # ── Multiplicador Constante ──

    def _crear_tab_mult_const(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Mult. Constante")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.mc_constante = self._crear_input(input_frame, "Constante (a):", 0, "5")
        self.mc_valor_ini = self._crear_input(input_frame, "Valor Inicial (X₀):", 1, "1234")
        self.mc_iteraciones = self._crear_input(input_frame, "Iteraciones:", 2, "10")
        self.mc_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 3, "4")
        self.mc_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.mc_periodo_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._mc_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._mc_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._mc_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.mc_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
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
                self.mc_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
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
                    fg="#2563eb",
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Productos Medios ──

    def _crear_tab_prod_medios(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Productos Medios")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.pm_semilla1 = self._crear_input(input_frame, "Semilla 1:", 0, "1234")
        self.pm_semilla2 = self._crear_input(input_frame, "Semilla 2:", 1, "5678")
        self.pm_iteraciones = self._crear_input(input_frame, "Iteraciones:", 2, "10")
        self.pm_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 3, "4")
        self.pm_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.pm_periodo_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._pm_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._pm_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._pm_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.pm_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
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
                self.pm_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
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
                    fg="#2563eb",
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Cuadrados Medios ──

    def _crear_tab_cuad_medios(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Cuadrados Medios")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.cm_semilla = self._crear_input(input_frame, "Semilla:", 0, "1234")
        self.cm_iteraciones = self._crear_input(input_frame, "Iteraciones:", 1, "10")
        self.cm_digitos = self._crear_input(input_frame, "Dígitos Centrales:", 2, "4")
        self.cm_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.cm_periodo_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._cm_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._cm_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._cm_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.cm_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
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
                self.cm_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
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
                    fg="#2563eb",
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Congruencial Lineal ──

    def _crear_tab_congruencial_lineal(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Cong. Lineal")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.cl_a = self._crear_input(input_frame, "Multiplicador (a):", 0, "1664525")
        self.cl_c = self._crear_input(input_frame, "Incremento (c):", 1, "1013904223")
        self.cl_m = self._crear_input(input_frame, "Módulo (m):", 2, "4294967296")
        self.cl_semilla = self._crear_input(input_frame, "Semilla (X₀):", 3, "12345")
        self.cl_iteraciones = self._crear_input(input_frame, "Iteraciones:", 4, "10")
        self.cl_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.cl_periodo_label.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._cl_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._cl_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._cl_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.cl_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.cl_tree = self._crear_tabla(table_frame)

    def _cl_generar(self):
        try:
            a = int(self.cl_a.get())
            c = int(self.cl_c.get())
            m = int(self.cl_m.get())
            semilla = int(self.cl_semilla.get())
            iteraciones = int(self.cl_iteraciones.get())
            self._validar_positivos(a, c, m, semilla, iteraciones)
            resultados = congruencial_lineal.generar(a, c, m, semilla, iteraciones)
            self._cl_limpiar()
            for it, xn, ri in resultados:
                self.cl_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cl_limpiar(self):
        for item in self.cl_tree.get_children():
            self.cl_tree.delete(item)

    def _cl_verificar_periodo(self):
        try:
            a = int(self.cl_a.get())
            c = int(self.cl_c.get())
            m = int(self.cl_m.get())
            semilla = int(self.cl_semilla.get())
            self._validar_positivos(a, c, m, semilla)
            periodo = congruencial_lineal.calcular_periodo(a, c, m, semilla)
            if periodo is None:
                self.cl_periodo_label.config(text="No se encontró repetición en el límite establecido", fg="#dc2626")
            else:
                txt = f"✓ Período: {periodo['unicos']} únicos (ciclo {periodo['longitud_ciclo']}, repite {periodo['valor_repetido']} en iteración {periodo['iteracion_repetida']})"
                if periodo.get("periodo_completo"):
                    txt += " — ¡PeríODO COMPLETO!"
                self.cl_periodo_label.config(text=txt, fg="#2563eb")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Congruencial Multiplicativo ──

    def _crear_tab_congruencial_multiplicativo(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Cong. Multiplicativo")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.cmg_a = self._crear_input(input_frame, "Multiplicador (a):", 0, "16807")
        self.cmg_m = self._crear_input(input_frame, "Módulo (m):", 1, "2147483647")
        self.cmg_semilla = self._crear_input(input_frame, "Semilla (X₀):", 2, "12345")
        self.cmg_iteraciones = self._crear_input(input_frame, "Iteraciones:", 3, "10")
        self.cmg_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.cmg_periodo_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._cmg_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._cmg_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._cmg_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.cmg_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.cmg_tree = self._crear_tabla(table_frame)

    def _cmg_generar(self):
        try:
            a = int(self.cmg_a.get())
            m = int(self.cmg_m.get())
            semilla = int(self.cmg_semilla.get())
            iteraciones = int(self.cmg_iteraciones.get())
            self._validar_positivos(a, m, semilla, iteraciones)
            resultados = congruencial_multiplicativo.generar(a, m, semilla, iteraciones)
            self._cmg_limpiar()
            for it, xn, ri in resultados:
                self.cmg_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cmg_limpiar(self):
        for item in self.cmg_tree.get_children():
            self.cmg_tree.delete(item)

    def _cmg_verificar_periodo(self):
        try:
            a = int(self.cmg_a.get())
            m = int(self.cmg_m.get())
            semilla = int(self.cmg_semilla.get())
            self._validar_positivos(a, m, semilla)
            periodo = congruencial_multiplicativo.calcular_periodo(a, m, semilla)
            if periodo is None:
                self.cmg_periodo_label.config(text="No se encontró repetición en el límite establecido", fg="#dc2626")
            else:
                self.cmg_periodo_label.config(
                    text=f"✓ Período: {periodo['unicos']} únicos (ciclo {periodo['longitud_ciclo']}, repite {periodo['valor_repetido']} en iteración {periodo['iteracion_repetida']})",
                    fg="#2563eb",
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Mersenne Twister ──

    def _crear_tab_mersenne_twister(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Mersenne Twister")
        input_frame = ttk.LabelFrame(tab, text="Parámetros", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.mt_semilla = self._crear_input(input_frame, "Semilla:", 0, "42")
        self.mt_iteraciones = self._crear_input(input_frame, "Iteraciones:", 1, "10")
        self.mt_periodo_label = tk.Label(input_frame, text="", fg="#2563eb", bg="#f0f0f0")
        self.mt_periodo_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Generar", command=self._mt_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._mt_limpiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verificar Período", command=self._mt_verificar_periodo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Enviar a Pruebas", command=lambda: self._enviar_a_pruebas(self.mt_tree)).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.mt_tree = self._crear_tabla(table_frame)

    def _mt_generar(self):
        try:
            semilla = int(self.mt_semilla.get())
            iteraciones = int(self.mt_iteraciones.get())
            self._validar_positivos(semilla, iteraciones)
            resultados = mersenne_twister.generar(semilla, iteraciones)
            self._mt_limpiar()
            for it, xn, ri in resultados:
                self.mt_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _mt_limpiar(self):
        for item in self.mt_tree.get_children():
            self.mt_tree.delete(item)

    def _mt_verificar_periodo(self):
        try:
            semilla = int(self.mt_semilla.get())
            self._validar_positivos(semilla)
            periodo = mersenne_twister.calcular_periodo(semilla)
            if periodo is None:
                self.mt_periodo_label.config(text="No se encontró repetición (período extremadamente largo)", fg="#059669")
            else:
                self.mt_periodo_label.config(
                    text=f"✓ Período detectado: {periodo['unicos']} únicos (ciclo {periodo['longitud_ciclo']})",
                    fg="#2563eb",
                )
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    # ── Lotka-Volterra ──

    def _crear_tab_lotka_volterra(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Lotka-Volterra")
        input_frame = ttk.LabelFrame(tab, text="Parámetros del modelo", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        self.lv_alpha = self._crear_input(input_frame, "α (tasa natalidad presa):", 0, "1.5")
        self.lv_beta = self._crear_input(input_frame, "β (tasa depredación):", 1, "1.0")
        self.lv_delta = self._crear_input(input_frame, "δ (tasa crecimiento depredador):", 2, "3.0")
        self.lv_gamma = self._crear_input(input_frame, "γ (tasa mortalidad depredador):", 3, "1.0")
        self.lv_x0 = self._crear_input(input_frame, "Población inicial presas (X₀):", 4, "10")
        self.lv_y0 = self._crear_input(input_frame, "Población inicial depredadores (Y₀):", 5, "5")
        self.lv_dt = self._crear_input(input_frame, "Paso temporal (dt):", 6, "0.01")
        self.lv_iteraciones = self._crear_input(input_frame, "Iteraciones:", 7, "500")
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Simular", command=self._lv_generar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._lv_limpiar).pack(side="left", padx=5)
        table_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.lv_tree = self._crear_tabla(table_frame, columns=("t", "presas", "depredadores"), col_widths=(80, 150, 150))

    def _lv_generar(self):
        try:
            alpha = float(self.lv_alpha.get())
            beta = float(self.lv_beta.get())
            delta = float(self.lv_delta.get())
            gamma = float(self.lv_gamma.get())
            x0 = float(self.lv_x0.get())
            y0 = float(self.lv_y0.get())
            dt = float(self.lv_dt.get())
            iteraciones = int(self.lv_iteraciones.get())
            if any(v <= 0 for v in [alpha, beta, delta, gamma, x0, y0, dt]):
                raise ValueError("Todos los valores deben ser positivos")
            if iteraciones <= 0:
                raise ValueError("Iteraciones debe ser positivo")
            resultados = lotka_volterra.generar(alpha, beta, delta, gamma, x0, y0, dt, iteraciones)
            self._lv_limpiar()
            # Mostrar cada N iteraciones para no saturar la tabla
            paso = max(1, iteraciones // 50)
            for i, (it, t, presas, depredadores) in enumerate(resultados):
                if i % paso == 0 or i == len(resultados) - 1:
                    self.lv_tree.insert("", "end", values=(t, presas, depredadores))
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _lv_limpiar(self):
        for item in self.lv_tree.get_children():
            self.lv_tree.delete(item)

    # ── Pruebas Estadísticas ──

    def _crear_tab_pruebas(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Pruebas Estadísticas")

        input_frame = ttk.LabelFrame(tab, text="Datos de entrada", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(input_frame, text="Ingrese números separados por coma, espacio o línea:").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5)
        )
        self.pe_texto = tk.Text(input_frame, height=5, width=80, font=("Consolas", 10))
        self.pe_texto.grid(row=1, column=0, columnspan=2, padx=5, pady=3)
        self.pe_texto.insert("1.0", "0.6394, 0.0250, 0.2750, 0.2232, 0.7365, 0.8762, 0.1134, 0.5489, 0.4329, 0.9671")

        config_frame = ttk.LabelFrame(tab, text="Configuración", padding=10)
        config_frame.pack(fill="x", pady=(0, 10))
        self.pe_alpha = self._crear_input(config_frame, "Alpha (nivel sig.):", 0, "0.05")
        self.pe_intervalos = self._crear_input(config_frame, "Intervalos (χ²):", 1, "10")
        self.pe_lag = self._crear_input(config_frame, "Lag (autocorrelación):", 2, "1")

        tests_frame = ttk.LabelFrame(config_frame, text="Pruebas a ejecutar", padding=5)
        tests_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.pe_ck_promedio = tk.BooleanVar(value=True)
        self.pe_ck_varianza = tk.BooleanVar(value=True)
        self.pe_ck_chisq = tk.BooleanVar(value=True)
        self.pe_ck_ks = tk.BooleanVar(value=True)
        self.pe_ck_rachas = tk.BooleanVar(value=True)
        self.pe_ck_rachas_tend = tk.BooleanVar(value=True)
        self.pe_ck_autocorr = tk.BooleanVar(value=True)

        row1 = ttk.Frame(tests_frame)
        row1.pack(fill="x", pady=2)
        ttk.Checkbutton(row1, text="Promedio", variable=self.pe_ck_promedio).pack(side="left", padx=8)
        ttk.Checkbutton(row1, text="Varianza", variable=self.pe_ck_varianza).pack(side="left", padx=8)
        ttk.Checkbutton(row1, text="Chi-cuadrada", variable=self.pe_ck_chisq).pack(side="left", padx=8)
        ttk.Checkbutton(row1, text="Kolmogorov-Smirnov", variable=self.pe_ck_ks).pack(side="left", padx=8)

        row2 = ttk.Frame(tests_frame)
        row2.pack(fill="x", pady=2)
        ttk.Checkbutton(row2, text="Rachas (arriba/abajo)", variable=self.pe_ck_rachas).pack(side="left", padx=8)
        ttk.Checkbutton(row2, text="Rachas tendencia", variable=self.pe_ck_rachas_tend).pack(side="left", padx=8)
        ttk.Checkbutton(row2, text="Autocorrelación", variable=self.pe_ck_autocorr).pack(side="left", padx=8)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Ejecutar Pruebas", command=self._pe_ejecutar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self._pe_limpiar).pack(side="left", padx=5)

        result_frame = ttk.LabelFrame(tab, text="Resultados", padding=5)
        result_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.pe_resultado = tk.Text(result_frame, height=14, width=90, font=("Consolas", 10), state="disabled")
        self.pe_resultado.pack(fill="both", expand=True)

    def _pe_ejecutar(self):
        try:
            raw = self.pe_texto.get("1.0", "end-1c").strip()
            if not raw:
                messagebox.showerror("Error", "Ingrese al menos un número")
                return
            partes = raw.replace(",", " ").split()
            numeros = [float(p) for p in partes]
            alpha = float(self.pe_alpha.get())
            intervalos = int(self.pe_intervalos.get())
            lag = int(self.pe_lag.get())
            if not (0 < alpha < 1):
                raise ValueError("Alpha debe estar entre 0 y 1")
            if intervalos < 2:
                raise ValueError("Intervalos debe ser al menos 2")

            pruebas = []
            nombres = []
            if self.pe_ck_promedio.get():
                pruebas.append(pruebas_estadisticas.prueba_promedio)
                nombres.append("Promedio")
            if self.pe_ck_varianza.get():
                pruebas.append(pruebas_estadisticas.prueba_varianza)
                nombres.append("Varianza")
            if self.pe_ck_chisq.get():
                pruebas.append(lambda n, a: pruebas_estadisticas.prueba_chi_cuadrada(n, intervalos, a))
                nombres.append("Chi-cuadrada")
            if self.pe_ck_ks.get():
                pruebas.append(pruebas_estadisticas.prueba_uniformidad_ks)
                nombres.append("Kolmogorov-Smirnov")
            if self.pe_ck_rachas.get():
                pruebas.append(pruebas_estadisticas.prueba_rachas)
                nombres.append("Rachas")
            if self.pe_ck_rachas_tend.get():
                pruebas.append(pruebas_estadisticas.prueba_rachas_tendencia)
                nombres.append("Rachas tendencia")
            if self.pe_ck_autocorr.get():
                pruebas.append(lambda n, a: pruebas_estadisticas.prueba_independencia_autocorrelacion(n, lag, a))
                nombres.append("Autocorrelación")

            if not pruebas:
                messagebox.showerror("Error", "Seleccione al menos una prueba")
                return

            self._pe_limpiar()
            salida = f"{'='*72}\n"
            salida += f"  PRUEBAS ESTADÍSTICAS — {len(numeros)} números, α={alpha}\n"
            salida += f"{'='*72}\n\n"

            for prueba, nombre in zip(pruebas, nombres):
                res = prueba(numeros, alpha)
                salida += f"► {res['prueba']}\n"
                salida += f"  Estadístico: {res['estadistico']}\n"
                salida += f"  Valor calculado: {res['valor_calculado']:.6f}\n"
                if "valor_critico" in res:
                    salida += f"  Valor crítico: {res['valor_critico']:.6f}\n"
                if "valor_critico_inferior" in res:
                    salida += f"  Valor crítico inferior: {res['valor_critico_inferior']:.6f}\n"
                if "valor_critico_superior" in res:
                    salida += f"  Valor crítico superior: {res['valor_critico_superior']:.6f}\n"
                if "limite_inferior" in res and "limite_superior" in res:
                    salida += f"  Límite inferior: {res['limite_inferior']:.6f}\n"
                    salida += f"  Límite superior: {res['limite_superior']:.6f}\n"
                if nombre == "Promedio":
                    salida += f"  Media muestral: {res['media']:.6f}\n"
                if nombre == "Varianza":
                    salida += f"  Varianza muestral: {res['varianza_muestral']:.6f}\n"
                if nombre == "Chi-cuadrada":
                    salida += f"  Intervalos: {res['intervalos']},  Grados libertad: {res['grados_libertad']}\n"
                    salida += f"  Frecuencia esperada: {res['frecuencia_esperada']:.2f}\n"
                    salida += f"  Frecuencias: {res['frecuencias']}\n"
                if nombre == "Rachas":
                    salida += f"  Rachas observadas: {res['runs']},  Esperadas: {res['media_runs']:.2f}\n"
                    salida += f"  n1 (sobre media): {res.get('n1', '?')},  n2 (bajo media): {res.get('n2', '?')}\n"
                if nombre == "Autocorrelación":
                    salida += f"  Autocorrelación: {res['autocorrelacion']:.6f},  Lag: {res.get('lag', '?')}\n"
                salida += f"  ¿Acepta H0?: {'SÍ ✓' if res['acepta_H0'] else 'NO ✗'}\n"
                salida += f"  → {res['interpretacion']}\n\n"

            self.pe_resultado.config(state="normal")
            self.pe_resultado.delete("1.0", "end")
            self.pe_resultado.insert("1.0", salida)
            self.pe_resultado.config(state="disabled")

        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _pe_limpiar(self):
        self.pe_resultado.config(state="normal")
        self.pe_resultado.delete("1.0", "end")
        self.pe_resultado.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
