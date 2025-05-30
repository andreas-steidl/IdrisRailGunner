import tkinter as tk
from tkinter import ttk
import time
import threading
import pygame
import os
from dotenv import load_dotenv


class RailgunTimerApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.overrideredirect(True)
        self.master.attributes('-topmost', True)
        self.master.geometry("200x100")
        self.master.configure(bg='black')

        self._offset_x = 0
        self._offset_y = 0
        self.master.bind('<Button-1>', self.click_window)
        self.master.bind('<B1-Motion>', self.drag_window)

        self.close_button = tk.Button(master, text="X", command=self.master.destroy, bd=0, bg='black', fg='gray', padx=5, pady=2)
        self.close_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.style = ttk.Style(master)
        self.style.theme_use('default')
        self.style.configure("Charge.Horizontal.TProgressbar", troughcolor='gray', background='green', borderwidth=0, relief='flat')
        self.style.configure("Cooldown.Horizontal.TProgressbar", troughcolor='gray', background='red', borderwidth=0, relief='flat')

        self.charge_label = tk.Label(master, text="Charge", bg='black', fg='white')
        self.charge_label.pack(pady=(10, 0))
        self.charge_progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", maximum=100,
                                               style="Charge.Horizontal.TProgressbar")
        self.charge_progress.pack(fill='x', padx=5, pady=(0, 5))

        self.cooldown_label = tk.Label(master, text="Ready", bg='black', fg='white')
        self.cooldown_label.pack()
        self.cooldown_progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", maximum=100,
                                                 style="Cooldown.Horizontal.TProgressbar")
        self.cooldown_progress.pack(fill='x', padx=5, pady=(0, 5))

        load_dotenv()
        self.cooldown_time = int(os.getenv("COOLDOWN_TIME", 20))
        self.charge_time = int(os.getenv("CHARGE_TIME", 20))

        self.charging = False
        self.cooling_down = False
        self.charge_start_time = None

        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_thread = threading.Thread(target=self.joystick_listener, daemon=True)
            self.joystick_thread.start()
        else:
            print("No joystick detected")

    def click_window(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def drag_window(self, event):
        x = self.master.winfo_pointerx() - self._offset_x
        y = self.master.winfo_pointery() - self._offset_y
        self.master.geometry(f'+{x}+{y}')

    def start_charge(self):
        if not self.charging and not self.cooling_down:
            self.charging = True
            self.charge_start_time = time.time()
            threading.Thread(target=self.update_charge_progress, daemon=True).start()

    def stop_charge(self):
        if self.charging:
            self.charging = False
            elapsed = time.time() - self.charge_start_time
            charge_percent = min(100, int((elapsed / self.charge_time) * 100))
            if charge_percent >= 100:
                self.overcharge()
            else:
                self.charge_progress['value'] = charge_percent
                self.charge_label.config(text=f"Charge: {charge_percent}%")
                self.start_cooldown()

    def overcharge(self):
        self.charge_progress['value'] = 0
        self.charge_label.config(text="OVERCHARGE!")
        self.start_cooldown()

    def update_charge_progress(self):
        blink_state = True
        while self.charging:
            elapsed = time.time() - self.charge_start_time
            charge_percent = min(100, int((elapsed / self.charge_time) * 100))
            if charge_percent >= 100:
                self.charging = False
                self.overcharge()
                return

            self.charge_progress['value'] = charge_percent
            self.charge_label.config(text=f"Charge: {charge_percent}%")

            if charge_percent >= 95:
                color = 'red' if blink_state else 'yellow'
                blink_state = not blink_state
            elif charge_percent >= 90:
                color = 'yellow'
            else:
                color = 'green'
            self.style.configure("Charge.Horizontal.TProgressbar", background=color)
            time.sleep(0.1)

    def start_cooldown(self):
        self.cooling_down = True
        for i in range(self.cooldown_time):
            percent = int(((i + 1) / self.cooldown_time) * 100)
            self.cooldown_progress['value'] = percent
            self.cooldown_label.config(text=f"Cooldown: {self.cooldown_time - i - 1}s")
            self.style.configure("Cooldown.Horizontal.TProgressbar", background='green')
            time.sleep(1)

        self.cooling_down = False
        self.cooldown_progress['value'] = 100
        self.style.configure("Cooldown.Horizontal.TProgressbar", background='gray')
        self.flash_cooldown_ready()

    def flash_cooldown_ready(self):
        self.cooldown_label.config(text="Ready")
        self.charge_progress['value'] = 0
        self.charge_label.config(text="Charge")

        blink_duration = 2  # seconds
        end_time = time.time() + blink_duration
        while time.time() < end_time:
            self.style.configure("Cooldown.Horizontal.TProgressbar", background='green')
            self.cooldown_label.config(text="Ready")
            time.sleep(0.1)
            self.style.configure("Cooldown.Horizontal.TProgressbar", background='gray')
            self.cooldown_label.config(text="Ready")
            time.sleep(0.1)

        self.cooldown_label.config(text="Ready")
        self.style.configure("Cooldown.Horizontal.TProgressbar", background='gray')
        self.style.configure("Charge.Horizontal.TProgressbar", background='green')

    def joystick_listener(self):
        holding = False
        while True:
            pygame.event.pump()
            if self.joystick.get_button(0):
                if not holding:
                    self.start_charge()
                    holding = True
            else:
                if holding:
                    self.stop_charge()
                    holding = False
            time.sleep(0.1)


if __name__ == "__main__":
    root = tk.Tk()
    app = RailgunTimerApp(root)
    root.mainloop()
