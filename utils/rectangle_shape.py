class RectangleShape:
    def __init__(self, canvas_frame, points=None):
        self.canvas_frame = canvas_frame
        self.canvas = canvas_frame.canvas

        self.shape_type = "rectangle"  # 图形类型 矩形
        self.points = []  # 存储左上和右下顶点的坐标及id 顶点坐标是相对于图片的坐标，而不是canvas上的绝对坐标
        self.rectangle_id = None  # 矩形对象id

        self.json_points = points  # 保存顶点坐标为json格式，用于保存和加载
        self.temp_rectangle = None  # 动态矩形对象
        self.complete = False  # 是否完成矩形绘制

        self.current_local_point = ()  # 当前鼠标位置

        self.last_zoom_ratio = canvas_frame.zoom_ratio  # 保存当前缩放比例

        self.root = self.get_root_window()

        self.is_select = False  # 是否该多边形被选中(默认未选中)

    def find_intersection(self, width, height, x1, y1, x2, y2):  # 计算与图片的交点
        # 计算斜率 k
        if x2 == x1:  # 垂直线，斜率无穷大
            # 交点只能是上边界或下边界
            if y2 < 0:  # 点在图片上方，交于上边界 y=0
                return (x1, 0)
            else:  # 点在图片下方，交于下边界 y=height
                return (x1, height)
        else:
            k = (y2 - y1) / (x2 - x1)

        # 计算与四条边界的交点
        intersections = []

        # (1) 与左边界 x=0 的交点
        y_at_x0 = y1 - k * x1
        if 0 <= y_at_x0 <= height:
            intersections.append((0, y_at_x0))

        # (2) 与右边界 x=width 的交点
        y_at_xwidth = y1 + k * (width - x1)
        if 0 <= y_at_xwidth <= height:
            intersections.append((width, y_at_xwidth))

        # (3) 与上边界 y=0 的交点
        if k != 0:  # 避免除零错误
            x_at_y0 = (k * x1 - y1) / k
            if 0 <= x_at_y0 <= width:
                intersections.append((x_at_y0, 0))

        # (4) 与下边界 y=height 的交点
        if k != 0:  # 避免除零错误
            x_at_yheight = (height - y1 + k * x1) / k
            if 0 <= x_at_yheight <= width:
                intersections.append((x_at_yheight, height))

        # 筛选在线段上的点（t ∈ [0, 1]）
        valid_intersections = []
        for (x, y) in intersections:
            # 计算 t 值
            if x2 != x1:
                t = (x - x1) / (x2 - x1)
            else:  # 垂直线，用 y 计算 t
                t = (y - y1) / (y2 - y1)

            if 0 <= t <= 1:  # 确保在线段上
                valid_intersections.append((x, y))

        # 由于 (x1,y1) 在图片内，(x2,y2) 在图片外，应该只有一个交点
        return valid_intersections[0] if valid_intersections else None

    def complete_rectangle(self):
        """
        完成矩形的绘制
        矩形绘制完成的标志修改，矩形添加到canvas的shape列表中，重新实例化一个矩形对象操作均由本函数实现
        """
        # 删除动态线条
        if self.temp_rectangle:
            self.canvas.delete(self.temp_rectangle)

        # 绘制完整的矩形
        x0, y0, _ = self.points[0]  # 第一个顶点坐标
        x0 = x0 * self.canvas_frame.zoom_ratio[0]
        y0 = y0 * self.canvas_frame.zoom_ratio[0]
        x_last, y_last, _ = self.points[-1]  # 第二个顶点坐标
        x_last = x_last * self.canvas_frame.zoom_ratio[0]
        y_last = y_last * self.canvas_frame.zoom_ratio[0]
        self.rectangle_id = self.canvas.create_rectangle(x_last, y_last, x0, y0, fill="", outline="#800000", width=3)  # 完成矩形绘制
        self.complete = True  # 标记矩形完成
        # 将点都转成红色
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="#800000")

        self.canvas_frame.shape.append(self)  # 将当前矩形添加到shape列表中
        self.canvas_frame.create_new_current_operation()  # 重新实例化一个shape
        # print(self.canvas_frame.shape)  # 打印测试是否添加成功

    def bind_events(self):  # 每次新建一个绘图对象就要绑定事件
        self.on_click_id = self.canvas.bind("<Button-1>", self.on_click, add="+")      # 左键点击确定点  "+"表示添加新绑定而不覆盖现有绑定
        self.on_mouse_move_id = self.canvas.bind("<Motion>", self.on_mouse_move, add="+")   # 鼠标移动动态跟随
        self.root.bind("<Control-z>", self.undo)         # Ctrl+Z 撤销

    def on_click(self, event):
        """
        鼠标点击事件：确定一个点，绘制或完成矩形绘制
        """
        # 获取鼠标点击的 Canvas 坐标
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # 如果当前没有图片，直接返回
        current_image = self.canvas_frame.current_image
        if current_image is None:
            return

        # 获取当前图片的宽高
        img_width = current_image.width
        img_height = current_image.height

        # 检查点击位置是否在图片范围内
        if 0 <= x <= img_width and 0 <= y <= img_height:
            # points = [(x, y)]
            if self.complete:
                return  # 完成的多边形不允许添加新点

            # 检查是否为矩形的第二个点
            if len(self.points) >= 1:
                image_x = x / self.canvas_frame.zoom_ratio[0]
                image_y = y / self.canvas_frame.zoom_ratio[0]
                point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                                   fill="#00ff00")  # 绘制点(绘制点需要使用canvas上的实际坐标)
                self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

                self.complete_rectangle()  # 完成矩形绘制
                return

            # 添加当前点到顶点列表
            # 将canvas上的坐标转化为相对于图片的坐标（即原始像素坐标）
            image_x = x / self.canvas_frame.zoom_ratio[0]
            image_y = y / self.canvas_frame.zoom_ratio[0]
            point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#00ff00")  # 绘制点(绘制点需要使用canvas上的实际坐标)
            self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

    def on_mouse_move(self, event):
        """
        鼠标移动事件：动态显示从最后一个点到当前鼠标位置的线条
        """
        # 获取鼠标当前的 Canvas 坐标
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # 如果当前没有图片，直接返回
        current_image = self.canvas_frame.current_image
        if current_image is None:
            return

        # 获取当前图片的宽高
        img_width = current_image.width
        img_height = current_image.height

        # 如果没有点或矩形已完成完成，则直接返回
        if not self.points or self.complete:
            return

        last_x, last_y, _ = self.points[-1]  # 也就是第一个顶点坐标
        last_x = last_x * self.canvas_frame.zoom_ratio[0]
        last_y = last_y * self.canvas_frame.zoom_ratio[0]

        # 保存当前点的相对坐标
        if 0 <= x <= img_width and 0 <= y <= img_height:  # 如果当前鼠标位置在图片内则保存当前点的相对坐标
            self.current_local_point = (x / self.canvas_frame.zoom_ratio[0], y / self.canvas_frame.zoom_ratio[0])
        else:  # 如果当前鼠标位置在图片外则保存当前点的相对坐标为图片边界上的点
            self.current_local_point = self.find_intersection(img_width, img_height, last_x, last_y, x, y)
            self.current_local_point = (self.current_local_point[0] / self.canvas_frame.zoom_ratio[0],
                                        self.current_local_point[1] / self.canvas_frame.zoom_ratio[0])

        # 删除之前的临时矩形
        if self.temp_rectangle:
            self.canvas.delete(self.temp_rectangle)

        # 绘制新的临时矩形
        if 0 <= x <= img_width and 0 <= y <= img_height:  # 如果当前鼠标位置在图片内
            self.temp_rectangle = self.canvas.create_rectangle(last_x, last_y, x, y, fill="", outline="#00ff00",
                                                               width=3)
        else:  # 如果当前鼠标位置在图片外
            # 鼠标当前点与上一个点之间的连线与图片边界的交点作为绘制的临时点
            meeting_point = self.find_intersection(img_width, img_height, last_x, last_y, x, y)
            self.temp_rectangle = self.canvas.create_rectangle(last_x, last_y, meeting_point[0], meeting_point[1],
                                                               fill="", outline="#00ff00", width=3)

    def undo(self, event=None):
        """
        撤销上一步操作：删除最后一个点和其对应的边线
        """
        if not self.points:
            return

        # 删除最后一个点(也就是第一个顶点)
        _, _, point_id = self.points.pop()
        self.canvas.delete(point_id)

        # 删除动态矩形
        if self.temp_rectangle:
            self.canvas.delete(self.temp_rectangle)

    def unbind_events(self):  # 结束该对象的绘制需要解绑事件
        self.canvas.unbind("<Button-1>", self.on_click_id)
        self.canvas.unbind("<Motion>", self.on_mouse_move_id)
        self.root.unbind("<Control-z>")

    def bind_edit_events(self):  # 绑定编辑事件
        self.select()  # 选中多边形，将颜色改为蓝色
        self.move_polygon()  # 绑定移动多边形的多个事件
        self._hover_id = self.canvas.bind("<Motion>", self._on_hover, add='+')


    def unbind_edit_events(self):  # 解绑编辑事件
        if self.is_select:  # 如果该多边形被选中则可以解绑，否则不需要解绑
            self.is_select = False  # 标记该多边形未被选中
            self.deselect()  # 取消选中多边形，将颜色改为红色
            self.canvas.unbind("<Motion>", self._hover_id)  # 解绑悬停事件
            self.canvas.unbind("<Button-1>", self.button1_id)  # 解绑鼠标按下事件
            # self.canvas.unbind("<B1-Motion>")  # 解绑鼠标拖动事件
            self.canvas.unbind("<ButtonRelease-1>")  # 解绑鼠标释放事件

    def bind_image_zoom_event(self):  # 绑定到图片缩放事件
        self.canvas.bind("<MouseWheel>", self.canvas_frame.on_zoom)  # 滚轮缩放事件

    def get_root_window(self):
        """递归找到 Tk 根窗口"""
        parent = self.canvas
        while parent.master is not None:
            parent = parent.master
        return parent

    def redraw(self, dx=0, dy=0):  # 因图片缩放或标注移动重新绘制以正确显示
        if self.complete:
            # 记录所有点的坐标
            points = [(x + dx, y + dy) for x, y, _ in self.points]
            # 删除所有点和矩形
            for _, _, point_id in self.points:
                self.canvas.delete(point_id)
            if self.rectangle_id:
                self.canvas.delete(self.rectangle_id)
            # 重新绘制点和矩形
            self.points = []
            self.rectangle_id = None
            # 绘制点
            for i, (image_x, image_y) in enumerate(points):
                # 将相对于图片的坐标转化为canvas上的坐标并绘制
                x = image_x * self.canvas_frame.zoom_ratio[0]
                y = image_y * self.canvas_frame.zoom_ratio[0]
                point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#800000")  # 绘制点(绘制点还是需要canvas上的实际坐标)
                self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

            # 绘制矩形
            x1, y1, _ = self.points[0]
            x2, y2, _ = self.points[1]
            self.rectangle_id = self.canvas.create_rectangle(x1 * self.canvas_frame.zoom_ratio[0], y1 * self.canvas_frame.zoom_ratio[0],
                                                             x2 * self.canvas_frame.zoom_ratio[0], y2 * self.canvas_frame.zoom_ratio[0],
                                                             fill="", outline="#800000", width=3)  # 完成矩形绘制

            # 根据是否选中，改变颜色
            if self.is_select:
                self.select()
            else:
                self.deselect()


    def dynamic_draw(self):  # 动态重绘矩形 这个矩形是没有绘制完成的
        if not self.complete:
            # 记录所有点的坐标
            points = [(x, y) for x, y, _ in self.points]
            # 删除所有点和动态矩形
            for _, _, point_id in self.points:
                self.canvas.delete(point_id)
            if self.temp_rectangle:
                self.canvas.delete(self.temp_rectangle)

            # 重新绘制点和动态矩形
            self.points = []
            self.temp_rectangle = None
            # 绘制点
            for i, (image_x, image_y) in enumerate(points):
                # 将相对于图片的坐标转化为canvas上的坐标并绘制
                x = image_x * self.canvas_frame.zoom_ratio[0]
                y = image_y * self.canvas_frame.zoom_ratio[0]
                point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                                   fill="#00ff00")  # 绘制点(绘制点还是需要canvas上的实际坐标)
                self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

            # 绘制动态矩形
            last_x, last_y, _ = self.points[-1]
            # 获取鼠标当前的 Canvas 坐标 并将其转换为 canvas 上的坐标 并绘制动态矩形
            self.temp_rectangle = self.canvas.create_rectangle(last_x * self.canvas_frame.zoom_ratio[0],
                                                               last_y * self.canvas_frame.zoom_ratio[0],
                                                               self.current_local_point[0] * self.canvas_frame.zoom_ratio[0],
                                                               self.current_local_point[1] * self.canvas_frame.zoom_ratio[0],
                                                               fill="", outline="#800000", width=3)

    def to_dict(self):
        if self.complete:
            return {'type': 'rectangle', 'points': [(x, y) for x, y, _ in self.points]}

    def draw_json(self):
        self.complete = True
        # 绘制点
        for i, (image_x, image_y) in enumerate(self.json_points):
            # 将相对于图片的坐标转化为canvas上的坐标并绘制
            x = image_x * self.canvas_frame.zoom_ratio[0]
            y = image_y * self.canvas_frame.zoom_ratio[0]
            point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#800000")  # 绘制点(绘制点还是需要canvas上的实际坐标)
            self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

        # 绘制矩形
        x1, y1, _ = self.points[0]
        x2, y2, _ = self.points[1]
        self.rectangle_id = self.canvas.create_rectangle(x1 * self.canvas_frame.zoom_ratio[0],
                                                         y1 * self.canvas_frame.zoom_ratio[0],
                                                         x2 * self.canvas_frame.zoom_ratio[0],
                                                         y2 * self.canvas_frame.zoom_ratio[0],
                                                         fill="", outline="#800000", width=3)

    def delete_myself(self):  # 删除单个多边形，包括点和矩形
        for _, _, point_id in self.points:
            self.canvas.delete(point_id)
        self.canvas.delete(self.rectangle_id)

    def is_in_shape(self, x, y):  # 判断所给的相对位置的点是否在这个矩形内
        if not self.complete or len(self.points) < 2:
            return False
        x1, y1, _ = self.points[0]
        x2, y2, _ = self.points[1]
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)
        return left <= x <= right and top <= y <= bottom

    def find_nearest_vertex(self, canvas_x, canvas_y, tolerance=8):  # 检测鼠标是否在顶点容差内
        """0
        返回距离 (canvas_x, canvas_y) 最近的顶点索引，不在容差内则返回 None
        参数使用 canvas 坐标而非图片坐标，因为容差是视觉像素概念，与缩放比例无关
        tolerance=8 表示鼠标距离顶点圆心 8 像素以内就认定为"靠近"
        """
        if not self.complete or not self.points:
            return None  # 如果多边形未完成或没有点，则返回 None
        zoom = self.canvas_frame.zoom_ratio[0]
        min_dist = float('inf')  # 初始化最小距离为无穷大
        nearest_idx = None  # 初始化最近顶点索引为 None
        for i, (img_x, img_y, _) in enumerate(self.points):  # 遍历所有顶点
            cx = img_x * zoom  # 将相对于图片的坐标转化为canvas上的坐标
            cy = img_y * zoom  # 将相对于图片的坐标转化为canvas上的坐标
            dist = ((canvas_x - cx) ** 2 + (canvas_y - cy) ** 2) ** 0.5  # 计算鼠标到顶点的距离
            if dist < min_dist:  # 如果当前顶点距离更近
                min_dist = dist  # 更新最小距离
                nearest_idx = i  # 更新最近顶点索引
        return nearest_idx if min_dist <= tolerance else None  # 返回最近顶点索引，若不在容差内则返回 None

    def select(self):
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="blue")  # 选中时将点的颜色改为蓝色
        self.canvas.itemconfig(self.rectangle_id, outline="blue")  # 选中时将矩形的颜色改为蓝色

    def deselect(self):
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="#800000")  # 取消选中时将点的颜色改回红色
        self.canvas.itemconfig(self.rectangle_id, outline="#800000")  # 取消选中时将矩形的颜色改回红色

    def move_polygon(self):  # 移动多边形
        # 整个移动多边形
        self.drag_data = {"x": 0, "y": 0}  # 拖拽状态变量， 记录按下时相对于图片的位置
        self.drag_mode = None  # "vertex" | "polygon" | None  拖拽模式， None 表示未拖拽
        self.drag_vertex_idx = None  # 被拖拽的顶点索引 这个索引也就是在points列表中的下标
        self._drag_snapshot = None  # 撤销操作的快照，用于恢复到上一个状态时使用
        self._drag_moved = False  # 新增：本次拖拽是否确实移动过
        # 绑定鼠标事件
        self.button1_id = self.canvas.bind("<Button-1>", self.mouse_press_event, add='+')  # 绑定鼠标按下事件
        # self.canvas.bind("<B1-Motion>", self.mouse_drag)  # 绑定鼠标拖动事件
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release_event)  # 绑定鼠标松开事件

    def mouse_press_event(self, event):
        print("触发鼠标按下事件")
        # 判断当前点击的位置是否在当前选中的多边形内  或者  判断当前点击位置是否在标注点附近
        temp_x = self.canvas.canvasx(event.x)  # 获取鼠标点击的 Canvas 坐标x
        temp_y = self.canvas.canvasy(event.y)  # 获取鼠标点击的 Canvas 坐标y
        # 将canvas的坐标转化为图片上的相对坐标
        temp_image_x = temp_x / self.canvas_frame.zoom_ratio[0]
        temp_image_y = temp_y / self.canvas_frame.zoom_ratio[0]

        # 优先级 1：顶点拖拽
        vertex_idx = self.find_nearest_vertex(temp_x, temp_y, tolerance=8)  # 检测鼠标是否在顶点容差内
        if vertex_idx is not None:  # 如果鼠标在顶点容差内
            self.drag_mode = "vertex"  # 设置拖拽模式为顶点拖拽
            self.drag_vertex_idx = vertex_idx  # 记录被拖拽的顶点索引
            img_x, img_y, _ = self.points[vertex_idx]  # 获取被拖拽的顶点的图片坐标
            self._drag_snapshot = {
                'type': 'move_vertex',
                'vertex_idx': vertex_idx,
                'old_pos': (img_x, img_y),
            }  # 记录被拖拽的顶点的旧位置
            self._drag_moved = False  # 本次拖拽是否确实移动过
            self.drag_data["x"] = event.x / self.canvas_frame.zoom_ratio[0]
            self.drag_data["y"] = event.y / self.canvas_frame.zoom_ratio[0]
            self.canvas.config(cursor="crosshair")
            self.canvas.bind("<B1-Motion>", self.mouse_drag_vertex, add='+')  # 绑定鼠标拖动事件(顶点拖拽)
            return

        # 优先级 2：整体拖拽
        if not self.is_in_shape(temp_image_x, temp_image_y):
            return  # 如果点击的位置不在当前选中的多边形内，则直接返回
        self.drag_mode = "polygon"
        self._drag_snapshot = {
            'type': 'move_polygon',
            'old_points': [(x, y) for x, y, _ in self.points],
        }  # 记录被拖拽的多边形的旧位置
        self._drag_moved = False  # 本次拖拽是否确实移动过

        # 处理鼠标按下事件（按下不松开）
        self.drag_data["x"] = event.x / self.canvas_frame.zoom_ratio[0]  # 记录鼠标按下时相对于图片的x坐标
        self.drag_data["y"] = event.y / self.canvas_frame.zoom_ratio[0]  # 记录鼠标按下时相对于图片的y坐标

        # 改变光标样式
        self.canvas.config(cursor="fleur")

        # 按下按钮时绑定拖拽事件（防止标注瞬移）
        self.canvas.bind("<B1-Motion>", self.mouse_drag)  # 绑定鼠标拖动事件

    def mouse_drag_vertex(self, event):  # 处理顶点拖拽事件
        dx = event.x / self.canvas_frame.zoom_ratio[0] - self.drag_data["x"]
        dy = event.y / self.canvas_frame.zoom_ratio[0] - self.drag_data["y"]

        # 计算顶点新位置（图片坐标）
        img_x, img_y, point_id = self.points[self.drag_vertex_idx]  # 获取被拖拽的顶点的图片坐标
        new_img_x = img_x + dx  # 计算新位置的x坐标
        new_img_y = img_y + dy  # 计算新位置的y坐标

        # 更新画布上的顶点圆
        zoom = self.canvas_frame.zoom_ratio[0]
        cx, cy = new_img_x * zoom, new_img_y * zoom  # 计算新位置的圆心坐标
        self.canvas.coords(point_id, cx - 5, cy - 5, cx + 5, cy + 5)  # 更新顶点圆的坐标，保持圆的半径为5像素

        # 更新顶点数据
        self.points[self.drag_vertex_idx] = (new_img_x, new_img_y, point_id)

        # 更新与该顶点相连的两条边
        self._update_vertex_rectangle(self.drag_vertex_idx)  # 更新被拖拽的顶点关联的两条边

        # 更新拖拽基准点
        self.drag_data["x"] = event.x / self.canvas_frame.zoom_ratio[0]
        self.drag_data["y"] = event.y / self.canvas_frame.zoom_ratio[0]

        self._drag_moved = True  # 本次拖拽确实移动过

    def mouse_drag(self, event):  # 处理鼠标拖动事件
        # if self.is_drag:  # 只有在拖拽状态下才处理
        # 计算鼠标相对于图片的移动的距离
        dx = event.x / self.canvas_frame.zoom_ratio[0] - self.drag_data["x"]
        dy = event.y / self.canvas_frame.zoom_ratio[0] - self.drag_data["y"]

        # 重绘多边形
        self.redraw(dx, dy)

        # 更新上次鼠标位置
        self.drag_data["x"] = event.x / self.canvas_frame.zoom_ratio[0]  # 更新上次鼠标位置的x坐标
        self.drag_data["y"] = event.y / self.canvas_frame.zoom_ratio[0]  # 更新上次鼠标位置的y坐标

        self._drag_moved = True

    def mouse_release_event(self, event):  # 处理鼠标松开事件
        # 恢复光标样式
        self.canvas.config(cursor="")
        # 松开按钮时解绑拖动事件（防止标注瞬移）
        self.canvas.unbind("<B1-Motion>")  # 解绑鼠标拖动事件

        if self._drag_snapshot is not None and self._drag_moved:  # 只有在拖拽状态下才处理
            self._drag_snapshot['shape'] = self  # 记录当前选中的多边形
            self.canvas_frame.push_edit_action(self._drag_snapshot)  # 推送编辑操作到撤销栈

        self._drag_snapshot = None
        self._drag_moved = False
        self.drag_mode = None
        self.drag_vertex_idx = None


    def _update_vertex_rectangle(self, vertex_idx):  # 更新矩形轮廓的 canvas 坐标
        """矩形用单个 rectangle_id 表示，顶点拖拽后更新整个矩形轮廓"""
        zoom = self.canvas_frame.zoom_ratio[0]
        x1, y1, _ = self.points[0]
        x2, y2, _ = self.points[1]
        self.canvas.coords(self.rectangle_id, x1 * zoom, y1 * zoom, x2 * zoom, y2 * zoom)

    def _on_hover(self, event):  # 悬停光标反馈 鼠标悬停时给用户视觉提示
        temp_x = self.canvas.canvasx(event.x)
        temp_y = self.canvas.canvasy(event.y)
        if self.find_nearest_vertex(temp_x, temp_y, tolerance=8) is not None:
            self.canvas.config(cursor="hand2")
        else:
            temp_ix = temp_x / self.canvas_frame.zoom_ratio[0]
            temp_iy = temp_y / self.canvas_frame.zoom_ratio[0]
            self.canvas.config(cursor="fleur" if self.is_in_shape(temp_ix, temp_iy) else "")