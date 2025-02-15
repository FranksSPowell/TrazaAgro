#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación de interfaz gráfica (tkinter) para consultar depósitos de SENASA.
Se guardan las credenciales y la URL (entorno test o producción) en un archivo JSON.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import pandas as pd

class SenasaApp:
    def __init__(self, root):
        """
        Constructor de la clase SenasaApp. Configura la ventana principal y crea los componentes.
        """
        self.root = root
        self.root.title("Consulta de Trazabilidad SENASA")
        
        # Tamaño fijo de la ventana
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Crear contenedor para el menú y las pestañas
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        self.tab_frame = tk.Frame(root)
        self.tab_frame.pack(side="right", expand=True, fill="both")
        
        # Menú de navegación
        tk.Button(self.menu_frame, text="Consulta Depósitos", command=self.mostrar_pestaña_consulta).pack(pady=10)
        tk.Button(self.menu_frame, text="Configuración", command=self.mostrar_pestaña_config).pack(pady=10)
        
        # Crear pestañas
        self.tab_control = ttk.Notebook(self.tab_frame)
        self.pestaña_consulta = ttk.Frame(self.tab_control)
        self.pestaña_config = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.pestaña_consulta, text="Consulta Depósitos")
        self.tab_control.add(self.pestaña_config, text="Configuración")
        self.tab_control.pack(expand=1, fill="both")

        # Configurar las pestañas
        self.configurar_pestaña_config()
        self.configurar_pestaña_consulta()

        # Botón de cerrar
        self.boton_cerrar = tk.Button(
            root,
            text="Cerrar",
            command=root.quit,
            bg="red",
            fg="white"
        )
        self.boton_cerrar.pack(pady=10, side="bottom", fill="x")

    # ------------------------------------------------
    # PESTAÑA DE CONFIGURACIÓN
    # ------------------------------------------------
    def configurar_pestaña_config(self):
        """Configura la pestaña de Configuración."""
        ttk.Label(self.pestaña_config, text="CUIT:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.cuit_entry = ttk.Entry(self.pestaña_config)
        self.cuit_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.pestaña_config, text="Usuario:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.user_entry = ttk.Entry(self.pestaña_config)
        self.user_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.pestaña_config, text="Contraseña:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.pass_entry = ttk.Entry(self.pestaña_config, show="*")
        self.pass_entry.grid(row=2, column=1, padx=10, pady=10)

        # Botones de selección de entorno
        self.env_var = tk.StringVar(value="test")
        ttk.Radiobutton(self.pestaña_config, text="Prueba", variable=self.env_var, value="test").grid(row=3, column=0, padx=10, pady=10)
        ttk.Radiobutton(self.pestaña_config, text="Producción", variable=self.env_var, value="production").grid(row=3, column=1, padx=10, pady=10)

        # Botón para guardar la configuración
        ttk.Button(self.pestaña_config, text="Guardar Configuración", command=self.guardar_config).grid(row=4, column=0, columnspan=2, pady=20)

    def guardar_config(self):
        """Guarda la configuración ingresada por el usuario en un archivo JSON."""
        cuit = self.cuit_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        environment = self.env_var.get()

        # Validación básica de los campos
        if not cuit or not user or not password:
            self.mostrar_error("Todos los campos (CUIT, Usuario y Contraseña) deben estar completos.")
            return
        
        # Seleccionar la URL según el entorno
        url = (
            "https://test.senasa.gov.ar/agrotraza/src/api/"
            if environment == "test"
            else "https://aps2.senasa.gov.ar/agrotraza/src/api/"
        )

        # Guardar configuración en un diccionario
        config = {
            "cuit": cuit,
            "user": user,
            "password": password,
            "url": url
        }

        # Guardar configuración en archivo JSON
        try:
            with open("config.json", "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Configuración", "Configuración guardada con éxito.")
        except Exception as e:
            self.mostrar_error(f"Error al guardar la configuración: {e}")

    # ------------------------------------------------
    # PESTAÑA DE CONSULTA
    # ------------------------------------------------
    def configurar_pestaña_consulta(self):
        """Configura la pestaña de Consulta de Depósitos."""
        ttk.Label(self.pestaña_consulta, text="Consulta de Depósitos", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Botón para realizar la consulta
        ttk.Button(self.pestaña_consulta, text="Consultar Depósitos", command=self.consultar_depositos).grid(row=1, column=0, pady=10)
        
        # Configuración de estilo para la tabla
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Arial", 10))
        style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))
        
        columns = ("depositId", "companyName", "depositName", "addressStreet")
        self.result_table = ttk.Treeview(
            self.pestaña_consulta,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        # Configurar encabezados de la tabla
        self.result_table.heading("depositId", text="ID Depósito")
        self.result_table.heading("companyName", text="Compañía")
        self.result_table.heading("depositName", text="Nombre Depósito")
        self.result_table.heading("addressStreet", text="Dirección")
        
        # Ajustar tamaño de columnas
        self.result_table.column("depositId", width=100)
        self.result_table.column("companyName", width=200)
        self.result_table.column("depositName", width=150)
        self.result_table.column("addressStreet", width=150)

        # Definir colores para las filas alternas
        self.result_table.tag_configure('odd', background='white')
        self.result_table.tag_configure('even', background='#e6f7ff')
        
        # Ubicar la tabla en la ventana
        self.result_table.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        # Botón para exportar a Excel en la parte inferior derecha
        ttk.Button(self.pestaña_consulta, text="Exportar a Excel", command=self.exportar_a_excel).grid(row=3, column=1, padx=10, pady=10, sticky="e")
        
        # Log de errores y devoluciones
        self.log_area = tk.Text(self.pestaña_consulta, height=2, width=70, state="disabled", fg="red")
        self.log_area.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def consultar_depositos(self):
        """Realiza la consulta de depósitos al servidor de SENASA."""
        if not self.configuracion_valida():
            self.mostrar_error("Configura los datos antes de hacer consultas.")
            return

        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            self.mostrar_error("Configura los datos antes de hacer consultas (no se encontró config.json).")
            return

        url = config["url"] + "Consulta_Deposito"
        params = {
            "authUser": config["user"],
            "authPass": config["password"],
            "userTaxId": config["cuit"]
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list):
                    # Limpiar la tabla antes de cargar nuevos datos
                    for item in self.result_table.get_children():
                        self.result_table.delete(item)
                    
                    # Cargar datos en la tabla
                    self.resultados = data  # Guardamos los datos para exportar
                    for i, deposito in enumerate(data):
                        tag = 'even' if i % 2 == 0 else 'odd'
                        self.result_table.insert(
                            "",
                            "end",
                            values=(
                                deposito["depositId"],
                                deposito["companyName"],
                                deposito["depositName"],
                                deposito["addressStreet"]
                            ),
                            tags=(tag,)
                        )
                    
                    # Mostrar mensaje de éxito en verde
                    self.log_area.config(state="normal")
                    self.log_area.delete(1.0, tk.END)
                    self.log_area.insert(tk.END, "Consulta realizada exitosamente\n", "success")
                    self.log_area.tag_config("success", foreground="green")
                    self.log_area.config(state="disabled")
                else:
                    self.mostrar_error("Respuesta inesperada del servidor. Se esperaba una lista de depósitos.")
            else:
                self.mostrar_error(f"Error en la consulta: {response.status_code}")

        except requests.RequestException as e:
            self.mostrar_error(f"No se pudo realizar la consulta: {e}")

    def exportar_a_excel(self):
        """Exporta los resultados de la tabla a un archivo Excel."""
        if not hasattr(self, 'resultados') or not self.resultados:
            self.mostrar_error("No hay datos para exportar.")
            return
        
        try:
            df = pd.DataFrame(self.resultados)
            df.to_excel("resultado_consulta.xlsx", index=False)
            messagebox.showinfo("Exportación exitosa", "Los datos se exportaron correctamente a 'resultado_consulta.xlsx'.")
        except Exception as e:
            self.mostrar_error(f"Error al exportar a Excel: {e}")

    # ------------------------------------------------
    # MÉTODOS AUXILIARES
    # ------------------------------------------------
    def mostrar_pestaña_consulta(self):
        """Muestra la pestaña de consulta de depósitos."""
        self.tab_control.select(self.pestaña_consulta)

    def mostrar_pestaña_config(self):
        """Muestra la pestaña de configuración y carga los datos guardados."""
        self.tab_control.select(self.pestaña_config)
        self.cargar_config()

    def cargar_config(self):
        """Carga la configuración guardada (si existe) en los campos de entrada."""
        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                self.cuit_entry.delete(0, tk.END)
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)

                self.cuit_entry.insert(0, config.get("cuit", ""))
                self.user_entry.insert(0, config.get("user", ""))
                self.pass_entry.insert(0, config.get("password", ""))

                # Determinar entorno a partir de la URL
                if "test" in config.get("url", ""):
                    self.env_var.set("test")
                else:
                    self.env_var.set("production")

        except FileNotFoundError:
            self.mostrar_error("No se encontró ninguna configuración guardada (config.json).")

    def configuracion_valida(self):
        """Verifica que haya una configuración válida en el archivo JSON."""
        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
            return all(
                key in config and config[key]
                for key in ["cuit", "user", "password", "url"]
            )
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return False

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el log y en una ventana emergente."""
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"ERROR: {mensaje}\n")
        self.log_area.config(state="disabled")
        messagebox.showerror("Error", mensaje)


# ------------------------------------------------
# EJECUCIÓN DEL PROGRAMA
# ------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SenasaApp(root)
    root.mainloop()
