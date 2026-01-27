import tkinter as tk
import requests
import threading
import os
import time
import json
import subprocess
import ctypes
from PIL import Image, ImageTk

WIDTH, HEIGHT = 460, 330
INSTALL_DIR = r"C:\Raven"
VERSION_FILE = os.path.join(INSTALL_DIR, "version.json")
LOGO_PATH = "logo.png"
API_URL = "https://api.github.com/repos/MnaX-make/RavenClient/releases/latest"

BG = "magenta"
SHELL = "#0f0f14"
PANEL = "#141418"
TOPBAR = "#1b1b22"
ACCENT = "#3b3b3b"
TEXT = "#e6e6eb"
SUBTEXT = "#9a9aa3"

class RavenInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.geometry(f"{WIDTH}x{HEIGHT}+600+300")
        self.configure(bg=BG)
        self.attributes("-alpha", 0.98)
        self.wm_attributes("-transparentcolor", BG)
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.frames = {}
        self.draw_ui()
        self.fade_in()
        threading.Thread(target=self.update_watcher, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def fade_in(self):
        for i in range(21):
            self.attributes("-alpha", 0.05 + i / 20)
            self.update()
            time.sleep(0.02)

    def draw_ui(self):
        self.round_rect(6, 6, WIDTH - 6, HEIGHT - 6, 34, SHELL)
        self.round_rect(12, 12, WIDTH - 12, HEIGHT - 12, 30, PANEL)
        self.topbar_id = self.round_rect(20, 20, WIDTH - 20, 60, 22, TOPBAR)
        self.canvas.tag_bind(self.topbar_id, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.topbar_id, "<B1-Motion>", self.do_drag)

        x_offset = 30
        if os.path.exists(LOGO_PATH):
            img = Image.open(LOGO_PATH).resize((24, 24))
            self.title_logo = ImageTk.PhotoImage(img)
            self.canvas.create_image(x_offset, 40, image=self.title_logo, anchor="w")
            x_offset += 30

        self.title_text = self.canvas.create_text(x_offset, 40, text="Ｒａｖｅｎ Ｃｌｉｅｎｔ", fill=TEXT, font=("Segoe UI", 12), anchor="w")
        self.canvas.tag_bind(self.title_text, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.title_text, "<B1-Motion>", self.do_drag)

        self.round_button(WIDTH - 56, 26, 30, 30, "✕", self.hide_window)
        self.round_button(20, 90, 100, 28, "Install", lambda: self.show_frame("install"))
        self.round_button(130, 90, 100, 28, "How to Run", lambda: self.show_frame("setup"))

        self.frames["install"] = tk.Frame(self.canvas, width=WIDTH-40, height=HEIGHT-150, bg=PANEL)
        self.frames["install"].place(x=20, y=130)
        self.frames["setup"] = tk.Frame(self.canvas, width=WIDTH-40, height=HEIGHT-150, bg=PANEL)
        self.frames["setup"].place(x=20, y=130)
        self.frames["setup"].lower()

        self.status_text = tk.Label(self.frames["install"], text="Idle", fg=SUBTEXT, bg=PANEL, font=("Segoe UI", 10))
        self.status_text.place(relx=0.5, rely=0.05, anchor="n")

        self.progress_bg = tk.Canvas(self.frames["install"], width=WIDTH-140, height=18, bg="#1a1a1f", highlightthickness=0)
        self.progress_bg.place(relx=0.5, rely=0.25, anchor="n")
        self.progress_fill = self.progress_bg.create_rectangle(0,0,0,18, fill=ACCENT, width=0)

        self.install_btn = self.create_center_button(self.frames["install"], 140, 140, 40, "Install / Update", self.start_install)
        self.setup_label = tk.Label(self.frames["setup"], text="To run Raven Client:\n1. Open SetupRavenClient.reg in \"C:\\Raven\"\n2. Then Open VRChat\n3. Enjoy!", fg=TEXT, bg=PANEL, font=("Segoe UI", 12))
        self.setup_label.place(relx=0.5, rely=0.2, anchor="n")
        self.show_frame("install")

    def show_frame(self, name):
        for f in self.frames.values():
            f.lower()
        self.frames[name].lift()

    def start_drag(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def do_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        self.geometry(f"+{self.winfo_x()+dx}+{self.winfo_y()+dy}")
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def hide_window(self):
        self.withdraw()

    def round_rect(self, x1, y1, x2, y2, r, color):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.canvas.create_polygon(points, smooth=True, fill=color, outline=color)

    def round_button(self, x, y, w, h, text, command):
        rect = self.round_rect(x, y, x + w, y + h, 14, ACCENT)
        label = self.canvas.create_text(x + w//2, y + h//2, text=text, fill="white", font=("Segoe UI", 11))
        self.canvas.tag_bind(rect, "<Button-1>", lambda e: command())
        self.canvas.tag_bind(label, "<Button-1>", lambda e: command())
        return rect

    def create_center_button(self, parent, y, w, h, text, command):
        x = (WIDTH-40 - w)//2
        btn_canvas = tk.Canvas(parent, width=w, height=h, bg=PANEL, highlightthickness=0)
        btn_canvas.place(x=x, y=y)
        r = 20
        points = [r,0, w-r,0, w,0, w,r, w,h-r, w,h, w-r,h, r,h, 0,h, 0,h-r, 0,r, 0,0]
        btn_shape = btn_canvas.create_polygon(points, smooth=True, fill=ACCENT, outline=ACCENT)
        btn_text = btn_canvas.create_text(w/2, h/2, text=text, fill="white", font=("Segoe UI", 12, "bold"))
        btn_canvas.tag_bind(btn_shape, "<Button-1>", lambda e: command())
        btn_canvas.tag_bind(btn_text, "<Button-1>", lambda e: command())
        return btn_canvas

    def start_install(self):
        threading.Thread(target=self.install_latest, daemon=True).start()

    def install_latest(self):
        os.makedirs(INSTALL_DIR, exist_ok=True)
        self.status_text.config(text="Downloading...")
        try:
            data = requests.get(API_URL).json()
            assets = data["assets"]
            total = sum(a["size"] for a in assets)
            done = 0
            for asset in assets:
                r = requests.get(asset["browser_download_url"], stream=True)
                path = os.path.join(INSTALL_DIR, asset["name"])
                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                            done += len(chunk)
                            self.progress_bg.coords(self.progress_fill, 0,0,int((done/total)*(WIDTH-140)),18)
            with open(VERSION_FILE, "w") as f:
                json.dump({"version": data["tag_name"]}, f)
            self.status_text.config(text="Installed")
        except:
            self.status_text.config(text="Install failed")

    def send_notification(self, title, message):
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

    def update_watcher(self):
        while True:
            try:
                latest = requests.get(API_URL).json()["tag_name"]
                local = None
                if os.path.exists(VERSION_FILE):
                    with open(VERSION_FILE) as f:
                        local = json.load(f)["version"]
                if local != latest:
                    self.deiconify()
                    self.show_frame("install")
                    self.status_text.config(text="New update available!")
                    self.send_notification("Raven Client Update", "New update available!\nOpen C:\\Raven to update.")
            except:
                self.status_text.config(text="Update check failed")
            time.sleep(120)

if __name__ == "__main__":
    RavenInstaller().mainloop()
