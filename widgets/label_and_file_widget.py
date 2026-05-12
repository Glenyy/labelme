import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from widgets.file_list_widget import FileListWidget
from widgets.label_list_widget import LabelListWidget


class LabelAndFileWidget(ttk.Frame):
    def __init__(self, master, canvas_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.canvas_frame = canvas_frame

        self.create_widget()

    def create_widget(self):
        self.label_list_widget = LabelListWidget(master=self, canvas_frame=self.canvas_frame)
        self.label_list_widget.pack(fill=BOTH, side=TOP, expand=YES, pady=(0, 5))
        self.file_list_widget = FileListWidget(master=self, canvas_frame=self.canvas_frame)
        self.file_list_widget.pack(fill=BOTH, side=BOTTOM, expand=YES, pady=(0, 5))
