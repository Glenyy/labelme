import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from widgets import imgdir
from utils.open_file import open_file
from utils.open_dir import open_dir
from utils.save_to_json import save_to_json


class ToolFileEventListener:
    def on_mouse_in_button(self, tip):
        print('ToolFileEventListener')


class ToolFileWidget(ttk.Frame):
    def __init__(self, master, toolFileDialogEventListener, canvas_frame, header_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.toolFileDialogEventListener = toolFileDialogEventListener
        self.canvas_frame = canvas_frame
        self.header_frame = header_frame

        self.create_widget()

        # 绑定键盘点击事件


    def create_widget(self):
        self.create_file_frame()

    def create_file_frame(self):
        self.file_frame = ttk.Frame(self, style='frame.TFrame')
        self.file_frame.pack(fill=BOTH)

        # 创建打开按钮
        open_img_path = os.path.join(imgdir, "open.png")
        open_img = Image.open(open_img_path)
        open_img.thumbnail((25, 25), Image.LANCZOS)
        self.open_photo_img = ImageTk.PhotoImage(open_img)  # 使用self防止图片对象被垃圾回收
        self.open_btn = ttk.Button(self.file_frame, text='打开(O)', image=self.open_photo_img, compound=TOP,
                                   style='tool.TButton', takefocus=False, command=self.open_file)
        self.open_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('打开图像或标签文件'))
        self.open_btn.pack(fill=BOTH, side=LEFT, padx=(5, 0), pady=5)

        # 创建打开目录按钮
        self.open_dir_btn = ttk.Button(self.file_frame, text='打开目录', image=self.open_photo_img, compound=TOP,
                                       style='tool.TButton', takefocus=False, command=self.open_dir)
        self.open_dir_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('打开目录'))
        self.open_dir_btn.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建上一幅按钮
        prev_img_path = os.path.join(imgdir, "prev.png")
        prev_img = Image.open(prev_img_path)
        prev_img.thumbnail((25, 25), Image.LANCZOS)
        self.prev_photo_img = ImageTk.PhotoImage(prev_img)  # 使用self防止图片对象被垃圾回收
        self.prev_btn = ttk.Button(self.file_frame, text='上一幅(P)', image=self.prev_photo_img, compound=TOP,
                                   style='tool.TButton', takefocus=False, state=DISABLED, command=self.prev_image)
        self.prev_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('打开上一幅(按Ctl+Shift拷贝标签)'))
        self.prev_btn.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建下一幅按钮
        next_img_path = os.path.join(imgdir, "next.png")
        next_img = Image.open(next_img_path)
        next_img.thumbnail((25, 25), Image.LANCZOS)
        self.next_photo_img = ImageTk.PhotoImage(next_img)  # 使用self防止图片对象被垃圾回收
        self.next_btn = ttk.Button(self.file_frame, text='下一幅(N)', image=self.next_photo_img, compound=TOP,
                                   style='tool.TButton', takefocus=False, state=DISABLED, command=self.next_image)
        self.next_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('打开下一幅(按Ctl+Shift拷贝标签)'))
        self.next_btn.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建保存按钮
        save_img_path = os.path.join(imgdir, "save.png")
        save_img = Image.open(save_img_path)
        save_img.thumbnail((25, 25), Image.LANCZOS)
        self.save_photo_img = ImageTk.PhotoImage(save_img)  # 使用self防止图片对象被垃圾回收
        self.save_btn = ttk.Button(self.file_frame, text='保存(S)', image=self.save_photo_img, compound=TOP,
                                   style='tool.TButton', takefocus=False, state=DISABLED, command=self.save_to_json)
        self.save_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('保存标签到文件'))
        self.save_btn.pack(fill=BOTH, side=LEFT, pady=5)

        # 创建删除按钮
        # delete_img_path = os.path.join(imgdir, "delete.png")
        # delete_img = Image.open(delete_img_path)
        # delete_img.thumbnail((25, 25), Image.LANCZOS)
        # self.delete_photo_img = ImageTk.PhotoImage(delete_img)  # 使用self防止图片对象被垃圾回收
        # self.delete_btn = ttk.Button(self.file_frame, text='删除(D)', image=self.delete_photo_img, compound=TOP,
        #                            style='tool.TButton', takefocus=False, state=DISABLED)
        # self.delete_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('删除当前标签文件'))
        # self.delete_btn.pack(fill=BOTH, side=LEFT, padx=(0, 5), pady=5)

    def on_mouse_in_button(self, tip):
        # print("鼠标移动到按钮")
        self.toolFileDialogEventListener.on_mouse_in_button(tip)

    def open_file(self):
        self.path = open_file()
        if self.path:
            self.canvas_frame.clear_shapes()  # 清空所绘制的图形
            # 改变按钮状态
            self.header_frame.file_menu.entryconfig(self.header_frame.close_index, state=NORMAL)
            self.header_frame.view_menu.entryconfig(self.header_frame.zoom_in_index, state=NORMAL)
            self.header_frame.view_menu.entryconfig(self.header_frame.zoom_out_index, state=NORMAL)
            self.header_frame.view_menu.entryconfig(self.header_frame.fit_window_index, state=NORMAL)
            self.header_frame.file_menu.entryconfig(self.header_frame.pre_img_index, state=DISABLED)
            self.header_frame.file_menu.entryconfig(self.header_frame.next_img_index, state=DISABLED)

            self.header_frame.edit_menu.entryconfig(self.header_frame.polygon_index, state=NORMAL)
            self.header_frame.edit_menu.entryconfig(self.header_frame.rectangle_index, state=NORMAL)
            # self.header_frame.edit_menu.entryconfig(self.header_frame.circle_index, state=NORMAL)
            # self.header_frame.edit_menu.entryconfig(self.header_frame.line_index, state=NORMAL)

            self.prev_btn.config(state=DISABLED)
            self.next_btn.config(state=DISABLED)
            self.save_btn.config(state=NORMAL)

            self.tool_polygonal_editor_frame.create_polygonal_button.config(state=NORMAL)
            self.tool_polygonal_editor_frame.edit_polygonal_button.config(state=NORMAL)

            self.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
            self.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)

            # 显示图片
            # 判断是否为json数据
            if self.path.endswith('.json'):  # 是json数据则直接调用load_json
                self.canvas_frame.image_path_json = self.path  # 将这个json文件路径单独保存到canvas_frame的image_path_json中
                self.canvas_frame.load_json(self.path)
            else:
                self.canvas_frame.image_path_dir = []  # 清空图片路径列表 否则新打开的图片路径添加进去会被第一张已经关闭的图片覆盖
                self.canvas_frame.image_path_dir.append(self.path)
                self.canvas_frame.image_path_json = None  # 这次打开的是图片，所以要将上一个json路径清除，否则在保存时，检测到该路径不为空会出现保存错误
                self.canvas_frame.image_index = 0
                self.canvas_frame.display_image(self.canvas_frame.image_path_dir[0])
        else:
            return

    def open_dir(self):
        self.path_dir = open_dir()
        if self.path_dir:
            self.canvas_frame.clear_shapes()
            # 改变按钮状态
            self.header_frame.file_menu.entryconfig(self.header_frame.close_index, state=NORMAL)
            self.header_frame.view_menu.entryconfig(self.header_frame.zoom_in_index, state=NORMAL)
            self.header_frame.view_menu.entryconfig(self.header_frame.zoom_out_index, state=NORMAL)
            self.header_frame.file_menu.entryconfig(self.header_frame.pre_img_index, state=NORMAL)
            self.header_frame.file_menu.entryconfig(self.header_frame.next_img_index, state=NORMAL)

            self.header_frame.edit_menu.entryconfig(self.header_frame.polygon_index, state=NORMAL)
            self.header_frame.edit_menu.entryconfig(self.header_frame.rectangle_index, state=NORMAL)
            self.header_frame.edit_menu.entryconfig(self.header_frame.circle_index, state=NORMAL)
            self.header_frame.edit_menu.entryconfig(self.header_frame.line_index, state=NORMAL)


            self.prev_btn.config(state=NORMAL)
            self.next_btn.config(state=NORMAL)

            self.tool_polygonal_editor_frame.create_polygonal_button.config(state=NORMAL)
            self.tool_polygonal_editor_frame.edit_polygonal_button.config(state=NORMAL)

            self.header_frame.view_menu.entryconfig(self.header_frame.fit_window_index, state=NORMAL)

            self.save_btn.config(state=NORMAL)

            self.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
            self.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)

            # 显示图片
            self.canvas_frame.image_path_dir = self.path_dir
            self.canvas_frame.image_path_json = None  # 这次打开的是图片，所以要将上一个json路径清除，否则在保存时，检测到该路径不为空会出现保存错误
            self.canvas_frame.image_index = 0
            self.canvas_frame.display_image(self.canvas_frame.image_path_dir[0])
        else:
            return

    def next_image(self):
        self.canvas_frame.next_image()
        self.canvas_frame.clear_shapes()
        # 关闭图片后会将header_frame的放大按钮状态设置为DISABLED，点击下一张重新出现图片时需要重新设置状态
        self.header_frame.file_menu.entryconfig(self.header_frame.close_index, state=NORMAL)
        self.header_frame.view_menu.entryconfig(self.header_frame.zoom_in_index, state=NORMAL)
        self.header_frame.view_menu.entryconfig(self.header_frame.zoom_out_index, state=NORMAL)

        self.header_frame.view_menu.entryconfig(self.header_frame.fit_window_index, state=NORMAL)

        self.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
        self.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)

    def prev_image(self):
        self.canvas_frame.prev_image()
        self.canvas_frame.clear_shapes()

    def save_to_json(self):  # 将标注好的图片保存为json
        image_path = self.canvas_frame.image_path_dir[self.canvas_frame.image_index]
        image_width, image_height = self.canvas_frame.original_image.size
        shapes = self.canvas_frame.shape_to_dict()
        if self.canvas_frame.image_path_json is not None:
            save_to_json(shapes, image_path, image_width, image_height, self.canvas_frame.image_path_json)
        else:
            save_to_json(shapes, image_path, image_width, image_height)


    def set_tool_polygonal_editor_frame(self, tool_polygonal_editor_frame):
        self.tool_polygonal_editor_frame = tool_polygonal_editor_frame

    def set_tool_adaptation_frame(self, tool_adaptation_frame):
        self.tool_adaptation_frame = tool_adaptation_frame


