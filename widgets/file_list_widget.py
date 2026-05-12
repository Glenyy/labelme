"""
靠canvas右边的文件列表框，用于显示当前项目下的所有图片，点击图片可以切换到canvas上显示该图片
"""
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import os

class FileListWidget(ttk.Frame):
    def __init__(self, master, canvas_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.canvas_frame = canvas_frame
        self.file_list = []
        self._syncing = False  # 新增：防递归标志
        self.create_widget()

    def create_widget(self):
        # 标题
        name_frame = ttk.Frame(self, style='name.TFrame')
        name_frame.pack(fill=X, side=TOP)
        name_label = ttk.Label(name_frame, text='文件列表', style='name.TLabel')
        name_label.pack(fill=X, side=TOP)

        # 文件列表框
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, side=BOTTOM, expand=YES)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill=Y)
        self.file_list_box = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, width=40,
                                        exportselection=False)  # 绑定滚动条
        self.file_list_box.pack(fill=BOTH, side=LEFT, expand=YES)
        scrollbar.config(command=self.file_list_box.yview)  # 滚动条与列表框关联
        self.update_file_listbox()
        self.file_list_box.bind('<<ListboxSelect>>', self._on_file_select)  # 新增

    def update_file_listbox(self):  # 更新文件列表框显示的内容
        self.file_list = self.canvas_frame.image_path_dir  # 获取当前项目下的所有图片
        self.file_list_box.delete(0, tk.END)
        for path in self.file_list:
            # 获取path最末尾的文件名
            file_name = os.path.basename(path)
            self.file_list_box.insert('end', file_name)

    def select_index(self, index):
        """选中指定索引的文件行并确保可见（供canvas外部同步调用）"""
        if 0 <= index < len(self.file_list):
            self._syncing = True
            self.file_list_box.selection_clear(0, tk.END)
            self.file_list_box.selection_set(index)
            self.file_list_box.see(index)
            self._syncing = False

    def _on_file_select(self, event):
        # """点击文件列表项时切换到对应图片"""
        # if self._syncing:
        #     return
        # selected = self.file_list_box.curselection()
        # if selected:
        #     index = selected[0]
        #     if 0 <= index < len(self.canvas_frame.image_path_dir):
        #         self.canvas_frame.image_index = index
        #         file_path = self.canvas_frame.image_path_dir[index]
        #         self.canvas_frame.display_image(file_path)
        """点击文件列表项时切换到对应图片"""
        if self._syncing:
            return
        selected = self.file_list_box.curselection()
        if selected:
            index = selected[0]
            if 0 <= index < len(self.canvas_frame.image_path_dir):
                if not self.canvas_frame._maybe_save_before_switch():
                    # 用户取消，回退选中状态到之前显示的图片
                    self._syncing = True
                    self.select_index(self.canvas_frame.image_index)
                    self._syncing = False
                    return
                self.canvas_frame.image_index = index
                file_path = self.canvas_frame.image_path_dir[index]
                self.canvas_frame.display_image(file_path)
