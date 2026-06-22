class CanvasTruck:
    """Represents the graphical and logical state of a 2D truck with strict timestamps."""
    def __init__(self, canvas, t_id, ai_total_est, ai_load_est, cargo_info, start_x, sim_time_now):
        self.canvas = canvas
        self.t_id = t_id
        self.ai_total_est = ai_total_est
        self.ai_load_est = ai_load_est 
        self.cargo_info = cargo_info
        self.x = start_x
        self.y = 220 
        self.state = "QUEUE"
        
        self.t_arrival = sim_time_now
        self.t_start_load = None
        self.t_end_load = None
        self.t_exit = None
        
        self.trailer = canvas.create_rectangle(self.x, self.y-40, self.x+50, self.y-10, fill="#95A5A6", outline="#2C3E50")
        self.cabin = canvas.create_rectangle(self.x+52, self.y-25, self.x+72, self.y-10, fill="#ECF0F1", outline="#2C3E50")
        self.w1 = canvas.create_oval(self.x+5, self.y-15, self.x+20, self.y, fill="#212F3D")
        self.w2 = canvas.create_oval(self.x+30, self.y-15, self.x+45, self.y, fill="#212F3D")
        self.w3 = canvas.create_oval(self.x+55, self.y-15, self.x+70, self.y, fill="#212F3D")
        self.items = [self.trailer, self.cabin, self.w1, self.w2, self.w3]

    def move_to(self, target_x):
        if self.x < target_x:
            dx = min(5, target_x - self.x)
            self.x += dx
            for item in self.items: 
                self.canvas.move(item, dx, 0)
        return self.x >= target_x

    def set_loading_color(self):
        self.canvas.itemconfig(self.trailer, fill="#52BE80")

    def clear(self):
        for item in self.items: 
            self.canvas.delete(item)