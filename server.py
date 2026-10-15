from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = "https://dvpfynkqtjwkvmcndael.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a3ZtY25kYWVsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTIwODM1MDcsImV4cCI6MjEwNzY1OTUwN30.7gjZWE3AbR1ta8grbzr-Xpdd5vugYm0KSFJ54giI89Y"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: index.html no encontrado.</h1>"

class LoginRequest(BaseModel):
    usuario: str
    pin: str

class RegistroManualRequest(BaseModel):
    usuario: str
    entrada: str
    salida: str | None = None
    es_continua: bool = False

class EditarRegistroRequest(BaseModel):
    registro_id: int
    entrada: str
    salida: str | None = None

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
    res = supabase.table("usuarios").select("*").ilike("usuario", req.usuario.strip()).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    user_info = res.data[0]
    if str(user_info["pin"]).strip() != str(req.pin).strip():
        raise HTTPException(status_code=400, detail="PIN incorrecto")
    
    return {
        "usuario": user_info["usuario"],
        "pin": req.pin,
        "rol_sistema": user_info.get("rol_sistema", "trabajador")
    }

@app.post("/api/cambiar-pin")
def cambiar_pin(req: CambiarPinRequest):
    res = supabase.table("usuarios").select("*").ilike("usuario", req.usuario.strip()).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    u_real = res.data[0]["usuario"]
    if str(res.data[0]["pin"]).strip() != str(req.pin_actual).strip():
        raise HTTPException(status_code=400, detail="El PIN actual es incorrecto")
    
    supabase.table("usuarios").update({"pin": req.pin_nuevo.strip()}).eq("usuario", u_real).execute()
    return {"mensaje": "PIN actualizado correctamente"}

@app.post("/api/mis-horas")
def mis_horas(req: LoginRequest):
    res_u = supabase.table("usuarios").select("*").ilike("usuario", req.usuario.strip()).execute()
    if not res_u.data or str(res_u.data[0]["pin"]).strip() != str(req.pin).strip():
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    u_real = res_u.data[0]["usuario"]
    res_a = supabase.table("asistencias").select("*").eq("usuario", u_real).execute()
    return {"registros": res_a.data}

@app.post("/api/marcar")
def marcar(req: LoginRequest):
    res_u = supabase.table("usuarios").select("*").ilike("usuario", req.usuario.strip()).execute()
    if not res_u.data or str(res_u.data[0]["pin"]).strip() != str(req.pin).strip():
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    u_real = res_u.data[0]["usuario"]
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    res_activo = supabase.table("asistencias").select("*").eq("usuario", u_real).is_("salida", "null").execute()
    
    if res_activo.data:
        activo = res_activo.data[0]
        if activo.get("receso_inicio") and not activo.get("receso_fin"):
            supabase.table("asistencias").update({"receso_fin": hora_actual}).eq("id", activo["id"]).execute()
        else:
            supabase.table("asistencias").update({"salida": hora_actual}).eq("id", activo["id"]).execute()
    else:
        supabase.table("asistencias").insert({
            "usuario": u_real,
            "entrada": hora_actual,
            "receso_inicio": None,
            "receso_fin": None,
            "salida": None,
            "es_continua": False
        }).execute()
        
    return {"mensaje": "Acción registrada con éxito"}

@app.post("/api/receso")
def receso(req: LoginRequest):
    res_u = supabase.table("usuarios").select("*").ilike("usuario", req.usuario.strip()).execute()
    if not res_u.data or str(res_u.data[0]["pin"]).strip() != str(req.pin).strip():
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    u_real = res_u.data[0]["usuario"]
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    res_activo = supabase.table("asistencias").select("*").eq("usuario", u_real).is_("salida", "null").execute()
    if not res_activo.data:
        raise HTTPException(status_code=400, detail="No tienes ningún turno activo para pausar.")
        
    activo = res_activo.data[0]
    if not activo.get("receso_inicio"):
        supabase.table("asistencias").update({"receso_inicio": hora_actual}).eq("id", activo["id"]).execute()
    elif not activo.get("receso_fin"):
        supabase.table("asistencias").update({"receso_fin": hora_actual}).eq("id", activo["id"]).execute()
    else:
        supabase.table("asistencias").update({"salida": hora_actual}).eq("id", activo["id"]).execute()
        supabase.table("asistencias").insert({
            "usuario": u_real,
            "entrada": hora_actual,
            "receso_inicio": None,
            "receso_fin": None,
            "salida": None,
            "es_continua": True
        }).execute()

    return {"mensaje": "Receso procesado con éxito"}

@app.get("/api/admin/datos")
def admin_datos():
    res_u = supabase.table("usuarios").select("*").execute()
    res_a = supabase.table("asistencias").select("*").execute()
    
    usuarios_dict = {}
    for u in res_u.data:
        usuarios_dict[u["usuario"]] = u
        
    return {"usuarios": usuarios_dict, "asistencias": res_a.data}

@app.post("/api/admin/registro-manual")
def admin_registro_manual(req: RegistroManualRequest):
    nombre_usuario = req.usuario.strip()
    res_u = supabase.table("usuarios").select("*").ilike("usuario", nombre_usuario).execute()
    
    if not res_u.data:
        u_creado = nombre_usuario.capitalize()
        tipo = "Gasolina" if u_creado.lower() == "planta" else "Horas"
        tarifa = 0.0 if tipo == "Gasolina" else 1.5
        supabase.table("usuarios").insert({
            "usuario": u_creado,
            "pin": "1234",
            "rol_sistema": "trabajador",
            "tipo_pago": tipo,
            "monto_fijo": 0.0,
            "tarifa_hora": tarifa,
            "area": "Operaciones"
        }).execute()
        usuario_real = u_creado
    else:
        usuario_real = res_u.data[0]["usuario"]

    supabase.table("asistencias").insert({
        "usuario": usuario_real,
        "entrada": req.entrada,
        "receso_inicio": None,
        "receso_fin": None,
        "salida": req.salida,
        "es_continua": req.es_continua
    }).execute()
    
    return {"mensaje": "Registro manual guardado con éxito"}

@app.post("/api/admin/editar-registro")
def admin_editar_registro(req: EditarRegistroRequest):
    res = supabase.table("asistencias").update({
        "entrada": req.entrada,
        "salida": req.salida
    }).eq("id", req.registro_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"mensaje": "Registro actualizado correctamente"}

@app.delete("/api/admin/eliminar-registro/{registro_id}")
def admin_eliminar_registro(registro_id: int):
    res = supabase.table("asistencias").delete().eq("id", registro_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"mensaje": "Registro eliminado"}

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    nuevo_nombre = req.usuario.strip()
    
    if req.usuario_antiguo and req.usuario_antiguo != nuevo_nombre:
        supabase.table("usuarios").delete().eq("usuario", req.usuario_antiguo).execute()
        
    payload = {
        "usuario": nuevo_nombre,
        "pin": req.pin,
        "rol_sistema": req.rol_sistema,
        "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo if req.tipo_pago.lower() == "fijo" else 0.0,
        "tarifa_hora": req.tarifa_hora if req.tipo_pago.lower() == "horas" else 0.0,
        "area": req.area
    }
    supabase.table("usuarios").upsert(payload).execute()
    return {"mensaje": "Usuario guardado correctamente"}

@app.delete("/api/admin/usuario/{usuario}")
def admin_eliminar_usuario(usuario: str):
    res = supabase.table("usuarios").delete().ilike("usuario", usuario).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}

@app.get("/api/admin/exportar-excel")
def exportar_excel():
    res_a = supabase.table("asistencias").select("*").execute()
    data_rows = []
    for r in res_a.data:
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
