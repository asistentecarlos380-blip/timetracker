from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import json
import os
import pandas as pd
from datetime import datetime

app = FastAPI()

DB_FILE = "database.json"

def inicializar_bd():
    if not os.path.exists(DB_FILE):
        datos_iniciales = {
            "usuarios": {
                "ADMIN": {"pin": "1234", "rol_sistema": "admin", "tipo_pago": "Fijo", "monto_fijo": 150.0, "tarifa_hora": 0.0, "area": "Gerencia"},
                "Ricardo": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Ronald": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Lisander": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Daniel": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Betzaida": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Brayan": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Gerson": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Matias": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Planta": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"}
            },
            "asistencias": []
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(datos_iniciales, f, indent=2, ensure_ascii=False)

inicializar_bd()

def leer_db():
    if not os.path.exists(DB_FILE):
        inicializar_bd()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def escribir_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: index.html no encontrado en el servidor.</h1>"

class LoginRequest(BaseModel):
    usuario: str
    pin: str

class RegistroManualRequest(BaseModel):
    usuario: str
    entrada: str
    salida: str | None = None
    es_continua: bool = False

class AjustarSalidaRequest(BaseModel):
    registro_id: int
    hora_salida: str

class UsuarioAdminRequest(BaseModel):
    usuario_antiguo: str | None = None
    usuario: str
    pin: str
    tipo_pago: str
    monto_fijo: float = 0.0
    tarifa_hora: float = 1.5
    area: str = "Operaciones"
    rol_sistema: str = "trabajador"

class CambiarPinRequest(BaseModel):
    usuario: str
    pin_actual: str
    pin_nuevo: str

@app.post("/api/login")
def login(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    # Búsqueda insensible a mayúsculas/minúsculas para permitir el ingreso
    usuario_encontrado = None
    for u in usuarios:
        if u.lower() == req.usuario.strip().lower():
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    if usuarios[usuario_encontrado]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="PIN incorrecto")
    
    return {
        "usuario": usuario_encontrado,
        "rol_sistema": usuarios[usuario_encontrado].get("rol_sistema", "trabajador")
    }

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    nuevo_nombre = req.usuario.strip()
    
    # Eliminar clave antigua si cambió de nombre
    if req.usuario_antiguo and req.usuario_antiguo in usuarios and req.usuario_antiguo != nuevo_nombre:
        del usuarios[req.usuario_antiguo]
        
    usuarios[nuevo_nombre] = {
        "pin": req.pin,
        "rol_sistema": req.rol_sistema,
        "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo if req.tipo_pago.lower() != "horas" else 0.0,
        "tarifa_hora": req.tarifa_hora if req.tipo_pago.lower() == "horas" else 0.0,
        "area": req.area
    }
    db["usuarios"] = usuarios
    escribir_db(db)
    return {"mensaje": "Usuario guardado correctamente"}
