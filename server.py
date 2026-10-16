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

PERSONAL_FIJO = {
    "ADMIN": {"usuario": "ADMIN", "pin": "1234", "rol_sistema": "admin", "tipo_pago": "Fijo", "monto_fijo": 300.0, "tarifa_hora": 1.5, "area": "Gerencia"},
    "Ricardo": {"usuario": "Ricardo", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Ronald": {"usuario": "Ronald", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Lisander": {"usuario": "Lisander", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Daniel": {"usuario": "Daniel", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Betzaida": {"usuario": "Betzaida", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Brayan": {"usuario": "Brayan", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Gerson": {"usuario": "Gerson", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Matias": {"usuario": "Matias", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Horas", "monto_fijo": 0.0, "tarifa_hora": 1.5, "area": "Operaciones"},
    "Planta": {"usuario": "Planta", "pin": "1234", "rol_sistema": "trabajador", "tipo_pago": "Gasolina", "monto_fijo": 0.0, "tarifa_hora": 0.5, "area": "Operaciones"}
}

HISTORIAL_INICIAL = [
    {"usuario": "Ronald", "entrada": "14-10-2026 05:52:00 PM", "salida": "15-10-2026 12:02:00 AM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "14-10-2026 03:40:00 PM", "salida": "15-10-2026 02:58:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "14-10-2026 12:32:00 PM", "salida": "14-10-2026 06:02:00 PM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "14-10-2026 12:32:00 PM", "salida": "14-10-2026 06:01:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "14-10-2026 12:00:00 PM", "salida": "15-10-2026 12:04:00 AM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "13-10-2026 05:35:00 PM", "salida": "14-10-2026 12:10:00 AM", "es_continua": False},
    {"usuario": "Gerson", "entrada": "13-10-2026 05:30:00 PM", "salida": "13-10-2026 11:13:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "13-10-2026 04:30:00 PM", "salida": "14-10-2026 02:09:00 AM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "13-10-2026 10:59:00 AM", "salida": "14-10-2026 12:10:00 AM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "13-10-2026 10:12:00 AM", "salida": "13-10-2026 06:03:00 PM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "13-10-2026 08:53:00 AM", "salida": "13-10-2026 06:01:00 PM", "es_continua": False},
    {"usuario": "Planta", "entrada": "12-10-2026 06:50:00 PM", "salida": "12-10-2026 11:55:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "12-10-2026 05:29:00 PM", "salida": "12-10-2026 11:21:00 PM", "es_continua": False},
    {"usuario": "Gerson", "entrada": "12-10-2026 05:15:00 PM", "salida": "12-10-2026 11:01:00 PM", "es_continua": False},
    {"usuario": "Matias", "entrada": "12-10-2026 03:22:00 PM", "salida": "12-10-2026 05:14:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "12-10-2026 03:21:00 PM", "salida": "13-10-2026 03:12:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "12-10-2026 11:09:00 AM", "salida": "13-10-2026 03:02:00 AM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "12-10-2026 11:00:00 AM", "salida": "13-10-2026 12:02:00 AM", "es_continua": False},
    {"usuario": "Matias", "entrada": "11-10-2026 03:50:00 PM", "salida": "11-10-2026 07:54:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "11-10-2026 03:32:00 PM", "salida": "12-10-2026 02:35:00 AM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "11-10-2026 11:45:00 AM", "salida": "11-10-2026 08:16:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "11-10-2026 10:20:00 AM", "salida": "11-10-2026 05:04:00 PM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "11-10-2026 10:14:00 AM", "salida": "11-10-2026 07:54:00 PM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "11-10-2026 10:14:00 AM", "salida": "11-10-2026 07:57:00 PM", "es_continua": False},
    {"usuario": "Matias", "entrada": "10-10-2026 06:15:00 PM", "salida": "10-10-2026 11:30:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "10-10-2026 04:30:00 PM", "salida": "10-10-2026 11:30:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "10-10-2026 02:02:00 PM", "salida": "10-10-2026 11:10:00 PM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "10-10-2026 12:55:00 PM", "salida": "10-10-2026 05:30:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "10-10-2026 11:10:00 AM", "salida": "10-10-2026 11:30:00 PM", "es_continua": False},
    {"usuario": "Gerson", "entrada": "10-10-2026 10:17:00 AM", "salida": "10-10-2026 05:16:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "09-10-2026 03:53:00 PM", "salida": "10-10-2026 12:31:00 AM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "09-10-2026 03:19:00 PM", "salida": "10-10-2026 02:35:00 AM", "es_continua": False},
    {"usuario": "Planta", "entrada": "09-10-2026 11:40:00 AM", "salida": "09-10-2026 05:20:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "09-10-2026 11:00:00 AM", "salida": "09-10-2026 06:00:00 PM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "09-10-2026 11:00:00 AM", "salida": "09-10-2026 05:47:00 PM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "09-10-2026 09:56:00 AM", "salida": "10-10-2026 02:35:00 AM", "es_continua": False},
    {"usuario": "Gerson", "entrada": "08-10-2026 05:39:00 PM", "salida": "08-10-2026 11:09:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "08-10-2026 11:36:00 AM", "salida": "09-10-2026 02:26:00 AM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "08-10-2026 11:03:00 AM", "salida": "08-10-2026 05:17:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "08-10-2026 10:59:00 AM", "salida": "09-10-2026 12:02:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "08-10-2026 09:13:00 AM", "salida": "08-10-2026 06:08:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "07-10-2026 05:40:00 PM", "salida": "07-10-2026 11:58:00 PM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "07-10-2026 03:09:00 PM", "salida": "08-10-2026 03:42:00 AM", "es_continua": False},
    {"usuario": "Betzaida", "entrada": "07-10-2026 01:30:00 PM", "salida": "07-10-2026 05:43:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "07-10-2026 11:00:00 AM", "salida": "08-10-2026 12:01:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "07-10-2026 10:01:00 AM", "salida": "08-10-2026 03:16:00 AM", "es_continua": False},
    {"usuario": "Gerson", "entrada": "06-10-2026 05:59:00 PM", "salida": "06-10-2026 11:07:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "06-10-2026 05:52:00 PM", "salida": "07-10-2026 12:00:00 AM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "06-10-2026 03:00:00 PM", "salida": "07-10-2026 02:42:00 AM", "es_continua": False},
    {"usuario": "Planta", "entrada": "06-10-2026 12:40:00 PM", "salida": "06-10-2026 06:20:00 PM", "es_continua": False},
    {"usuario": "Brayan", "entrada": "06-10-2026 11:15:00 AM", "salida": "06-10-2026 07:12:00 PM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "06-10-2026 11:00:00 AM", "salida": "07-10-2026 12:02:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "06-10-2026 08:54:00 AM", "salida": "06-10-2026 07:12:00 PM", "es_continua": False},
    {"usuario": "Ronald", "entrada": "05-10-2026 06:36:00 PM", "salida": "06-10-2026 12:01:00 AM", "es_continua": False},
    {"usuario": "Daniel", "entrada": "05-10-2026 04:30:00 PM", "salida": "06-10-2026 03:24:00 AM", "es_continua": False},
    {"usuario": "Ricardo", "entrada": "05-10-2026 01:15:00 PM", "salida": "06-10-2026 03:24:00 AM", "es_continua": False},
    {"usuario": "Lisander", "entrada": "05-10-2026 12:00:00 PM", "salida": "06-10-2026 12:02:00 AM", "es_continua": False}
]

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
            
            patch_ui = """
            <script>
            document.addEventListener("DOMContentLoaded", () => {
                // 1. Tuerca global en panel admin
                const headerActions = document.querySelector('header') || document.querySelector('.flex.justify-between') || document.querySelector('#panel-admin');
                if (headerActions && !document.getElementById('btn-config-global')) {
                    const btnConfig = document.createElement('button');
                    btnConfig.id = 'btn-config-global';
                    btnConfig.className = 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white p-2.5 rounded-lg text-sm flex items-center justify-center shadow transition ml-2 border border-slate-700';
                    btnConfig.title = 'Configuración Global de Tarifas';
                    btnConfig.innerHTML = '<i class="fas fa-cog"></i>';
                    btnConfig.onclick = abrirModalConfigGlobal;
                    
                    const btnExcel = document.querySelector('button:has(.fa-file-excel)') || document.querySelector('#exportar-excel') || headerActions.querySelector('button');
                    if (btnExcel && btnExcel.parentNode) {
                        btnExcel.parentNode.insertBefore(btnConfig, btnExcel.nextSibling);
                    }
                }

                // 2. Control estricto de vistas: Administrador vs Trabajador
                setTimeout(() => {
                    const esAdmin = document.body.textContent.includes('Panel de Administración') || 
                                    document.body.textContent.includes('Personal Registrado y Tarifas') ||
                                    document.querySelector('button:has(.fa-file-excel)') !== null;

                    if (esAdmin) {
                        // Cuadro de nómina general solo en admin
                        const seccionNomina = document.querySelector('#resumen-horas') || document.querySelector('div:has(table)') || document.querySelector('.overflow-x-auto');
                        if (seccionNomina && !document.getElementById('cuadro-total-nomina-general')) {
                            const contenedorTotal = document.createElement('div');
                            contenedorTotal.id = 'cuadro-total-nomina-general';
                            contenedorTotal.className = 'mb-4 p-4 bg-slate-900 border border-emerald-500/50 rounded-xl flex items-center justify-between shadow-xl';
                            contenedorTotal.innerHTML = `
                                <div class="flex items-center gap-3">
                                    <div class="bg-emerald-500/20 p-3 rounded-lg text-emerald-400 text-xl">
                                        <i class="fas fa-wallet"></i>
                                    </div>
                                    <div>
                                        <h4 class="text-xs uppercase font-bold text-slate-400">Nómina Total a Pagar (General)</h4>
                                        <p class="text-xs text-slate-500">Suma total incluyendo administradores, personal y planta</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <span id="monto-total-nomina-general" class="text-2xl font-black text-emerald-400">$0.00</span>
                                    <button onclick="calcularSumaTotalNomina()" class="block text-xs text-emerald-400 hover:underline mt-1">Actualizar Total</button>
                                </div>
                            `;
                            seccionNomina.parentNode.insertBefore(contenedorTotal, seccionNomina);
                            calcularSumaTotalNomina();
                        }
                        
                        // Enriquecer tabla personal (espacio al lado del área, iconos limpios)
                        enriquecerTablaPersonalAdmin();
                    } else {
                        // ELIMINAR CUADRO DE NÓMINA TOTAL EN PANEL TRABAJADOR
                        const cuadroTrabajador = document.getElementById('cuadro-total-nomina-general');
                        if (cuadroTrabajador) cuadroTrabajador.remove();
                    }
                }, 500);

                // 3. Simulador de cobro trabajador en su menú
                const observerTrabajador = new MutationObserver(() => {
                    const dropdownMenu = document.querySelector('#menu-config-trabajador') || document.querySelector('.dropdown-menu') || document.querySelector('[role="menu"]') || document.querySelector('.absolute.right-0.mt-2');
                    if (dropdownMenu && !document.getElementById('simulador-cobro-btn')) {
                        if (!dropdownMenu.innerHTML.includes('Simulador')) {
                            const itemSimulador = document.createElement('a');
                            itemSimulador.id = 'simulador-cobro-btn';
                            itemSimulador.className = 'block px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white cursor-pointer flex items-center gap-2';
                            itemSimulador.innerHTML = '<i class="fas fa-calculator text-emerald-400"></i> Simulador de Cobro';
                            itemSimulador.onclick = abrirSimuladorTrabajador;
                            dropdownMenu.appendChild(itemSimulador);
                        }
                    }
                });
                observerTrabajador.observe(document.body, { childList: true, subtree: true });
            });

            window.calcularSumaTotalNomina = function() {
                const spanTotal = document.getElementById('monto-total-nomina-general');
                if (!spanTotal) return;

                let sumaPrecisa = 0;
                document.querySelectorAll('tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 5) {
                        const ultimoTexto = celdas[celdas.length - 1].textContent.trim();
                        if (ultimoTexto.startsWith('$')) {
                            const v = parseFloat(ultimoTexto.replace('$', ''));
                            if (!isNaN(v)) sumaPrecisa += v;
                        }
                    }
                });
                spanTotal.textContent = `$${sumaPrecisa.toFixed(2)}`;
            }

            function enriquecerTablaPersonalAdmin() {
                let usuariosActivos = new Set();
                document.querySelectorAll('tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 3) {
                        const nombreUsr = celdas[0].textContent.trim();
                        const salidaTxt = celdas[2].textContent.trim();
                        if (salidaTxt.toLowerCase().includes('curso') || salidaTxt.toLowerCase().includes('activo')) {
                            usuariosActivos.add(nombreUsr);
                        }
                    }
                });

                document.querySelectorAll('tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 6) {
                        // Cambiar texto de acciones por iconos limpios (Detalles, Editar, Borrar)
                        const celdaAcciones = celdas[celdas.length - 1];
                        if (celdaAcciones && !celdaAcciones.dataset.iconos) {
                            celdaAcciones.dataset.iconos = "true";
                            celdaAcciones.innerHTML = celdaAcciones.innerHTML
                                .replace(/Detalles/g, '<i class="fas fa-eye text-indigo-400 hover:text-indigo-300 cursor-pointer text-base mr-3" title="Detalles"></i>')
                                .replace(/Editar/g, '<i class="fas fa-edit text-emerald-400 hover:text-emerald-300 cursor-pointer text-base mr-3" title="Editar"></i>')
                                .replace(/Borrar/g, '<i class="fas fa-trash text-rose-500 hover:text-rose-400 cursor-pointer text-base" title="Borrar"></i>');
                        }

                        // Agregar estado Activo y botón Finalizar al lado del Área (aprovechando el espacio horizontal)
                        const nombrePersonal = celdas[0].textContent.trim();
                        if (usuariosActivos.has(nombrePersonal) && !tr.dataset.enriquecido) {
                            tr.dataset.enriquecido = "true";
                            const celdaArea = celdas[4]; 
                            if (celdaArea && !celdaArea.innerHTML.includes('Activo')) {
                                const areaTexto = celdaArea.textContent.trim();
                                celdaArea.innerHTML = `
                                    <div class="flex items-center gap-3">
                                        <span>${areaTexto}</span>
                                        <span class="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-full text-xs font-bold inline-flex items-center gap-1 shadow-sm">
                                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Activo
                                        </span>
                                        <button onclick="forzarCierreIndividual('${nombrePersonal}')" class="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-full text-xs font-bold shadow transition inline-flex items-center">
                                            Finalizar
                                        </button>
                                    </div>
                                `;
                            }
                        }
                    }
                });
            }

            async function forzarCierreIndividual(usuario) {
                // Confirmación obligatoria para evitar cierres por error
                if (!confirm(`¿Estás 100% seguro de finalizar el turno activo de ${usuario}?`)) return;
                try {
                    const res = await fetch('/api/admin/forzar-cierre', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ usuario: usuario })
                    });
                    const data = await res.json();
                    if (res.ok) {
                        alert(data.mensaje || "¡Turno finalizado con éxito!");
                        location.reload();
                    } else {
                        alert(data.detail || "Error al finalizar el turno.");
                    }
                } catch(e) {
                    alert("Error de conexión: " + e);
                }
            }

            function abrirModalConfigGlobal() {
                let modal = document.getElementById('modal-config-global');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'modal-config-global';
                    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4';
                    modal.innerHTML = `
                        <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 text-white shadow-2xl">
                            <h3 class="text-lg font-bold mb-4 flex items-center gap-2 text-emerald-400">
                                <i class="fas fa-sliders-h"></i> Configuración Global de Tarifas
                            </h3>
                            <p class="text-sm text-slate-400 mb-4">
                                Actualiza la tarifa por hora para <b>todo el personal al mismo tiempo</b>.
                            </p>
                            <div class="mb-4">
                                <label class="block text-xs uppercase font-bold text-slate-400 mb-1">Nueva Tarifa General ($ / hora)</label>
                                <input type="number" step="0.1" id="input-tarifa-global" value="1.5" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white">
                            </div>
                            <div class="flex justify-end gap-3 mt-6">
                                <button onclick="document.getElementById('modal-config-global').remove()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm">Cancelar</button>
                                <button onclick="guardarTarifaGlobal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-bold">Aplicar a Todos</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(modal);
                }
            }

            async function guardarTarifaGlobal() {
                const nuevaTarifa = parseFloat(document.getElementById('input-tarifa-global').value);
                if (isNaN(nuevaTarifa) || nuevaTarifa < 0) {
                    alert("Por favor ingresa una tarifa válida.");
                    return;
                }
                try {
                    const res = await fetch('/api/admin/configurar-tarifas-global', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ tarifa_hora: nuevaTarifa })
                    });
                    if (res.ok) {
                        alert("¡Tarifa global aplicada con éxito a todo el personal!");
                        document.getElementById('modal-config-global').remove();
                        location.reload();
                    } else {
                        alert("Hubo un error al actualizar las tarifas.");
                    }
                } catch(e) {
                    alert("Error de conexión: " + e);
                }
            }

            function abrirSimuladorTrabajador() {
                let modal = document.getElementById('modal-simulador-trabajador');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'modal-simulador-trabajador';
                    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4';
                    modal.innerHTML = `
                        <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-sm w-full p-6 text-white shadow-2xl">
                            <h3 class="text-lg font-bold mb-3 flex items-center gap-2 text-emerald-400">
                                <i class="fas fa-calculator"></i> Simulador de Cobro
                            </h3>
                            <p class="text-xs text-slate-400 mb-4">
                                Ingresa tu tarifa referencial y visualiza tu cálculo estimado.
                            </p>
                            
                            <div class="mb-4">
                                <label class="block text-xs uppercase font-bold text-slate-400 mb-1">1. Tarifa Referencial ($ / hora)</label>
                                <input type="number" step="0.1" id="input-tarifa-ref" value="1.5" oninput="calcularTotalSimulado()" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white font-bold text-lg">
                            </div>

                            <div class="mb-5 bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-center">
                                <span class="block text-xs uppercase font-bold text-slate-400 mb-1">2. Total Estimado a Cobrar</span>
                                <span id="resultado-simulado-total" class="text-2xl font-black text-emerald-400">$0.00</span>
                                <span id="info-horas-base" class="block text-xs text-slate-400 mt-1">Suma total de horas</span>
                            </div>

                            <div class="flex justify-end gap-3">
                                <button onclick="document.getElementById('modal-simulador-trabajador').remove()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-bold">Cerrar</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(modal);
                    calcularTotalSimulado();
                }
            }

            function calcularTotalSimulado() {
                const tarifaInput = document.getElementById('input-tarifa-ref');
                const resultadoSpan = document.getElementById('resultado-simulado-total');
                const infoHoras = document.getElementById('info-horas-base');
                if (!tarifaInput || !resultadoSpan) return;

                const tarifa = parseFloat(tarifaInput.value) || 0;
                let sumaHorasUnicas = 0;
                let filasVistas = new Set();
                
                document.querySelectorAll('tr').forEach(tr => {
                    const textoFila = tr.textContent;
                    const matchHrs = textoFila.match(/([0-9]+\.[0-9]+)\s*hrs/);
                    if (matchHrs && !filasVistas.has(textoFila)) {
                        filasVistas.add(textoFila);
                        const val = parseFloat(matchHrs[1]);
                        if (!isNaN(val) && val < 200) {
                            sumaHorasUnicas += val;
                        }
                    }
                });

                if (sumaHorasUnicas === 0) {
                    const elPeriodo = document.querySelector('#total-periodo, .total-periodo');
                    if (elPeriodo) {
                        const match = elPeriodo.textContent.match(/([0-9]+\.[0-9]+)/);
                        if (match) sumaHorasUnicas = parseFloat(match[1]) || 0;
                    }
                }

                const total = tarifa * sumaHorasUnicas;
                resultadoSpan.textContent = `$${total.toFixed(2)}`;
                infoHoras.textContent = `Suma de ${sumaHorasUnicas.toFixed(2)} hrs únicas`;
            }
            </script>
            """
            
            footer_v = '<div style="text-align:center; padding:15px; color:#64748b; font-size:13px; font-family:monospace;">Control de Asistencia — v1.1.0</div></body>'
            if "</body>" in content:
                content = content.replace("</body>", patch_ui + footer_v)
            return content
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

class ConfigGlobalRequest(BaseModel):
    tarifa_hora: float

class ForzarCierreRequest(BaseModel):
    usuario: str

@app.post("/api/login")
def login(req: LoginRequest):
    u = req.usuario.strip()
    p = str(req.pin).strip()
    if u.lower() == "admin" and p == "1234":
        return {"usuario": "ADMIN", "pin": "1234", "rol_sistema": "admin"}
    
    res = supabase.table("usuarios").select("*").ilike("usuario", u).execute()
    user_info = res.data[0] if res.data else None
    if not user_info:
        for k, v in PERSONAL_FIJO.items():
            if k.lower() == u.lower():
                user_info = v
                break
    if not user_info or str(user_info["pin"]).strip() != p:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"usuario": user_info["usuario"], "pin": req.pin, "rol_sistema": user_info.get("rol_sistema", "trabajador")}

@app.post("/api/admin/forzar-cierre")
def forzar_cierre(req: ForzarCierreRequest):
    u_real = req.usuario.strip().capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    try:
        res_activo = supabase.table("asistencias").select("*").ilike("usuario", u_real).is_("salida", "null").execute()
        if not res_activo.data:
            raise HTTPException(status_code=400, detail=f"No se encontró ningún turno activo para {u_real}")
        
        activo = res_activo.data[0]
        supabase.table("asistencias").update({"salida": hora_actual}).eq("id", activo["id"]).execute()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": f"¡Turno de {u_real} finalizado correctamente a las {hora_actual}!"}

@app.post("/api/cambiar-pin")
def cambiar_pin(req: CambiarPinRequest):
    try:
        supabase.table("usuarios").update({"pin": req.pin_nuevo.strip()}).ilike("usuario", req.usuario.strip()).execute()
    except Exception:
        pass
    return {"mensaje": "PIN actualizado"}

@app.post("/api/mis-horas")
def mis_horas(req: LoginRequest):
    u = req.usuario.strip()
    if u.lower() == "admin" and str(req.pin).strip() == "1234":
        try:
            res_a = supabase.table("asistencias").select("*").execute()
            return {"registros": res_a.data if res_a.data else []}
        except Exception:
            return {"registros": []}
            
    try:
        res_all = supabase.table("asistencias").select("*").execute()
        registros_filtrados = []
        if res_all.data:
            for r in res_all.data:
                usr_reg = str(r.get("usuario", "")).strip().lower()
                if usr_reg == u.lower():
                    registros_filtrados.append(r)
        return {"registros": registros_filtrados}
    except Exception:
        return {"registros": []}

@app.post("/api/marcar")
def marcar(req: LoginRequest):
    u = req.usuario.strip()
    u_real = "ADMIN" if u.lower() == "admin" else u.capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    try:
        res_activo = supabase.table("asistencias").select("*").ilike("usuario", u_real).is_("salida", "null").execute()
        if res_activo.data:
            activo = res_activo.data[0]
            if activo.get("receso_inicio") and not activo.get("receso_fin"):
                supabase.table("asistencias").update({"receso_fin": hora_actual}).eq("id", activo["id"]).execute()
            else:
                supabase.table("asistencias").update({"salida": hora_actual}).eq("id", activo["id"]).execute()
        else:
            supabase.table("asistencias").insert({
                "usuario": u_real, "entrada": hora_actual, "receso_inicio": None, "receso_fin": None, "salida": None, "es_continua": False
            }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Registrado con éxito"}

@app.post("/api/receso")
def receso(req: LoginRequest):
    u = req.usuario.strip()
    u_real = "ADMIN" if u.lower() == "admin" else u.capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    try:
        res_activo = supabase.table("asistencias").select("*").ilike("usuario", u_real).is_("salida", "null").execute()
        if not res_activo.data:
            raise HTTPException(status_code=400, detail="No hay turno activo")
        activo = res_activo.data[0]
        if not activo.get("receso_inicio"):
            supabase.table("asistencias").update({"receso_inicio": hora_actual}).eq("id", activo["id"]).execute()
        elif not activo.get("receso_fin"):
            supabase.table("asistencias").update({"receso_fin": hora_actual}).eq("id", activo["id"]).execute()
        else:
            supabase.table("asistencias").update({"salida": hora_actual}).eq("id", activo["id"]).execute()
            supabase.table("asistencias").insert({
                "usuario": u_real, "entrada": hora_actual, "receso_inicio": None, "receso_fin": None, "salida": None, "es_continua": True
            }).execute()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Receso procesado"}

@app.get("/api/admin/datos")
def admin_datos():
    usuarios_dict = PERSONAL_FIJO.copy()
    try:
        res_u = supabase.table("usuarios").select("*").execute()
        if res_u.data:
            for u in res_u.data:
                usuarios_dict[u["usuario"]] = u
    except Exception:
        pass

    asistencias_list = []
    try:
        res_a = supabase.table("asistencias").select("*").execute()
        if res_a.data and len(res_a.data) > 0:
            asistencias_list = res_a.data
        else:
            supabase.table("asistencias").insert(HISTORIAL_INICIAL).execute()
            res_a_nuevas = supabase.table("asistencias").select("*").execute()
            asistencias_list = res_a_nuevas.data if res_a_nuevas.data else HISTORIAL_INICIAL
    except Exception:
        asistencias_list = HISTORIAL_INICIAL

    return {"usuarios": usuarios_dict, "asistencias": asistencias_list}

@app.post("/api/admin/configurar-tarifas-global")
def configurar_tarifas_global(req: ConfigGlobalRequest):
    try:
        res_u = supabase.table("usuarios").select("usuario").execute()
        if res_u.data:
            for u in res_u.data:
                supabase.table("usuarios").update({"tarifa_hora": req.tarifa_hora}).eq("usuario", u["usuario"]).execute()
        for k in PERSONAL_FIJO:
            PERSONAL_FIJO[k]["tarifa_hora"] = req.tarifa_hora
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Tarifa global actualizada con éxito"}

@app.post("/api/admin/registro-manual")
def admin_registro_manual(req: RegistroManualRequest):
    try:
        supabase.table("asistencias").insert({
            "usuario": req.usuario.strip().capitalize(), "entrada": req.entrada, "receso_inicio": None, "receso_fin": None, "salida": req.salida, "es_continua": req.es_continua
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Guardado"}

@app.post("/api/admin/editar-registro")
def admin_editar_registro(req: EditarRegistroRequest):
    try:
        supabase.table("asistencias").update({"entrada": req.entrada, "salida": req.salida}).eq("id", req.registro_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Actualizado"}

@app.delete("/api/admin/eliminar-registro/{registro_id}")
def admin_eliminar_registro(registro_id: int):
    try:
        supabase.table("asistencias").delete().eq("id", registro_id).execute()
    except Exception:
        pass
    return {"mensaje": "Eliminado"}

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    payload = {
        "usuario": req.usuario.strip(), "pin": req.pin, "rol_sistema": req.rol_sistema, "tipo_pago": req.tipo_pago,
        "monto_fijo": req.monto_fijo if req.tipo_pago.lower() == "fijo" else 0.0,
        "tarifa_hora": req.tarifa_hora if req.tipo_pago.lower() == "horas" else 0.0, "area": req.area
    }
    try:
        supabase.table("usuarios").upsert(payload).execute()
    except Exception:
        pass
    return {"mensaje": "Guardado"}

@app.delete("/api/admin/usuario/{usuario}")
def admin_eliminar_usuario(usuario: str):
    try:
        supabase.table("usuarios").delete().ilike("usuario", usuario).execute()
    except Exception:
        pass
    return {"mensaje": "Eliminado"}

@app.get("/api/admin/exportar-excel")
def exportar_excel():
    try:
        res_a = supabase.table("asistencias").select("*").execute()
        data_rows = [{"ID": r["id"], "Usuario": r["usuario"], "Entrada": r["entrada"], "Salida": r["salida"] if r["salida"] else "En Curso", "Es Continua": "Sí" if r["es_continua"] else "No"} for r in res_a.data] if res_a.data else []
    except Exception:
        data_rows = []
    df = pd.DataFrame(data_rows)
    export_path = "reporte_asistencia.xlsx"
    df.to_excel(export_path, index=False)
    return FileResponse(export_path, filename="Reporte_Asistencia.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
