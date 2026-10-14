from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
import uvicorn
from datetime import datetime

app = FastAPI()

DATA_FILE = "system_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"usuarios": {"admin": {"pin": "9999", "rol": "admin"}}, "asistencias": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "usuarios" not in data:
                data["usuarios"] = {"admin": {"pin": "9999", "rol": "admin"}}
            if "asistencias" not in data:
                data["asistencias"] = []
            return data
    except:
        return {"usuarios": {"admin": {"pin": "9999", "rol": "admin"}}, "asistencias": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class LoginReq(BaseModel):
    usuario: str
    pin: str

class UserReq(BaseModel):
    usuario: str
    pin: str
    rol: str = "trabajador"

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
    usuario_clean = req.usuario.strip().lower()
    
    # Buscar usuario (case-insensitive)
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == usuario_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")
        
    rol = data["usuarios"][user_key].get("rol", "trabajador")
    return {"status": "ok", "usuario": user_key, "rol": rol}

# API para marcar entrada/salida
@app.post("/api/marcar")
def marcar(req: LoginReq):
    data = load_data()
    usuario_clean = req.usuario.strip().lower()
    
    user_key = None
    for k in data["usuarios"]:
        if k.lower() == usuario_clean:
            user_key = k
            break
            
    if not user_key or data["usuarios"][user_key]["pin"] != req.pin.strip():
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrecto")

    ahora = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    # Buscar si tiene un turno abierto
    for reg in reversed(data["asistencias"]):
        if reg["usuario"].lower() == usuario_clean and reg["salida"] is None:
            reg["salida"] = ahora
            save_data(data)
            return {"status": "salida", "mensaje": f"Salida registrada a las {ahora}"}

    # Si no tiene turno abierto, se registra entrada
    nuevo_reg = {
        "id": len(data["asistencias"]) + 1,
        "usuario": user_key,
        "entrada": ahora,
        "salida": None
    }
    data["asistencias"].append(nuevo_reg)
    save_data(data)
    return {"status": "entrada", "mensaje": f"Entrada registrada a las {ahora}"}

# API Admin: Obtener datos
@app.get("/api/admin/datos")
def admin_datos():
    return load_data()

# API Admin: Crear / Editar Usuario
@app.post("/api/admin/usuario")
def guardar_usuario(req: UserReq):
    data = load_data()
    data["usuarios"][req.usuario.strip()] = {
        "pin": req.pin.strip(),
        "rol": req.rol.strip()
    }
    save_data(data)
    return {"status": "ok"}

# API Admin: Eliminar Usuario
@app.delete("/api/admin/usuario/{usuario}")
def eliminar_usuario(usuario: str):
    data = load_data()
    if usuario in data["usuarios"]:
        del data["usuarios"][usuario]
        save_data(data)
    return {"status": "ok"}

# API Admin: Editar Salida Manualmente
@app.post("/api/admin/ajustar-salida")
def ajustar_salida(req: CheckoutReq):
    data = load_data()
    for reg in data["asistencias"]:
        if reg["id"] == req.registro_id:
            reg["salida"] = req.hora_salida
            save_data(data)
            return {"status": "ok", "mensaje": "Hora de salida actualizada"}
    raise HTTPException(status_code=404, detail="Registro no encontrado")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
