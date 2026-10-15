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
                "ADMIN": {"pin": "1234", "rol_sistema": "admin", "tipo_pago": "Fijo", "monto_fijo": 300.0, "tarifa_hora": 0.0, "area": "Gerencia"},
                "Ricardo": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Ronald": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Lisander": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Daniel": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Betzaida": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Brayan": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Gerson": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Matias": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
                "Planta": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Gasolina", "monto_fijo": 0.0, "tarifa_hora": 0.0, "area": "Operaciones"}
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
        "pin": req.pin,
        "rol_sistema": usuarios[usuario_encontrado].get("rol_sistema", "trabajador")
    }

@app.post("/api/cambiar-pin")
def cambiar_pin(req: CambiarPinRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    u_encontrado = None
    for u in usuarios:
        if u.lower() == req.usuario.strip().lower():
            u_encontrado = u
            break

    if not u_encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuarios[u_encontrado]["pin"] != req.pin_actual:
        raise HTTPException(status_code=400, detail="El PIN actual es incorrecto")
    
    if not req.pin_nuevo or len(req.pin_nuevo.strip()) < 4:
        raise HTTPException(status_code=400, detail="El nuevo PIN debe tener al menos 4 caracteres")
    
    usuarios[u_encontrado]["pin"] = req.pin_nuevo.strip()
    db["usuarios"] = usuarios
    escribir_db(db)
    return {"mensaje": "PIN actualizado correctamente"}

@app.post("/api/mis-horas")
def mis_horas(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    u_encontrado = None
    for u in usuarios:
        if u.lower() == req.usuario.strip().lower():
            u_encontrado = u
            break
            
    if not u_encontrado or usuarios[u_encontrado]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    registros = [r for r in db.get("asistencias", []) if r["usuario"].lower() == req.usuario.strip().lower()]
    return {"registros": registros}

@app.post("/api/marcar")
def marcar(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    u_encontrado = None
    for u in usuarios:
        if u.lower() == req.usuario.strip().lower():
            u_encontrado = u
            break
            
    if not u_encontrado or usuarios[u_encontrado]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    asistencias = db.get("asistencias", [])
    activo = None
    for r in asistencias:
        if r["usuario"].lower() == u_encontrado.lower() and r["salida"] is None:
            activo = r
            break
            
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    if activo:
        if activo.get("receso_inicio") and not activo.get("receso_fin"):
            activo["receso_fin"] = hora_actual
        else:
            activo["salida"] = hora_actual
    else:
        nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
        nuevo_reg = {
            "id": nuevo_id,
            "usuario": u_encontrado,
            "entrada": hora_actual,
            "receso_inicio": None,
            "receso_fin": None,
            "salida": None,
            "es_continua": False
        }
        asistencias.append(nuevo_reg)
        
    db["asistencias"] = asistencias
    escribir_db(db)
    return {"mensaje": "Acción registrada con éxito"}

@app.post("/api/receso")
def receso(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    u_encontrado = None
    for u in usuarios:
        if u.lower() == req.usuario.strip().lower():
            u_encontrado = u
            break
            
    if not u_encontrado or usuarios[u_encontrado]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    asistencias = db.get("asistencias", [])
    activo = None
    for r in asistencias:
        if r["usuario"].lower() == u_encontrado.lower() and r["salida"] is None:
            activo = r
            break
            
    if not activo:
        raise HTTPException(status_code=400, detail="No tienes ningún turno activo para pausar.")
        
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    if not activo.get("receso_inicio"):
        activo["receso_inicio"] = hora_actual
    elif not activo.get("receso_fin"):
        activo["receso_fin"] = hora_actual
    else:
        nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
        nuevo_reg = {
            "id": nuevo_id,
            "usuario": u_encontrado,
            "entrada": hora_actual,
            "receso_inicio": None,
            "receso_fin": None,
            "salida": None,
            "es_continua": True
        }
        activo["salida"] = hora_actual
        asistencias.append(nuevo_reg)

    db["asistencias"] = asistencias
    escribir_db(db)
    return {"mensaje": "Receso procesado con éxito"}

@app.get("/api/admin/datos")
def admin_datos():
    db = leer_db()
    return {"usuarios": db.get("usuarios", {}), "asistencias": db.get("asistencias", [])}

@app.post("/api/admin/registro-manual")
def admin_registro_manual(req: RegistroManualRequest):
    db = leer_db()
    asistencias = db.get("asistencias", [])
    usuarios = db.get("usuarios", {})
    nombre_usuario = req.usuario.strip()
    
    usuario_real = None
    for u in usuarios:
        if u.lower() == nombre_usuario.lower():
            usuario_real = u
            break
            
    if not usuario_real:
        usuario_real = nombre_usuario.capitalize()
        tipo = "Gasolina" if usuario_real.lower() == "planta" else "Horas"
        tarifa = 0.0 if tipo == "Gasolina" else 1.5
        usuarios[usuario_real] = {
            "pin": "1234",
            "rol_sistema": "trabajador",
            "tipo_pago": tipo,
            "monto_fijo": 0.0,
            "tarifa_hora": tarifa,
            "area": "Operaciones"
        }
        db["usuarios"] = usuarios

    nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
    nuevo_reg = {
        "id": nuevo_id,
        "usuario": usuario_real,
        "entrada": req.entrada,
        "receso_inicio": None,
        "receso_fin": None,
        "salida": req.salida,
        "es_continua": req.es_continua
    }
    asistencias.append(nuevo_reg)
    db["asistencias"] = asistencias
    escribir_db(db)
    return {"mensaje": "Registro manual guardado con éxito"}

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    nuevo_nombre = req.usuario.strip()
    
    if req.usuario_antiguo and req.usuario_antiguo in usuarios and req.usuario_antiguo != nuevo_nombre:
        del usuarios[req.usuario_antiguo]
        
    usuarios[nuevo_nombre] = {
        "pin": req.pin,
        "rol_sistema": req.rol_sistema,
        "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo if req.tipo_pago.lower() == "fijo" else 0.0,
        "tarifa_hora": req.tarifa_hora if req.tipo_pago.lower() == "horas" else 0.0,
        "area": req.area
    }
    db["usuarios"] = usuarios
    escribir_db(db)
    return {"mensaje": "Usuario guardado correctamente"}

@app.delete("/api/admin/usuario/{usuario}")
def admin_eliminar_usuario(usuario: str):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    u_eliminar = None
    for u in usuarios:
        if u.lower() == usuario.lower():
            u_eliminar = u
            break
            
    if u_eliminar:
        del usuarios[u_eliminar]
        db["usuarios"] = usuarios
        escribir_db(db)
        return {"mensaje": "Usuario eliminado"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.get("/api/admin/exportar-excel")
def exportar_excel():
    db = leer_db()
    asistencias = db.get("asistencias", [])
    data_rows = []
    for r in asistencias:
        data_rows.append({
            "ID": r["id"],
            "Usuario": r["usuario"],
            "Entrada": r["entrada"],
            "Salida": r["salida"] if r["salida"] else "En Curso",
            "Es Continua": "Sí" if r["es_continua"] else "No"
        })
        
    df = pd.DataFrame(data_rows)
    export_path = "reporte_asistencia.xlsx"
    df.to_excel(export_path, index=False)
    return FileResponse(export_path, filename="Reporte_Asistencia.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
