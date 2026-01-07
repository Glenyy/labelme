import os
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import constants
from PIL import Image, ImageTk
from pathlib import Path
from widgets.tool_file_widget import ToolFileWidget
from widgets.tool_polygonal_editor_widget import ToolPolygonalEditorWidget
from widgets.tool_adaptation_widget import ToolAdaptationWidget


class toolEventListener:
    def on_mouse_in_button(self, tip):
        print('ToolEventListener')

class ToolWidget(ttk.Frame):
    def __init__(self, master, toolEventListener, canvas_frame, header_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.toolEventListener = toolEventListener
        self.canvas_frame = canvas_frame
        self.header_frame = header_frame

        self.imgdir = Path(__file__).parent.parent / 'icons'  # 获取图标文件夹路径

        self.create_widget()

    def create_widget(self):
        self.create_tool_button()

    def create_tool_button(self):
        self.image_opr_frame = ttk.Frame(self, relief=GROOVE, borderwidth=0)
        self.image_opr_frame.pack(fill=BOTH, expand=YES, side=LEFT)

        self.tool_file_frame = ToolFileWidget(self.image_opr_frame, self, self.canvas_frame, self.header_frame)
        self.tool_file_frame.pack(fill=Y, side=LEFT, ipadx=0.5)

        self.tool_polygonal_editor_frame = ToolPolygonalEditorWidget(self.image_opr_frame, self, self.canvas_frame,
                                                                     self.header_frame)
        self.tool_polygonal_editor_frame.pack(fill=Y, side=LEFT)

        self.tool_adaptation_frame = ToolAdaptationWidget(self.image_opr_frame, self, self.canvas_frame)
        self.tool_adaptation_frame.pack(fill=Y, side=LEFT)

        self.tool_file_frame.set_tool_polygonal_editor_frame(self.tool_polygonal_editor_frame)
        self.tool_file_frame.set_tool_adaptation_frame(self.tool_adaptation_frame)

    def on_mouse_in_button(self, tip):
        # print("鼠标移动到按钮")
        self.toolEventListener.on_mouse_in_button(tip)

