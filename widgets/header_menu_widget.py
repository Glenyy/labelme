import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
from widgets import imgdir
from utils.open_file import open_file
from utils.open_dir import open_dir
from utils.polygon_shape import PolygonShape


class HeaderMenuWidget(ttk.Frame):
    def __init__(self, master, canvas_frame, ai_service=None):
        ttk.Frame.__init__(self, master)
        super().__init__()
        self.master = master
        self.canvas_frame = canvas_frame
        self.ai_service = ai_service

        self.create_polygon = 'create_polygon'
        self.create_rectangle = 'create_rectangle'
        self.create_circle = 'create_circle'
        self.create_line = 'create_line'
        self.edit_polygon = 'edit_polygon'

        self.ai_annotate_index = None

        self.create_widget()

        # 找到Tk跟窗口
        root = self.canvas_frame.get_root_window()
        root.bind("<a>", self.prev_image)
        root.bind("<d>", self.next_image)

    def create_widget(self):
        self.create_menu_bar()

    def create_menu_bar(self):
        self.menu_bar = ttk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_help_menu()

    def create_file_menu(self):
        self.file_menu = ttk.Menu(self.menu_bar, tearoff=False)
        # 打开菜单
        open_img_path = os.path.join(imgdir, "open.png")
        open_img = Image.open(open_img_path)
        open_img.thumbnail((15, 15), Image.LANCZOS)
        self.open_photo_img = ImageTk.PhotoImage(open_img)  # 使用self防止图片对象被垃圾回收
        self.file_menu.add_command(label='打开(O)', underline=0, font=('等线', 10),
                                   image=self.open_photo_img, compound=LEFT,
                                   accelerator="Ctrl+O", command=self.open_file)
        # 下一幅菜单
        next_img_path = os.path.join(imgdir, "next.png")
        next_img = Image.open(next_img_path)
        next_img.thumbnail((15, 15), Image.LANCZOS)
        next_img_gray = next_img.convert("LA") # 转为灰度图像
        self.next_photo_img = ImageTk.PhotoImage(next_img)  # 使用self防止图片对象被垃圾回收
        self.next_photo_img_gray = ImageTk.PhotoImage(next_img_gray)  # 使用self防止图片对象被垃圾回收
        self.file_menu.add_command(label='下一幅(N)', underline=0, font=('等线', 10),
                                   image=self.next_photo_img, compound=LEFT, command=self.next_image,
                                   accelerator="D", state=DISABLED)
        self.next_img_index = self.file_menu.index("end")
        # 上一幅菜单
        prev_img_path = os.path.join(imgdir, "prev.png")
        prev_img = Image.open(prev_img_path)
        prev_img.thumbnail((15, 15), Image.LANCZOS)
        self.prev_photo_img = ImageTk.PhotoImage(prev_img)  # 使用self防止图片对象被垃圾回收
        self.file_menu.add_command(label='上一幅(P)', underline=0, font=('等线', 10),
                                   image=self.prev_photo_img, compound=LEFT, command=self.prev_image,
                                   accelerator="A", state=DISABLED)
        self.pre_img_index = self.file_menu.index("end")
        # 打开目录
        self.file_menu.add_command(label='打开目录(D)', underline=0, font=('等线', 10),
                                   image=self.open_photo_img, compound=LEFT,
                                   accelerator="Ctrl+D", command=self.open_dir)

        # 关闭
        close_img_path = os.path.join(imgdir, "close.png")
        close_img = Image.open(close_img_path)
        close_img.thumbnail((15, 15), Image.LANCZOS)
        self.close_photo_img = ImageTk.PhotoImage(close_img)  # 使用self防止图片对象被垃圾回收
        self.file_menu.add_command(label='关闭(C)', underline=0, font=('等线', 10),
                                   image=self.close_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="Ctrl+W", command=self.close_file)

        self.close_index = self.file_menu.index("end")

        # 添加分隔符
        self.file_menu.add_separator()

        # 退出按钮
        quit_img_path = os.path.join(imgdir, "quit.png")
        quit_img = Image.open(quit_img_path)
        quit_img.thumbnail((15, 15), Image.LANCZOS)
        self.quit_photo_img = ImageTk.PhotoImage(quit_img)  # 使用self防止图片对象被垃圾回收
        self.file_menu.add_command(label='退出(Q)', underline=0, font=('等线', 10),
                                   image=self.quit_photo_img, compound=LEFT,
                                   accelerator="Ctrl+Q", command=self.quit)
        self.menu_bar.add_cascade(label='文件(F)', menu=self.file_menu, underline=0, font=('等线', 10))


    def create_edit_menu(self):
        self.edit_menu = ttk.Menu(self.menu_bar, tearoff=False)
        objects_img_path = os.path.join(imgdir, "objects.png")
        objects_img = Image.open(objects_img_path)
        objects_img.thumbnail((15, 15), Image.LANCZOS)
        self.objects_photo_img = ImageTk.PhotoImage(objects_img)  # 使用self防止图片对象被垃圾回收
        # 创建多边形
        self.edit_menu.add_command(label='创建多边形', underline=0, font=('等线', 10),
                                   image=self.objects_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="Ctrl+N",
                                   command=lambda: self.update_current_operation(self.create_polygon))
        self.polygon_index = self.edit_menu.index('end')

        # 创建矩形
        self.edit_menu.add_command(label='创建矩形', underline=0, font=('等线', 10),
                                   image=self.objects_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="Ctrl+R", command=lambda: self.update_current_operation(self.create_rectangle))
        self.rectangle_index = self.edit_menu.index('end')

        # # 创建圆
        # self.edit_menu.add_command(label='创建圆', underline=0, font=('等线', 10),
        #                            image=self.objects_photo_img, compound=LEFT, state=DISABLED,
        #                            command=lambda: self.update_current_operation(self.create_circle))
        # self.circle_index = self.edit_menu.index('end')
        #
        # # 创建直线
        # self.edit_menu.add_command(label='创建直线', underline=0, font=('等线', 10),
        #                            image=self.objects_photo_img, compound=LEFT, state=DISABLED,
        #                            command=lambda: self.update_current_operation(self.create_line))
        # self.line_index = self.edit_menu.index('end')

        # AI标注
        self.edit_menu.add_separator()
        ai_img_path = os.path.join(imgdir, "expert.png")
        ai_img = Image.open(ai_img_path)
        ai_img.thumbnail((15, 15), Image.LANCZOS)
        self.ai_photo_img = ImageTk.PhotoImage(ai_img)
        self.edit_menu.add_command(
            label='绘制AI标注',
            underline=4,
            font=('等线', 10),
            image=self.ai_photo_img,
            compound=LEFT,
            state=DISABLED,
            accelerator="Ctrl+Shift+A",
            command=self.on_ai_annotate,
        )
        self.ai_annotate_index = self.edit_menu.index('end')

        self.menu_bar.add_cascade(label='编辑(E)', menu=self.edit_menu, underline=0, font=('等线', 10))



    def create_view_menu(self):
        self.view_menu = ttk.Menu(self.menu_bar, tearoff=False)
        # 标记对话框

        # 标签列表对话框

        # 多边形列表对话框

        # 文件列表对话框

        # 添加分隔符
        self.view_menu.add_separator()

        # 填充所绘多边形
        color_img_path = os.path.join(imgdir, "color.png")
        color_img = Image.open(color_img_path)
        color_img.thumbnail((15, 15), Image.LANCZOS)
        self.color_photo_img = ImageTk.PhotoImage(color_img)  # 使用self防止图片对象被垃圾回收
        self.view_menu.add_command(label='填充所绘多边形(F)', underline=0, font=('等线', 10),
                                   image=self.color_photo_img, compound=LEFT)

        # 添加分隔符
        self.view_menu.add_separator()

        # 隐藏多边形
        eye_img_path = os.path.join(imgdir, "eye.png")
        eye_img = Image.open(eye_img_path)
        eye_img.thumbnail((15, 15), Image.LANCZOS)
        self.eye_photo_img = ImageTk.PhotoImage(eye_img)  # 使用self防止图片对象被垃圾回收
        self.view_menu.add_command(label='隐藏多边形(H)', underline=0, font=('等线', 10),
                                   image=self.eye_photo_img, compound=LEFT, state=DISABLED)

        # 显示多边形
        self.view_menu.add_command(label='显示多边形(S)', underline=0, font=('等线', 10),
                                   image=self.eye_photo_img, compound=LEFT, state=DISABLED)

        # 开关多边形
        self.view_menu.add_command(label='开关多边形(S)', underline=0, font=('等线', 10),
                                   image=self.eye_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="T")

        # 添加分隔符
        self.view_menu.add_separator()

        # 放大
        zoom_in_img_path = os.path.join(imgdir, "zoom-in.png")
        zoom_in_img = Image.open(zoom_in_img_path)
        zoom_in_img.thumbnail((15, 15), Image.LANCZOS)
        self.zoom_in_photo_img = ImageTk.PhotoImage(zoom_in_img)  # 使用self防止图片对象被垃圾回收
        self.view_menu.add_command(label='放大(I)', underline=0, font=('等线', 10),
                                   image=self.zoom_in_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="Ctrl+i", command=self.zoom_in)
        self.zoom_in_index = self.view_menu.index("end")  # 获取菜单项索引

        # 缩小
        zoom_out_img_path = os.path.join(imgdir, "zoom-out.png")
        zoom_out_img = Image.open(zoom_out_img_path)
        zoom_out_img.thumbnail((15, 15), Image.LANCZOS)
        self.zoom_out_photo_img = ImageTk.PhotoImage(zoom_out_img)  # 使用self防止图片对象被垃圾回收
        self.view_menu.add_command(label='缩小(Z)', underline=0, font=('等线', 10),
                                   image=self.zoom_out_photo_img, compound=LEFT, state=DISABLED,
                                   accelerator="Ctrl+o", command=self.zoom_out)
        self.zoom_out_index = self.view_menu.index("end")  # 获取菜单项索引

        self.menu_bar.add_cascade(label='视图(V)', menu=self.view_menu, underline=0, font=('等线', 10))

        # 添加分隔符
        self.view_menu.add_separator()

        # 适应窗口
        fit_window_img_path = os.path.join(imgdir, "fit-window.png")
        fit_window_img = Image.open(fit_window_img_path)
        fit_window_img.thumbnail((15, 15), Image.LANCZOS)
        self.fit_window_photo_img = ImageTk.PhotoImage(fit_window_img)  # 使用self防止图片对象被垃圾回收
        self.view_menu.add_command(label='适应窗口(W)', underline=0, font=('等线', 10),
                                   image=self.fit_window_photo_img, compound=LEFT, state=DISABLED, accelerator="Ctrl+F")
        self.fit_window_index = self.view_menu.index("end")  # 获取菜单项索引

    def create_help_menu(self):
        self.help_menu = ttk.Menu(self.menu_bar, tearoff=False)

        self.menu_bar.add_cascade(label='帮助(H)', menu=self.help_menu, underline=0, font=('等线', 10))

    def open_file(self):
        self.path = open_file()
        if self.path:
            self.canvas_frame.clear_shapes()
            # 改变按钮状态
            self.file_menu.entryconfig(self.close_index, state=NORMAL)
            self.file_menu.entryconfig(self.pre_img_index, state=DISABLED)
            self.file_menu.entryconfig(self.next_img_index, state=DISABLED)

            self.edit_menu.entryconfig(self.polygon_index, state=NORMAL)
            self.edit_menu.entryconfig(self.rectangle_index, state=NORMAL)
            # self.edit_menu.entryconfig(self.circle_index, state=NORMAL)
            # self.edit_menu.entryconfig(self.line_index, state=NORMAL)

            if self.ai_annotate_index is not None and self.ai_service is not None:
                self.edit_menu.entryconfig(self.ai_annotate_index, state=NORMAL)

            self.view_menu.entryconfig(self.zoom_in_index, state=NORMAL)
            self.view_menu.entryconfig(self.zoom_out_index, state=NORMAL)

            self.tool_widget_frame.tool_file_frame.prev_btn.config(state=DISABLED)
            self.tool_widget_frame.tool_file_frame.next_btn.config(state=DISABLED)
            self.tool_widget_frame.tool_file_frame.save_btn.config(state=NORMAL)

            self.tool_widget_frame.tool_polygonal_editor_frame.create_polygonal_button.config(state=NORMAL)
            self.tool_widget_frame.tool_polygonal_editor_frame.edit_polygonal_button.config(state=NORMAL)

            self.view_menu.entryconfig(self.fit_window_index, state=NORMAL)
            self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
            self.tool_widget_frame.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)


            # 显示图片
            # 判断是否为json数据
            if self.path.endswith('.json'):  # 是json数据则直接调用load_json
                self.canvas_frame.image_path_json = self.path  # 将这个json文件路径单独保存到canvas_frame的image_path_json中
                self.canvas_frame.load_json(self.path)
                self.canvas_frame.image_path_dir = []
                self.canvas_frame.update_file_list()  # 单文件模式下，清空文件列表
            else:
                self.canvas_frame.image_path_dir = []  # 清空图片路径列表 否则新打开的图片路径添加进去会被第一张已经关闭的图片覆盖
                self.canvas_frame.update_file_list()  # 单文件模式下，清空文件列表
                self.canvas_frame.image_path_dir.append(self.path)
                self.canvas_frame.image_path_json = None  # 这次打开的是图片，所以要将上一个json路径清楚，否则在保存时，检测到该路径不为空会出现保存错误
                self.canvas_frame.image_index = 0
                self.canvas_frame.display_image(self.canvas_frame.image_path_dir[0])

        else:
            return

    def open_dir(self):
        self.path_dir = open_dir()
        if self.path_dir:
            self.canvas_frame.clear_shapes()
            # 改变按钮状态
            self.file_menu.entryconfig(self.next_img_index, state=NORMAL)
            self.file_menu.entryconfig(self.pre_img_index, state=NORMAL)

            self.file_menu.entryconfig(self.close_index, state=NORMAL)

            self.edit_menu.entryconfig(self.polygon_index, state=NORMAL)
            self.edit_menu.entryconfig(self.rectangle_index, state=NORMAL)
            # self.edit_menu.entryconfig(self.circle_index, state=NORMAL)
            # self.edit_menu.entryconfig(self.line_index, state=NORMAL)

            if self.ai_annotate_index is not None and self.ai_service is not None:
                self.edit_menu.entryconfig(self.ai_annotate_index, state=NORMAL)

            self.view_menu.entryconfig(self.zoom_in_index, state=NORMAL)
            self.view_menu.entryconfig(self.zoom_out_index, state=NORMAL)

            self.tool_widget_frame.tool_file_frame.prev_btn.config(state=NORMAL)
            self.tool_widget_frame.tool_file_frame.next_btn.config(state=NORMAL)
            self.tool_widget_frame.tool_file_frame.save_btn.config(state=NORMAL)

            self.tool_widget_frame.tool_polygonal_editor_frame.create_polygonal_button.config(state=NORMAL)
            self.tool_widget_frame.tool_polygonal_editor_frame.edit_polygonal_button.config(state=NORMAL)

            self.view_menu.entryconfig(self.fit_window_index, state=NORMAL)
            self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
            self.tool_widget_frame.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)

            # 显示图片
            self.canvas_frame.image_path_dir = self.path_dir
            self.canvas_frame.update_file_list()
            self.canvas_frame.image_path_json = None  # 这次打开的是图片，所以要将上一个json路径清除，否则在保存时，检测到该路径不为空会出现保存错误
            self.canvas_frame.image_index = 0
            self.canvas_frame.display_image(self.canvas_frame.image_path_dir[0])
        else:
            return

    def close_file(self):
        self.canvas_frame.close_img_file()
        self.canvas_frame.clear_shapes()
        self.canvas_frame.image_path_dir = []  # 清空图片路径列表
        self.canvas_frame.image_path_json = None  # 这次打开的是图片，所以要将上一个json路径清除

        # 改变按钮状态
        self.file_menu.entryconfig(self.next_img_index, state=DISABLED)
        self.file_menu.entryconfig(self.pre_img_index, state=DISABLED)
        self.file_menu.entryconfig(self.close_index, state=DISABLED)

        self.edit_menu.entryconfig(self.polygon_index, state=DISABLED)
        self.edit_menu.entryconfig(self.rectangle_index, state=DISABLED)
        # self.edit_menu.entryconfig(self.circle_index, state=DISABLED)
        # self.edit_menu.entryconfig(self.line_index, state=DISABLED)

        if self.ai_annotate_index is not None:
            self.edit_menu.entryconfig(self.ai_annotate_index, state=DISABLED)

        self.view_menu.entryconfig(self.zoom_in_index, state=DISABLED)
        self.view_menu.entryconfig(self.zoom_out_index, state=DISABLED)

        self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(state=DISABLED)
        self.tool_widget_frame.tool_adaptation_frame.adaptation_entry.config(state=DISABLED)

        self.tool_widget_frame.tool_polygonal_editor_frame.create_polygonal_button.config(state=DISABLED)
        self.tool_widget_frame.tool_polygonal_editor_frame.edit_polygonal_button.config(state=DISABLED)

        self.view_menu.entryconfig(self.fit_window_index, state=DISABLED)





    def zoom_in(self):
        self.canvas_frame.zoom_in()

    def zoom_out(self):
        self.canvas_frame.zoom_out()

    def set_tool_widget_frame(self, tool_widget_frame):
        self.tool_widget_frame = tool_widget_frame
        self.view_menu.entryconfig(self.fit_window_index,
                                   command=self.tool_widget_frame.tool_adaptation_frame.adaptation_event)

    def next_image(self, event=None):
        self.canvas_frame.next_image()
        # self.canvas_frame.clear_shapes()
        # 关闭图片后会将header_frame的关闭 放大 缩小按钮状态设置为DISABLED，点击下一张重新出现图片时需要重新设置状态
        self.file_menu.entryconfig(self.close_index, state=NORMAL)
        self.view_menu.entryconfig(self.zoom_in_index, state=NORMAL)
        self.view_menu.entryconfig(self.zoom_out_index, state=NORMAL)
        self.view_menu.entryconfig(self.fit_window_index, state=NORMAL)

        self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(state=NORMAL)
        self.tool_widget_frame.tool_adaptation_frame.adaptation_entry.config(state=NORMAL)

    def prev_image(self, event=None):
        self.canvas_frame.prev_image()
        # self.canvas_frame.clear_shapes()

    def update_current_operation(self, operation):
        if self.canvas_frame.current_operation is not None:  # 如果当前操作存在，则先解绑事件
            self.canvas_frame.current_operation.unbind_events()
        self.canvas_frame.current_operation_tip = operation  # 设置当前操作
        self.canvas_frame.set_current_operation()  # 创建对象

    def on_ai_annotate(self):
        import os
        import threading
        from tkinter import messagebox

        if self.ai_service is None:
            messagebox.showerror("错误", "AI服务未初始化")
            return

        if self.ai_service.current_model is None:
            messagebox.showerror("错误", "未选择AI模型，请在工具栏选择模型")
            return

        original_image = self.canvas_frame.original_image
        if original_image is None:
            messagebox.showerror("错误", "请先打开一张图片")
            return

        # 先快速检查服务是否在线（5秒超时），避免等120秒无反馈
        if not self.ai_service.health_check(timeout=5):
            messagebox.showerror(
                "AI服务不可达",
                "无法连接到AI服务，请确认：\n"
                "1. 模型服务已启动\n"
                "2. 服务地址配置正确\n"
                "（可通过环境变量 AI_SERVER_URL 设置地址）"
            )
            return

        if self.ai_annotate_index is not None:
            self.edit_menu.entryconfig(self.ai_annotate_index, state=DISABLED)

        if hasattr(original_image, 'filename') and original_image.filename:
            file_name = os.path.basename(original_image.filename)
        else:
            file_name = "image.jpg"

        def _run():
            try:
                shapes = self.ai_service.predict(original_image, file_name)
                self.master.after(0, lambda s=shapes: self._on_ai_result(s))
            except Exception as exc:
                self.master.after(0, lambda e=str(exc): self._on_ai_error(e))

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _on_ai_result(self, shapes):
        from tkinter import messagebox
        if shapes:
            self.canvas_frame.load_ai_shapes(shapes)
            messagebox.showinfo("AI标注完成", f"成功标注 {len(shapes)} 个对象")
        else:
            messagebox.showinfo("AI标注", "未检测到对象")
        if self.ai_annotate_index is not None:
            self.edit_menu.entryconfig(self.ai_annotate_index, state=NORMAL)

    def _on_ai_error(self, error_msg):
        from tkinter import messagebox
        messagebox.showerror("AI标注错误", f"标注失败：\n{error_msg}")
        if self.ai_annotate_index is not None:
            self.edit_menu.entryconfig(self.ai_annotate_index, state=NORMAL)
