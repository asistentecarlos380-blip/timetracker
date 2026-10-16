from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import json

app = FastAPI()

SUPABASE_URL = "https://dvpfynkqtjwkmcndael.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2cGZ5bmtxdGp3a21jbmRhZWwiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTc5MjA4MzUwNywiZXhwIjoyMTA3NjU5NTA3fQ.7gjZWE3AbR1ta8grbzr-Xpdd5vugYm0KSFJ54giI89Y"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

PERSONAL_FIJO = {
    "ADMIN": {"usuario": "ADMIN", "pin": "1234", "rol_sistema": "admin", "tipo_pago": "Semanal", "monto_fijo": 150.0, "tarifa_hora": 150.0, "area": "Gerencia"},
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

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
            
            personal_json = json.dumps(PERSONAL_FIJO)
            
            patch_ui = """
            <script>
            window._dbPersonalGlobal = """ + personal_json + """;

            document.addEventListener("DOMContentLoaded", () => {
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

                if (window.alert && !window._alertaNeutralizada) {
                    window._alertaNeutralizada = true;
                    const alertaOriginal = window.alert;
                    window.alert = function(msg) {
                        if (typeof msg === 'string' && msg.includes('Selecciona ambas fechas')) {
                            return;
                        }
                        alertaOriginal(msg);
                    };
                }

                setInterval(() => {
                    document.querySelectorAll('input[type="number"]').forEach(input => {
                        if (input.step !== 'any') {
                            input.setAttribute('step', 'any');
                        }
                    });
                }, 400);

                const observerModalUsuario = new MutationObserver(() => {
                    document.querySelectorAll('select').forEach(sel => {
                        if (sel.innerHTML.includes('Horas') && !sel.innerHTML.includes('Semanal')) {
                            const opt = document.createElement('option');
                            opt.value = 'Semanal';
                            opt.textContent = 'Semanal';
                            sel.appendChild(opt);
                        }
                    });

                    const selectPago = document.querySelector('select[name="tipo_pago"]') || Array.from(document.querySelectorAll('select')).find(s => s.value === 'Semanal' || s.value === 'Fijo');
                    if (selectPago) {
                        const contenedorInput = selectPago.closest('.space-y-4') || selectPago.parentElement.parentElement;
                        if (contenedorInput) {
                            contenedorInput.querySelectorAll('label').forEach(lbl => {
                                if (lbl.textContent.toLowerCase().includes('fijo') || lbl.textContent.toLowerCase().includes('tarifa') || lbl.textContent.toLowerCase().includes('monto')) {
                                    if (selectPago.value === 'Semanal') {
                                        lbl.textContent = 'Monto Semanal ($)';
                                    } else if (selectPago.value === 'Horas') {
                                        lbl.textContent = 'Tarifa por Hora ($)';
                                    }
                                }
                            });
                        }
                    }
                });
                observerModalUsuario.observe(document.body, { childList: true, subtree: true });

                setTimeout(() => {
                    let inputsFecha = [];
                    document.querySelectorAll('input').forEach(el => {
                        if ((el.placeholder && el.placeholder.includes('dd/mm/aaaa')) || el.type === 'date' || el.id.includes('desde') || el.id.includes('hasta')) {
                            inputsFecha.push(el);
                        }
                    });

                    if (inputsFecha.length >= 2) {
                        const hoy = new Date();
                        const diaSemana = hoy.getDay();
                        const diffLunes = hoy.getDate() - diaSemana + (diaSemana === 0 ? -6 : 1);
                        const lunesSemana = new Date(new Date().setDate(diffLunes));
                        const domingoSemana = new Date(lunesSemana);
                        domingoSemana.setDate(lunesSemana.getDate() + 6);

                        const pad = function(n) { return n < 10 ? '0' + n : n; };
                        const formatDDMMYYYY = function(d) { return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear(); };

                        const lunesStr = formatDDMMYYYY(lunesSemana);
                        const domingoStr = formatDDMMYYYY(domingoSemana);

                        let inputDesde = inputsFecha[inputsFecha.length - 2];
                        let inputHasta = inputsFecha[inputsFecha.length - 1];

                        const setVal = function(el, val) {
                            if (el && !el.value) {
                                el.value = val;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        };

                        setVal(inputDesde, lunesStr);
                        setVal(inputHasta, domingoStr);

                        setTimeout(function() {
                            const btnCalcular = document.querySelector('button:has(.fa-calculator)') || Array.from(document.querySelectorAll('button')).find(function(el) { return el.textContent.includes('Calcular'); });
                            if (btnCalcular) {
                                try { btnCalcular.click(); } catch(err) {}
                            }
                        }, 300);
                    }
                }, 400);

                setTimeout(() => {
                    const esAdmin = document.body.textContent.includes('Panel de Administración') || 
                                    document.body.textContent.includes('Personal Registrado y Tarifas') ||
                                    document.querySelector('button:has(.fa-file-excel)') !== null;

                    if (esAdmin) {
                        enriquecerTablaPersonalAdmin();
                    }
                }, 500);

                setTimeout(() => {
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
                }, 1000);
            });

            function parsearFechaPersonalizada(str) {
                if(!str) return null;
                let partes = str.split(' ');
                if(partes.length < 3) return new Date(str);
                let f = partes[0].split('-');
                if(f.length !== 3) return new Date(str);
                let d = parseInt(f[0]), m = parseInt(f[1]), y = parseInt(f[2]);
                let h = partes[1].split(':');
                let hh = parseInt(h[0]), mm = parseInt(h[1]), ss = parseInt(h[2] || 0);
                let ampm = partes[2];
                if(ampm && ampm.toUpperCase() === 'PM' && hh < 12) hh += 12;
                if(ampm && ampm.toUpperCase() === 'AM' && hh === 12) hh = 0;
                return new Date(y, m-1, d, hh, mm, ss);
            }

            function enriquecerTablaPersonalAdmin() {
                let usuariosActivosInfo = {};
                
                document.querySelectorAll('tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 4) {
                        const nombreUsr = celdas[0].textContent.trim();
                        const entradaTxt = celdas[1].textContent.trim();
                        const salidaTxt = celdas[2].textContent.trim();
                        if (salidaTxt.toLowerCase().includes('curso') || salidaTxt.toLowerCase().includes('activo')) {
                            let fechaEntrada = parsearFechaPersonalizada(entradaTxt);
                            let horasAbierto = fechaEntrada ? (new Date() - fechaEntrada) / (1000 * 60 * 60) : 0;
                            usuariosActivosInfo[nombreUsr] = horasAbierto;
                        }
                    }
                });

                document.querySelectorAll('tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 6) {
                        const celdaAcciones = celdas[celdas.length - 1];
                        if (celdaAcciones && !celdaAcciones.dataset.iconos) {
                            celdaAcciones.dataset.iconos = "true";
                            const botones = celdaAcciones.querySelectorAll('button');
                            if (botones.length >= 3) {
                                let onclickDetalle = botones[0].getAttribute('onclick');
                                let onclickEditar = botones[1].getAttribute('onclick');
                                let onclickBorrar = botones[2].getAttribute('onclick');

                                celdaAcciones.innerHTML = '<div class="flex items-center justify-end gap-3"><i class="fas fa-eye text-indigo-400 hover:text-indigo-300 cursor-pointer text-base" onclick="' + onclickDetalle + '" title="Ver Historial"></i><i class="fas fa-edit text-emerald-400 hover:text-emerald-300 cursor-pointer text-base" onclick="' + onclickEditar + '" title="Editar"></i><i class="fas fa-trash text-rose-500 hover:text-rose-400 cursor-pointer text-base" onclick="' + onclickBorrar + '" title="Borrar"></i></div>';
                            }
                        }

                        const nombrePersonal = celdas[0].textContent.trim();
                        
                        if (celdas.length >= 4) {
                            let pagoTipoTxt = celdas[2] ? celdas[2].textContent.trim() : '';
                            if (pagoTipoTxt.toLowerCase() === 'semanal' || pagoTipoTxt.toLowerCase() === 'fijo') {
                                if (window._dbPersonalGlobal && window._dbPersonalGlobal[nombrePersonal]) {
                                    let montoSe = window._dbPersonalGlobal[nombrePersonal].monto_fijo || window._dbPersonalGlobal[nombrePersonal].tarifa_hora || 150;
                                    celdas[3].textContent = '$' + parseFloat(montoSe).toFixed(2);
                                }
                            }
                        }

                        if (usuariosActivosInfo[nombrePersonal] !== undefined && !tr.dataset.enriquecido) {
                            tr.dataset.enriquecido = "true";
                            const horasActivo = usuariosActivosInfo[nombrePersonal];
                            const esTurnoExtendido = horasActivo >= 10;
                            
                            const celdaArea = celdas[4]; 
                            if (celdaArea && !celdaArea.innerHTML.includes('Activo')) {
                                const areaTexto = celdaArea.textContent.trim();
                                celdaArea.innerHTML = '<div class="flex items-center gap-2 flex-wrap"><span>' + areaTexto + '</span><span class="px-2.5 py-0.5 ' + (esTurnoExtendido ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40') + ' rounded-full text-xs font-bold inline-flex items-center gap-1 shadow-sm"><span class="w-1.5 h-1.5 rounded-full ' + (esTurnoExtendido ? 'bg-amber-400 animate-ping' : 'bg-emerald-400 animate-pulse') + '"></span> ' + (esTurnoExtendido ? '⚠️ >10h Activo' : 'Activo') + '</span><button onclick="forzarCierreIndividual(\\'' + nombrePersonal + '\\')" class="px-2.5 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-full text-xs font-bold shadow transition inline-flex items-center">Finalizar</button></div>';
                            }
                        }
                    }
                });

                const botonCalcular = document.querySelector('button:has(.fa-calculator)') || Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Calcular Horas'));
                if (botonCalcular && !botonCalcular.dataset.modalAgregado) {
                    botonCalcular.dataset.modalAgregado = "true";
                    const eventoOriginal = botonCalcular.onclick;
                    botonCalcular.onclick = function(e) {
                        if (eventoOriginal) eventoOriginal.apply(this, arguments);
                        setTimeout(corregirCalculosSemanalesEnResumen, 200);
                        setTimeout(mostrarModalTotalGeneral, 400);
                    };
                }
            }

            function corregirCalculosSemanalesEnResumen() {
                document.querySelectorAll('#tabla-resumen-fechas tr, table tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 5) {
                        let trabajador = celdas[0].textContent.trim();
                        if (window._dbPersonalGlobal && window._dbPersonalGlobal[trabajador]) {
                            let usrData = window._dbPersonalGlobal[trabajador];
                            let tipoP = (usrData.tipo_pago || '').toLowerCase();
                            if (tipoP === 'semanal' || tipoP === 'fijo') {
                                let montoF = usrData.monto_fijo || usrData.tarifa_hora || 150.0;
                                celdas[3].textContent = '1 Semana';
                                celdas[4].textContent = '$' + parseFloat(montoF).toFixed(2);
                            }
                        }
                    }
                });
            }

            function mostrarModalTotalGeneral() {
                let totalGeneral = 0;
                let detalleHtml = '';

                document.querySelectorAll('#tabla-resumen-fechas tr').forEach(tr => {
                    const celdas = tr.querySelectorAll('td');
                    if (celdas.length >= 5) {
                        const trabajador = celdas[0].textContent.trim();
                        let pagoStr = celdas[4].textContent.trim().replace('$', '');
                        let valor = parseFloat(pagoStr) || 0;
                        
                        if (window._dbPersonalGlobal && window._dbPersonalGlobal[trabajador]) {
                            let usrData = window._dbPersonalGlobal[trabajador];
                            let tipoP = (usrData.tipo_pago || '').toLowerCase();
                            if (tipoP === 'semanal' || tipoP === 'fijo') {
                                valor = usrData.monto_fijo || usrData.tarifa_hora || 150.0;
                                celdas[4].textContent = '$' + valor.toFixed(2);
                            }
                        }

                        totalGeneral += valor;
                        detalleHtml += '<div class="flex justify-between border-b border-slate-800/60 py-1 px-2 text-xs"><span class="text-slate-200 font-medium">' + trabajador + '</span><span class="font-bold text-emerald-400">$' + valor.toFixed(2) + '</span></div>';
                    }
                });

                if (!detalleHtml) return;

                let modal = document.getElementById('modal-total-general-emergente');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'modal-total-general-emergente';
                    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4';
                    document.body.appendChild(modal);
                }

                modal.innerHTML = '<div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full p-5 text-white shadow-2xl animate-fade-in"><div class="flex justify-between items-center mb-2 border-b border-slate-800 pb-2"><h3 class="text-sm font-bold flex items-center gap-2 text-emerald-400"><i class="fas fa-file-invoice-dollar"></i> Resumen de Nómina y Total General</h3><button onclick="document.getElementById(\\'modal-total-general-emergente\\').remove()" class="text-slate-400 hover:text-white text-lg">&times;</button></div><p class="text-[11px] text-slate-400 mb-2">Desglose calculado para el período seleccionado:</p><div class="space-y-1 mb-3 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800 max-h-60 overflow-y-auto">' + detalleHtml + '</div><div class="bg-emerald-950/40 border border-emerald-500/40 rounded-xl p-3 flex justify-between items-center mb-4 shadow-inner"><span class="text-xs font-bold uppercase tracking-wider text-emerald-300">Total General a Pagar:</span><span class="text-xl font-black text-emerald-400">$' + totalGeneral.toFixed(2) + '</span></div><div class="flex justify-end"><button onclick="document.getElementById(\\'modal-total-general-emergente\\').remove()" class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-xs font-bold transition shadow-lg shadow-emerald-600/30">Cerrar Ventana</button></div></div>';
            }

            async function forzarCierreIndividual(usuario) {
                if (!confirm('¿Estás seguro de finalizar el turno activo de ' + usuario + '?')) return;
                try {
                    await fetch('/api/admin/forzar-cierre', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ usuario: usuario })
                    });
                    location.reload();
                } catch(e) {
                    location.reload();
                }
            }

            function abrirModalConfigGlobal() {
                let modal = document.getElementById('modal-config-global');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'modal-config-global';
                    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4';
                    modal.innerHTML = '<div class="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 text-white shadow-2xl"><h3 class="text-lg font-bold mb-4 flex items-center gap-2 text-emerald-400"><i class="fas fa-sliders-h"></i> Configuración Global de Tarifas</h3><p class="text-sm text-slate-400 mb-4">Actualiza la tarifa por hora para <b>todo el personal al mismo tiempo</b>.</p><div class="mb-4"><label class="block text-xs uppercase font-bold text-slate-400 mb-1">Nueva Tarifa General ($ / hora)</label><input type="number" step="any" id="input-tarifa-global" value="1.5" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white"></div><div class="flex justify-end gap-3 mt-6"><button onclick="document.getElementById(\\'modal-config-global\\').remove()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm">Cancelar</button><button onclick="guardarTarifaGlobal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-bold">Aplicar a Todos</button></div></div>';
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
                    const hoy = new Date();
                    const diaSemana = hoy.getDay();
                    const diffLunes = hoy.getDate() - diaSemana + (diaSemana === 0 ? -6 : 1);
                    const lunesSemana = new Date(new Date().setDate(diffLunes));
                    const domingoSemana = new Date(lunesSemana);
                    domingoSemana.setDate(lunesSemana.getDate() + 6);
                    const pad = function(n) { return n < 10 ? '0' + n : n; };
                    const formatDDMMYYYY = function(d) { return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear(); };

                    modal = document.createElement('div');
                    modal.id = 'modal-simulador-trabajador';
                    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4';
                    modal.innerHTML = '<div class="bg-slate-900 border border-slate-700 rounded-xl max-w-sm w-full p-6 text-white shadow-2xl"><h3 class="text-lg font-bold mb-3 flex items-center gap-2 text-emerald-400"><i class="fas fa-calculator"></i> Simulador de Cobro</h3><p class="text-xs text-slate-400 mb-3">Selecciona el rango de fechas y tu tarifa para calcular.</p><div class="grid grid-cols-2 gap-2 mb-3"><div><label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Desde</label><input type="text" id="sim-desde" value="' + formatDDMMYYYY(lunesSemana) + '" onchange="calcularTotalSimulado()" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-xs text-white"></div><div><label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Hasta</label><input type="text" id="sim-hasta" value="' + formatDDMMYYYY(domingoSemana) + '" onchange="calcularTotalSimulado()" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-xs text-white"></div></div><div class="mb-3"><label class="block text-xs uppercase font-bold text-slate-400 mb-1">Tarifa ($ / hora)</label><input type="number" step="any" id="input-tarifa-ref" value="1.5" oninput="calcularTotalSimulado()" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-bold text-sm"></div><div class="mb-4 bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-center"><span class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Total Estimado a Cobrar</span><span id="resultado-simulado-total" class="text-xl font-black text-emerald-400">$0.00</span><span id="info-horas-base" class="block text-[11px] text-slate-400 mt-1">Suma total de horas</span></div><div class="flex justify-end gap-2"><button onclick="document.getElementById(\\'modal-simulador-trabajador\\').remove()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-bold">Cerrar</button></div></div>';
                    document.body.appendChild(modal);
                    calcularTotalSimulado();
                }
            }

            function parsearFechaDMY(str) {
                if (!str) return null;
                let p = str.split('/');
                if (p.length !== 3) return null;
                return new Date(parseInt(p[2]), parseInt(p[1]) - 1, parseInt(p[0]));
            }

            function calcularTotalSimulado() {
                const tarifaInput = document.getElementById('input-tarifa-ref');
                const resultadoSpan = document.getElementById('resultado-simulado-total');
                const infoHoras = document.getElementById('info-horas-base');
                const simDesde = document.getElementById('sim-desde');
                const simHasta = document.getElementById('sim-hasta');
                if (!tarifaInput || !resultadoSpan || !simDesde || !simHasta) return;

                const tarifa = parseFloat(tarifaInput.value) || 0;
                let totalHorasPeriodo = 0;
                let filasVistas = new Set();

                document.querySelectorAll('tr').forEach(tr => {
                    const textoFila = tr.textContent;
                    const matchHrs = textoFila.match(/([0-9]+\.[0-9]+)\s*hrs/);
                    if (matchHrs && !filasVistas.has(textoFila)) {
                        filasVistas.add(textoFila);
                        const val = parseFloat(matchHrs[1]);
                        if (!isNaN(val) && val < 200) totalHorasPeriodo += val;
                    }
                });

                const total = tarifa * totalHorasPeriodo;
                resultadoSpan.textContent = '$' + total.toFixed(2);
                infoHoras.textContent = 'Suma de ' + totalHorasPeriodo.toFixed(2) + ' hrs del período seleccionado';
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
    
    for k, v in PERSONAL_FIJO.items():
        if k.lower() == u.lower() and str(v["pin"]).strip() == p:
            return {"usuario": v["usuario"], "pin": p, "rol_sistema": v.get("rol_sistema", "trabajador")}

    if supabase:
        try:
            res = supabase.table("usuarios").select("*").ilike("usuario", u).execute()
            user_info = res.data[0] if res.data else None
            if user_info and str(user_info.get("pin", "")).strip() == p:
                return {"usuario": user_info["usuario"], "pin": p, "rol_sistema": user_info.get("rol_sistema", "trabajador")}
        except Exception:
            pass

    raise HTTPException(status_code=400, detail="Credenciales inválidas")

@app.post("/api/admin/forzar-cierre")
def forzar_cierre(req: ForzarCierreRequest):
    u_real = req.usuario.strip().capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    if supabase:
        try:
            res_all = supabase.table("asistencias").select("*").ilike("usuario", u_real).execute()
            if res_all.data:
                for r in res_all.data:
                    if not r.get("salida"):
                        supabase.table("asistencias").update({"salida": hora_actual}).eq("id", r["id"]).execute()
        except Exception as e:
            print("Error al forzar cierre en Supabase:", e)

    return {"mensaje": f"Turno de {u_real} finalizado"}

@app.post("/api/cambiar-pin")
def cambiar_pin(req: CambiarPinRequest):
    u = req.usuario.strip()
    pin_actual = str(req.pin_actual).strip()
    pin_nuevo = str(req.pin_nuevo).strip()

    actualizado = False
    for k, v in PERSONAL_FIJO.items():
        if k.lower() == u.lower():
            if str(v["pin"]).strip() == pin_actual:
                PERSONAL_FIJO[k]["pin"] = pin_nuevo
                actualizado = True
            else:
                raise HTTPException(status_code=400, detail="PIN actual incorrecto")
            break

    if supabase:
        try:
            res = supabase.table("usuarios").select("*").ilike("usuario", u).execute()
            if res.data:
                user_info = res.data[0]
                if str(user_info.get("pin", "")).strip() == pin_actual:
                    supabase.table("usuarios").update({"pin": pin_nuevo}).ilike("usuario", u).execute()
                    actualizado = True
                elif not actualizado:
                    raise HTTPException(status_code=400, detail="PIN actual incorrecto")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e

    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"mensaje": "PIN actualizado con éxito"}

@app.post("/api/mis-horas")
def mis_horas(req: LoginRequest):
    u = req.usuario.strip()
    registros_filtrados = []
    
    if supabase:
        try:
            res_all = supabase.table("asistencias").select("*").execute()
            if res_all.data:
                for r in res_all.data:
                    usr_reg = str(r.get("usuario", "")).strip().lower()
                    if u.lower() == "admin" or usr_reg == u.lower():
                        registros_filtrados.append(r)
        except Exception as e:
            print("Error al obtener mis-horas desde Supabase:", e)

    return {"registros": registros_filtrados}

@app.post("/api/marcar")
def marcar(req: LoginRequest):
    u = req.usuario.strip()
    u_real = "ADMIN" if u.lower() == "admin" else u.capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    turno_abierto_id = None
    if supabase:
        try:
            res_all = supabase.table("asistencias").select("*").ilike("usuario", u_real).execute()
            if res_all.data:
                for r in res_all.data:
                    if not r.get("salida"):
                        turno_abierto_id = r["id"]
                        break
        except Exception:
            pass

    if turno_abierto_id and supabase:
        try:
            supabase.table("asistencias").update({"salida": hora_actual}).eq("id", turno_abierto_id).execute()
        except Exception as e:
            print("Error al marcar salida en Supabase:", e)
    else:
        nuevo_registro = {"usuario": u_real, "entrada": hora_actual, "receso_inicio": None, "receso_fin": None, "salida": None, "es_continua": False}
        if supabase:
            try:
                supabase.table("asistencias").insert(nuevo_registro).execute()
            except Exception as e:
                print("Error al insertar nueva entrada en Supabase:", e)
        
    return {"mensaje": "Registrado con éxito"}

@app.post("/api/receso")
def receso(req: LoginRequest):
    u = req.usuario.strip()
    u_real = "ADMIN" if u.lower() == "admin" else u.capitalize()
    hora_actual = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    
    if supabase:
        try:
            res_all = supabase.table("asistencias").select("*").ilike("usuario", u_real).execute()
            if res_all.data:
                for r in res_all.data:
                    if not r.get("salida"):
                        supabase.table("asistencias").update({"salida": hora_actual}).eq("id", r["id"]).execute()
                        break
        except Exception as e:
            print("Error al procesar receso en Supabase:", e)

    return {"mensaje": "Receso procesado y tiempo detenido"}

@app.get("/api/admin/datos")
def admin_datos():
    usuarios_dict = PERSONAL_FIJO.copy()
    if supabase:
        try:
            res_u = supabase.table("usuarios").select("*").execute()
            if res_u.data:
                for u in res_u.data:
                    tipo = str(u.get("tipo_pago", "")).lower()
                    if tipo in ["fijo", "semanal"]:
                        if not u.get("monto_fijo") or u.get("monto_fijo") == 0:
                            u["monto_fijo"] = u.get("tarifa_hora", 150.0)
                        if not u.get("tarifa_hora") or u.get("tarifa_hora") == 0:
                            u["tarifa_hora"] = u["monto_fijo"]
                    usuarios_dict[u["usuario"]] = u
        except Exception as e:
            print("Error al cargar usuarios desde Supabase:", e)

    asistencias_list = []
    if supabase:
        try:
            res_a = supabase.table("asistencias").select("*").execute()
            if res_a.data is not None:
                asistencias_list = res_a.data
        except Exception as e:
            print("Error al cargar asistencias desde Supabase:", e)

    return {"usuarios": usuarios_dict, "asistencias": asistencias_list}

@app.post("/api/admin/configurar-tarifas-global")
def configurar_tarifas_global(req: ConfigGlobalRequest):
    try:
        for k in PERSONAL_FIJO:
            PERSONAL_FIJO[k]["tarifa_hora"] = req.tarifa_hora
        if supabase:
            try:
                res_u = supabase.table("usuarios").select("usuario").execute()
                if res_u.data:
                    for u in res_u.data:
                        supabase.table("usuarios").update({"tarifa_hora": req.tarifa_hora}).eq("usuario", u["usuario"]).execute()
            except Exception as e:
                print("Error al configurar tarifa global en Supabase:", e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"mensaje": "Tarifa global actualizada con éxito"}

@app.post("/api/admin/registro-manual")
def admin_registro_manual(req: RegistroManualRequest):
    nuevo = {"usuario": req.usuario.strip().capitalize(), "entrada": req.entrada, "receso_inicio": None, "receso_fin": None, "salida": req.salida, "es_continua": req.es_continua}
    if supabase:
        try:
            supabase.table("asistencias").insert(nuevo).execute()
        except Exception as e:
            print("Error al insertar registro manual en Supabase:", e)
    return {"mensaje": "Guardado"}

@app.post("/api/admin/editar-registro")
def admin_editar_registro(req: EditarRegistroRequest):
    if supabase:
        try:
            supabase.table("asistencias").update({"entrada": req.entrada, "salida": req.salida}).eq("id", req.registro_id).execute()
        except Exception as e:
            print("Error al editar registro en Supabase:", e)
    return {"mensaje": "Actualizado"}

@app.delete("/api/admin/eliminar-registro/{registro_id}")
def admin_eliminar_registro(registro_id: int):
    if supabase:
        try:
            supabase.table("asistencias").delete().eq("id", registro_id).execute()
        except Exception as e:
            print("Error al eliminar registro en Supabase:", e)
    return {"mensaje": "Eliminado"}

@app.post("/api/admin/usuario")
def admin_guardar_usuario(req: UsuarioAdminRequest):
    tipo = req.tipo_pago.strip()
    val_monto = req.monto_fijo if req.monto_fijo > 0 else req.tarifa_hora
    
    if tipo.lower() in ["fijo", "semanal"]:
        m_fijo = val_monto if val_monto > 0 else 150.0
        t_hora = m_fijo
    elif tipo.lower() == "gasolina":
        m_fijo = 0.0
        t_hora = 0.5
    else:
        m_fijo = 0.0
        t_hora = req.tarifa_hora if req.tarifa_hora > 0 else 1.5

    payload = {
        "usuario": req.usuario.strip(),
        "pin": str(req.pin).strip(),
        "rol_sistema": req.rol_sistema,
        "tipo_pago": tipo,
        "monto_fijo": m_fijo,
        "tarifa_hora": t_hora,
        "area": req.area
    }
    
    PERSONAL_FIJO[req.usuario.strip()] = payload

    if supabase:
        try:
            if req.usuario_antiguo and req.usuario_antiguo.strip() != req.usuario.strip():
                supabase.table("usuarios").delete().ilike("usuario", req.usuario_antiguo.strip()).execute()
            
            supabase.table("usuarios").upsert(payload).execute()
        except Exception as e:
            print("Error al guardar usuario en Supabase:", e)
            
    return {"mensaje": "Guardado exitosamente"}

@app.delete("/api/admin/usuario/{usuario}")
def admin_eliminar_usuario(usuario: str):
    if usuario in PERSONAL_FIJO:
        del PERSONAL_FIJO[usuario]
    if supabase:
        try:
            supabase.table("usuarios").delete().ilike("usuario", usuario).execute()
        except Exception as e:
            print("Error al eliminar usuario en Supabase:", e)
    return {"mensaje": "Eliminado"}

@app.get("/api/admin/exportar-excel")
def exportar_excel():
    data_rows = []
    if supabase:
        try:
            res_a = supabase.table("asistencias").select("*").execute()
            if res_a.data:
                data_rows = [{"ID": r["id"], "Usuario": r["usuario"], "Entrada": r["entrada"], "Salida": r["salida"] if r["salida"] else "En Curso", "Es Continua": "Sí" if r["es_continua"] else "No"} for r in res_a.data]
        except Exception as e:
            print("Error al exportar excel desde Supabase:", e)
            
    df = pd.DataFrame(data_rows)
    export_path = "reporte_asistencia.xlsx"
    df.to_excel(export_path, index=False)
    return FileResponse(export_path, filename="Reporte_Asistencia.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
