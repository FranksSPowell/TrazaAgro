# Consulta de Trazabilidad SENASA

Este proyecto es una aplicación de escritorio desarrollada en **Python** (usando `tkinter`) para consultar los depósitos de SENASA a través de su API, con la posibilidad de exportar los resultados a Excel.

## Características

- **Interfaz gráfica** de usuario con `tkinter`.
- **Gestión de credenciales y entorno** de prueba/producción.
- **Consulta de Depósitos** a través de la API de SENASA.
- **Exportación** de los resultados a un archivo Excel (`.xlsx`).

## Requisitos

- Python 3.7 o superior (recomendado Python 3.9+).
- Librerías:
  - `requests`
  - `pandas`
  - `openpyxl` (se instala junto con `pandas` para exportar a Excel)
  - `tkinter` (generalmente viene incluido con Python en la mayoría de distribuciones).

Puedes instalar las dependencias con:
```bash
pip install requests pandas openpyxl
