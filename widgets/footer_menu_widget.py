import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import constants


class FooterMenuWidget(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master

        self.create_widgets()

    def create_widgets(self):
        self.create_mouse_position_label()

    def create_mouse_position_label(self):
        self.coordinate_label_frame = ttk.Frame(self)
        self.coordinate_label_frame.pack(side=BOTTOM, fill=X)
        self.coordinate_label = ttk.Label(self.coordinate_label_frame, text="labelme启动完了", style='mouse.TLabel')
        self.coordinate_label.pack(side=LEFT)

    def show_mouse_position(self, x, y):
        self.coordinate_label.config(text=f"Mouse is at: x={x}, y={y}")

    def show_mouse_in_button(self, tip):
        self.coordinate_label.config(text=tip)
