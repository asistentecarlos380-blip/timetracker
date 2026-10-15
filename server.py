from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import json
import pandas as pd
import uvicorn
from datetime import datetime, timezone, timedelta

app = FastAPI()

DATA_FILE = "system_data.json"
TZ_VE = timezone(timedelta(hours=-4))

USUARIOS_PREDETERMINADOS = {
    "admin": {"pin": "9999", "tipo_pago": "Fijo", "monto_fijo": 300.0, "tarifa_hora": 0.0, "area": "Administración", "rol_sistema": "admin"},
    "user": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Ventas", "rol_sistema": "trabajador"},
    "Luz": {"pin": "1234", "tipo_pago": "Gasolina", "monto_fijo": 150.0, "tarifa_hora": 0.0, "area": "Planta", "rol_sistema": "trabajador"},
    "Ronald": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Ricardo": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Daniel": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Betzaida": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Lisander": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Brayan": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Gerson": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Matias": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Gestión", "rol_sistema": "trabajador"},
    "Planta": {"pin": "1234", "tipo_pago": "Horas", "monto_fijo": 150.0, "tarifa_hora": 1.5, "area": "Planta", "rol_sistema": "trabajador"}
}

def get_hora_actual():
    return datetime.now(TZ_VE).strftime("%Y-%m-%d %I:%M:%S %p")

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"usuarios": USUARIOS_PREDETERMINADOS, "asistencias": []}
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "usuarios" not in data or not data["usuarios"]:
                data["usuarios"] = USUARIOS_PREDETERMINADOS
            else:
                for u, info in USUARIOS_PREDETERMINADOS.items():
                    if u not in data["usuarios"]:
                        data["usuarios"][u] = info
            if "asistencias" not in data:
                data["asistencias"] = []
            return data
    except:
        data = {"usuarios": USUARIOS_PREDETERMINADOS, "asistencias": []}
        save_data(data)
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_fh_excel(str_fh):
    try:
        partes = str_fh.split(' ')
        f = partes[0].split('-')
        h = partes[1].split(':')
        ampm = partes[2]
        hh = int(h[0])
        if ampm == 'PM' and hh < 12: hh += 12
        if ampm == 'AM' and hh == 12: hh = 0
        return datetime(int(f[0]), int(f[1]), int(f[2]), hh, int(h[1]), int(h[2]))
    except:
        return None

class LoginReq(BaseModel):
    usuario: str
    pin: str

class UserReq(BaseModel):
    usuario_antiguo: str = ""
    usuario: str
    pin: str
    tipo_pago: str = "Horas"
    monto_fijo: float = 300.0
    tarifa_hora: float = 1.5
    area: str = "Gestión"
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
        "tipo_pago": u_info.get("tipo_pago", "Horas")
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
            return {"status": "salida", "mensaje": f"Turno finalizado (Salida) a las {ahora}"}

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
    return {"status": "entrada", "mensaje": f"Turno iniciado (Entrada) a las {ahora}"}

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
                reg["salida"] = ahora
                save_data(data)
                return {"status": "receso_inicio", "mensaje": f"Receso iniciado a las {ahora}. Turno en pausa."}
            elif reg.get("receso_fin") is None:
                reg["receso_fin"] = ahora
                nuevo_continua = {
                    "id": len(data["asistencias"]) + 1,
                    "usuario": user_key,
                    "entrada": ahora,
                    "receso_inicio": None,
                    "receso_fin": None,
                    "salida": None,
                    "es_continua": True
                }
                data["asistencias"].append(nuevo_continua)
                save_data(data)
                return {"status": "receso_fin", "mensaje": f"Receso finalizado a las {ahora}. ¡Continuando turno!"}
            else:
                raise HTTPException(status_code=400, detail="Ya registraste un receso en este turno")
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

@app.get("/api/admin/exportar-excel")
def exportar_excel():
    data = load_data()
    usuarios_list = list(data["usuarios"].keys())
    filas_excel = []
    
    for u in usuarios_list:
        fila_principal = {"Trabajador": u}
        fila_continua = {"Trabajador": f"{u} CONTINUA"}
        u_regs = [r for r in data["asistencias"] if r["usuario"].lower() == u.lower()]
        principales = [r for r in u_regs if not r.get("es_continua")]
        continuas = [r for r in u_regs if r.get("es_continua")]
        
        for r in principales:
            if r.get("entrada"):
                fecha = r["entrada"].split(' ')[0]
                fila_principal[f"{fecha} Entr"] = r["entrada"].split(' ')[1] + " " + r["entrada"].split(' ')[2]
                fila_principal[f"{fecha} Sal"] = r["salida"].split(' ')[1] + " " + r["salida"].split(' ')[2] if r.get("salida") else ""
                if r.get("salida"):
                    d1 = parse_fh_excel(r["entrada"])
                    d2 = parse_fh_excel(r["salida"])
                    if d1 and d2:
                        fila_principal[f"{fecha} Horas"] = round(max(0.0, (d2 - d1).total_seconds() / 3600.0), 2)

        for r in continuas:
            if r.get("entrada"):
                fecha = r["entrada"].split(' ')[0]
                fila_continua[f"{fecha} Entr"] = r["entrada"].split(' ')[1] + " " + r["entrada"].split(' ')[2]
                fila_continua[f"{fecha} Sal"] = r["salida"].split(' ')[1] + " " + r["salida"].split(' ')[2] if r.get("salida") else ""
                if r.get("salida"):
                    d1 = parse_fh_excel(r["entrada"])
                    d2 = parse_fh_excel(r["salida"])
                    if d1 and d2:
                        fila_continua[f"{fecha} Horas"] = round(max(0.0, (d2 - d1).total_seconds() / 3600.0), 2)

        filas_excel.append(fila_principal)
        filas_excel.append(fila_continua)

    df_matriz = pd.DataFrame(filas_excel)
    df_usuarios = pd.DataFrame([{
        "Usuario": u, "PIN": info.get("pin"), "Tipo_Pago": info.get("tipo_pago"),
        "Monto_Fijo": info.get("monto_fijo"), "Tarifa_Hora": info.get("tarifa_hora"),
        "Area": info.get("area"), "Rol_Sistema": info.get("rol_sistema")
    } for u, info in data["usuarios"].items()])

    df_asistencias = pd.DataFrame(data["asistencias"] if data["asistencias"] else [{"id": "", "usuario": "", "entrada": "", "receso_inicio": "", "receso_fin": "", "salida": ""}])

    file_path = "respaldo_nomina.xlsx"
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_matriz.to_excel(writer, sheet_name="Control Semanal", index=False)
        df_usuarios.to_excel(writer, sheet_name="Usuarios", index=False)
        df_asistencias.to_excel(writer, sheet_name="Asistencias Brutas", index=False)

    return FileResponse(file_path, filename=f"Control_Horas_Semanales_{datetime.now().strftime('%Y-%m-%d')}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/api/admin/importar-excel")
async def importar_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        temp_path = "temp_import.xlsx"
        with open(temp_path, "wb") as f:
            f.write(contents)

        df_usuarios = pd.read_excel(temp_path, sheet_name="Usuarios")
        df_asistencias = pd.read_excel(temp_path, sheet_name="Asistencias Brutas")

        usuarios_dict = {}
        for _, row in df_usuarios.iterrows():
            u_name = str(row["Usuario"])
            usuarios_dict[u_name] = {
                "pin": str(row["PIN"]),
                "tipo_pago": str(row["Tipo_Pago"]),
                "monto_fijo": float(row["Monto_Fijo"]) if pd.notna(row["Monto_Fijo"]) else 300.0,
                "tarifa_hora": float(row["Tarifa_Hora"]) if pd.notna(row["Tarifa_Hora"]) else 1.5,
                "area": str(row["Area"]) if pd.notna(row["Area"]) else "General",
                "rol_sistema": str(row["Rol_Sistema"]) if pd.notna(row["Rol_Sistema"]) else "trabajador"
            }

        asistencias_list = []
        for _, row in df_asistencias.iterrows():
            if pd.isna(row["usuario"]) or str(row["usuario"]).strip() == "":
                continue
            asistencias_list.append({
                "id": int(row["id"]) if pd.notna(row["id"]) else len(asistencias_list) + 1,
                "usuario": str(row["usuario"]),
                "entrada": str(row["entrada"]),
                "receso_inicio": str(row["receso_inicio"]) if pd.notna(row["receso_inicio"]) else None,
                "receso_fin": str(row["receso_fin"]) if pd.notna(row["receso_fin"]) else None,
                "salida": str(row["salida"]) if pd.notna(row["salida"]) else None,
                "es_continua": bool(row.get("es_continua", False)) if pd.notna(row.get("es_continua", False)) else False
            })

        nuevo_estado = {
            "usuarios": usuarios_dict,
            "asistencias": asistencias_list
        }
        save_data(nuevo_estado)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {"status": "ok", "mensaje": "Excel importado y datos restaurados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo Excel: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
