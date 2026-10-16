import json
import os
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from supabase import create_client, Client

app = FastAPI()

# Bloqueo de subprocesos para evitar corrupción de datos por fichajes simultáneos
data_lock = threading.Lock()

SUPABASE_URL = "https://dvpfynkqtjwkvmcndael.supabase.co"
SUPABASE_KEY = "eyJhGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpcCI6MioiZFhBmXBhZmZSISIsInJIa2I1MiJjGZ5mXzZ3YWYj35kY2Y3bKvWsIiWicm9sZSI6IicmF1bC1JMC1pLCJpYyJpY3YxMDImNTEwMjM0aWNzImV3ODI1NjIwMDAwMjM0QjIzYjZaR1R1WnN3NzI0ZGISI3B1ZDV2ugYm0KSFJ54giI89Y"

ATTENDANCE_FILE = "attendance_history.json"
SYSTEM_FILE = "system_data.json"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PERSONAL_FIJO = {
    "ADMIN": {"usuario": "ADMIN", "pin": "1234", "rol_sistema": "admin", "tipo_pago": "Fijo", "monto_fijo": 300.0, "tarifa_hora": 1.5, "area": "Gerencia"},
    "Ricardo": {"usuario": "Ricardo", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Ronald": {"usuario": "Ronald", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Lisander": {"usuario": "Lisander", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Daniel": {"usuario": "Daniel", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Betzaida": {"usuario": "Betzaida", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Brayan": {"usuario": "Brayan", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
}

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
    fmt = "%Y-%m-%d %H:%M:%S"
    entrada = datetime.strptime(hora_entrada_str, fmt)
    salida = datetime.strptime(hora_salida_str, fmt)
    diferencia = salida - entrada
    dia_asignacion = entrada.strftime("%Y-%m-%d")
    return {
        "dia_asignacion": dia_asignacion,
        "total_horas": diferencia.total_seconds() / 3600
    }

# Endpoint principal para servir la interfaz Matrix
@app.get("/", response_class=HTMLResponse)
def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Error: index.html no encontrado</h1>", status_code=404)

# Endpoint de estado para prevenir errores 404 en peticiones iniciales del navegador
@app.get("/api/status")
@app.get("/status")
def health_check():
    return {"status": "ok", "message": "Sistema operativo"}
