from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import json
import os

app = FastAPI()

DB_FILE = "database.json"

# Modelo para cambio de PIN del usuario
class CambiarPinRequest(BaseModel):
    usuario: str
    pin_actual: str
    pin_nuevo: str

@app.post("/api/cambiar-pin")
def cambiar_pin_usuario(req: CambiarPinRequest):
    if not os.path.exists(DB_FILE):
        raise HTTPException(status_code=404, detail="Base de datos no encontrada")
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    usuarios = data.get("usuarios", {})
    if req.usuario not in usuarios:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar PIN actual
    if usuarios[req.usuario].get("pin") != req.pin_actual:
        raise HTTPException(status_code=400, detail="El PIN actual es incorrecto")
    
    # Validar que el nuevo PIN sea válido (mínimo 4 dígitos)
    if not req.pin_nuevo or len(req.pin_nuevo.strip()) < 4:
        raise HTTPException(status_code=400, detail="El nuevo PIN debe tener al menos 4 caracteres")
    
    # Actualizar PIN
    usuarios[req.usuario]["pin"] = req.pin_nuevo.strip()
    data["usuarios"] = usuarios
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return {"mensaje": "PIN actualizado correctamente"}
