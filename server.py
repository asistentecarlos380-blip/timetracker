from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import json
import uvicorn
from datetime import datetime
import zoneinfo

app = FastAPI()

DATA_FILE = "system_data.json"
TZ_VE = zoneinfo.ZoneInfo("America/Caracas")

def get_hora_actual():
    return datetime.now(TZ_VE).strftime("%Y-%m-%d %I:%M:%S %p")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "usuarios": {
                "admin": {"pin": "9999", "tipo_pago": "fijo", "monto_fijo": 150.0, "tarifa_hora": 0.0, "area": "Administración", "rol_sistema": "admin"}
            },
            "asistencias": []
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "usuarios" not in data:
                data["usuarios"] = {"admin": {"pin": "9999", "tipo_pago": "fijo", "monto_fijo": 150.0, "tarifa_hora": 0.0, "area": "Administración", "rol_sistema": "admin"}}
            if "asistencias" not in data:
                data["asistencias"] = []
            return data
    except:
        return {
            "usuarios": {
                "admin": {"pin": "9999", "tipo_pago": "fijo", "monto_fijo": 150.0, "tarifa_hora": 0.0, "area": "Administración", "rol_sistema": "admin"}
            },
            "asistencias": []
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class LoginReq(BaseModel):
    usuario: str
    pin: str

class UserReq(BaseModel):
    usuario_antiguo: str = ""
    usuario: str
    pin: str
    tipo_pago: str = "horas"
    monto_fijo: float = 150.0
    tarifa_hora: float = 1.1
    area: str = "General"
    rol_sistema: str = "trabajador"

class CheckoutReq(BaseModel):
    registro_id: int
    hora_salida: str

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h2>index.html no encontrado</h2>", status_code=404)

@app.post("/api/login")
def login(req: LoginReq):
    data = load_data()
    u_clean = req.usuario.strip().lower()
    
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == u_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")
        
    u_info = data["usuarios"][user_key]
    return {
        "status": "ok",
        "usuario": user_key,
        "rol_sistema": u_info.get("rol_sistema", "trabajador"),
        "tipo_pago": u_info.get("tipo_pago", "horas")
    }

@app.post("/api/marcar")
def marcar(req: LoginReq):
    data = load_data()
    u_clean = req.usuario.strip().lower()
    
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == u_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")

    ahora = get_hora_actual()
    
    for reg in reversed(data["asistencias"]):
        if reg["usuario"].lower() == u_clean and reg["salida"] is None:
            if reg.get("receso_inicio") and not reg.get("receso_fin"):
                reg["receso_fin"] = ahora
            reg["salida"] = ahora
            save_data(data)
            return {"status": "salida", "mensaje": f"Salida registrada a las {ahora}"}

    nuevo_reg = {
        "id": len(data["asistencias"]) + 1,
        "usuario": user_key,
        "entrada": ahora,
        "receso_inicio": None,
        "receso_fin": None,
        "salida": None
    }
    data["asistencias"].append(nuevo_reg)
    save_data(data)
    return {"status": "entrada", "mensaje": f"Registro iniciado a las {ahora}"}

@app.post("/api/receso")
def gestionar_receso(req: LoginReq):
    data = load_data()
    u_clean = req.usuario.strip().lower()
    
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == u_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")

    ahora = get_hora_actual()
    
    for reg in reversed(data["asistencias"]):
        if reg["usuario"].lower() == u_clean and reg["salida"] is None:
            if reg.get("receso_inicio") is None:
                reg["receso_inicio"] = ahora
                save_data(data)
                return {"status": "receso_inicio", "mensaje": f"Receso iniciado a las {ahora}"}
            elif reg.get("receso_fin") is None:
                reg["receso_fin"] = ahora
                save_data(data)
                return {"status": "receso_fin", "mensaje": f"Receso finalizado a las {ahora}"}
            else:
                raise HTTPException(status_code=400, detail="Ya registraste un receso")

    raise HTTPException(status_code=400, detail="No tienes un turno activo abierto")

@app.post("/api/mis-horas")
def mis_horas(req: LoginReq):
    data = load_data()
    u_clean = req.usuario.strip().lower()
    
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == u_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")

    registros = [r for r in data["asistencias"] if r["usuario"].lower() == u_clean]
    return {"status": "ok", "usuario": user_key, "registros": registros}

@app.get("/api/admin/datos")
def admin_datos():
    return load_data()

@app.post("/api/admin/usuario")
def guardar_usuario(req: UserReq):
    data = load_data()
    nombre_antiguo = req.usuario_antiguo.strip()
    nombre_nuevo = req.usuario.strip()

    if nombre_antiguo and nombre_antiguo in data["usuarios"] and nombre_antiguo != nombre_nuevo:
        data["usuarios"][nombre_nuevo] = data["usuarios"].pop(nombre_antiguo)
        for reg in data["asistencias"]:
            if reg["usuario"].lower() == nombre_antiguo.lower():
                reg["usuario"] = nombre_nuevo

    data["usuarios"][nombre_nuevo] = {
        "pin": req.pin.strip(),
        "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo,
        "tarifa_hora": req.tarifa_hora,
        "area": req.area.strip(),
        "rol_sistema": req.rol_sistema.strip()
    }
    save_data(data)
    return {"status": "ok"}

@app.delete("/api/admin/usuario/{usuario}")
def eliminar_usuario(usuario: str):
    data = load_data()
    if usuario in data["usuarios"]:
        del data["usuarios"][usuario]
        save_data(data)
    return {"status": "ok"}

@app.post("/api/admin/ajustar-salida")
def ajustar_salida(req: CheckoutReq):
    data = load_data()
    for reg in data["asistencias"]:
        if reg["id"] == req.registro_id:
            reg["salida"] = req.hora_salida
            save_data(data)
            return {"status": "ok", "mensaje": "Hora de salida actualizada"}
    raise HTTPException(status_code=404, detail="Registro no encontrado")

# API Admin: Importar Base de Datos completa
@app.post("/api/admin/importar")
def importar_datos(nuevo_estado: dict):
    if "usuarios" not in nuevo_estado or "asistencias" not in nuevo_estado:
        raise HTTPException(status_code=400, detail="Formato de respaldo inválido")
    save_data(nuevo_estado)
    return {"status": "ok", "mensaje": "Base de datos restaurada correctamente"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
