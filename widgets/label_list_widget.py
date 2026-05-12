"""
靠canvas右边的标签列表框，用于显示当前图片下的所有标注标签，点击标签可以切换标签为选中状态
"""
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *


class LabelListWidget(ttk.Frame):
    def __init__(self, master, canvas_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.canvas_frame = canvas_frame
        self._syncing = False
        self.create_widget()

    def create_widget(self):
        # 标题
        name_frame = ttk.Frame(self, style='name.TFrame')
        name_frame.pack(fill=X, side=TOP)
        name_label = ttk.Label(name_frame, text='标签列表', style='name.TLabel')
        name_label.pack(fill=X, side=TOP)

        # 标签列表框
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, side=BOTTOM, expand=YES)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill=Y)
        self.label_list_box = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, width=40,
                                         exportselection=False)
        self.label_list_box.pack(fill=BOTH, side=LEFT, expand=YES)
        scrollbar.config(command=self.label_list_box.yview)
        self.label_list_box.bind('<<ListboxSelect>>', self._on_label_select)

    def update_label_listbox(self):
        """从 canvas_frame.shape 刷新标签列表"""
        self._syncing = True
        self.label_list_box.delete(0, tk.END)
        for i, shape in enumerate(self.canvas_frame.shape):
            display = f"{i + 1}. {shape.label}" if shape.label else f"{i + 1}. {shape.shape_type}"
            self.label_list_box.insert('end', display)
        self._syncing = False

    def _on_label_select(self, event):
        """点击标签时选中对应的标注图形，进入编辑状态"""
        if self._syncing:
            return
        selected = self.label_list_box.curselection()
        if selected:
            index = selected[0]
            if 0 <= index < len(self.canvas_frame.shape):
                target_shape = self.canvas_frame.shape[index]
                # 切换到编辑模式
                if self.canvas_frame.current_operation_tip != 'edit_polygon':
                    self.canvas_frame.current_operation_tip = 'edit_polygon'
                    self.canvas_frame.set_current_operation()
                # 取消旧选中
                if self.canvas_frame.selected_depiction:
                    self.canvas_frame.selected_depiction.deselect()
                    self.canvas_frame.selected_depiction.unbind_edit_events()
                # 选中目标
                target_shape.is_select = True
                target_shape.bind_edit_events()
                self.canvas_frame.selected_depiction = target_shape
                self.canvas_frame.tool_widget_frame.tool_polygonal_editor_frame.delete_polygonal_button.config(state=tk.NORMAL)

# import ttkbootstrap as ttk
# import tkinter as tk
# from ttkbootstrap.constants import *
#
#
# class LabelListWidget(ttk.Frame):
#     def __init__(self, master, canvas_frame):
#         ttk.Frame.__init__(self, master)
#         super().__init__(master)
#         self.master = master
#         self.canvas_frame = canvas_frame
#         self.shape_label_list = []
#         self.create_widget()
#
#     def create_widget(self):
#         # 标题
#         name_frame = ttk.Frame(self, style='name.TFrame')
#         name_frame.pack(fill=X, side=TOP)
#         name_label = ttk.Label(name_frame, text='标签列表', style='name.TLabel')
#         name_label.pack(fill=X, side=TOP)
#
#         # 标签列表框
#         list_frame = ttk.Frame(self)
#         list_frame.pack(fill=BOTH, side=BOTTOM, expand=YES)
#         scrollbar = tk.Scrollbar(list_frame)
#         scrollbar.pack(side='right', fill=Y)
#         self.label_list_box = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, width=40)  # 绑定滚动条
#         self.label_list_box.pack(fill=BOTH, side=LEFT, expand=YES)
#         scrollbar.config(command=self.label_list_box.yview)  # 滚动条与列表框关联
#         self.update_label_listbox()
#
#     def update_label_listbox(self):  # 更新标签列表框显示的内容
#         self.label_list_box.delete(0, tk.END)
#         for label in self.shape_label_list:
#             self.label_list_box.insert('end', label)
