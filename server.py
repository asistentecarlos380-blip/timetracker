from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = "https://dvpfynkqtjwkmcndael.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a21jbmRhZWwiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyODkzNTczMSwiZXhwIjoyMDQ0NTExNzMxfQ.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a21jbmRhZWwiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyODkzNTczMSwiZXhwIjoyMDQ0NTExNzMxfQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PERSONAL_FIJO = {
    "ADMIN": {"usuario": "ADMIN", "pin": "1234", "rol_sistema": "admin", "tipo_pago": "Fijo", "tarifa": 300, "cargo": "Gerencia"},
    "Ricardo": {"usuario": "Ricardo", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Ronald": {"usuario": "Ronald", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Lisander": {"usuario": "Lisander", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Daniel": {"usuario": "Daniel", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Betzaida": {"usuario": "Betzaida", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Brayan": {"usuario": "Brayan", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Gerson": {"usuario": "Gerson", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Matias": {"usuario": "Matias", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "tarifa": 1.5, "cargo": "Operaciones"},
    "Planta": {"usuario": "Planta", "pin": "0000", "rol_sistema": "trabajador", "tipo_pago": "Gasolina", "tarifa": 0.5, "cargo": "Generador"}
}

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de Asistencia v1.1.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body { background-color: #0b0f19; color: #f3f4f6; font-family: ui-sans-serif, system-ui, sans-serif; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between">
    <div id="app" class="p-6 max-w-7xl mx-auto w-full">
        <header class="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
            <div>
                <h1 class="text-2xl font-bold tracking-wide text-emerald-400">Control de Asistencia <span class="text-xs bg-emerald-900 text-emerald-300 px-2 py-0.5 rounded-full">v1.1.0</span></h1>
                <p class="text-xs text-gray-400">Gestión de Turnos, Pausas y Nómina</p>
            </div>
            <div id="header-actions" class="flex items-center gap-3"></div>
        </header>
        <main id="main-content">
            <!-- Contenido Dinámico -->
        </main>
    </div>
    <footer class="text-center py-4 text-xs text-gray-500 border-t border-gray-800">
        Control de Asistencia v1.1.0 &copy; 2026 - Sistema Robusto de Gestión
    </footer>

    <script>
        const SUPABASE_URL = "https://dvpfynkqtjwkmcndael.supabase.co";
        const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a21jbmRhZWwiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyODkzNTczMSwiZXhwIjoyMDQ0NTExNzMxfQ.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a21jbmRhZWwiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyODkzNTczMSwiZXhwIjoyMDQ0NTExNzMxfQ";
        const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        let usuarioActual = JSON.parse(localStorage.getItem('usuario_actual')) || null;

        document.addEventListener("DOMContentLoaded", () => {
            renderizarApp();
        });

        function renderizarApp() {
            const headerActions = document.getElementById('header-actions');
            if (usuarioActual) {
                headerActions.innerHTML = `
                    <button onclick="abrirConfiguracion()" class="bg-gray-800 hover:bg-gray-700 p-2.5 rounded-xl text-gray-300 transition" title="Configuración"><i class="fa-solid fa-gear"></i></button>
                    <button onclick="cerrarSesion()" class="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-xl text-sm font-semibold transition shadow-lg shadow-red-900/30 flex items-center gap-2"><i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión</button>
                `;
                if (usuarioActual.rol_sistema === 'admin') {
                    renderizarPanelAdmin();
                } else {
                    renderizarPanelTrabajador();
                }
            } else {
                headerActions.innerHTML = '';
                renderizarLogin();
            }
        }

        function renderizarLogin() {
            const main = document.getElementById('main-content');
            main.innerHTML = `
                <div class="max-w-md mx-auto bg-gray-900/80 border border-gray-800 p-8 rounded-2xl shadow-2xl backdrop-blur-md mt-12">
                    <h2 class="text-xl font-bold mb-6 text-center text-emerald-400">Iniciar Sesión</h2>
                    <form onsubmit="handleLogin(event)" class="space-y-4">
                        <div>
                            <label class="block text-xs text-gray-400 mb-1 font-semibold uppercase">Usuario</label>
                            <input type="text" id="login-usuario" required class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1 font-semibold uppercase">PIN de Acceso</label>
                            <input type="password" id="login-pin" required class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500">
                        </div>
                        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl transition shadow-lg shadow-emerald-900/30">Ingresar al Sistema</button>
                    </form>
                </div>
            `;
        }

        function handleLogin(e) {
            e.preventDefault();
            const usr = document.getElementById('login-usuario').value.trim();
            const pin = document.getElementById('login-pin').value.trim();
            
            if (usr === "ADMIN" && pin === "1234") {
                usuarioActual = { usuario: "ADMIN", rol_sistema: "admin" };
            } else {
                usuarioActual = { usuario: usr, rol_sistema: "trabajador" };
            }
            localStorage.setItem('usuario_actual', JSON.stringify(usuarioActual));
            renderizarApp();
        }

        function cerrarSesion() {
            localStorage.removeItem('usuario_actual');
            usuarioActual = null;
            renderizarApp();
        }

        function renderizarPanelTrabajador() {
            const main = document.getElementById('main-content');
            main.innerHTML = `
                <div class="max-w-xl mx-auto bg-gray-900/80 border border-gray-800 p-8 rounded-2xl shadow-2xl text-center mt-12">
                    <h2 class="text-2xl font-bold mb-2">Bienvenido, <span class="text-emerald-400">${usuarioActual.usuario}</span></h2>
                    <p class="text-sm text-gray-400 mb-8">Selecciona una acción para registrar tu turno o pausa actual.</p>
                    <div class="grid grid-cols-2 gap-4">
                        <button onclick="fichar('entrada')" class="bg-emerald-600 hover:bg-emerald-500 py-4 px-6 rounded-xl font-bold text-lg shadow-lg shadow-emerald-900/30 transition flex items-center justify-center gap-2"><i class="fa-solid fa-play"></i> Fichar Entrada</button>
                        <button onclick="fichar('salida')" class="bg-red-600 hover:bg-red-500 py-4 px-6 rounded-xl font-bold text-lg shadow-lg shadow-red-900/30 transition flex items-center justify-center gap-2"><i class="fa-solid fa-stop"></i> Fichar Salida</button>
                    </div>
                </div>
            `;
        }

        function fichar(tipo) {
            alert(`Acción registrada exitosamente: ${tipo.toUpperCase()}`);
        }

        function renderizarPanelAdmin() {
            const main = document.getElementById('main-content');
            main.innerHTML = `
                <div class="space-y-8">
                    <!-- Resumen Financiero y Nómina -->
                    <div class="bg-gray-900/80 border border-gray-800 p-6 rounded-2xl flex justify-between items-center">
                        <div>
                            <h3 class="text-lg font-bold text-emerald-400">Resumen General de Nómina</h3>
                            <p class="text-xs text-gray-400">Incluye pagos por hora, sueldos fijos y gastos de gasolina (Planta).</p>
                        </div>
                        <button onclick="abrirModalNomina()" class="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-xl text-sm font-bold transition flex items-center gap-2"><i class="fa-solid fa-file-invoice-dollar"></i> Ver Desglose de Pagos</button>
                    </div>

                    <!-- Personal Registrado y Tarifas -->
                    <div class="bg-gray-900/80 border border-gray-800 rounded-2xl overflow-hidden">
                        <div class="p-6 border-b border-gray-800 flex justify-between items-center">
                            <h3 class="font-bold text-lg">Personal Registrado y Tarifas</h3>
                            <button class="bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded-lg text-xs font-bold"><i class="fa-solid fa-plus"></i> Nuevo</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse text-sm">
                                <thead>
                                    <tr class="bg-gray-800/50 text-gray-400 text-xs uppercase">
                                        <th class="p-4">Usuario</th>
                                        <th class="p-4">PIN</th>
                                        <th class="p-4">Pago</th>
                                        <th class="p-4">Tarifa</th>
                                        <th class="p-4">Cargo / Área</th>
                                        <th class="p-4 text-center">Estado / Forzar</th>
                                        <th class="p-4 text-right">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-800">
                                    <tr>
                                        <td class="p-4 font-semibold">Ricardo</td>
                                        <td class="p-4 text-gray-400">.... <i class="fa-solid fa-eye text-xs text-emerald-400"></i></td>
                                        <td class="p-4">Horas</td>
                                        <td class="p-4 text-emerald-400">$1.5</td>
                                        <td class="p-4 text-gray-400">Operaciones</td>
                                        <td class="p-4 text-center">
                                            <span class="bg-emerald-500/20 text-emerald-400 px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1"><i class="fa-solid fa-circle text-[8px] animate-pulse"></i> Activo</span>
                                            <button onclick="forzarSalida('Ricardo')" class="bg-red-600 hover:bg-red-500 p-1.5 rounded-lg text-white ml-2 text-xs" title="Forzar Salida"><i class="fa-solid fa-power-off"></i></button>
                                        </td>
                                        <td class="p-4 text-right space-x-2">
                                            <button class="text-gray-400 hover:text-emerald-400 p-1" title="Detalles"><i class="fa-solid fa-eye"></i></button>
                                            <button class="text-gray-400 hover:text-amber-400 p-1" title="Editar"><i class="fa-solid fa-pen-to-square"></i></button>
                                            <button class="text-gray-400 hover:text-red-400 p-1" title="Borrar"><i class="fa-solid fa-trash"></i></button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Asistencias Consolidadas por Día y Trabajador -->
                    <div class="bg-gray-900/80 border border-gray-800 rounded-2xl overflow-hidden">
                        <div class="p-6 border-b border-gray-800">
                            <h3 class="font-bold text-lg">Asistencias en Tiempo Real (Consolidado Diario)</h3>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse text-sm">
                                <thead>
                                    <tr class="bg-gray-800/50 text-gray-400 text-xs uppercase">
                                        <th class="p-4">Trabajador</th>
                                        <th class="p-4">Fecha de Jornada</th>
                                        <th class="p-4">Total Horas del Día</th>
                                        <th class="p-4 text-right">Detalle y Acciones</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-800">
                                    <tr>
                                        <td class="p-4 font-semibold">Ricardo</td>
                                        <td class="p-4">15-10-2026</td>
                                        <td class="p-4 text-emerald-400">8.50 hrs</td>
                                        <td class="p-4 text-right space-x-2">
                                            <button onclick="abrirDetalleDia('Ricardo', '15-10-2026')" class="bg-gray-800 hover:bg-gray-700 text-emerald-400 p-2 rounded-lg text-xs font-semibold inline-flex items-center gap-1"><i class="fa-solid fa-eye"></i> Ver Desglose</button>
                                            <button class="text-gray-400 hover:text-red-400 p-1" title="Borrar"><i class="fa-solid fa-trash"></i></button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Modal de Desglose de Pagos -->
                <div id="modal-nomina" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                    <div class="bg-gray-900 border border-gray-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl">
                        <h3 class="text-lg font-bold text-emerald-400 mb-4">Desglose Detallado de Nómina</h3>
                        <div class="space-y-3 text-sm max-h-96 overflow-y-auto pr-2">
                            <div class="flex justify-between border-b border-gray-800 pb-2">
                                <span>ADMIN (Fijo)</span>
                                <span class="font-bold text-emerald-400">$300.00</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-800 pb-2">
                                <span>Ricardo (117.27 hrs @ $1.5)</span>
                                <span class="font-bold text-emerald-400">$175.90</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-800 pb-2">
                                <span>Planta - Gasolina (16.42 hrs @ 1.4L/h × $0.5)</span>
                                <span class="font-bold text-emerald-400">$11.49</span>
                            </div>
                        </div>
                        <div class="mt-6 pt-4 border-t border-gray-800 flex justify-between items-center text-base font-bold">
                            <span>Total General Nómina:</span>
                            <span class="text-emerald-400 text-xl">$487.39</span>
                        </div>
                        <button onclick="cerrarModalNomina()" class="mt-6 w-full bg-gray-800 hover:bg-gray-700 py-2.5 rounded-xl text-sm font-semibold transition">Cerrar</button>
                    </div>
                </div>

                <!-- Modal de Detalle Diario de Horas -->
                <div id="modal-detalle-dia" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
                    <div class="bg-gray-900 border border-gray-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl">
                        <h3 id="modal-detalle-titulo" class="text-lg font-bold text-emerald-400 mb-4">Detalle de Jornada</h3>
                        <div class="space-y-3 text-sm">
                            <div class="bg-gray-800/50 p-3 rounded-xl border border-gray-800 flex justify-between">
                                <span class="text-gray-400">Entrada Turno:</span>
                                <span class="font-semibold">15-10-2026 08:00:00 AM</span>
                            </div>
                            <div class="bg-gray-800/50 p-3 rounded-xl border border-gray-800 flex justify-between">
                                <span class="text-gray-400">Pausas / Recesos:</span>
                                <span class="font-semibold">30 mins (1:00 PM - 1:30 PM)</span>
                            </div>
                            <div class="bg-gray-800/50 p-3 rounded-xl border border-gray-800 flex justify-between">
                                <span class="text-gray-400">Salida Turno:</span>
                                <span class="font-semibold">15-10-2026 05:00:00 PM</span>
                            </div>
                        </div>
                        <button onclick="cerrarDetalleDia()" class="mt-6 w-full bg-gray-800 hover:bg-gray-700 py-2.5 rounded-xl text-sm font-semibold transition">Cerrar</button>
                    </div>
                </div>
            `;
        }

        function abrirModalNomina() {
            document.getElementById('modal-nomina').classList.remove('hidden');
            document.getElementById('modal-nomina').classList.add('flex');
        }

        function cerrarModalNomina() {
            document.getElementById('modal-nomina').classList.remove('flex');
            document.getElementById('modal-nomina').classList.add('hidden');
        }

        function abrirDetalleDia(trabajador, fecha) {
            document.getElementById('modal-detalle-titulo').innerText = `Detalle de ${trabajador} (${fecha})`;
            document.getElementById('modal-detalle-dia').classList.remove('hidden');
            document.getElementById('modal-detalle-dia').classList.add('flex');
        }

        function cerrarDetalleDia() {
            document.getElementById('modal-detalle-dia').classList.remove('flex');
            document.getElementById('modal-detalle-dia').classList.add('hidden');
        }

        function forzarSalida(trabajador) {
            alert(`Turno finalizado a la fuerza para ${trabajador}`);
        }

        function abrirConfiguracion() {
            alert("Abriendo configuración del sistema...");
        }
    </script>
</body>
</html>
    """
