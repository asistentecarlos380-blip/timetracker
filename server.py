from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import shutil
import pandas as pd
from datetime import datetime

app = FastAPI()

DB_FILE = "database.json"

# Inicializar base de datos por defecto si no existe
def inicializar_bd():
    if not os.path.exists(DB_FILE):
        datos_iniciales = {
            "usuarios": {
                "admin": {"pin": "1234", "rol_sistema": "admin", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Gerencia"},
                "RICARDO": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "RONALD": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "LISANDER": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "DANIEL": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "BETZAIDA": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "BRAYAN": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "GERSON": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "MATIAS": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"},
                "PLANTA": {"pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 150, "tarifa_hora": 1.5, "area": "Operaciones"}
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

# RUTA RAÍZ PARA SERVIR EL INDEX.HTML
@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: index.html no encontrado en el servidor.</h1>"

# MODELOS DE DATOS
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
    monto_fijo: float
    tarifa_hora: float
    area: str
    rol_sistema: str

class CambiarPinRequest(BaseModel):
    usuario: str
    pin_actual: str
    pin_nuevo: str

# ENDPOINTS DE AUTENTICACIÓN Y USUARIOS
@app.post("/api/login")
def login(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    if req.usuario not in usuarios:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    if usuarios[req.usuario]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="PIN incorrecto")
    
    return {
        "usuario": req.usuario,
        "rol_sistema": usuarios[req.usuario].get("rol_sistema", "trabajador")
    }

@app.post("/api/cambiar-pin")
def cambiar_pin(req: CambiarPinRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    if req.usuario not in usuarios:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuarios[req.usuario]["pin"] != req.pin_actual:
        raise HTTPException(status_code=400, detail="El PIN actual es incorrecto")
    
    if not req.pin_nuevo or len(req.pin_nuevo.strip()) < 4:
        raise HTTPException(status_code=400, detail="El nuevo PIN debe tener al menos 4 caracteres")
    
    usuarios[req.usuario]["pin"] = req.pin_nuevo.strip()
    db["usuarios"] = usuarios
    escribir_db(db)
    return {"mensaje": "PIN actualizado correctamente"}

# ENDPOINTS DE ASISTENCIA Y FICHAR
@app.post("/api/mis-horas")
def mis_horas(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    if req.usuario not in usuarios or usuarios[req.usuario]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    registros = [r for r in db.get("asistencias", []) if r["usuario"].upper() == req.usuario.upper()]
    return {"registros": registros}

@app.post("/api/marcar")
def marcar(req: LoginRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    if req.usuario not in usuarios or usuarios[req.usuario]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    asistencias = db.get("asistencias", [])
    usuario_mayus = req.usuario.upper()
    
    # Buscar turno abierto
    activo = None
    for r in asistencias:
        if r["usuario"].upper() == usuario_mayus and r["salida"] is None:
            activo = r
            break
            
    hora_actual = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    if activo:
        # Si está en receso activo, lo finaliza o si no, cierra el turno
        if activo.get("receso_inicio") and not activo.get("receso_fin"):
            activo["receso_fin"] = hora_actual
        else:
            activo["salida"] = hora_actual
    else:
        # Nuevo registro
        nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
        nuevo_reg = {
            "id": nuevo_id,
            "usuario": usuario_mayus,
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
    if req.usuario not in usuarios or usuarios[req.usuario]["pin"] != req.pin:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    asistencias = db.get("asistencias", [])
    usuario_mayus = req.usuario.upper()
    
    activo = None
    for r in asistencias:
        if r["usuario"].upper() == usuario_mayus and r["salida"] is None:
            activo = r
            break
            
    if not activo:
        raise HTTPException(status_code=400, detail="No tienes ningún turno activo para pausar.")
        
    hora_actual = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    if not activo.get("receso_inicio"):
        activo["receso_inicio"] = hora_actual
    elif not activo.get("receso_fin"):
        activo["receso_fin"] = hora_actual
    else:
        # Si ya tuvo receso, abre nuevo tramo continuo
        nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
        nuevo_reg = {
            "id": nuevo_id,
            "usuario": usuario_mayus,
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

# ENDPOINTS DE ADMINISTRACIÓN
@app.get("/api/admin/datos")
def admin_datos():
    db = leer_db()
    return {"usuarios": db.get("usuarios", {}), "asistencias": db.get("asistencias", [])}

@app.post("/api/admin/registro-manual")
def admin_registro_manual(req: RegistroManualRequest):
    db = leer_db()
    asistencias = db.get("asistencias", [])
    nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
    
    nuevo_reg = {
        "id": nuevo_id,
        "usuario": req.usuario.upper(),
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

@app.post("/api/admin/ajustar-salida")
def admin_ajustar_salida(req: AjustarSalidaRequest):
    db = leer_db()
    asistencias = db.get("asistencias", [])
    encontrado = False
    for r in asistencias:
        if r["id"] == req.registro_id:
            r["salida"] = req.hora_salida
            encontrado = True
            break
    if not encontrado:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    db["asistencias"] = asistencias
    escribir_db(db)
    return {"mensaje": "Salida ajustada"}

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    
    if req.usuario_antiguo and req.usuario_antiguo in usuarios and req.usuario_antiguo != req.usuario:
        del usuarios[req.usuario_antiguo]
        
    usuarios[req.usuario.upper()] = {
        "pin": req.pin,
        "rol_sistema": req.rol_sistema,
        "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo,
        "tarifa_hora": req.tarifa_hora,
        "area": req.area
    }
    db["usuarios"] = usuarios
    escribir_db(db)
    return {"mensaje": "Usuario guardado correctamente"}

@app.delete("/api/admin/usuario/{usuario}")
def admin_eliminar_usuario(usuario: str):
    db = leer_db()
    usuarios = db.get("usuarios", {})
    if usuario.upper() in usuarios:
        del usuarios[usuario.upper()]
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

@app.post("/api/admin/importar-excel")
async def importar_excel(file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = "temp_import.xlsx"
    with open(temp_path, "wb") as f:
        f.write(contents)
        
    try:
        df = pd.read_excel(temp_path)
        db = leer_db()
        asistencias = db.get("asistencias", [])
        nuevo_id = max([r["id"] for r in asistencias], default=0) + 1
        
        importados = 0
        for _, row in df.iterrows():
            usuario = str(row.get("Usuario", "")).strip().upper()
            entrada = str(row.get("Entrada", "")).strip()
            salida_val = row.get("Salida", None)
            salida = str(salida_val).strip() if pd.notna(salida_val) and str(salida_val).strip().lower() != "en curso" else None
            
            if usuario and entrada:
                asistencias.append({
                    "id": nuevo_id,
                    "usuario": usuario,
                    "entrada": entrada,
                    "receso_inicio": None,
                    "receso_fin": None,
                    "salida": salida,
                    "es_continua": False
                })
                nuevo_id += 1
                importados += 1
                
        db["asistencias"] = asistencias
        escribir_db(db)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"mensaje": f"¡Se importaron {importados} registros desde el Excel con éxito!"}
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo Excel: {str(e)}")
