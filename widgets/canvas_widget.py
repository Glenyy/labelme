import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import constants
from utils.polygon_shape import PolygonShape
import json


class ScrolledCanvas(tk.Canvas):
    """
    一个容器中的画布是为自己制造自动垂直和水平滚动栏
    """
    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)

        vbar = tk.Scrollbar(master)
        hbar = tk.Scrollbar(master, orient='horizontal')

        vbar.pack(side=RIGHT, fill=Y)  # 在栏后面打包画布
        hbar.pack(side=BOTTOM, fill=X)

        vbar.config(command=self.yview)
        hbar.config(command=self.xview)
        self.config(yscrollcommand=vbar.set)
        self.config(xscrollcommand=hbar.set)


class CanvasWidgetEventListener:
    def on_mouse_move(self, x, y):
        print('canvasWidgetEventListener')


class CanvasWidget(ttk.Frame):
    def __init__(self, master, canvasWidgetEventListener):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.canvasWidgetEventListener = canvasWidgetEventListener

        self.image_path_dir = []  # 存储所有Image图片路径
        self.image_path_json = None  # 单独存储json文件路径
        self.image_index = 0  # 当前图片索引

        self.current_operation_tip = None  # 当前画布上的绘图操作
        self.current_operation = None  # 根据当前绘图操作current_operation_tip创建对应实例

        self.original_image = None  # 存储原始图片对象
        self.current_image = None  # 当前图片对象
        self.keep_img = None  # 保持对当前显示的图像引用，防止被垃圾回收机制回收
        self.zoom_ratio = [1, 1]  # 缩放比例

        self.shape = []

        self.selected_depiction = None  # 当前选中的多边形

        # 找到Tk跟窗口
        self.root = self.get_root_window()
        self.root.bind("<Control-Key-i>", self.shortcut_zoom_in)
        self.root.bind("<Control-Key-o>", self.shortcut_zoom_out)
        # 绑定鼠标滚轮事件
        self.root.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows 和 Linux
        # # 绑定鼠标左击事件
        # self.root.bind("<Button-1>", self.on_mouse_press_event)  # 需要只在图片范围内生效，不是整个canvas生效

        self.edit_undo_stack = []  # 编辑操作撤销栈


        self.create_widget()

    def create_widget(self):
        self.create_canvas()

    def create_canvas(self):
        self.canvas_frame_bar = ttk.Frame(self)
        self.canvas_frame_bar.pack(fill=BOTH, expand=YES)
        self.canvas = ScrolledCanvas(self.canvas_frame_bar, bg='#f0f0f0', relief=SUNKEN, bd=0.5, highlightthickness=0)
        # 启用双缓冲
        self.canvas.config(highlightthickness=0, takefocus=1)
        self.canvas.pack(fill=BOTH, expand=YES)

        # 绑定 Canvas 尺寸变化事件
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.canvas.bind('<Motion>', self.on_mouse_move)

    def on_mouse_move(self, event):
        # print('mouse in canvas')
        x = float(self.canvas.canvasx(event.x))
        y = float(self.canvas.canvasy(event.y))
        x = round(x, 14)
        y = round(y, 14)
        # print('当前坐标（用于展示精度）', (x, y))  这里因为event只能获取整数级的坐标 导致精度损失严重 后续需要调整 考虑新的坐标获取方式
        self.canvasWidgetEventListener.on_mouse_move(x, y)

    def on_canvas_resize(self, event):  # canvas上没有加载图片时用该函数
        """
        当 Canvas 大小发生变化时，动态设置 scrollregion 保持中心点为 (0, 0)。
        """
        width = event.width
        height = event.height
        # 设置 scrollregion，将中心点设置为 (0, 0)
        self.canvas.configure(scrollregion=(-width / 2, -height / 2, width / 2, height / 2))  # 指定左上角及右下角坐标

    def on_img_canvas_resize(self, event):
        # 添加防抖处理，避免频繁重绘
        if hasattr(self, '_resize_id'):
            self.after_cancel(self._resize_id)
        self._resize_id = self.after(100, self._do_resize, event)

    def _do_resize(self, event):
        """
        当 有图片的Canvas 大小发生变化时，动态设置 scrollregion 保持图片左上角为（0，0） 图片在canvas中 居中显示
        """
        canvas_width = event.width
        canvas_height = event.height
        img_width = self.keep_img.width()
        img_height = self.keep_img.height()
        # 居中图片
        self.center_image(canvas_width, canvas_height, img_width, img_height)
        # 更新所有已存在的多边形
        for shape in self.shape:
            shape.redraw()
        # 更新当前正在绘制的多边形
        if self.current_operation:
            self.current_operation.dynamic_draw()


    def display_image(self, file_path):
        self.edit_undo_stack.clear()  # 清空撤销栈
        if file_path:
            self.canvas.delete('all')
            # 打开图片并创建 PhotoImage 对象
            self.original_image = Image.open(file_path)
            self.current_image = Image.open(file_path)

            self.tool_widget_frame.tool_adaptation_frame.adaptation_window()  # 打开就适应窗口
            self.tool_widget_frame.tool_adaptation_frame.update_zoom_ratio(self.zoom_ratio)  # 打开就更新显示的比例

            # 将canvas绑定到图片大小变化
            self.canvas.bind("<Configure>", self.on_img_canvas_resize)

    def load_json(self, file_path):  # 加载json文件，将json数据中的图片路径和多边形数据加载到canvas中
        # 获取json数据
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        # 获取图片路径
        image_path = json_data['image_path']
        self.image_path_dir = []
        self.image_path_dir.append(image_path)
        self.image_index = 0
        shapes = json_data['shapes']  # 这个shapes是json数据中的shapes字段

        self.canvas.delete('all')
        # 打开图片并创建 PhotoImage 对象
        self.original_image = Image.open(image_path)
        self.current_image = Image.open(image_path)

        self.tool_widget_frame.tool_adaptation_frame.adaptation_window()  # 打开就适应窗口
        self.tool_widget_frame.tool_adaptation_frame.update_zoom_ratio(self.zoom_ratio)  # 打开就更新显示的比例

        # 将canvas绑定到图片大小变化
        self.canvas.bind("<Configure>", self.on_img_canvas_resize)

        # 通过shapes数据绘制多边形
        for shape in shapes:  # 遍历shapes字段中的每个shape
            if shape['type'] == 'polygon':
                points = shape['points']
                # 创建多边形
                polygon = PolygonShape(self, points)
                polygon.draw_json()
                self.shape.append(polygon)

    def center_image(self, canvas_width, canvas_height, img_width, img_height):  # 图片居中显示且左上角坐标为0
        # 设置 scrollregion，使 Canvas 的 (0, 0) 对应图片的左上角
        self.canvas.configure(scrollregion=(0, 0, img_width, img_height))

        # 将原图片删除
        self.canvas.delete("all")
        # 在 Canvas 的 (0, 0) 插入图片
        self.canvas.create_image(0, 0, anchor=NW, image=self.keep_img)

        # 计算图片中心的偏移量
        offset_x = (img_width - canvas_width) // 2
        offset_y = (img_height - canvas_height) // 2

        # 调整滚动条，使图片视觉居中
        self.canvas.xview_moveto(offset_x / img_width)
        self.canvas.yview_moveto(offset_y / img_height)

    def zoom_in(self):
        # 图片放大操作 每次放大10%
        self.adjust_zoom(1.1)
        self.tool_widget_frame.tool_adaptation_frame.is_adaptation = False
        self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(style='tool.TButton')
        self.unbind("<Configure>")  # 解绑图片大小变化事件


    def zoom_out(self):
        # 图片缩小操作 每次缩小10%
        self.adjust_zoom(0.9)
        self.tool_widget_frame.tool_adaptation_frame.is_adaptation = False
        self.tool_widget_frame.tool_adaptation_frame.adaptation_btn.config(style='tool.TButton')
        self.unbind("<Configure>")

    def adjust_zoom(self, scale_factor):
        """
        基于原始图片调整缩放比例并重新绘制。
        """
        if self.current_image and self.original_image:
            zoom_ratio = [x * scale_factor for x in self.zoom_ratio]

            # 计算新的尺寸，基于原始图片
            original_width, original_height = self.original_image.size
            new_width = int(original_width * zoom_ratio[0])
            new_height = int(original_height * zoom_ratio[1])

            # 限制缩小比例
            if new_width < 1 or new_height < 1:  # 自定义最小尺寸限制
                # print("Reached minimum zoom limit")
                return

            # 更新缩放比例
            self.zoom_ratio = [x * scale_factor for x in self.zoom_ratio]
            # print('当前缩放比例', self.zoom_ratio)

            # 缩放图片
            self.current_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.keep_img = ImageTk.PhotoImage(self.current_image)

            # 获取 Canvas 和图片的宽高
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.keep_img.width()
            img_height = self.keep_img.height()

            # 居中图片
            self.center_image(canvas_width, canvas_height, img_width, img_height)

            # 更新所有已存在的多边形
            for shape in self.shape:
                shape.redraw()

            # 更新当前正在绘制的多边形
            if self.current_operation:
                self.current_operation.dynamic_draw()

            # 更新adaptation_entry显示的比例
            self.tool_widget_frame.tool_adaptation_frame.update_zoom_ratio(self.zoom_ratio)

    def adaption_canvas(self, zoom_ratio):  # 根据给出的缩放比率列表来进行缩放以达到适应窗口的功能
        self.zoom_ratio = zoom_ratio
        # 计算新的尺寸，基于原始图片
        original_width, original_height = self.original_image.size
        new_width = int(original_width * zoom_ratio[0])
        new_height = int(original_height * zoom_ratio[1])

        # 限制缩小比例
        if new_width < 1 or new_height < 1:  # 自定义最小尺寸限制
            return

        # 缩放图片
        self.current_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        self.keep_img = ImageTk.PhotoImage(self.current_image)

        # 获取 Canvas 和图片的宽高
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width = self.keep_img.width()
        img_height = self.keep_img.height()

        # 居中图片
        self.center_image(canvas_width, canvas_height, img_width, img_height)

        # 更新所有已存在的多边形
        for shape in self.shape:
            shape.redraw()

        # 更新当前正在绘制的多边形
        if self.current_operation:
            self.current_operation.dynamic_draw()

        # 更新adaptation_entry显示的比例
        self.tool_widget_frame.tool_adaptation_frame.update_zoom_ratio(self.zoom_ratio)

    def set_zoom_ratio(self, zoom_ratio):
        self.zoom_ratio = zoom_ratio

        if self.current_image and self.original_image:
            # 计算新的尺寸，基于原始图片
            original_width, original_height = self.original_image.size
            new_width = int(original_width * zoom_ratio[0])
            new_height = int(original_height * zoom_ratio[1])

            # 限制缩小比例
            if new_width < 1 or new_height < 1:  # 自定义最小尺寸限制
                return

            # 缩放图片
            self.current_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.keep_img = ImageTk.PhotoImage(self.current_image)

            # 获取 Canvas 和图片的宽高
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.keep_img.width()
            img_height = self.keep_img.height()

            # 居中图片
            self.center_image(canvas_width, canvas_height, img_width, img_height)

            # 更新所有已存在的多边形
            for shape in self.shape:
                shape.redraw()
            # 更新当前正在绘制的多边形
            if self.current_operation:
                self.current_operation.dynamic_draw()

    def shortcut_zoom_in(self, event):
        if self.current_image:
            self.zoom_in()

    def shortcut_zoom_out(self, event):
        if self.current_image:
            self.zoom_out()

    def on_mouse_wheel(self, event):
        """
        处理鼠标滚轮事件，支持 Ctrl + 滚轮放大缩小
        """
        if event.state & 0x4:  # 检测 Ctrl 键是否按下 (0x4 是 Ctrl 的修饰符)
            if event.delta > 0:  # 向上滚动
                self.zoom_in()
            elif event.delta < 0:  # 向下滚动
                self.zoom_out()

    def adaption_window(self):
        pass

    def get_root_window(self):
        """递归找到 Tk 根窗口"""
        parent = self.master
        while parent.master is not None:
            parent = parent.master
        return parent

    def close_img_file(self):
        self.edit_undo_stack.clear()  # 清空撤销栈
        self.current_image = None
        self.keep_img = None
        self.canvas.delete("all")
        self.image_index = None

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.configure(scrollregion=(-width / 2, -height / 2, width / 2, height / 2))
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def next_image(self):
        if self.image_index is not None:
            if self.image_index >= len(self.image_path_dir) - 1:
                return
            self.image_index += 1
            self.display_image(self.image_path_dir[self.image_index])
        else:
            self.image_index = 0
            self.display_image(self.image_path_dir[self.image_index])

    def prev_image(self):
        if self.image_index is not None:
            if self.image_index <= 0:
                return
            self.image_index -= 1
            self.display_image(self.image_path_dir[self.image_index])

    def set_tool_widget_frame(self, tool_widget_frame):
        self.tool_widget_frame = tool_widget_frame

    def push_edit_action(self, action):
        """将一次编辑操作推入撤销栈"""
        self.edit_undo_stack.append(action)

    def undo_edit_action(self, event=None):  # 撤销编辑操作(核心)
        if not self.edit_undo_stack:
            return
        action = self.edit_undo_stack.pop()
        t = action['type']
        shape = action['shape']

        if t == 'move_vertex':
            idx = action['vertex_idx']
            ox, oy = action['old_pos']
            _, _, point_id = shape.points[idx]
            shape.points[idx] = (ox, oy, point_id)
            shape.redraw()

        elif t == 'move_polygon':
            old_points = action['old_points']
            for i, (ox, oy) in enumerate(old_points):
                _, _, point_id = shape.points[i]
                shape.points[i] = (ox, oy, point_id)
            shape.redraw()

        # elif t == 'delete_polygon':
        #     shape_data = action['shape_data']
        #     new_shape = PolygonShape(self, shape_data['points'])
        #     new_shape.draw_json()
        #     self.shape.append(new_shape)

    def set_current_operation(self):  # 根据传递过来的tip创建操作对象
        if self.current_operation_tip == 'create_polygon':  # 如果tip是create_polygon则创建绘制多边形的对象
            self.current_operation = PolygonShape(self)
            for shape in self.shape:
                shape.deselect()  # 当前操作状态改变时，取消之前选中的多边形
            self.tool_widget_frame.tool_polygonal_editor_frame.delete_polygonal_button.config(state=DISABLED)  # 处于绘制多边形模式，禁用删除按钮
            self.canvas.unbind("<Button-1>")  # 解除当前绑定的事件
            self.current_operation.bind_events()
        elif self.current_operation_tip == 'edit_polygon':  # 进入编辑多边形的模式
            self.current_operation = None  # 编辑多边形模式不需要创建新的对象 但是要可以对目前canvas上所有的图形编辑操作，包括删除、移动、缩放等（且这些操作在其对应的shape类中实现）
            self.canvas.bind("<Button-1>", self.on_edit_depiction_click)  # 绑定点击事件，用于选择多边形进行编辑
            self.root.bind("<Control-z>", self.undo_edit_action)  # 绑定撤销编辑操作的事件



    def create_new_current_operation(self):  # 每次完成一个shape的绘制时，都需要创建一个新的shape实例，在对应的绘图工具类中调用
        self.current_operation.unbind_events()  # 解除当前绑定
        if self.current_operation_tip == 'create_polygon':
            self.current_operation = PolygonShape(self)
            self.current_operation.bind_events()

    def shape_to_dict(self):  # 遍历所有shape图形并转化为字典
        shapes = []
        for shape in self.shape:
            shapes.append(shape.to_dict())
        return shapes

    def clear_shapes(self):  # 清除所有多边形
        for shape in self.shape:
            shape.delete_myself()
        self.shape = []

    def on_edit_depiction_click(self, event):
        # 判断当前点击的位置是否在当前选中的多边形内
        if self.selected_depiction:
            temp_x = self.canvas.canvasx(event.x)  # 获取鼠标点击的 Canvas 坐标x
            temp_y = self.canvas.canvasy(event.y)  # 获取鼠标点击的 Canvas 坐标y
            # 将canvas的坐标转化为图片上的相对坐标
            temp_image_x = temp_x / self.zoom_ratio[0]
            temp_image_y = temp_y / self.zoom_ratio[0]
            if self.selected_depiction.is_in_polygon(temp_image_x, temp_image_y):
                return  # 如果点击的位置在当前选中的多边形内，则直接返回，不应该再次触发on_edit_depiction_click函数的主要内容
            # 点击在多边形外但靠近顶点，也保留选中状态（放行给顶点拖拽）
            if self.selected_depiction.find_nearest_vertex(temp_x, temp_y, tolerance=8) is not None:
                return

        # 接下来要修改这边，我要先根据鼠标点击的位置来判断有没有选择新的多边形，如果选择了得解绑旧的多边形编辑事件，没选择也得解绑
        """点击选择多边形"""
        x = self.canvas.canvasx(event.x)  # 获取鼠标点击的 Canvas 坐标x
        y = self.canvas.canvasy(event.y)  # 获取鼠标点击的 Canvas 坐标y
        # 将canvas的坐标转化为图片上的相对坐标
        image_x = x / self.zoom_ratio[0]
        image_y = y / self.zoom_ratio[0]

        # 取消之前选中的多边形并且解绑编辑事件
        if self.selected_depiction:
            self.selected_depiction.deselect()
            self.selected_depiction.unbind_edit_events()  # 解绑选中多边形的编辑事件
        # 选择新多边形
        selected_depiction = self.select_depiction_at_position(image_x, image_y)  # 根据当前点击位置判断是否有多边形 是哪一个多边形
        if selected_depiction:
            self.selected_depiction = selected_depiction  # 后续编辑操作在该被选中的图形实现代码中进行（如删除、移动、缩放等）
            self.selected_depiction.is_select = True  # 标记该多边形已被选中
            self.selected_depiction.bind_edit_events()  # 绑定选中多边形的编辑事件
            print("绑定编辑事件")

            self.tool_widget_frame.tool_polygonal_editor_frame.delete_polygonal_button.config(state=NORMAL)  # 如果有选中的多边形，则启用删除按钮

        else:  # 如果没有选中的多边形，则禁用删除按钮
            self.selected_depiction = None
            self.tool_widget_frame.tool_polygonal_editor_frame.delete_polygonal_button.config(state=DISABLED)

    def select_depiction_at_position(self, x, y):  # 根据当前点击位置判断是否有多边形 是哪一个多边形
        for shape in self.shape:
            if shape.is_in_polygon(x, y):
                return shape
        return








































































    # def on_mouse_press_event(self, event):  # 处理鼠标按下事件，记录顶点坐标
    #     # 获取鼠标点击的 Canvas 坐标
    #     x = self.canvas.canvasx(event.x)
    #     y = self.canvas.canvasy(event.y)
    #
    #     # 如果当前没有图片，直接返回
    #     if self.current_image is None:
    #         return
    #
    #     # 获取当前图片的宽高
    #     img_width = self.current_image.width
    #     img_height = self.current_image.height
    #
    #     # 检查点击位置是否在图片范围内
    #     if 0 <= x <= img_width and 0 <= y <= img_height:
    #         points = [(x, y)]
    #         # 判断当前是什么绘图操作
    #         if self.current_operation is None:  # 没有操作，直接返回
    #             return
    #         if self.current_operation == 'polygon':  # 如果是多边形，则传递当前的顶点给绘制多边形的方法
    #             print(self.current_operation)
    #             # # 重新绑定鼠标左击事件
    #             # self.root.unbind('<Button-1>')
    #             # self.root.bind('<Button-1>', self.on_polygon_click)
    #             self.create_polygon(points)
    #             return
    #         if self.current_operation == 'rectangle':  # 如果是直线，则传递当前的顶点给绘制直线的方法
    #             print(self.current_operation)
    #         if self.current_operation == 'circle':
    #             print(self.current_operation)
    #         if self.current_operation == 'line':  # 如果是直线，则传递当前的顶点给绘制直线的方法
    #             print(self.current_operation)

    # def on_mouse_release_event(self, event):
    #     pass
    #
    # def is_closed(self):  # 多边形闭合检查
    #     pass
    #
    # def finalise(self):
    #     pass
    #
    # def create_polygon(self, points):  # 创建多边形
    #     pass
    #
    # def create_line(self, start, end):  # 创建直线
    #     pass
    #
    # def on_canvas_mouse_move(self, event):
    #     pass

    # def on_polygon_click(self, event):
    #     # 获取鼠标点击的 Canvas 坐标
    #     x = self.canvas.canvasx(event.x)
    #     y = self.canvas.canvasy(event.y)
    #
    #     # 如果当前没有图片，直接返回
    #     if self.current_image is None:
    #         return
    #
    #     # 获取当前图片的宽高
    #     img_width = self.current_image.width
    #     img_height = self.current_image.height
    #
    #     if 0 <= x <= img_width and 0 <= y <= img_height:
    #         points = [(x, y)]
    #
    #         if self.complete:
    #             return  # 完成的多边形不允许添加新点




if __name__ == '__main__':
    root = tk.Tk()
    app = CanvasWidget(root, canvasWidgetEventListener=CanvasWidgetEventListener())
    app.pack()
    root.mainloop()
