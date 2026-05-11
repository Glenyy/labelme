import os
from widgets import imgdir
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from theme.styles import set_styles
from tkinter import messagebox


class ChooseLabelWindow(tk.Toplevel):
    def __init__(self, master, canvas_frame, label_list):
        super().__init__(master)
        self.master = master
        self.canvas_frame = canvas_frame
        self.label_list = label_list
        self.title("标注标签")

        # 设置窗口位置居中
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (300 // 2)
        self.geometry(f'300x275+{x}+{y}')

        # self.resizable(False, False)

        self.default_label_name = "输入标注标签名称"
        self.label_var = tk.StringVar()
        self.label_var.set(self.default_label_name)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

        self.create_widgets()

    def on_close(self):
        pass  # 禁用关闭窗口，必须要对多边形设置标注标签

    def create_widgets(self):
        # 标签输入框
        label_entry = ttk.Entry(self, width=50, style='label.TEntry', textvariable=self.label_var)
        if self.default_label_name == "输入标注标签名称":
            label_entry.config(foreground='grey')

        label_entry.pack(pady=(10, 0), padx=5, fill=X)

        def on_label_entry_click(event):
            if label_entry.get() == self.default_label_name:
                label_entry.delete(0, "end")
                label_entry.config(foreground='black')
        def on_label_entry_focus_out(event):
            if label_entry.get() == '':
                label_entry.insert(0, self.default_label_name)
                label_entry.config(foreground='grey')
        label_entry.bind('<FocusIn>', on_label_entry_click)
        label_entry.bind('<FocusOut>', on_label_entry_focus_out)

        # 按钮
        btn_frame = ttk.Frame(self, style='label.TFrame')
        btn_frame.pack(pady=(5, 0), padx=5, fill=X)
        ok_img_path = os.path.join(imgdir, "done.png")
        ok_img = Image.open(ok_img_path)
        ok_img.thumbnail((15, 15), Image.LANCZOS)
        self.ok_photo_img = ImageTk.PhotoImage(ok_img)  # 使用self防止图片对象被垃圾回收
        ok_btn = ttk.Button(btn_frame, text='确定', image=self.ok_photo_img, compound=LEFT, command=self.ok,
                            style='label.TButton', takefocus=False)
        # cancel_btn = ttk.Button(btn_frame, text='取消', command=self.cancel, style='label.TButton', takefocus=False)
        # cancel_btn.pack(side=RIGHT, padx=5)
        ok_btn.pack(side=RIGHT, padx=0)

        # 标签列表框
        list_frame = ttk.Frame(self, style='label.TFrame')
        list_frame.pack(fill=BOTH)
        label_list_box = tk.Listbox(list_frame, height=10)
        label_list_box.pack(pady=(5, 0), padx=5, fill=BOTH)
        for label in self.label_list:
            label_list_box.insert('end', label)

        def on_select(event):
            """获取选中的项目"""
            # 获取选中的索引
            selected_indices = label_list_box.curselection()
            if selected_indices:
                # 获取选中项的值
                selected_value = label_list_box.get(selected_indices[0])
                # 将该值传递到label_entry中
                label_entry.delete(0, "end")
                label_entry.insert(0, selected_value)
                label_entry.config(foreground='black')
        # 绑定选中事件
        label_list_box.bind('<<ListboxSelect>>', on_select)

    def ok(self):
        label_name = self.label_var.get()
        if label_name == self.default_label_name:
            # 提示用户输入标注标签名称
            messagebox.showwarning("警告", "请输入标注标签名称")
        else:
            # 将标注标签名称传递到canvas的list中
            for label in self.canvas_frame.label_list:
                if label == label_name:  # 标签已存在 则不需要重复存入列表
                    self.destroy()
                    return
                else:
                    continue
            self.canvas_frame.label_list.append(label_name)
            self.destroy()

    # def cancel(self):
    #     self.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    set_styles(ttk.Style())
    label_list = ['cat', 'dog', 'rabbit', 'bird']
    choose_label_window = ChooseLabelWindow(root, label_list)
    root.mainloop()





