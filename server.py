import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI
import socketio
import uvicorn
import os
import json

# 1. Configuración de Socket.IO y FastAPI
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
app = socketio.ASGIApp(sio, app)

# Control de inactividad de 10 minutos para desconexiones
pending_disconnects = {}

async def monitor_offline_workers():
    while True:
        await asyncio.sleep(60) # Revisa cada 60 segundos
        now = datetime.now()
        for sid, disconnect_time in list(pending_disconnects.items()):
            if now - disconnect_time > timedelta(minutes=10):
                print(f"Turno cerrado automáticamente por 10 minutos de inactividad para sid: {sid}")
                # Aquí puedes agregar la lógica para actualizar tu JSON de asistencia si es necesario
                del pending_disconnects[sid]

@sio.event
async def connect(sid, environ):
    if sid in pending_disconnects:
        del pending_disconnects[sid]
    print(f"Trabajador conectado: {sid}")

@sio.event
async def disconnect(sid):
    pending_disconnects[sid] = datetime.now()
    print(f"Trabajador desconectado: {sid}")

# 2. Ejecución compatible con servidores locales y en la nube (Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)