class PolygonShape:
    def __init__(self, canvas_frame, points=None):
        self.canvas_frame = canvas_frame
        self.canvas = canvas_frame.canvas

        self.shape_type = "polygon"  # 图形类型 多边形
        self.points = []  # 存储顶点  顶点坐标是相对于图片的坐标，而不是canvas上的绝对坐标
        # 所有 Shape 对象中的 points 都是以图像左上角为原点 (0,0)，单位是像素
        # 所以在保存 Shape 对象时，需要保存图像的缩放比例和偏移量，以便在加载时正确地绘制 Shape 对象
        self.json_points = points  # 保存顶点坐标为json格式，用于保存和加载

        self.lines = []   # 存储边线的 ID
        self.temp_line = None  # 动态线条
        self.complete = False  # 是否完成多边形
        self.current_local_point = ()  # 当前鼠标位置

        self.last_zoom_ratio = canvas_frame.zoom_ratio  # 保存当前缩放比例

        self.root = self.get_root_window()

    def on_click(self, event):
        """
        鼠标点击事件：确定一个点，绘制或完成多边形
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

            # 检查是否回到起点（闭合多边形）
            if len(self.points) >= 3 and self.is_close_to_first_point(x, y):
                self.complete_polygon()
                return

            # 添加当前点到顶点列表
            # 将canvas上的坐标转化为相对于图片的坐标（即原始像素坐标）
            image_x = x / self.canvas_frame.zoom_ratio[0]
            image_y = y / self.canvas_frame.zoom_ratio[0]
            point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#00ff00")  # 绘制点(绘制点还是需要canvas上的实际坐标)
            self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

            # 如果已有点，则绘制边线
            if len(self.points) > 1:
                # 获取前一个点的原始像素坐标并转化为canvas上的坐标
                prev_x, prev_y, _ = self.points[-2]
                prev_x = prev_x * self.canvas_frame.zoom_ratio[0]
                prev_y = prev_y * self.canvas_frame.zoom_ratio[0]
                line_id = self.canvas.create_line(prev_x, prev_y, x, y, fill="#00ff00", width=3)
                self.lines.append(line_id)

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

        # 检查点击位置是否在图片范围内
        # if 0 <= x <= img_width and 0 <= y <= img_height:
        if not self.points or self.complete:
            return

        last_x, last_y, _ = self.points[-1]
        last_x = last_x * self.canvas_frame.zoom_ratio[0]
        last_y = last_y * self.canvas_frame.zoom_ratio[0]

        # 保存当前点的相对坐标
        if 0 <= x <= img_width and 0 <= y <= img_height:  # 如果当前鼠标位置在图片内则保存当前点的相对坐标
            self.current_local_point = (x / self.canvas_frame.zoom_ratio[0], y / self.canvas_frame.zoom_ratio[0])
        else:  # 如果当前鼠标位置在图片外则保存当前点的相对坐标为图片边界上的点
            self.current_local_point = self.find_intersection(img_width, img_height, last_x, last_y, x, y)
            self.current_local_point = (self.current_local_point[0] / self.canvas_frame.zoom_ratio[0],
                                        self.current_local_point[1] / self.canvas_frame.zoom_ratio[0])

        # 删除之前的临时线条
        if self.temp_line:
            self.canvas.delete(self.temp_line)

        # 绘制新的临时线条
        if 0 <= x <= img_width and 0 <= y <= img_height:  # 如果当前鼠标位置在图片内
            self.temp_line = self.canvas.create_line(last_x, last_y, x, y, fill="#00ff00", width=3)
        else:  # 如果当前鼠标位置在图片外
            # 鼠标当前点与上一个点之间的连线与图片边界的交点作为绘制的临时点
            meeting_point = self.find_intersection(img_width, img_height, last_x, last_y, x, y)
            self.temp_line = self.canvas.create_line(last_x, last_y, meeting_point[0], meeting_point[1],
                                                     fill="#00ff00", width=3)
        # print(self.points)

            # 当前所有点围成动态阴影多边形 tkinter不支持带透明度（Alpha）通道的颜色表示，暂时不实现
            # if len(self.points) >= 2:
            #     self.canvas.delete("shadow")  # 删除之前的阴影
            #     shadow_points = []
            #     for point in self.points:
            #         shadow_points = shadow_points + [(point[0], point[1])]
            #     shadow_points = shadow_points + [(x, y)]
            #     self.canvas.create_polygon(shadow_points, fill="#00ff00", outline="", tags="shadow")

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

    def complete_polygon(self):
        """
        完成多边形的绘制：闭合多边形
        """
        # 删除动态线条
        if self.temp_line:
            self.canvas.delete(self.temp_line)

        # 绘制最后一条边，连接到起点
        x0, y0, _ = self.points[0]
        x0 = x0 * self.canvas_frame.zoom_ratio[0]
        y0 = y0 * self.canvas_frame.zoom_ratio[0]
        x_last, y_last, _ = self.points[-1]
        x_last = x_last * self.canvas_frame.zoom_ratio[0]
        y_last = y_last * self.canvas_frame.zoom_ratio[0]
        line_id = self.canvas.create_line(x_last, y_last, x0, y0, fill="#00ff00", width=3)
        self.lines.append(line_id)
        self.complete = True  # 标记多边形完成
        # 将点和线都转成红色
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="#800000")
        for line_id in self.lines:
            self.canvas.itemconfig(line_id, fill="#800000")

        self.canvas_frame.shape.append(self)  # 将当前多边形添加到shape列表中
        self.canvas_frame.create_new_current_operation()  # 重新实例化一个shape
        print(self.canvas_frame.shape)  # 打印测试是否添加成功

    def is_close_to_first_point(self, x, y, tolerance=10):
        """
        检查鼠标是否接近第一个顶点，用于判断闭合多边形
        """
        if not self.points:
            return False

        x0, y0, _ = self.points[0]
        x0 = x0 * self.canvas_frame.zoom_ratio[0]
        y0 = y0 * self.canvas_frame.zoom_ratio[0]
        return (x - x0) ** 2 + (y - y0) ** 2 <= tolerance ** 2

    def undo(self, event=None):
        """
        撤销上一步操作：删除最后一个点和其对应的边线
        """
        # if self.complete:
        #     for _, _, point_id in self.points:
        #         self.canvas.delete(point_id)
        #     for line_id in self.lines:
        #         self.canvas.delete(line_id)
        #     self.points = []
        #     self.lines = []
        #     self.canvas.delete(self.temp_line)
        #     self.temp_line = None
        #     self.complete = False
        #     return  # 直接删除多边形

        if not self.points:
            return

        # 删除最后一个点
        _, _, point_id = self.points.pop()
        self.canvas.delete(point_id)

        # 删除最后一条线（如果有）
        if self.lines:
            line_id = self.lines.pop()
            self.canvas.delete(line_id)
        if not self.points:
            self.canvas.delete(self.temp_line)

        # # 如果撤销到空状态，清空完成状态
        # if not self.points:
        #     self.complete = False

        # 如果有动态线条，重新更新动态线条
        if self.points and self.temp_line:
            self.canvas.delete(self.temp_line)
            last_x, last_y, _ = self.points[-1]
            last_x = last_x * self.canvas_frame.zoom_ratio[0]
            last_y = last_y * self.canvas_frame.zoom_ratio[0]

            # 获取鼠标的屏幕坐标 (因为这个undo函数绑定的是root而不是canvas，所以获取的坐标要转换成canvas坐标）
            x_screen, y_screen = self.canvas.winfo_pointerxy()
            # 转换为 Canvas 坐标
            x = self.canvas.canvasx(x_screen - self.canvas.winfo_rootx())
            y = self.canvas.canvasy(y_screen - self.canvas.winfo_rooty())

            self.temp_line = self.canvas.create_line(last_x, last_y, x, y, fill="#00ff00", width=3)

    def bind_events(self):
        self.on_click_id = self.canvas.bind("<Button-1>", self.on_click, add="+")      # 左键点击确定点
        self.on_mouse_move_id = self.canvas.bind("<Motion>", self.on_mouse_move, add="+")   # 鼠标移动动态跟随
        self.root.bind("<Control-z>", self.undo)         # Ctrl+Z 撤销

    def unbind_events(self):
        self.canvas.unbind("<Button-1>", self.on_click_id)
        self.canvas.unbind("<Motion>", self.on_mouse_move_id)
        self.root.unbind("<Control-z>")

    def bind_image_zoom_event(self):  # 绑定到图片缩放事件
        self.canvas.bind("<MouseWheel>", self.canvas_frame.on_zoom)  # 滚轮缩放事件

    def get_root_window(self):
        """递归找到 Tk 根窗口"""
        parent = self.canvas
        while parent.master is not None:
            parent = parent.master
        return parent

    def redraw(self):  # 因图片缩放重新绘制
        if self.complete:
            # 记录所有点的坐标
            points = [(x, y) for x, y, _ in self.points]
            # 删除所有点和线
            for _, _, point_id in self.points:
                self.canvas.delete(point_id)
            for line_id in self.lines:
                self.canvas.delete(line_id)
            # 重新绘制点和线
            self.points = []
            self.lines = []
            # 绘制点
            for i, (image_x, image_y) in enumerate(points):
                # 将相对于图片的坐标转化为canvas上的坐标并绘制
                x = image_x * self.canvas_frame.zoom_ratio[0]
                y = image_y * self.canvas_frame.zoom_ratio[0]
                point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#800000")  # 绘制点(绘制点还是需要canvas上的实际坐标)
                self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

            # 绘制线
            for i in range(len(self.points)):
                x1, y1, _ = self.points[i]
                x2, y2, _ = self.points[(i + 1) % len(self.points)]
                line_id = self.canvas.create_line(x1 * self.canvas_frame.zoom_ratio[0], y1 * self.canvas_frame.zoom_ratio[0],
                                                  x2 * self.canvas_frame.zoom_ratio[0], y2 * self.canvas_frame.zoom_ratio[0],
                                                  fill="#800000", width=3)  # 绘制线(绘制线还是需要canvas上的实际坐标)
                self.lines.append(line_id)

    def dynamic_draw(self):  # 动态重绘多边形
        if not self.complete:
            # 记录所有点的坐标
            points = [(x, y) for x, y, _ in self.points]
            # 删除所有点和线
            for _, _, point_id in self.points:
                self.canvas.delete(point_id)
            for line_id in self.lines:
                self.canvas.delete(line_id)
            # 重新绘制点和线
            self.points = []
            self.lines = []
            # 绘制点
            for i, (image_x, image_y) in enumerate(points):
                # 将相对于图片的坐标转化为canvas上的坐标并绘制
                x = image_x * self.canvas_frame.zoom_ratio[0]
                y = image_y * self.canvas_frame.zoom_ratio[0]
                point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                                   fill="#00ff00")  # 绘制点(绘制点还是需要canvas上的实际坐标)
                self.points.append((image_x, image_y, point_id))  # 存储点和其 ID
            # 绘制线
            for i in range(len(self.points) - 1):
                x1, y1, _ = self.points[i]
                x2, y2, _ = self.points[(i + 1)]
                line_id = self.canvas.create_line(x1 * self.canvas_frame.zoom_ratio[0],
                                                  y1 * self.canvas_frame.zoom_ratio[0],
                                                  x2 * self.canvas_frame.zoom_ratio[0],
                                                  y2 * self.canvas_frame.zoom_ratio[0],
                                                  fill="#00ff00", width=3)  # 绘制线(绘制线还是需要canvas上的实际坐标)
                self.lines.append(line_id)
            # 绘制最后一个点到鼠标当前点的线
            if len(self.points) > 0:
                last_x, last_y, _ = self.points[-1]
                # 获取鼠标当前的 Canvas 坐标
                self.temp_line = self.canvas.create_line(last_x * self.canvas_frame.zoom_ratio[0],
                                                         last_y * self.canvas_frame.zoom_ratio[0],
                                                         self.current_local_point[0] * self.canvas_frame.zoom_ratio[0],
                                                         self.current_local_point[1] * self.canvas_frame.zoom_ratio[0],
                                                         fill="#00ff00", width=3)  # 绘制线(绘制线还是需要canvas上的实际坐标)

    def to_dict(self):
        if self.complete:
            return {'type': 'polygon', 'points': [(x, y) for x, y, _ in self.points]}

    def draw_json(self):
        self.complete = True
        # 绘制点
        for i, (image_x, image_y) in enumerate(self.json_points):
            # 将相对于图片的坐标转化为canvas上的坐标并绘制
            x = image_x * self.canvas_frame.zoom_ratio[0]
            y = image_y * self.canvas_frame.zoom_ratio[0]
            point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#800000")  # 绘制点(绘制点还是需要canvas上的实际坐标)
            self.points.append((image_x, image_y, point_id))  # 存储点和其 ID

        # 绘制线
        for i in range(len(self.points)):
            x1, y1, _ = self.points[i]
            x2, y2, _ = self.points[(i + 1) % len(self.json_points)]
            line_id = self.canvas.create_line(x1 * self.canvas_frame.zoom_ratio[0],
                                              y1 * self.canvas_frame.zoom_ratio[0],
                                              x2 * self.canvas_frame.zoom_ratio[0],
                                              y2 * self.canvas_frame.zoom_ratio[0],
                                              fill="#800000", width=3)  # 绘制线(绘制线还是需要canvas上的实际坐标)
            self.lines.append(line_id)

    def delete_myself(self):  # 删除多边形
        for _, _, point_id in self.points:
            self.canvas.delete(point_id)
        for line_id in self.lines:
            self.canvas.delete(line_id)

    def is_in_polygon(self, x, y):  # 判断所给的相对位置的点是否在这个多边形内(射线法)
        n = len(self.points)
        inside = False

        # 遍历多边形的每一条边
        for i in range(n):
            x1, y1, _ = self.points[i]
            x2, y2, _ = self.points[(i + 1) % n]  # 下一条边（循环）

            # 检查点是否在多边形的边上
            if self.point_on_segment((x1, y1), (x2, y2), (x, y)):
                return True

            # 计算射线与边的交点
            if ((y1 > y) != (y2 > y)):  # 点的 y 坐标在边的 y 范围内
                # 计算交点的 x 坐标
                x_intersect = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x <= x_intersect:  # 交点在射线右侧
                    inside = not inside

        return inside

    def point_on_segment(self, p1, p2, p):
        """判断点 p 是否在线段 p1-p2 上（包括端点）"""
        x, y = p
        x1, y1 = p1
        x2, y2 = p2

        # 点 p 必须在 p1 和 p2 的矩形范围内
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            # 叉积为 0 表示共线
            cross_product = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
            if abs(cross_product) < 1e-10:  # 避免浮点误差
                return True
        return False

    def select(self):
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="blue")  # 选中时将点的颜色改为蓝色
        for line_id in self.lines:
            self.canvas.itemconfig(line_id, fill="blue")  # 选中时将线的颜色改为蓝色

    def deselect(self):
        for _, _, point_id in self.points:
            self.canvas.itemconfig(point_id, fill="#800000")  # 取消选中时将点的颜色改回红色
        for line_id in self.lines:
            self.canvas.itemconfig(line_id, fill="#800000")  # 取消选中时将线的颜色改回红色






    # def update_scale(self, zoom_ratio):
    #     """
    #     根据新的缩放比例更新多边形的位置和大小
    #     """
    #     if not self.points:
    #         return
    #
    #     # 计算缩放比例变化
    #     scale_x = zoom_ratio[0] / self.last_zoom_ratio[0] if hasattr(self, 'last_zoom_ratio') else 1
    #     scale_y = zoom_ratio[1] / self.last_zoom_ratio[1] if hasattr(self, 'last_zoom_ratio') else 1
    #     self.last_zoom_ratio = zoom_ratio
    #
    #     # 更新所有点
    #     for i, (x, y, point_id) in enumerate(self.points):
    #         new_x = x * scale_x
    #         new_y = y * scale_y
    #         self.points[i] = (new_x, new_y, point_id)
    #
    #         # 更新点的显示
    #         self.canvas.coords(point_id,
    #                            new_x - 5, new_y - 5,
    #                            new_x + 5, new_y + 5)
    #
    #     # 更新所有线条
    #     for i, line_id in enumerate(self.lines):
    #         if i == 0:
    #             x1, y1, _ = self.points[0]
    #             x2, y2, _ = self.points[1]
    #         else:
    #             x1, y1, _ = self.points[i]
    #             x2, y2, _ = self.points[i + 1] if i + 1 < len(self.points) else self.points[0]
    #
    #         self.canvas.coords(line_id, x1, y1, x2, y2)
    #
    #     # 更新临时线条
    #     if self.temp_line and len(self.points) > 0:
    #         last_x, last_y, _ = self.points[-1]
    #         x_screen, y_screen = self.canvas.winfo_pointerxy()
    #         x = self.canvas.canvasx(x_screen - self.canvas.winfo_rootx())
    #         y = self.canvas.canvasy(y_screen - self.canvas.winfo_rooty())
    #         self.canvas.coords(self.temp_line, last_x, last_y, x, y)