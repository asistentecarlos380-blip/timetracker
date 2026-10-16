import json
import os
import threading
from datetime import datetime, timedelta

# Bloqueo de subprocesos para evitar corrupción de datos por fichajes simultáneos
data_lock = threading.Lock()

ATTENDANCE_FILE = "attendance_history.json"
SYSTEM_FILE = "system_data.json"

def read_json(file_path):
    with data_lock:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_json(file_path, data):
    with data_lock:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def calcular_horas_turno(hora_entrada_str, hora_salida_str):
    """
    Calcula las horas trabajadas asegurando que si el turno cruza la medianoche,
    se acredite y asigne al día de inicio del turno.
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    entrada = datetime.strptime(hora_entrada_str, fmt)
    salida = datetime.strptime(hora_salida_str, fmt)
    
    # Si la salida es menor que la entrada en términos de hora pero del mismo día natural,
    # o si ocurre al día siguiente, manejamos el cálculo de la diferencia temporal.
    diferencia = salida - entrada
    
    # El día clave al que se le suman las horas es la fecha de entrada
    dia_asignacion = entrada.strftime("%Y-%m-%d")
    
    return {
        "dia_asignacion": dia_asignacion,
        "total_horas": diferencia.total_seconds() / 3600
    }

# Ejemplo de integración en tus rutas de fichaje:
# (Mantén tus rutas actuales de Flask/FastAPI/HTTP server, incorporando 'read_json' y 'write_json')
