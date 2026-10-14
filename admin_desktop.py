import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socketio
import threading
import requests
from datetime import datetime

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel Administrador - TimeTracker Pro")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f4f6f9")

        self.hourly_rate = 5.0
        self.workers_db = {}

        self.sio = socketio.Client()
        self.setup_socket_events()
        
        threading.Thread(target=self.connect_server, daemon=True).start()

        self.create_widgets()

    def connect_server(self):
        try:
            self.sio.connect('http://localhost:5000')
        except Exception as e:
            print(f"Error de conexión: {e}")

    def setup_socket_events(self):
        @self.sio.event
        def update_dashboard(data):
            self.root.after(0, lambda: self.refresh_data(data))

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#0d6efd", height=70, padx=20)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="🛡️ Panel Administrador - Control Quincenal", font=("Segoe UI", 14, "bold"), bg="#0d6efd", fg="white").pack(side=tk.LEFT, pady=15)

        # Botones administrativos superiores
        btn_header_frame = tk.Frame(header, bg="#0d6efd")
        btn_header_frame.pack(side=tk.RIGHT, pady=12)

        tk.Button(btn_header_frame, text="⚙️ Configurar Personal & PINs", bg="#212529", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=6, command=self.open_config_window).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_header_frame, text="🔍 Historial Fechas", bg="#ffc107", fg="black", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=6, command=self.open_history_window).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_header_frame, text="🔄 Cierre Quincena", bg="#dc3545", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=6, command=self.reset_fortnight).pack(side=tk.LEFT, padx=4)

        body = tk.Frame(self.root, bg="#f4f6f9", padx=20, pady=15)
        body.pack(fill=tk.BOTH, expand=True)

        # Barra de configuración de Tarifa por Hora
        top_bar = tk.Frame(body, bg="#f4f6f9")
        top_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_bar, text="Precio por Hora ($):", font=("Segoe UI", 10, "bold"), bg="#f4f6f9").pack(side=tk.LEFT, padx=(0, 5))
        self.rate_entry = ttk.Entry(top_bar, width=10)
        self.rate_entry.insert(0, "5.0")
        self.rate_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_bar, text="Actualizar Tarifa", bg="#198754", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=2, command=self.update_hourly_rate).pack(side=tk.LEFT, padx=10)

        # Tabla / Treeview principal
        columns = ("Puesto", "Trabajador", "Estado", "Hora de Entrada", "Horas Acumuladas", "Total a Pagar ($)")
        self.tree = ttk.Treeview(body, columns=columns, show="headings", height=13)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=170, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(body, bg="#f4f6f9")
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="🛑 Forzar Salida (Cerrar Turno Manual)", bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=8, command=self.force_logout).pack(side=tk.LEFT)

    def refresh_data(self, data):
        workers_state = data.get("workers_state", {})
        settings = data.get("settings", {})
        self.workers_db = data.get("workers_db", {})

        self.hourly_rate = settings.get("hourly_rate", 5.0)
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, str(self.hourly_rate))

        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for puesto, info in workers_state.items():
            status_text = "🟢 En Línea" if info["status"] == "Online" else ("☕ En Receso" if info["status"] == "Break" else "🔴 Desconectado")
            
            total_secs = info.get("accumulated_seconds", 0)
            if info["status"] == "Online" and info.get("start_timestamp"):
                total_secs += (datetime.now().timestamp() - info["start_timestamp"])
            
            hours = int(total_secs // 3600)
            minutes = int((total_secs % 3600) // 60)
            time_str = f"{hours}h {minutes}m"

            # Cálculo de pago total
            total_hours = total_secs / 3600.0
            total_pay = total_hours * self.hourly_rate
            pay_str = f"${total_pay:,.2f}"

            self.tree.insert("", tk.END, values=(
                puesto, 
                info["worker"], 
                status_text, 
                info["clock_in"] if info["clock_in"] else "--:--", 
                time_str,
                pay_str
            ))

    def update_hourly_rate(self):
        try:
            rate = float(self.rate_entry.get())
            res = requests.post("http://localhost:5000/api/update_rate", json={"rate": rate})
            if res.status_code == 200:
                messagebox.showinfo("Éxito", "Tarifa por hora actualizada correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo actualizar.")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido.")

    def force_logout(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un puesto de la tabla.")
            return
        
        item_values = self.tree.item(selected, "values")
        self.sio.emit("worker_action", {"puesto": item_values[0], "action": "FORCE_OUT"})
        messagebox.showinfo("Éxito", f"Salida forzada para {item_values[0]}.")

    def reset_fortnight(self):
        confirm = messagebox.askyesno("Cierre Quincenal", "¿Estás seguro de reiniciar los contadores a CERO para el nuevo periodo de pago? (El historial archivado se conserva).")
        if confirm:
            try:
                res = requests.post("http://localhost:5000/api/reset_cycle")
                if res.status_code == 200:
                    messagebox.showinfo("Éxito", "Ciclo quincenal reiniciado a cero.")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    def open_config_window(self):
        cfg_win = tk.Toplevel(self.root)
        cfg_win.title("Gestión de Trabajadores y PINs")
        cfg_win.geometry("450x450")
        cfg_win.configure(bg="#f4f6f9")

        tk.Label(cfg_win, text="Asignar Nombre y PIN por Puesto", font=("Segoe UI", 12, "bold"), bg="#f4f6f9", fg="#0d6efd").pack(pady=15)

        frame = tk.Frame(cfg_win, bg="#f4f6f9", padx=20)
        frame.pack(fill=tk.BOTH, expand=True)

        entries = {}
        for puesto, info in self.workers_db.items():
            sub = tk.Frame(frame, bg="#f4f6f9", pady=5)
            sub.pack(fill=tk.X)

            tk.Label(sub, text=puesto, width=10, anchor=tk.W, font=("Segoe UI", 9, "bold"), bg="#f4f6f9").pack(side=tk.LEFT)
            
            e_name = ttk.Entry(sub, width=15)
            e_name.insert(0, info["name"])
            e_name.pack(side=tk.LEFT, padx=5)

            e_pin = ttk.Entry(sub, width=8, show="*")
            e_pin.insert(0, info["pin"])
            e_pin.pack(side=tk.LEFT, padx=5)

            entries[puesto] = (e_name, e_pin)

        def save_all_config():
            for puesto, (e_name, e_pin) in entries.items():
                requests.post("http://localhost:5000/api/update_worker", json={
                    "puesto": puesto,
                    "name": e_name.get(),
                    "pin": e_pin.get()
                })
            messagebox.showinfo("Éxito", "Configuración de personal guardada.")
            cfg_win.destroy()

        tk.Button(cfg_win, text="Guardar Cambios", bg="#198754", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=8, command=save_all_config).pack(pady=15)

    def open_history_window(self):
        hist_win = tk.Toplevel(self.root)
        hist_win.title("Historial por Rango de Fechas")
        hist_win.geometry("750x450")
        hist_win.configure(bg="#f4f6f9")

        top_frame = tk.Frame(hist_win, bg="#f4f6f9", padx=15, pady=15)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Desde (YYYY-MM-DD):", bg="#f4f6f9", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        start_entry = ttk.Entry(top_frame, width=12)
        start_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        start_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Hasta (YYYY-MM-DD):", bg="#f4f6f9", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 5))
        end_entry = ttk.Entry(top_frame, width=12)
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        end_entry.pack(side=tk.LEFT, padx=5)

        def search_history():
            try:
                res = requests.get(f"http://localhost:5000/api/history?start_date={start_entry.get()}&end_date={end_entry.get()}")
                data = res.json()
                for r in tree_h.get_children():
                    tree_h.delete(r)
                for item in data:
                    tree_h.insert("", tk.END, values=(item["date"], item["time"], item["puesto"], item["worker"], item["action"]))
            except Exception as ex:
                messagebox.showerror("Error", f"{ex}")

        tk.Button(top_frame, text="🔍 Buscar", bg="#0d6efd", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=search_history).pack(side=tk.LEFT, padx=15)

        columns_h = ("Fecha", "Hora", "Puesto", "Trabajador", "Acción")
        tree_h = ttk.Treeview(hist_win, columns=columns_h, show="headings", height=15)
        for col in columns_h:
            tree_h.heading(col, text=col)
            tree_h.column(col, width=130, anchor=tk.CENTER)
        tree_h.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        search_history()

if __name__ == "__main__":
    root = tk.Tk()
    AdminDashboard(root)
    root.mainloop()