import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import webbrowser
import threading
import subprocess
import os
import signal
from modulos import (
    multiplicador_constante,
    productos_medios,
    cuadrados_medios,
    congruencial_lineal,
    congruencial_multiplicativo,
    mersenne_twister,
    lotka_volterra,
    pruebas_estadisticas,
    covid_sim,
    dolares,
    quinua,
)
from modulos.roulette import Engine, Player, Statistics
from modulos.roulette.wheel_layout import SECUENCIA_RUEDA, COLORES
from modulos.roulette.sounds import sounds


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Simulación")
        self.root.geometry("960x960")

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
        self._crear_tab_roulette(self.notebook)
        self._crear_tab_covid(self.notebook)
        self._crear_tab_dolares(self.notebook)
        self._crear_tab_quinua(self.notebook)
        self._crear_music_player(root)

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

    # ── Helpers para gráficos ──

    def _crear_graficos(self, parent, prefix):
        frame = ttk.LabelFrame(parent, text="Gráficos", padding=5)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))
        fig.tight_layout(pad=3)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        setattr(self, f"{prefix}_fig", fig)
        setattr(self, f"{prefix}_ax1", ax1)
        setattr(self, f"{prefix}_ax2", ax2)
        setattr(self, f"{prefix}_canvas", canvas)
        return frame

    def _graficar_ris(self, prefix, ris, titulo=""):
        fig = getattr(self, f"{prefix}_fig")
        ax1 = getattr(self, f"{prefix}_ax1")
        ax2 = getattr(self, f"{prefix}_ax2")
        canvas = getattr(self, f"{prefix}_canvas")
        ax1.clear()
        ax2.clear()
        ax1.bar(range(1, len(ris) + 1), ris, color="#4f46e5", width=0.7)
        ax1.set_title(f"Serie de ri — {titulo}")
        ax1.set_xlabel("Iteración")
        ax1.set_ylabel("ri")
        ax1.set_ylim(0, 1)
        ax2.hist(ris, bins=10, range=(0, 1), color="#7c3aed", edgecolor="white")
        ax2.set_title(f"Histograma — {titulo}")
        ax2.set_xlabel("ri")
        ax2.set_ylabel("Frecuencia")
        fig.tight_layout()
        canvas.draw()

    def _limpiar_graficos(self, prefix):
        ax1 = getattr(self, f"{prefix}_ax1")
        ax2 = getattr(self, f"{prefix}_ax2")
        canvas = getattr(self, f"{prefix}_canvas")
        ax1.clear()
        ax2.clear()
        canvas.draw()

    def _graficar_lv(self, resultados):
        ax1 = self.lv_ax1
        ax2 = self.lv_ax2
        canvas = self.lv_canvas
        ax1.clear()
        ax2.clear()
        tiempos = [r[1] for r in resultados]
        presas = [r[2] for r in resultados]
        depredadores = [r[3] for r in resultados]
        ax1.plot(tiempos, presas, label="Presas", color="#059669")
        ax1.plot(tiempos, depredadores, label="Depredadores", color="#dc2626")
        ax1.set_title("Lotka-Volterra — Poblaciones")
        ax1.set_xlabel("Tiempo")
        ax1.set_ylabel("Población")
        ax1.legend()
        ax2.scatter(presas, depredadores, s=10, alpha=0.6, color="#7c3aed")
        ax2.set_title("Espacio de fases")
        ax2.set_xlabel("Presas")
        ax2.set_ylabel("Depredadores")
        self.lv_fig.tight_layout()
        canvas.draw()

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
        graficos_frame = self._crear_graficos(tab, "mc")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

    def _mc_generar(self):
        try:
            constante = int(self.mc_constante.get())
            valor_ini = int(self.mc_valor_ini.get())
            iteraciones = int(self.mc_iteraciones.get())
            digitos = int(self.mc_digitos.get())
            self._validar_positivos(constante, valor_ini, iteraciones, digitos)
            resultados = multiplicador_constante.generar(constante, valor_ini, iteraciones, digitos)
            self._mc_limpiar()
            ris = []
            for it, xn, ri in resultados:
                self.mc_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
                ris.append(ri)
            self._graficar_ris("mc", ris, "Mult. Constante")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _mc_limpiar(self):
        for item in self.mc_tree.get_children():
            self.mc_tree.delete(item)
        self._limpiar_graficos("mc")

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
        graficos_frame = self._crear_graficos(tab, "pm")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

    def _pm_generar(self):
        try:
            s1 = int(self.pm_semilla1.get())
            s2 = int(self.pm_semilla2.get())
            iteraciones = int(self.pm_iteraciones.get())
            digitos = int(self.pm_digitos.get())
            self._validar_positivos(s1, s2, iteraciones, digitos)
            resultados = productos_medios.generar(s1, s2, iteraciones, digitos)
            self._pm_limpiar()
            ris = []
            for it, xn, ri in resultados:
                self.pm_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
                ris.append(ri)
            self._graficar_ris("pm", ris, "Productos Medios")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _pm_limpiar(self):
        for item in self.pm_tree.get_children():
            self.pm_tree.delete(item)
        self._limpiar_graficos("pm")

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
        graficos_frame = self._crear_graficos(tab, "cm")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

    def _cm_generar(self):
        try:
            semilla = int(self.cm_semilla.get())
            iteraciones = int(self.cm_iteraciones.get())
            digitos = int(self.cm_digitos.get())
            self._validar_positivos(semilla, iteraciones, digitos)
            resultados = cuadrados_medios.generar(semilla, iteraciones, digitos)
            self._cm_limpiar()
            ris = []
            for it, xn, ri in resultados:
                self.cm_tree.insert("", "end", values=(it, xn, f"{ri:.{digitos}f}"))
                ris.append(ri)
            self._graficar_ris("cm", ris, "Cuadrados Medios")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cm_limpiar(self):
        for item in self.cm_tree.get_children():
            self.cm_tree.delete(item)
        self._limpiar_graficos("cm")

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
        graficos_frame = self._crear_graficos(tab, "cl")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

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
            ris = []
            for it, xn, ri in resultados:
                self.cl_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
                ris.append(ri)
            self._graficar_ris("cl", ris, "Cong. Lineal")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cl_limpiar(self):
        for item in self.cl_tree.get_children():
            self.cl_tree.delete(item)
        self._limpiar_graficos("cl")

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
        graficos_frame = self._crear_graficos(tab, "cmg")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

    def _cmg_generar(self):
        try:
            a = int(self.cmg_a.get())
            m = int(self.cmg_m.get())
            semilla = int(self.cmg_semilla.get())
            iteraciones = int(self.cmg_iteraciones.get())
            self._validar_positivos(a, m, semilla, iteraciones)
            resultados = congruencial_multiplicativo.generar(a, m, semilla, iteraciones)
            self._cmg_limpiar()
            ris = []
            for it, xn, ri in resultados:
                self.cmg_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
                ris.append(ri)
            self._graficar_ris("cmg", ris, "Cong. Multiplicativo")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _cmg_limpiar(self):
        for item in self.cmg_tree.get_children():
            self.cmg_tree.delete(item)
        self._limpiar_graficos("cmg")

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
        graficos_frame = self._crear_graficos(tab, "mt")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

    def _mt_generar(self):
        try:
            semilla = int(self.mt_semilla.get())
            iteraciones = int(self.mt_iteraciones.get())
            self._validar_positivos(semilla, iteraciones)
            resultados = mersenne_twister.generar(semilla, iteraciones)
            self._mt_limpiar()
            ris = []
            for it, xn, ri in resultados:
                self.mt_tree.insert("", "end", values=(it, xn, f"{ri:.6f}"))
                ris.append(ri)
            self._graficar_ris("mt", ris, "Mersenne Twister")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _mt_limpiar(self):
        for item in self.mt_tree.get_children():
            self.mt_tree.delete(item)
        self._limpiar_graficos("mt")

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
        graficos_frame = self._crear_graficos(tab, "lv")
        graficos_frame.pack(fill="both", expand=True, pady=(5, 0))

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
            self._graficar_lv(resultados)
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _lv_limpiar(self):
        for item in self.lv_tree.get_children():
            self.lv_tree.delete(item)
        self._limpiar_graficos("lv")

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


    # ── Ruleta ──

    def _crear_tab_roulette(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Ruleta")

        self.ruleta_engine = Engine()
        self.ruleta_player = Player()
        self.ruleta_stats = Statistics()
        self.ruleta_apuestas = []
        self.ruleta_ficha_actual = 10
        self.ruleta_girando = False
        self.ruleta_ultimo_resultado = None

        panel_izq = ttk.Frame(tab)
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 5))
        panel_der = ttk.Frame(tab)
        panel_der.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self._ruleta_crear_fichas(panel_izq)
        self._ruleta_crear_mesa(panel_izq)
        self._ruleta_crear_acciones(panel_izq)
        self._ruleta_crear_rueda(panel_der)
        self._ruleta_crear_info(panel_der)

    def _ruleta_crear_fichas(self, parent):
        frame = ttk.LabelFrame(parent, text="Fichas", padding=8)
        frame.pack(fill="x", pady=(0, 8))
        self.ruleta_ficha_botones = {}
        valores = [1, 5, 10, 25, 100, 500]
        colores_ficha = {"1": "#95a5a6", "5": "#e74c3c", "10": "#3498db",
                         "25": "#2ecc71", "100": "#2c3e50", "500": "#9b59b6"}
        inner = ttk.Frame(frame)
        inner.pack()
        for v in valores:
            btn = tk.Button(inner, text=str(v), width=4, height=1,
                            bg=colores_ficha[str(v)], fg="white",
                            font=("Arial", 9, "bold"),
                            relief="raised", bd=2,
                            command=lambda val=v: self._ruleta_seleccionar_ficha(val))
            btn.pack(side="left", padx=3)
            self.ruleta_ficha_botones[v] = btn
        self.ruleta_ficha_label = tk.Label(frame, text="Ficha: 10",
                                           font=("Arial", 9), fg="#7c3aed")
        self.ruleta_ficha_label.pack(pady=(4, 0))

    def _ruleta_seleccionar_ficha(self, valor):
        sounds.click()
        self.ruleta_ficha_actual = valor
        self.ruleta_ficha_label.config(text=f"Ficha: {valor}")
        for v, btn in self.ruleta_ficha_botones.items():
            btn.config(relief="sunken" if v == valor else "raised")

    def _ruleta_crear_mesa(self, parent):
        frame = ttk.LabelFrame(parent, text="Mesa de apuestas", padding=5)
        frame.pack(fill="both", expand=True)

        cols_frame = ttk.Frame(frame)
        cols_frame.pack()

        # Cero
        cero_frame = ttk.Frame(cols_frame)
        cero_frame.grid(row=0, column=0, columnspan=13, pady=2)
        btn = tk.Button(cero_frame, text="0", width=4, bg="#27ae60", fg="white",
                        font=("Arial", 10, "bold"), command=lambda: self._ruleta_apostar_numero(0))
        btn.pack()

        # 3 filas de números (estilo ruleta real)
        # Fila 1: 3,6,9,12,15,18,21,24,27,30,33,36
        filas = [
            [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
        ]
        for r, nums in enumerate(filas):
            for c, n in enumerate(nums):
                bg = "#e74c3c" if n in (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36) else "#2c3e50"
                btn = tk.Button(cols_frame, text=str(n), width=3, height=1,
                                bg=bg, fg="white", font=("Arial", 8, "bold"),
                                command=lambda x=n: self._ruleta_apostar_numero(x))
                btn.grid(row=r + 1, column=c + 1, padx=1, pady=1)

        # Botones de columna (2:1)
        col_bg = ["#e67e22", "#e67e22", "#e67e22"]
        for c in range(3):
            btn = tk.Button(cols_frame, text="2:1", width=3, bg=col_bg[c],
                            font=("Arial", 7, "bold"),
                            command=lambda col=c + 1: self._ruleta_apostar_columna(col))
            btn.grid(row=4, column=c * 4 + 2, columnspan=4, sticky="ew", padx=1)

        # Apuestas externas
        ext_frame = ttk.Frame(frame)
        ext_frame.pack(fill="x", pady=4)
        ext_bets = [
            ("1-18", "bajo"), ("PAR", "par"), ("ROJO", "rojo"),
            ("NEGRO", "negro"), ("IMPAR", "impar"), ("19-36", "alto"),
        ]
        for texto, tipo in ext_bets:
            bg = {"rojo": "#e74c3c", "negro": "#2c3e50", "par": "#2980b9",
                  "impar": "#8e44ad", "bajo": "#16a085", "alto": "#d35400"}[tipo]
            btn = tk.Button(ext_frame, text=texto, width=6, bg=bg, fg="white",
                            font=("Arial", 8, "bold"),
                            command=lambda t=tipo: self._ruleta_apostar_externa(t))
            btn.pack(side="left", padx=2)

        # Docenas
        doc_frame = ttk.Frame(frame)
        doc_frame.pack(fill="x", pady=2)
        for i, txt in enumerate(["1ª DOCENA", "2ª DOCENA", "3ª DOCENA"], 1):
            btn = tk.Button(doc_frame, text=txt, width=10, bg="#8e44ad", fg="white",
                            font=("Arial", 8, "bold"),
                            command=lambda d=i: self._ruleta_apostar_docena(d))
            btn.pack(side="left", padx=2)

    def _ruleta_apostar_numero(self, numero):
        if self.ruleta_girando:
            return
        monto = self.ruleta_ficha_actual
        if not self.ruleta_player.puede_apostar(monto):
            messagebox.showinfo("Saldo insuficiente", "No tienes suficiente saldo.")
            return
        sounds.chip()
        from modulos.roulette.bets import StraightUp
        self.ruleta_player.apostar(monto)
        self.ruleta_apuestas.append(StraightUp(monto, numero))
        self._ruleta_actualizar_saldo()

    def _ruleta_apostar_externa(self, tipo):
        if self.ruleta_girando:
            return
        monto = self.ruleta_ficha_actual
        if not self.ruleta_player.puede_apostar(monto):
            messagebox.showinfo("Saldo insuficiente", "No tienes suficiente saldo.")
            return
        sounds.chip()
        from modulos.roulette.bets import Red, Black, Even, Odd, Low, High
        mapa = {"rojo": Red, "negro": Black, "par": Even,
                "impar": Odd, "bajo": Low, "alto": High}
        if tipo in mapa:
            self.ruleta_player.apostar(monto)
            self.ruleta_apuestas.append(mapa[tipo](monto))
            self._ruleta_actualizar_saldo()

    def _ruleta_apostar_docena(self, docena):
        if self.ruleta_girando:
            return
        monto = self.ruleta_ficha_actual
        if not self.ruleta_player.puede_apostar(monto):
            messagebox.showinfo("Saldo insuficiente", "No tienes suficiente saldo.")
            return
        sounds.chip()
        from modulos.roulette.bets import Dozen
        self.ruleta_player.apostar(monto)
        self.ruleta_apuestas.append(Dozen(monto, docena))
        self._ruleta_actualizar_saldo()

    def _ruleta_apostar_columna(self, columna):
        if self.ruleta_girando:
            return
        monto = self.ruleta_ficha_actual
        if not self.ruleta_player.puede_apostar(monto):
            messagebox.showinfo("Saldo insuficiente", "No tienes suficiente saldo.")
            return
        sounds.chip()
        from modulos.roulette.bets import Column
        self.ruleta_player.apostar(monto)
        self.ruleta_apuestas.append(Column(monto, columna))
        self._ruleta_actualizar_saldo()

    def _ruleta_crear_acciones(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=8)
        self.ruleta_girar_btn = ttk.Button(frame, text="GIRAR", command=self._ruleta_girar,
                                            style="Accent.TButton")
        self.ruleta_girar_btn.pack(side="left", padx=3)
        ttk.Button(frame, text="Limpiar", command=self._ruleta_limpiar_mesa).pack(side="left", padx=3)
        ttk.Button(frame, text="Deshacer", command=self._ruleta_deshacer_apuesta).pack(side="left", padx=3)

    def _ruleta_crear_rueda(self, parent):
        frame = ttk.LabelFrame(parent, text="Ruleta", padding=5)
        frame.pack(fill="both", expand=True)

        self.ruleta_canvas = tk.Canvas(frame, width=320, height=320,
                                        bg="#1a1a2e", highlightthickness=0)
        self.ruleta_canvas.pack()
        self._ruleta_dibujar_rueda(0)

    def _ruleta_dibujar_rueda(self, angulo_offset):
        c = self.ruleta_canvas
        c.delete("all")
        cx, cy, R = 160, 160, 140
        angulo_por_segmento = 360 / 37

        c.create_oval(cx - R - 5, cy - R - 5, cx + R + 5, cy + R + 5,
                      outline="#c8a96e", width=3)
        c.create_oval(cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2,
                      outline="#8b7355", width=1)

        for i, num in enumerate(SECUENCIA_RUEDA):
            start = angulo_offset + i * angulo_por_segmento - 90
            color = {"rojo": "#e74c3c", "negro": "#2c3e50", "verde": "#27ae60"}[COLORES[num]]
            c.create_arc(cx - R, cy - R, cx + R, cy + R,
                         start=start, extent=angulo_por_segmento,
                         fill=color, outline="#1a1a2e", width=1)

            mid_angle = (start + angulo_por_segmento / 2) * 3.14159 / 180
            label_r = R * 0.78
            lx = cx + label_r * mid_angle
            ly = cy + label_r * mid_angle
            c.create_text(lx, ly, text=str(num), fill="white",
                          font=("Arial", 7, "bold"))

        c.create_oval(cx - 30, cy - 30, cx + 30, cy + 30,
                      fill="#1a1a2e", outline="#c8a96e", width=2)
        c.create_text(cx, cy, text="R", fill="#c8a96e",
                      font=("Times", 18, "italic"))

        punta_x1, punta_y1 = cx - 8, cy - R - 12
        punta_x2, punta_y2 = cx + 8, cy - R - 12
        punta_x3, punta_y3 = cx, cy - R + 5
        c.create_polygon(punta_x1, punta_y1, punta_x2, punta_y2,
                         punta_x3, punta_y3, fill="#f1c40f", outline="#d4a017")

    def _ruleta_crear_info(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Información", padding=8)
        info_frame.pack(fill="x", pady=(0, 8))

        self.ruleta_saldo_label = tk.Label(info_frame, text=f"Saldo: {self.ruleta_player.saldo}",
                                            font=("Arial", 12, "bold"), fg="#2ecc71")
        self.ruleta_saldo_label.pack(anchor="w")
        info_row = ttk.Frame(info_frame)
        info_row.pack(fill="x")
        self.ruleta_apuestas_label = tk.Label(info_row, text="Apuestas: 0",
                                               font=("Arial", 9))
        self.ruleta_apuestas_label.pack(side="left", padx=(0, 10))
        self.ruleta_total_apostado_label = tk.Label(info_row, text="Total: 0",
                                                     font=("Arial", 9), fg="#f1c40f")
        self.ruleta_total_apostado_label.pack(side="left")
        self.ruleta_ultimo_label = tk.Label(info_frame, text="🔄 Coloca tus apuestas y gira",
                                             font=("Arial", 10, "bold"), wraplength=280)
        self.ruleta_ultimo_label.pack(fill="x", pady=4)
        self.ruleta_ganancia_label = tk.Label(info_frame, text="",
                                               font=("Arial", 9))
        self.ruleta_ganancia_label.pack(anchor="w")

        hist_frame = ttk.LabelFrame(parent, text="Historial", padding=5)
        hist_frame.pack(fill="x", pady=(0, 8))

        self.ruleta_hist_frame = tk.Frame(hist_frame, bg="#1a1a2e")
        self.ruleta_hist_frame.pack(fill="x")

        stat_frame = ttk.LabelFrame(parent, text="Estadísticas", padding=5)
        stat_frame.pack(fill="both", expand=True)

        self.ruleta_stats_text = tk.Text(stat_frame, height=10, width=25,
                                          font=("Consolas", 8), state="disabled")
        self.ruleta_stats_text.pack(fill="both", expand=True)
        self._ruleta_actualizar_stats()

    def _ruleta_actualizar_saldo(self):
        self.ruleta_saldo_label.config(text=f"Saldo: {self.ruleta_player.saldo}")
        self.ruleta_apuestas_label.config(text=f"Apuestas: {len(self.ruleta_apuestas)}")
        total = sum(a.monto for a in self.ruleta_apuestas)
        self.ruleta_total_apostado_label.config(text=f"Total: {total}")

    def _ruleta_girar(self):
        if self.ruleta_girando:
            return
        if not self.ruleta_apuestas:
            messagebox.showinfo("Sin apuestas", "Coloca al menos una apuesta antes de girar.")
            return

        self.ruleta_girando = True
        self.ruleta_girar_btn.config(state="disabled")
        sounds.spin()
        resultado = self.ruleta_engine.spin()
        self.ruleta_ultimo_resultado = resultado

        target_index = SECUENCIA_RUEDA.index(resultado)
        angulo_por_seg = 360 / 37
        target_angle = 360 - target_index * angulo_por_seg - angulo_por_seg / 2
        total_rotacion = 1440 + target_angle

        total_frames = 90
        self._ruleta_animar(0, total_frames, total_rotacion, resultado)

    def _ruleta_animar(self, frame, total_frames, total_rotacion, resultado):
        t = frame / total_frames
        eased = 1 - (1 - t) ** 3
        angulo_actual = total_rotacion * eased
        self._ruleta_dibujar_rueda(angulo_actual)

        if frame < total_frames:
            self.root.after(33, lambda: self._ruleta_animar(frame + 1, total_frames, total_rotacion, resultado))
        else:
            self._ruleta_mostrar_resultado(resultado)

    def _ruleta_mostrar_resultado(self, resultado):
        ganancia_total, detalles = self.ruleta_engine.calcular_pagos(self.ruleta_apuestas, resultado)

        self.ruleta_player.cobrar(ganancia_total)
        self.ruleta_player.registrar_giro(resultado, self.ruleta_apuestas, ganancia_total)
        self.ruleta_player.guardar()
        self.ruleta_stats.registrar(resultado)

        color = COLORES[resultado]
        hex_color = {"rojo": "#e74c3c", "negro": "#2c3e50", "verde": "#27ae60"}[color]
        emoji_color = {"rojo": "🔴", "negro": "⚫", "verde": "🟢"}[color]
        self.ruleta_ultimo_label.config(
            text=f"{emoji_color} {resultado} — {color.upper()}", fg="white",
            bg=hex_color)

        if ganancia_total > 0:
            sounds.win()
            self.ruleta_ganancia_label.config(
                text=f"🎉 GANASTE +{ganancia_total} créditos", fg="#2ecc71", font=("Arial", 10, "bold"))
        else:
            sounds.lose()
            self.ruleta_ganancia_label.config(
                text=f"Sin ganancia esta vez", fg="#e74c3c", font=("Arial", 9))

        self._ruleta_actualizar_saldo()
        self._ruleta_actualizar_historial()
        self._ruleta_actualizar_stats()

        self.ruleta_apuestas = []
        self.ruleta_apuestas_label.config(text="Apuestas: 0")
        self.ruleta_girando = False
        self.ruleta_girar_btn.config(state="normal")

    def _ruleta_actualizar_historial(self):
        for w in self.ruleta_hist_frame.winfo_children():
            w.destroy()
        ultimos = self.ruleta_stats.ultimos(20)
        if not ultimos:
            tk.Label(self.ruleta_hist_frame, text="—", bg="#1a1a2e", fg="#64748b",
                     font=("Arial", 8)).pack()
            return
        for n in reversed(ultimos):
            hex_c = {"rojo": "#e74c3c", "negro": "#2c3e50", "verde": "#27ae60"}[COLORES[n]]
            lbl = tk.Label(self.ruleta_hist_frame, text=str(n), bg=hex_c, fg="white",
                            font=("Arial", 7, "bold"), width=3, height=1)
            lbl.pack(side="left", padx=1, pady=1)

    def _ruleta_actualizar_stats(self):
        self.ruleta_stats_text.config(state="normal")
        self.ruleta_stats_text.delete("1.0", "end")
        s = self.ruleta_stats
        stats = s.to_dict()
        texto = f"Total giros: {stats['total']}\n"
        texto += f"Rojo: {stats['pct_rojo']}%  |  "
        texto += f"Negro: {stats['pct_negro']}%\n"
        texto += f"Verde: {stats['pct_verde']}%  |  "
        texto += f"Par: {stats['pct_par']}%\n"
        texto += f"Impar: {stats['pct_impar']}%  |  "
        texto += f"Bajo: {stats['pct_bajo']}%\n"
        texto += f"Alto: {stats['pct_alto']}%\n"
        texto += f"Racha rojo: {stats['racha_rojo']}  |  "
        texto += f"Racha negro: {stats['racha_negro']}\n"
        if stats['calientes']:
            texto += f"Calientes: {', '.join(str(x) for x in stats['calientes'])}\n"
        if stats['frios']:
            texto += f"Fríos: {', '.join(str(x) for x in stats['frios'])}\n"
        self.ruleta_stats_text.insert("1.0", texto)
        self.ruleta_stats_text.config(state="disabled")

    def _ruleta_limpiar_mesa(self):
        if self.ruleta_girando:
            return
        total_devuelto = sum(a.monto for a in self.ruleta_apuestas)
        self.ruleta_player.saldo += total_devuelto
        self.ruleta_apuestas = []
        self._ruleta_actualizar_saldo()
        self.ruleta_apuestas_label.config(text="Apuestas: 0")

    def _ruleta_deshacer_apuesta(self):
        if self.ruleta_girando or not self.ruleta_apuestas:
            return
        ultima = self.ruleta_apuestas.pop()
        self.ruleta_player.saldo += ultima.monto
        self._ruleta_actualizar_saldo()
        self.ruleta_apuestas_label.config(text=f"Apuestas: {len(self.ruleta_apuestas)}")

    # ── Simulación Covid ──

    COVID_CMAP = ListedColormap(["#2563eb", "#b91c1c", "#16a34a", "#0f172a", "#e2e8f0"])
    COVID_LABELS = ["Sano", "Infectado", "Recuperado", "Fallecido", "Vacío"]
    COVID_COLORS_HEX = ["#2563eb", "#b91c1c", "#16a34a", "#0f172a", "#e2e8f0"]

    def _crear_tab_covid(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Simulación Covid")

        panel_izq = ttk.Frame(tab)
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 5))
        panel_der = ttk.Frame(tab)
        panel_der.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # ── Parámetros ──
        cfg = ttk.LabelFrame(panel_der, text="Parámetros", padding=10)
        cfg.pack(fill="x", pady=(0, 10))
        self.cv_filas = self._crear_input(cfg, "Filas:", 0, "50")
        self.cv_columnas = self._crear_input(cfg, "Columnas:", 1, "50")
        self.cv_densidad = self._crear_input(cfg, "Densidad población:", 2, "0.85")
        self.cv_infectados = self._crear_input(cfg, "Infectados iniciales:", 3, "5")
        self.cv_contagio = self._crear_input(cfg, "Prob. contagio:", 4, "0.30")
        self.cv_recuperacion = self._crear_input(cfg, "Días recuperación:", 5, "14")
        self.cv_muerte = self._crear_input(cfg, "Prob. muerte:", 6, "0.02")
        self.cv_iteraciones = self._crear_input(cfg, "Iteraciones:", 7, "100")
        self.cv_velocidad = self._crear_input(cfg, "Velocidad (ms):", 8, "100")

        # ── Botones ──
        btn_frame = ttk.Frame(panel_der)
        btn_frame.pack(fill="x", pady=5)
        self.cv_btn_iniciar = ttk.Button(btn_frame, text="▶ Iniciar", command=self._covid_iniciar)
        self.cv_btn_iniciar.pack(side="left", padx=3)
        self.cv_btn_pausa = ttk.Button(btn_frame, text="⏸ Pausar", command=self._covid_pausar, state="disabled")
        self.cv_btn_pausa.pack(side="left", padx=3)
        self.cv_btn_paso = ttk.Button(btn_frame, text="⏭ Paso", command=self._covid_paso, state="disabled")
        self.cv_btn_paso.pack(side="left", padx=3)
        ttk.Button(btn_frame, text="↺ Reiniciar", command=self._covid_reiniciar).pack(side="left", padx=3)

        # ── Barra de progreso ──
        self.cv_progress_frame = ttk.Frame(panel_der)
        self.cv_progress_frame.pack(fill="x", pady=(0, 8))
        self.cv_progress_label = ttk.Label(self.cv_progress_frame, text="Progreso: 0%", font=("", 8))
        self.cv_progress_label.pack(anchor="w")
        self.cv_progress_bar = ttk.Progressbar(self.cv_progress_frame, length=200, mode="determinate", value=0)
        self.cv_progress_bar.pack(fill="x")

        # ── Contadores con porcentajes ──
        info = ttk.LabelFrame(panel_der, text="Población", padding=10)
        info.pack(fill="x", pady=(0, 10))
        self.cv_label_iteracion = ttk.Label(info, text="Iteración: 0 / 0", font=("", 10, "bold"))
        self.cv_label_iteracion.pack(anchor="w")

        counts_frame = ttk.Frame(info)
        counts_frame.pack(fill="x")
        self.cv_labels_pob = {}
        estados = [
            ("Sanos", "🟦", "#60a5fa", covid_sim.SANO),
            ("Infectados", "🟥", "#ef4444", covid_sim.INFECTADO),
            ("Recuperados", "🟩", "#22c55e", covid_sim.RECUPERADO),
            ("Fallecidos", "⬛", "#1e293b", covid_sim.FALLECIDO),
            ("Vacío", "⬜", "#94a3b8", covid_sim.VACIO),
        ]
        for i, (nombre, icono, color, _) in enumerate(estados):
            lbl = ttk.Label(counts_frame, text=f"{icono} {nombre}: 0 (0%)", foreground=color, font=("", 9))
            lbl.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 15), pady=1)
            self.cv_labels_pob[nombre] = lbl

        # ─── Estadísticas resumen ───
        stats_frame = ttk.LabelFrame(panel_der, text="Resumen", padding=8)
        stats_frame.pack(fill="x", pady=(0, 5))
        self.cv_label_max_infectados = ttk.Label(stats_frame, text="Peak infección: —", font=("", 8))
        self.cv_label_max_infectados.pack(anchor="w")
        self.cv_label_total_recup = ttk.Label(stats_frame, text="Total recuperados: —", font=("", 8))
        self.cv_label_total_recup.pack(anchor="w")
        self.cv_label_tasa_mortalidad = ttk.Label(stats_frame, text="Tasa mortalidad: —", font=("", 8))
        self.cv_label_tasa_mortalidad.pack(anchor="w")

        self.cv_sim = None
        self.cv_corriendo = False
        self.cv_pausado = False
        self.cv_after_id = None
        self.cv_max_infectados = 0

        # ── Gráfico grid ──
        grid_frame = ttk.LabelFrame(panel_izq, text="Simulación", padding=5)
        grid_frame.pack(fill="both", expand=True)
        self.cv_fig, (self.cv_ax_grid, self.cv_ax_evol) = plt.subplots(1, 2, figsize=(14, 7),
                                                                         gridspec_kw={"width_ratios": [1.4, 1]})
        self.cv_fig.patch.set_facecolor("#f8fafc")
        self.cv_canvas = FigureCanvasTkAgg(self.cv_fig, master=grid_frame)
        self.cv_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.cv_im = None

    def _covid_iniciar(self):
        try:
            filas = int(self.cv_filas.get())
            columnas = int(self.cv_columnas.get())
            densidad = float(self.cv_densidad.get())
            infectados = int(self.cv_infectados.get())
            contagio = float(self.cv_contagio.get())
            recuperacion = int(self.cv_recuperacion.get())
            muerte = float(self.cv_muerte.get())
            iteraciones = int(self.cv_iteraciones.get())
            if any(v <= 0 for v in [filas, columnas, infectados, recuperacion, iteraciones]):
                raise ValueError("Filas, columnas, infectados, recuperación e iteraciones deben ser > 0")
            if not (0 < densidad <= 1):
                raise ValueError("Densidad debe estar entre 0 y 1")
            if not (0 <= contagio <= 1):
                raise ValueError("Probabilidad de contagio debe estar entre 0 y 1")
            if not (0 <= muerte <= 1):
                raise ValueError("Probabilidad de muerte debe estar entre 0 y 1")
            if infectados > filas * columnas * densidad:
                raise ValueError("Demasiados infectados iniciales para la población")

            self.cv_sim = covid_sim.CovidSim(
                filas=filas, columnas=columnas,
                densidad_poblacion=densidad,
                infectados_iniciales=infectados,
                probabilidad_contagio=contagio,
                dias_recuperacion=recuperacion,
                probabilidad_muerte=muerte,
            )
            self.cv_iteraciones_total = iteraciones
            self.cv_max_infectados = 0
            self.cv_corriendo = True
            self.cv_pausado = False
            self.cv_btn_iniciar.config(state="disabled")
            self.cv_btn_pausa.config(state="normal", text="⏸ Pausar")
            self.cv_btn_paso.config(state="normal")
            self.cv_progress_bar.config(value=0, maximum=iteraciones)
            self.cv_ax_evol.clear()
            self._covid_dibujar()
            self._covid_programar_paso()
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))

    def _covid_pausar(self):
        if self.cv_pausado:
            self.cv_pausado = False
            self.cv_btn_pausa.config(text="⏸ Pausar")
            self._covid_programar_paso()
        else:
            self.cv_pausado = True
            self.cv_btn_pausa.config(text="▶ Reanudar")
            if self.cv_after_id:
                self.root.after_cancel(self.cv_after_id)
                self.cv_after_id = None

    def _covid_paso(self):
        if self.cv_sim is None:
            return
        self.cv_sim.step()
        self._covid_dibujar()
        if self.cv_sim.iteracion >= self.cv_iteraciones_total:
            self._covid_detener()

    def _covid_programar_paso(self):
        if not self.cv_corriendo or self.cv_pausado or self.cv_sim is None:
            return
        if self.cv_sim.iteracion >= self.cv_iteraciones_total:
            self._covid_detener()
            return
        vel = max(10, int(self.cv_velocidad.get()))
        self.cv_after_id = self.root.after(vel, self._covid_paso)

    def _covid_dibujar(self):
        if self.cv_sim is None:
            return
        estado = self.cv_sim.obtener_estado()
        conteo = estado["conteo"]
        total_celdas = self.cv_sim.filas * self.cv_sim.columnas
        poblacion_total = total_celdas - conteo[covid_sim.VACIO]

        def pct(v):
            return round(v / poblacion_total * 100, 1) if poblacion_total > 0 else 0

        # Actualizar contadores con porcentajes
        self.cv_label_iteracion.config(text=f"Iteración: {estado['iteracion']} / {self.cv_iteraciones_total}")
        pob_map = {
            "Sanos": conteo[covid_sim.SANO],
            "Infectados": conteo[covid_sim.INFECTADO],
            "Recuperados": conteo[covid_sim.RECUPERADO],
            "Fallecidos": conteo[covid_sim.FALLECIDO],
            "Vacío": conteo[covid_sim.VACIO],
        }
        for nombre, lbl in self.cv_labels_pob.items():
            val = pob_map[nombre]
            pp = pct(val) if nombre != "Vacío" else round(val / total_celdas * 100, 1)
            lbl.config(text=f"{'🟦🟥🟩⬛⬜'[['Sanos','Infectados','Recuperados','Fallecidos','Vacío'].index(nombre)]} {nombre}: {val} ({pp}%)")

        # Resumen
        if conteo[covid_sim.INFECTADO] > self.cv_max_infectados:
            self.cv_max_infectados = conteo[covid_sim.INFECTADO]
        total_fallecidos = conteo[covid_sim.FALLECIDO]
        total_recuperados = conteo[covid_sim.RECUPERADO]
        total_fin = total_fallecidos + total_recuperados
        tasa_mortalidad = round(total_fallecidos / total_fin * 100, 1) if total_fin > 0 else 0
        self.cv_label_max_infectados.config(text=f"Peak infección: {self.cv_max_infectados} ({pct(self.cv_max_infectados)}%)")
        self.cv_label_total_recup.config(text=f"Recuperados: {total_recuperados}  |  Fallecidos: {total_fallecidos}")
        self.cv_label_tasa_mortalidad.config(text=f"Tasa mortalidad: {tasa_mortalidad}%")

        # Barra de progreso
        pct_progress = estado['iteracion'] / max(self.cv_iteraciones_total, 1) * 100
        self.cv_progress_bar.config(value=estado['iteracion'])
        self.cv_progress_label.config(text=f"Progreso: {min(int(pct_progress), 100)}%")

        # ── Grid ──
        self.cv_ax_grid.clear()
        self.cv_ax_grid.imshow(estado["grid"], cmap=self.COVID_CMAP, vmin=0, vmax=4, interpolation="nearest")

        # Leyenda de colores en el grid
        legend_patches = []
        for i in range(5):
            from matplotlib.patches import Patch
            legend_patches.append(Patch(color=self.COVID_COLORS_HEX[i], label=self.COVID_LABELS[i]))
        self.cv_ax_grid.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.06),
                               ncol=5, fontsize=6.5, framealpha=0.9, handlelength=1)

        total_pob = poblacion_total
        self.cv_ax_grid.set_title(f"Iteración {estado['iteracion']} — Población: {total_pob}", fontsize=10, fontweight="bold")
        self.cv_ax_grid.axis("off")

        # ── Evolución ──
        self.cv_ax_evol.clear()
        self.cv_ax_evol.set_facecolor("#f8fafc")
        hist = estado["historial"]
        iters = [h["iteracion"] for h in hist]

        s = [h[covid_sim.SANO] for h in hist]
        i_vals = [h[covid_sim.INFECTADO] for h in hist]
        r = [h[covid_sim.RECUPERADO] for h in hist]
        d = [h[covid_sim.FALLECIDO] for h in hist]

        self.cv_ax_evol.stackplot(iters, s, i_vals, r, d,
                                   colors=["#60a5fa", "#ef4444", "#22c55e", "#1e293b"],
                                   alpha=0.7, labels=["Sanos", "Infectados", "Recuperados", "Fallecidos"])
        self.cv_ax_evol.set_title("Evolución de la población", fontsize=10, fontweight="bold")
        self.cv_ax_evol.set_xlabel("Iteración", fontsize=8)
        self.cv_ax_evol.set_ylabel("Personas", fontsize=8)
        self.cv_ax_evol.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
        self.cv_ax_evol.set_xlim(0, max(iters) + 1)
        self.cv_ax_evol.set_ylim(0, total_celdas * 1.05)
        self.cv_ax_evol.tick_params(labelsize=7)
        self.cv_ax_evol.grid(True, alpha=0.15)

        # Línea punteada para peak de infección
        if self.cv_max_infectados > 0:
            peak_iter = next((h["iteracion"] for h in reversed(hist)
                             if h[covid_sim.INFECTADO] == self.cv_max_infectados), None)
            if peak_iter is not None:
                self.cv_ax_evol.axvline(x=peak_iter, color="#ef4444", linestyle="--", linewidth=0.8, alpha=0.5)
                self.cv_ax_evol.annotate(f"Peak: {self.cv_max_infectados}",
                                         xy=(peak_iter, self.cv_max_infectados),
                                         xytext=(peak_iter + max(iters) * 0.02, self.cv_max_infectados * 1.05),
                                         fontsize=6.5, color="#ef4444", fontweight="bold",
                                         arrowprops=dict(arrowstyle="->", color="#ef4444", lw=0.8))

        self.cv_fig.tight_layout()
        self.cv_canvas.draw()

    def _covid_reiniciar(self):
        if self.cv_after_id:
            self.root.after_cancel(self.cv_after_id)
            self.cv_after_id = None
        self.cv_sim = None
        self.cv_corriendo = False
        self.cv_pausado = False
        self.cv_max_infectados = 0
        self.cv_btn_iniciar.config(state="normal")
        self.cv_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.cv_btn_paso.config(state="disabled")
        self.cv_progress_bar.config(value=0)
        self.cv_progress_label.config(text="Progreso: 0%")
        self.cv_label_iteracion.config(text="Iteración: 0 / 0")
        for nombre, lbl in self.cv_labels_pob.items():
            lbl.config(text=f"{'🟦🟥🟩⬛⬜'[['Sanos','Infectados','Recuperados','Fallecidos','Vacío'].index(nombre)]} {nombre}: 0 (0%)")
        self.cv_label_max_infectados.config(text="Peak infección: —")
        self.cv_label_total_recup.config(text="Total recuperados: —")
        self.cv_label_tasa_mortalidad.config(text="Tasa mortalidad: —")
        self.cv_ax_grid.clear()
        self.cv_ax_grid.set_title("Presiona ▶ Iniciar", fontweight="bold")
        self.cv_ax_evol.clear()
        self.cv_canvas.draw()

    def _covid_detener(self):
        self.cv_corriendo = False
        self.cv_pausado = False
        self.cv_btn_iniciar.config(state="normal")
        self.cv_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.cv_btn_paso.config(state="disabled")
        if self.cv_after_id:
            self.root.after_cancel(self.cv_after_id)
            self.cv_after_id = None

    # ── Dólares (modelo económico Lotka-Volterra) ──

    def _crear_tab_dolares(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Dólares")

        panel_izq = ttk.Frame(tab)
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 5))
        panel_der = ttk.Frame(tab)
        panel_der.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # ── Parámetros ──
        cfg = ttk.LabelFrame(panel_der, text="Parámetros del modelo", padding=10)
        cfg.pack(fill="x", pady=(0, 10))
        self.dl_alpha = self._crear_input(cfg, "α — entrada de dólares:", 0, "0.25")
        self.dl_beta = self._crear_input(cfg, "β — presión sobre dólares:", 1, "0.08")
        self.dl_delta = self._crear_input(cfg, "δ — crecimiento de presión:", 2, "0.04")
        self.dl_gamma = self._crear_input(cfg, "γ — estabilización:", 3, "0.30")
        self.dl_x0 = self._crear_input(cfg, "Disponibilidad inicial ($):", 4, "10")
        self.dl_y0 = self._crear_input(cfg, "Presión inicial:", 5, "4")
        self.dl_tiempo = self._crear_input(cfg, "Tiempo a simular:", 6, "60")

        # ── Botones ──
        btn_frame = ttk.Frame(panel_der)
        btn_frame.pack(fill="x", pady=5)
        self.dl_btn_iniciar = ttk.Button(btn_frame, text="▶ Iniciar", command=self._dolares_iniciar)
        self.dl_btn_iniciar.pack(side="left", padx=3)
        self.dl_btn_pausa = ttk.Button(btn_frame, text="⏸ Pausar", command=self._dolares_pausar, state="disabled")
        self.dl_btn_pausa.pack(side="left", padx=3)
        self.dl_btn_paso = ttk.Button(btn_frame, text="⏭ Paso", command=self._dolares_paso, state="disabled")
        self.dl_btn_paso.pack(side="left", padx=3)
        ttk.Button(btn_frame, text="↺ Reiniciar", command=self._dolares_reiniciar).pack(side="left", padx=3)

        # ── Info en vivo ──
        info = ttk.LabelFrame(panel_der, text="Información", padding=8)
        info.pack(fill="x", pady=(0, 5))
        self.dl_label_iteracion = ttk.Label(info, text="Paso: 0 / 0", font=("", 9, "bold"))
        self.dl_label_iteracion.pack(anchor="w")
        self.dl_label_dolares = ttk.Label(info, text="💵 Dólares: —", font=("", 9), foreground="#d97706")
        self.dl_label_dolares.pack(anchor="w")
        self.dl_label_presion = ttk.Label(info, text="⚠ Presión: —", font=("", 9), foreground="#dc2626")
        self.dl_label_presion.pack(anchor="w")
        self.dl_label_equilibrio = ttk.Label(info, text="⚖ Equilibrio: —", font=("", 8), foreground="#059669")
        self.dl_label_equilibrio.pack(anchor="w")

        # ── Variables de estado ──
        self.dl_resultados = []
        self.dl_corriendo = False
        self.dl_pausado = False
        self.dl_after_id = None
        self.dl_paso_actual = 0
        self.dl_equilibrio = None

        # ── Gráficos ──
        graf_frame = ttk.LabelFrame(panel_izq, text="Simulación económica", padding=5)
        graf_frame.pack(fill="both", expand=True)
        self.dl_fig, (self.dl_ax_evo, self.dl_ax_fase) = plt.subplots(1, 2, figsize=(12, 5.5))
        self.dl_fig.patch.set_facecolor("#fffbeb")
        self.dl_canvas = FigureCanvasTkAgg(self.dl_fig, master=graf_frame)
        self.dl_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.dl_linea_evo_dolares = None
        self.dl_linea_evo_presion = None
        self.dl_punto_evo = None
        self.dl_linea_fase = None
        self.dl_punto_fase = None

    def _dolares_iniciar(self):
        alpha = float(self.dl_alpha.get())
        beta = float(self.dl_beta.get())
        delta = float(self.dl_delta.get())
        gamma = float(self.dl_gamma.get())
        x0 = int(self.dl_x0.get())
        y0 = int(self.dl_y0.get())
        tiempo = int(self.dl_tiempo.get())

        if any(v <= 0 for v in [alpha, beta, delta, gamma, x0, y0, tiempo]):
            messagebox.showerror("Error", "Todos los valores deben ser positivos")
            return

        res = dolares.simular(alpha, beta, delta, gamma, x0, y0, tiempo)
        self.dl_resultados = res["resultados"]
        self.dl_equilibrio = res["equilibrio"]
        self.dl_paso_actual = 0
        self.dl_corriendo = True
        self.dl_pausado = False

        self.dl_label_equilibrio.config(
            text=f"⚖ Equilibrio: $={res['equilibrio']['dolares']}, P={res['equilibrio']['presion']}"
        )

        self.dl_btn_iniciar.config(state="disabled")
        self.dl_btn_pausa.config(state="normal", text="⏸ Pausar")
        self.dl_btn_paso.config(state="normal")

        self._dolares_dibujar()
        self._dolares_programar_paso()

    def _dolares_pausar(self):
        if self.dl_pausado:
            self.dl_pausado = False
            self.dl_btn_pausa.config(text="⏸ Pausar")
            self._dolares_programar_paso()
        else:
            self.dl_pausado = True
            self.dl_btn_pausa.config(text="▶ Reanudar")
            if self.dl_after_id:
                self.root.after_cancel(self.dl_after_id)
                self.dl_after_id = None

    def _dolares_paso(self):
        if not self.dl_corriendo or not self.dl_resultados:
            return
        self.dl_paso_actual += 1
        if self.dl_paso_actual >= len(self.dl_resultados):
            self.dl_paso_actual = len(self.dl_resultados) - 1
            self._dolares_detener()
            return
        self._dolares_dibujar()

    def _dolares_programar_paso(self):
        if not self.dl_corriendo or self.dl_pausado or not self.dl_resultados:
            return
        if self.dl_paso_actual >= len(self.dl_resultados) - 1:
            self._dolares_detener()
            return
        self.dl_after_id = self.root.after(50, self._dolares_paso)

    def _dolares_dibujar(self):
        if not self.dl_resultados:
            return
        datos = self.dl_resultados[:self.dl_paso_actual + 1]
        total = len(self.dl_resultados)

        t = [d["t"] for d in datos]
        dol = [d["dolares"] for d in datos]
        pres = [d["presion"] for d in datos]

        t_full = [d["t"] for d in self.dl_resultados]
        dol_full = [d["dolares"] for d in self.dl_resultados]
        pres_full = [d["presion"] for d in self.dl_resultados]

        actual = self.dl_resultados[self.dl_paso_actual]

        self.dl_label_iteracion.config(text=f"Paso: {self.dl_paso_actual} / {total}")
        self.dl_label_dolares.config(text=f"💵 Dólares: {actual['dolares']:.2f}")
        self.dl_label_presion.config(text=f"⚠ Presión: {actual['presion']:.2f}")

        # Gráfico de evolución temporal
        self.dl_ax_evo.clear()
        self.dl_ax_evo.set_facecolor("#fffbeb")
        self.dl_ax_evo.plot(t_full, dol_full, color="#d97706", linewidth=1.5, alpha=0.5)
        self.dl_ax_evo.plot(t_full, pres_full, color="#dc2626", linewidth=1.5, alpha=0.5)
        self.dl_ax_evo.plot(t, dol, color="#d97706", linewidth=2.5, label="Dólares (disponibilidad)")
        self.dl_ax_evo.plot(t, pres, color="#dc2626", linewidth=2.5, label="Presión cambiaria")
        if self.dl_equilibrio:
            self.dl_ax_evo.axhline(y=self.dl_equilibrio["dolares"], color="#10b981",
                                    linestyle="--", linewidth=1, alpha=0.7, label=f"Eq. dólares={self.dl_equilibrio['dolares']}")
        self.dl_ax_evo.scatter([actual["t"]], [actual["dolares"]], color="#d97706", s=60, zorder=5, edgecolors="black")
        self.dl_ax_evo.scatter([actual["t"]], [actual["presion"]], color="#dc2626", s=60, zorder=5, edgecolors="black")
        self.dl_ax_evo.set_title("Evolución temporal", fontweight="bold")
        self.dl_ax_evo.set_xlabel("Tiempo")
        self.dl_ax_evo.set_ylabel("Valor")
        self.dl_ax_evo.legend(fontsize=7, loc="best")
        self.dl_ax_evo.grid(True, alpha=0.15)

        # Espacio de fases
        self.dl_ax_fase.clear()
        self.dl_ax_fase.set_face_color("#fffbeb") if hasattr(self.dl_ax_fase, 'set_face_color') else None
        self.dl_ax_fase.set_facecolor("#fffbeb")
        self.dl_ax_fase.plot(dol_full, pres_full, color="#7c3aed", linewidth=1.2, alpha=0.5)
        self.dl_ax_fase.plot(dol, pres, color="#7c3aed", linewidth=2.5)
        if self.dl_equilibrio:
            self.dl_ax_fase.scatter([self.dl_equilibrio["dolares"]], [self.dl_equilibrio["presion"]],
                                     color="#10b981", s=120, marker="*", zorder=5,
                                     label=f"Equilibrio\n($={self.dl_equilibrio['dolares']}, P={self.dl_equilibrio['presion']})")
        self.dl_ax_fase.scatter([actual["dolares"]], [actual["presion"]],
                                color="#ef4444", s=80, zorder=5, edgecolors="black", label="Actual")
        self.dl_ax_fase.set_title("Espacio de fases", fontweight="bold")
        self.dl_ax_fase.set_xlabel("Dólares (disponibilidad)")
        self.dl_ax_fase.set_ylabel("Presión cambiaria")
        self.dl_ax_fase.legend(fontsize=7, loc="best")
        self.dl_ax_fase.grid(True, alpha=0.15)

        self.dl_fig.tight_layout()
        self.dl_canvas.draw()

    def _dolares_reiniciar(self):
        if self.dl_after_id:
            self.root.after_cancel(self.dl_after_id)
            self.dl_after_id = None
        self.dl_resultados = []
        self.dl_corriendo = False
        self.dl_pausado = False
        self.dl_paso_actual = 0
        self.dl_equilibrio = None
        self.dl_btn_iniciar.config(state="normal")
        self.dl_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.dl_btn_paso.config(state="disabled")
        self.dl_label_iteracion.config(text="Paso: 0 / 0")
        self.dl_label_dolares.config(text="💵 Dólares: —")
        self.dl_label_presion.config(text="⚠ Presión: —")
        self.dl_label_equilibrio.config(text="⚖ Equilibrio: —")
        self.dl_ax_evo.clear()
        self.dl_ax_fase.clear()
        self.dl_ax_evo.set_title("Presiona ▶ Iniciar", fontweight="bold")
        self.dl_fig.tight_layout()
        self.dl_canvas.draw()

    def _dolares_detener(self):
        self.dl_corriendo = False
        self.dl_pausado = False
        self.dl_btn_iniciar.config(state="normal")
        self.dl_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.dl_btn_paso.config(state="disabled")
        if self.dl_after_id:
            self.root.after_cancel(self.dl_after_id)
            self.dl_after_id = None

    # ── Quinua (planta procesadora Lotka-Volterra) ──

    def _crear_tab_quinua(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Quinua")

        panel_izq = ttk.Frame(tab)
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 5))
        panel_der = ttk.Frame(tab)
        panel_der.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # ── Parámetros ──
        cfg = ttk.LabelFrame(panel_der, text="Parámetros de la planta", padding=10)
        cfg.pack(fill="x", pady=(0, 10))
        self.qn_alpha = self._crear_input(cfg, "α — tasa de llegada de quinua:", 0, "0.5")
        self.qn_beta = self._crear_input(cfg, "β — consumo por procesamiento:", 1, "0.02")
        self.qn_delta = self._crear_input(cfg, "δ — conversión stock→producción:", 2, "0.01")
        self.qn_gamma = self._crear_input(cfg, "γ — reducción (mantenimiento/fallas):", 3, "0.3")
        self.qn_x0 = self._crear_input(cfg, "Stock inicial de quinua (kg):", 4, "100")
        self.qn_y0 = self._crear_input(cfg, "Procesamiento inicial (kg/día):", 5, "30")
        self.qn_tiempo = self._crear_input(cfg, "Tiempo a simular (días):", 6, "100")

        # ── Botones ──
        btn_frame = ttk.Frame(panel_der)
        btn_frame.pack(fill="x", pady=5)
        self.qn_btn_iniciar = ttk.Button(btn_frame, text="▶ Iniciar", command=self._quinua_iniciar)
        self.qn_btn_iniciar.pack(side="left", padx=3)
        self.qn_btn_pausa = ttk.Button(btn_frame, text="⏸ Pausar", command=self._quinua_pausar, state="disabled")
        self.qn_btn_pausa.pack(side="left", padx=3)
        self.qn_btn_paso = ttk.Button(btn_frame, text="⏭ Paso", command=self._quinua_paso, state="disabled")
        self.qn_btn_paso.pack(side="left", padx=3)
        ttk.Button(btn_frame, text="↺ Reiniciar", command=self._quinua_reiniciar).pack(side="left", padx=3)

        # ── Info en vivo ──
        info = ttk.LabelFrame(panel_der, text="Información", padding=8)
        info.pack(fill="x", pady=(0, 5))
        self.qn_label_iteracion = ttk.Label(info, text="Paso: 0 / 0", font=("", 9, "bold"))
        self.qn_label_iteracion.pack(anchor="w")
        self.qn_label_stock = ttk.Label(info, text="🌾 Stock: — kg", font=("", 9), foreground="#16a34a")
        self.qn_label_stock.pack(anchor="w")
        self.qn_label_proceso = ttk.Label(info, text="🏭 Procesamiento: — kg/día", font=("", 9), foreground="#2563eb")
        self.qn_label_proceso.pack(anchor="w")
        self.qn_label_equilibrio = ttk.Label(info, text="⚖ Equilibrio: —", font=("", 8), foreground="#7c3aed")
        self.qn_label_equilibrio.pack(anchor="w")

        # ── Variables de estado ──
        self.qn_resultados = []
        self.qn_corriendo = False
        self.qn_pausado = False
        self.qn_after_id = None
        self.qn_paso_actual = 0
        self.qn_equilibrio = None

        # ── Tabla de resultados ──
        table_frame = ttk.LabelFrame(panel_izq, text="Resultados numéricos", padding=5)
        table_frame.pack(fill="both", expand=True, pady=(0, 5))
        self.qn_tree = self._crear_tabla(
            table_frame,
            columns=("t", "stock", "procesamiento"),
            col_widths=(80, 120, 120),
        )

        # ── Gráficos ──
        graf_frame = ttk.LabelFrame(panel_izq, text="Simulación de la planta", padding=5)
        graf_frame.pack(fill="both", expand=True)
        self.qn_fig, (self.qn_ax_evo, self.qn_ax_fase) = plt.subplots(1, 2, figsize=(12, 5.5))
        self.qn_fig.patch.set_facecolor("#f0fdf4")
        self.qn_canvas = FigureCanvasTkAgg(self.qn_fig, master=graf_frame)
        self.qn_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _qn_limpiar_tabla(self):
        for item in self.qn_tree.get_children():
            self.qn_tree.delete(item)

    def _quinua_iniciar(self):
        alpha = float(self.qn_alpha.get())
        beta = float(self.qn_beta.get())
        delta = float(self.qn_delta.get())
        gamma = float(self.qn_gamma.get())
        x0 = int(self.qn_x0.get())
        y0 = int(self.qn_y0.get())
        tiempo = int(self.qn_tiempo.get())

        if any(v <= 0 for v in [alpha, beta, delta, gamma, x0, y0, tiempo]):
            messagebox.showerror("Error", "Todos los valores deben ser positivos")
            return

        res = quinua.simular(alpha, beta, delta, gamma, x0, y0, tiempo)
        self.qn_resultados = res["resultados"]
        self.qn_equilibrio = res["equilibrio"]
        self.qn_paso_actual = 0
        self.qn_corriendo = True
        self.qn_pausado = False

        # Poblar tabla (cada ~50 filas)
        self._qn_limpiar_tabla()
        total = len(self.qn_resultados)
        paso = max(1, total // 50)
        for i, d in enumerate(self.qn_resultados):
            if i % paso == 0 or i == total - 1:
                self.qn_tree.insert("", "end", values=(d["t"], d["stock"], d["procesamiento"]))

        self.qn_label_equilibrio.config(
            text=f"⚖ Equilibrio: stock={res['equilibrio']['stock']} kg, proc.={res['equilibrio']['procesamiento']} kg/día"
        )

        self.qn_btn_iniciar.config(state="disabled")
        self.qn_btn_pausa.config(state="normal", text="⏸ Pausar")
        self.qn_btn_paso.config(state="normal")

        self._quinua_dibujar()
        self._quinua_programar_paso()

    def _quinua_pausar(self):
        if self.qn_pausado:
            self.qn_pausado = False
            self.qn_btn_pausa.config(text="⏸ Pausar")
            self._quinua_programar_paso()
        else:
            self.qn_pausado = True
            self.qn_btn_pausa.config(text="▶ Reanudar")
            if self.qn_after_id:
                self.root.after_cancel(self.qn_after_id)
                self.qn_after_id = None

    def _quinua_paso(self):
        if not self.qn_corriendo or not self.qn_resultados:
            return
        self.qn_paso_actual += 1
        if self.qn_paso_actual >= len(self.qn_resultados):
            self.qn_paso_actual = len(self.qn_resultados) - 1
            self._quinua_detener()
            return
        self._quinua_dibujar()

    def _quinua_programar_paso(self):
        if not self.qn_corriendo or self.qn_pausado or not self.qn_resultados:
            return
        if self.qn_paso_actual >= len(self.qn_resultados) - 1:
            self._quinua_detener()
            return
        self.qn_after_id = self.root.after(50, self._quinua_paso)

    def _quinua_dibujar(self):
        if not self.qn_resultados:
            return
        datos = self.qn_resultados[:self.qn_paso_actual + 1]
        total = len(self.qn_resultados)

        t = [d["t"] for d in datos]
        stock = [d["stock"] for d in datos]
        proc = [d["procesamiento"] for d in datos]

        t_full = [d["t"] for d in self.qn_resultados]
        stock_full = [d["stock"] for d in self.qn_resultados]
        proc_full = [d["procesamiento"] for d in self.qn_resultados]

        actual = self.qn_resultados[self.qn_paso_actual]

        self.qn_label_iteracion.config(text=f"Paso: {self.qn_paso_actual} / {total}")
        self.qn_label_stock.config(text=f"🌾 Stock: {actual['stock']:.0f} kg")
        self.qn_label_proceso.config(text=f"🏭 Procesamiento: {actual['procesamiento']:.0f} kg/día")

        # Evolución temporal
        self.qn_ax_evo.clear()
        self.qn_ax_evo.set_facecolor("#f0fdf4")
        self.qn_ax_evo.plot(t_full, stock_full, color="#16a34a", linewidth=1.5, alpha=0.5)
        self.qn_ax_evo.plot(t_full, proc_full, color="#2563eb", linewidth=1.5, alpha=0.5)
        self.qn_ax_evo.plot(t, stock, color="#16a34a", linewidth=2.5, label="Stock de quinua (kg)")
        self.qn_ax_evo.plot(t, proc, color="#2563eb", linewidth=2.5, label="Procesamiento (kg/día)")
        if self.qn_equilibrio:
            self.qn_ax_evo.axhline(y=self.qn_equilibrio["stock"], color="#7c3aed",
                                    linestyle="--", linewidth=1, alpha=0.7, label=f"Eq. stock={self.qn_equilibrio['stock']}")
        self.qn_ax_evo.scatter([actual["t"]], [actual["stock"]], color="#16a34a", s=60, zorder=5, edgecolors="black")
        self.qn_ax_evo.scatter([actual["t"]], [actual["procesamiento"]], color="#2563eb", s=60, zorder=5, edgecolors="black")
        self.qn_ax_evo.set_title("Evolución temporal", fontweight="bold")
        self.qn_ax_evo.set_xlabel("Tiempo (días)")
        self.qn_ax_evo.set_ylabel("Cantidad")
        self.qn_ax_evo.legend(fontsize=7, loc="best")
        self.qn_ax_evo.grid(True, alpha=0.15)

        # Espacio de fases
        self.qn_ax_fase.clear()
        self.qn_ax_fase.set_facecolor("#f0fdf4")
        self.qn_ax_fase.plot(stock_full, proc_full, color="#7c3aed", linewidth=1.2, alpha=0.5)
        self.qn_ax_fase.plot(stock, proc, color="#7c3aed", linewidth=2.5)
        if self.qn_equilibrio:
            self.qn_ax_fase.scatter([self.qn_equilibrio["stock"]], [self.qn_equilibrio["procesamiento"]],
                                     color="#7c3aed", s=120, marker="*", zorder=5,
                                     label=f"Equilibrio\n(stock={self.qn_equilibrio['stock']}, proc={self.qn_equilibrio['procesamiento']})")
        self.qn_ax_fase.scatter([actual["stock"]], [actual["procesamiento"]],
                                color="#ef4444", s=80, zorder=5, edgecolors="black", label="Actual")
        self.qn_ax_fase.set_title("Espacio de fases", fontweight="bold")
        self.qn_ax_fase.set_xlabel("Stock de quinua (kg)")
        self.qn_ax_fase.set_ylabel("Procesamiento (kg/día)")
        self.qn_ax_fase.legend(fontsize=7, loc="best")
        self.qn_ax_fase.grid(True, alpha=0.15)

        self.qn_fig.tight_layout()
        self.qn_canvas.draw()

    def _quinua_reiniciar(self):
        if self.qn_after_id:
            self.root.after_cancel(self.qn_after_id)
            self.qn_after_id = None
        self.qn_resultados = []
        self.qn_corriendo = False
        self.qn_pausado = False
        self.qn_paso_actual = 0
        self.qn_equilibrio = None
        self._qn_limpiar_tabla()
        self.qn_btn_iniciar.config(state="normal")
        self.qn_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.qn_btn_paso.config(state="disabled")
        self.qn_label_iteracion.config(text="Paso: 0 / 0")
        self.qn_label_stock.config(text="🌾 Stock: — kg")
        self.qn_label_proceso.config(text="🏭 Procesamiento: — kg/día")
        self.qn_label_equilibrio.config(text="⚖ Equilibrio: —")
        self.qn_ax_evo.clear()
        self.qn_ax_fase.clear()
        self.qn_ax_evo.set_title("Presiona ▶ Iniciar", fontweight="bold")
        self.qn_fig.tight_layout()
        self.qn_canvas.draw()

    def _quinua_detener(self):
        self.qn_corriendo = False
        self.qn_pausado = False
        self.qn_btn_iniciar.config(state="normal")
        self.qn_btn_pausa.config(state="disabled", text="⏸ Pausar")
        self.qn_btn_paso.config(state="disabled")
        if self.qn_after_id:
            self.root.after_cancel(self.qn_after_id)
            self.qn_after_id = None

    # ── Music Player ──

    MUSIC_URL = "https://www.youtube.com/watch?v=yaHf1FwMYA4"

    def _crear_music_player(self, root):
        frame = ttk.Frame(root, padding=(10, 4))
        frame.pack(side="bottom", fill="x", before=root.winfo_children()[0] if root.winfo_children() else None)

        self.music_process = None
        self.music_playing = False

        inner = ttk.Frame(frame)
        inner.pack(fill="x")
        self.music_btn = ttk.Button(inner, text="▶", width=3, command=self._music_toggle)
        self.music_btn.pack(side="left", padx=(0, 8))
        ttk.Label(inner, text="🎵 Fondue — Instrumental", font=("", 9)).pack(side="left", padx=(0, 12))
        ttk.Label(inner, text="Vol:", font=("", 8)).pack(side="left", padx=(0, 4))
        self.music_vol_var = tk.DoubleVar(value=50)
        vol_scale = ttk.Scale(inner, from_=0, to=100, variable=self.music_vol_var,
                              orient="horizontal", length=80, command=self._music_set_vol)
        vol_scale.pack(side="left")
        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", pady=(0, 0))

    def _music_toggle(self):
        if self.music_process and self.music_process.poll() is None:
            self.music_process.terminate()
            self.music_process = None
            self.music_playing = False
            self.music_btn.config(text="▶")
            return
        self.music_btn.config(text="⏳")
        threading.Thread(target=self._music_play, daemon=True).start()

    def _music_play(self):
        try:
            from yt_dlp import YoutubeDL
            with YoutubeDL({"quiet": True, "format": "bestaudio"}) as ydl:
                info = ydl.extract_info(self.MUSIC_URL, download=False)
                url = info["url"]
            ffplay = self._which("ffplay")
            if ffplay:
                self.music_playing = True
                self.music_process = subprocess.Popen(
                    [ffplay, "-nodisp", "-autoexit", "-volume", str(int(self.music_vol_var.get())), url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
                )
                self.music_process.wait()
            else:
                raise FileNotFoundError("ffplay no disponible")
        except Exception:
            webbrowser.open(self.MUSIC_URL)
        finally:
            self.music_playing = False
            self.root.after(0, lambda: self.music_btn.config(text="▶"))

    def _music_set_vol(self, val):
        if self.music_process and self.music_process.poll() is None:
            try:
                subprocess.run(
                    ["pactl", "set-sink-input-volume",
                     str(self.music_process.pid), f"{int(float(val))}%"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    @staticmethod
    def _which(cmd):
        for path in os.environ.get("PATH", "").split(os.pathsep):
            full = os.path.join(path, cmd)
            if os.path.isfile(full) and os.access(full, os.X_OK):
                return full
        return None


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
