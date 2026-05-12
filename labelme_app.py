import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from widgets.header_menu_widget import HeaderMenuWidget
from widgets.tool_widget import ToolWidget
from widgets.canvas_widget import CanvasWidget
from widgets.footer_menu_widget import FooterMenuWidget
from widgets.label_and_file_widget import LabelAndFileWidget


class LabelmeApp(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master)
        super().__init__()
        self.master = master
        self.pack(fill=BOTH, expand=YES)  # 父容器要填满可用空间才能使footer_frame贴底

        self.main_frame = ttk.Frame(self)
        self.canvas_frame = CanvasWidget(master=self.main_frame, canvasWidgetEventListener=self)
        self.label_and_file_widget = LabelAndFileWidget(master=self.main_frame, canvas_frame=self.canvas_frame)

        self.header_frame = HeaderMenuWidget(master=self.master, canvas_frame=self.canvas_frame)
        # header_frame.pack(fill=X, side=TOP)

        self.tool_widget_frame = ToolWidget(master=self, toolEventListener=self, canvas_frame=self.canvas_frame,
                                            header_frame=self.header_frame)
        self.header_frame.set_tool_widget_frame(self.tool_widget_frame)
        self.tool_widget_frame.pack(fill=X, side=TOP)

        self.footer_frame = FooterMenuWidget(master=self)
        self.footer_frame.pack(fill=X, side=BOTTOM)

        self.main_frame.pack(expand=YES, fill=BOTH, side=TOP)
        self.canvas_frame.pack(expand=YES, fill=BOTH, side=LEFT)
        self.label_and_file_widget.pack(expand=False, fill=BOTH, side=RIGHT)
        self.canvas_frame.canvas.config(bg='#f0f0f0')  # 由于在canvas_widget中设置了canvas的背景色未生效，这里强制设置canvas背景色
        self.canvas_frame.set_tool_widget_frame(self.tool_widget_frame)
        self.canvas_frame.set_label_list_frame(self.label_and_file_widget.label_list_widget)  # 将标签列表关联canvas
        self.canvas_frame.set_file_list_frame(self.label_and_file_widget.file_list_widget)  # 将文件列表关联canvas

    def on_mouse_move(self, x, y):
        self.master.show_mouse_position(x, y)

    def on_mouse_in_button(self, tip):
        self.master.show_mouse_in_button(tip)


