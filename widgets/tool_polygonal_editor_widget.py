import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from widgets import imgdir
from utils.polygon_shape import PolygonShape
from tkinter import messagebox


class ToolPolygonalEditorEventListener:
    def on_mouse_in_button(self, tip):
        print('ToolPolygonalEditorEventListener')


class ToolPolygonalEditorWidget(ttk.Frame):
    def __init__(self, master, toolPolygonalEditorEventListener, canvas_frame, header_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.toolPolygonalEditorEventListener = toolPolygonalEditorEventListener
        self.canvas_frame = canvas_frame
        self.header_frame = header_frame

        self.create_polygon = 'create_polygon'
        self.edit_polygon = 'edit_polygon'
        self.is_creating_polygon = False

        self.create_widget()

    def create_widget(self):
        self.create_polygonal_editor_frame()

    def create_polygonal_editor_frame(self):
        self.polygonal_editor_frame = ttk.Frame(self, style='frame.TFrame')
        self.polygonal_editor_frame.pack(fill=BOTH, expand=True)

        # 创建 创建多边形按钮
        create_polygonal_img_path = os.path.join(imgdir, "objects.png")
        create_polygonal_img = Image.open(create_polygonal_img_path)
        create_polygonal_img.thumbnail((25, 25), Image.LANCZOS)
        self.create_polygonal_photo_img = ImageTk.PhotoImage(create_polygonal_img)  # 使用self防止图片对象被垃圾回收
        self.create_polygonal_button = ttk.Button(self.polygonal_editor_frame, text='创建多边形',
                                                  image=self.create_polygonal_photo_img, compound=TOP,
                                                  style='tool.TButton', takefocus=False, state=DISABLED,
                                                  command=lambda: self.update_current_operation(self.create_polygon))
        self.create_polygonal_button.bind('<Enter>', lambda event: self.on_mouse_in_button('开始绘制多边形'))
        self.create_polygonal_button.pack(fill=BOTH, side=LEFT, padx=(5, 0), pady=5)

        # 创建 编辑多边形按钮
        edit_polygonal_img_path = os.path.join(imgdir, "edit.png")
        edit_polygonal_img = Image.open(edit_polygonal_img_path)
        edit_polygonal_img.thumbnail((25, 25), Image.LANCZOS)
        self.edit_polygonal_photo_img = ImageTk.PhotoImage(edit_polygonal_img)  # 使用self防止图片对象被垃圾回收
        self.edit_polygonal_button = ttk.Button(self.polygonal_editor_frame, text='编辑多边形',
                                                image=self.edit_polygonal_photo_img, compound=TOP,
                                                style='tool.TButton', takefocus=False, state=DISABLED,
                                                command=lambda: self.update_current_operation(self.edit_polygon))
        self.edit_polygonal_button.bind('<Enter>', lambda event: self.on_mouse_in_button('移动、编辑选中的多边形'))
        self.edit_polygonal_button.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建 复制多边形按钮
        # copy_polygonal_img_path = os.path.join(imgdir, "copy.png")
        # copy_polygonal_img = Image.open(copy_polygonal_img_path)
        # copy_polygonal_img.thumbnail((25, 25), Image.LANCZOS)
        # self.copy_polygonal_photo_img = ImageTk.PhotoImage(copy_polygonal_img)  # 使用self防止图片对象被垃圾回收
        # self.copy_polygonal_button = ttk.Button(self.polygonal_editor_frame, text='复制多边形',
        #                                         image=self.copy_polygonal_photo_img, compound=TOP,
        #                                         style='tool.TButton', takefocus=False, state=DISABLED)
        # self.copy_polygonal_button.bind('<Enter>', lambda event: self.on_mouse_in_button('为选中的多边形创建副本'))
        # self.copy_polygonal_button.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建 删除多边形按钮
        delete_polygonal_img_path = os.path.join(imgdir, "cancel.png")
        delete_polygonal_img = Image.open(delete_polygonal_img_path)
        delete_polygonal_img.thumbnail((25, 25), Image.LANCZOS)
        self.delete_polygonal_photo_img = ImageTk.PhotoImage(delete_polygonal_img)  # 使用self防止图片对象被垃圾回收
        self.delete_polygonal_button = ttk.Button(self.polygonal_editor_frame, text='删除多边形',
                                                  image=self.delete_polygonal_photo_img, compound=TOP,
                                                  style='tool.TButton', takefocus=False, state=DISABLED,
                                                  command=self.delete_now_click_depiction)
        self.delete_polygonal_button.bind('<Enter>', lambda event: self.on_mouse_in_button('删除选中的多边形'))
        self.delete_polygonal_button.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建 撤销按钮
        undo_img_path = os.path.join(imgdir, "undo.png")
        undo_img = Image.open(undo_img_path)
        undo_img.thumbnail((25, 25), Image.LANCZOS)
        self.undo_photo_img = ImageTk.PhotoImage(undo_img)  # 使用self防止图片对象被垃圾回收
        self.undo_btn = ttk.Button(self.polygonal_editor_frame, text='撤销(U)', image=self.undo_photo_img, compound=TOP,
                                   style='tool.TButton', takefocus=False, state=DISABLED,
                                   command=self.canvas_frame.undo_edit_action)
        self.undo_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('撤销最近一次添加和编辑'))
        self.undo_btn.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建 调节亮度对比度按钮
        # color__img_path = os.path.join(imgdir, "color.png")
        # color_img = Image.open(color__img_path)
        # color_img.thumbnail((25, 25), Image.LANCZOS)
        # self.color_photo_img = ImageTk.PhotoImage(color_img)  # 使用self防止图片对象被垃圾回收
        # self.color_btn = ttk.Button(self.polygonal_editor_frame, text='亮度对比度(B)',
        #                             image=self.color_photo_img, compound=TOP,
        #                             style='tool.TButton', takefocus=False, state=DISABLED)
        # self.color_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('调节亮度和对比度'))
        # self.color_btn.pack(fill=BOTH, side=LEFT, padx=(0, 5), pady=5)

    def on_mouse_in_button(self, tip):
        # print("鼠标移动到按钮")
        self.toolPolygonalEditorEventListener.on_mouse_in_button(tip)

    def update_current_operation(self, operation):  # 这里的operation是文字
        if self.canvas_frame.current_operation is not None:  # 如果当前操作存在，则先解绑事件
            self.canvas_frame.current_operation.unbind_events()
        self.canvas_frame.current_operation_tip = operation  # 设置当前操作
        self.canvas_frame.set_current_operation()  # 创建相应的绘图对象

    def delete_now_click_depiction(self):
        # if self.canvas_frame.selected_depiction is not None:
        #     # 提示是否要删除
        #     response = messagebox.askyesno("删除图形", "确定要删除选中的图形吗？")
        #     if response:
        #         self.canvas_frame.selected_depiction.delete_myself()  # 调用选中图形的删除方法，删除选中的图形
        #         # 在shape即保存的现有的图形中找到selected_depiction已经删除的图形并移除
        #         for shape in self.canvas_frame.shape:
        #             if shape == self.canvas_frame.selected_depiction:
        #                 self.canvas_frame.shape.remove(shape)  # 从shape列表中移除选中的图形
        #         self.canvas_frame.selected_depiction = None
        #         self.delete_polygonal_button.config(state=DISABLED)
        #         self.canvas_frame.update_label_list()  # 新增
        #     else:
        #         return
        if self.canvas_frame.selected_depiction is not None:
            response = messagebox.askyesno("删除图形", "确定要删除选中的图形吗？")
            if response:
                shape = self.canvas_frame.selected_depiction
                # 推入撤销栈，记录删除位置和 shape 数据
                idx = self.canvas_frame.shape.index(shape)
                self.canvas_frame.push_edit_action({
                    'type': 'delete_shape',
                    'shape': shape,
                    'index': idx,
                })
                shape.unbind_edit_events()  # 清除画布上的残留事件绑定
                shape.delete_myself()
                self.canvas_frame.shape.remove(shape)
                self.canvas_frame.selected_depiction = None
                self.delete_polygonal_button.config(state=DISABLED)
                self.canvas_frame.update_label_list()
            else:
                return


