import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import random 
from datetime import datetime, timedelta

# --- IMPORTAMOS NUESTRAS CLASES DE LOS OTROS ARCHIVOS ---
from api_security import APISimulator
from ml_model import CongestionPredictor, CARGO_DATABASE
from truck import CanvasTruck

class SmartPortApp:
    """Main application handling layout, UI and physics loop."""
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Puerto Inteligente - San Antonio")
        self.root.geometry("950x800")
        self.root.configure(bg="#2C3E50")
        
        self.api = APISimulator()
        self.predictor = CongestionPredictor()
        self.truck_list = []
        self.truck_counter = 1000
        
        self.simulated_time = datetime.now().replace(hour=8, minute=0, second=0)
        self.last_real_time = time.time()
        
        self._setup_ui()
        self._update_loop()

    def _setup_ui(self):
        self.canvas = tk.Canvas(self.root, height=300, bg="#90A4AE", highlightthickness=0)
        self.canvas.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.clock_label = self.canvas.create_text(850, 30, text="Hora: 08:00:00", font=("Segoe UI", 12, "bold"), fill="black")
        
        self.canvas.create_rectangle(0, 200, 950, 300, fill="#37474F", outline="")
        self.canvas.create_rectangle(400, 150, 550, 210, fill="#F4D03F", outline="") 
        self.canvas.create_text(475, 130, text="ZONA DE PREDICCIÓN IA", font=("Segoe UI", 11, "bold"), fill="#1C2833")
        self.canvas.create_rectangle(20, 100, 40, 300, fill="#2874A6") 
        self.canvas.create_text(30, 80, text="ENTRADA", font=("Segoe UI", 10, "bold"), fill="#1A5276")
        self.canvas.create_rectangle(900, 100, 920, 300, fill="#1E8449") 
        self.canvas.create_text(910, 80, text="SALIDA", font=("Segoe UI", 10, "bold"), fill="#145A32")

        self.control_frame = tk.LabelFrame(self.root, text=" ⚙️ Variables Ambientales ", bg="#2C3E50", fg="#F1C40F", font=("Segoe UI", 10, "bold"))
        self.control_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)

        tk.Label(self.control_frame, text="🌤️ Clima Actual:", bg="#2C3E50", fg="white", font=("Segoe UI", 11)).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        self.var_clima = tk.StringVar()
        self.combo_clima = ttk.Combobox(self.control_frame, textvariable=self.var_clima, state="readonly", width=35, font=("Segoe UI", 10))
        self.combo_clima['values'] = ("1 - Despejado", "2 - Nublado", "3 - Lluvia", "4 - Tormenta", "5 - Nieve / Hielo")
        self.combo_clima.current(0)
        self.combo_clima.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        self.btn_frame = tk.Frame(self.root, bg="#2C3E50")
        self.btn_frame.pack(fill=tk.X, pady=10)
        
        self.spawn_btn = tk.Button(self.btn_frame, text="SIMULAR LLEGADA DE CAMIÓN", font=("Segoe UI", 11, "bold"),
                                   bg="#3498DB", fg="white", activebackground="#2980B9", relief=tk.FLAT, padx=20, pady=5, command=self.spawn_truck)
        self.spawn_btn.pack()

        self.bottom_frame = tk.Frame(self.root, bg="#2C3E50")
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.terminal = scrolledtext.ScrolledText(self.bottom_frame, width=50, bg="#1E1E1E", fg="#A3BE8C", font=("Consolas", 10), padx=10, pady=10, relief=tk.FLAT)
        self.terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.log("SISTEMA INICIALIZADO. ESPERANDO CAMIONES...")

        self.registry = scrolledtext.ScrolledText(self.bottom_frame, width=45, bg="#17202A", fg="#F4D03F", font=("Consolas", 10), padx=10, pady=10, relief=tk.FLAT)
        self.registry.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.registry.insert(tk.END, "====== REGISTRO HISTÓRICO ======\n\n")

    def log(self, msg):
        timestamp = self.simulated_time.strftime('%H:%M:%S')
        self.terminal.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.terminal.see(tk.END)

    def spawn_truck(self):
        self.truck_counter += 1
        t_id = f"Camión-{self.truck_counter}"
        
        cargo_code = random.randint(1, 4)
        cargo_name, cargo_unit = CARGO_DATABASE[cargo_code]
        cargo_qty = random.randint(10, 100)
        cargo_str = f"{cargo_qty} {cargo_unit} de {cargo_name}"
        
        val_clima = int(self.var_clima.get().split(" - ")[0])
        txt_clima = self.var_clima.get().split(" - ")[1]

        api_data = self.api.get_secure_weather_data(injected_weather=val_clima)
        ai_load_est = self.predictor.predict_load_time(api_data["weather"], cargo_code, cargo_qty)
        
        queue_delay_est = 0.0
        for t in self.truck_list:
            if t.state == "QUEUE":
                queue_delay_est += t.ai_load_est
            elif t.state == "LOADING":
                remaining_time = (t.t_start_load + timedelta(minutes=t.ai_load_est)) - self.simulated_time
                if remaining_time.total_seconds() > 0:
                    queue_delay_est += remaining_time.total_seconds() / 60.0
        
        transit_in_est = 8.2 
        transit_out_est = 9.8 
        ai_total_est = queue_delay_est + ai_load_est + transit_in_est + transit_out_est
        
        self.log(f"--- LLEGADA: {t_id} ---")
        self.log(f"    - Carga: {cargo_str}")
        self.log(f"    - Clima: {txt_clima}")
        self.log(f"    - Estimado Total IA: {ai_total_est:.1f} min.")
        
        new_truck = CanvasTruck(self.canvas, t_id, ai_total_est, ai_load_est, cargo_str, start_x=-80, sim_time_now=self.simulated_time)
        self.truck_list.append(new_truck)

    def _update_loop(self):
        current_real_time = time.time()
        delta_seconds = current_real_time - self.last_real_time
        self.last_real_time = current_real_time
        self.simulated_time += timedelta(minutes=(delta_seconds * 5.0))
        
        self.canvas.itemconfig(self.clock_label, text=f"Hora: {self.simulated_time.strftime('%H:%M:%S')}")
        
        for i, truck in enumerate(self.truck_list):
            if truck.state == "QUEUE":
                target_x = 410 if i == 0 else (410 - (i * 90))
                if truck.move_to(target_x) and i == 0:
                    truck.state = "LOADING"
                    truck.t_start_load = self.simulated_time
                    truck.set_loading_color()
                    self.log(f"SISTEMA: {truck.t_id} operando carga.")
                    
            elif truck.state == "LOADING":
                if self.simulated_time >= (truck.t_start_load + timedelta(minutes=truck.ai_load_est)):
                    truck.state = "DEPARTING"
                    truck.t_end_load = self.simulated_time
                    self.log(f">>> SALIDA: {truck.t_id} despejó zona verde.")
                    
            elif truck.state == "DEPARTING":
                if truck.move_to(1000):
                    truck.t_exit = self.simulated_time
                    
                    ingreso_mins = (truck.t_start_load - truck.t_arrival).total_seconds() / 60.0
                    carga_mins = (truck.t_end_load - truck.t_start_load).total_seconds() / 60.0
                    salida_mins = (truck.t_exit - truck.t_end_load).total_seconds() / 60.0
                    total_real = ingreso_mins + carga_mins + salida_mins

                    summary = f"🚛 {truck.t_id}\n"
                    summary += f"📦 Carga: {truck.cargo_info}\n"
                    summary += f"🤖 Total Estimado IA : {truck.ai_total_est:.1f} min\n"
                    summary += f"   [ DESGLOSE REAL ]\n"
                    summary += f"   ├ Ingreso y Fila: {ingreso_mins:.1f} min\n"
                    summary += f"   ├ Carga y Op.   : {carga_mins:.1f} min\n"
                    summary += f"   ├ Tránsito Exit : {salida_mins:.1f} min\n"
                    summary += f"   └ TOTAL REAL    : {total_real:.1f} min\n"
                    summary += "-" * 40 + "\n"
                    
                    self.registry.insert(tk.END, summary)
                    self.registry.see(tk.END) 

                    truck.clear()
                    self.truck_list.remove(truck)
                    
        self.root.after(16, self._update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartPortApp(root)
    root.mainloop()