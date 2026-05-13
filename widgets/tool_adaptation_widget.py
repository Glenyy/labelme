import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from widgets import imgdir
from core.adaptation_image import adaptation_image


class ToolAdaptationEventListener:
    def on_mouse_in_button(self, tip):
        print('ToolAdaptationEventListener')


class ToolAdaptationWidget(ttk.Frame):
    def __init__(self, master, toolAdaptationEventListener, canvas_frame):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.toolAdaptationEventListener = toolAdaptationEventListener
        self.canvas_frame = canvas_frame

        self.is_adaptation = False

        self.create_widget()

    def create_widget(self):
        self.create_adaptation_frame()

    def create_adaptation_frame(self):
        self.adaptation_frame = ttk.Frame(self, style='frame.TFrame')
        self.adaptation_frame.pack(fill=BOTH, expand=True)

        # 创建适应窗口按钮
        adaptation_img_path = os.path.join(imgdir, "zoom.png")
        adaptation_img = Image.open(adaptation_img_path)
        adaptation_img.thumbnail((25, 25), Image.LANCZOS)
        self.adaptation_photo_img = ImageTk.PhotoImage(adaptation_img)  # 使用self防止图片对象被垃圾回收
        self.adaptation_btn = ttk.Button(self.adaptation_frame, text='适应窗口(F)', image=self.adaptation_photo_img,
                                         compound=TOP, style='tool.TButton', takefocus=False, state=DISABLED,
                                         command=self.adaptation_event)
        self.adaptation_btn.bind('<Enter>', lambda event: self.on_mouse_in_button('跟随窗口大小缩放'))
        self.adaptation_btn.pack(side=LEFT, padx=5, pady=5)

        # 缩放比例显示
        self.adaptation_text = ttk.Label(self.adaptation_frame, text='缩放', style='tool.TLabel')
        self.adaptation_text.pack(side=TOP, padx=0, pady=(5, 0))

        self.entry_frame = ttk.Frame(self.adaptation_frame)
        self.entry_frame.pack(side=BOTTOM, padx=(0, 2), pady=(0, 5))
        # 配置 Entry 验证函数
        validate_cmd = self.register(self.validate_input)  # 注册验证函数
        self.adaptation_entry = ttk.Entry(self.entry_frame, width=5, style='light', font=('等线', 10, 'bold'),
                                          justify='center', validate='key', validatecommand=(validate_cmd, '%P'))
        self.adaptation_entry.insert(0, '100')
        self.adaptation_entry.config(state=DISABLED)
        self.adaptation_entry.pack(side=LEFT)
        self.adaptation_entry.bind('<Return>', self.on_enter_key)  # 绑定回车事件
        self.percentage_text = ttk.Label(self.entry_frame, text='%', style='tool.TLabel')
        self.percentage_text.pack(side=LEFT)

    def on_mouse_in_button(self, tip):
        self.toolAdaptationEventListener.on_mouse_in_button(tip)

    def adaptation_window(self, event=None):  # 图片适应窗口按钮
        # 获取原始图片的宽高
        original_width, original_height = self.canvas_frame.original_image.size
        # 获取canvas的宽高
        canvas_width, canvas_height = self.canvas_frame.canvas.winfo_width(), self.canvas_frame.canvas.winfo_height()
        # 计算缩放比例
        zoom_ratio = adaptation_image(original_width, original_height, canvas_width, canvas_height)
        self.canvas_frame.adaption_canvas(zoom_ratio)

    def adaptation_event(self):  # 当点击了适应窗口后，就会绑定这个事件，在窗口大小改变时会自动适应窗口大小
        self.is_adaptation = not self.is_adaptation  # 切换适应窗口状态
        if self.is_adaptation:
            self.adaptation_btn.config(style='selected.TButton')
            # 将适应窗口绑定到窗口大小变化事件
            self.adaptation_window()
            self.canvas_frame.bind("<Configure>", self.adaptation_window)
        else:
            self.adaptation_btn.config(style='tool.TButton')
            # 解除适应窗口绑定
            self.canvas_frame.unbind("<Configure>")
            self.canvas_frame.adaption_canvas([1, 1])

    def validate_input(self, value):  # 验证输入框只能输入数字且0不能作为开头
        if value.isdigit() or value == "":
            return True
        else:
            return False

    def update_zoom_ratio(self, zoom_ratio):
        # 将缩放比例转换为百分比
        zoom_percentage = int(zoom_ratio[0] * 100)
        self.adaptation_entry.delete(0, END)  # 清空 Entry
        self.adaptation_entry.insert(0, str(zoom_percentage))  # 插入新的比例

    def on_enter_key(self, event):  # 处理回车事件，根据用户输入调整图片大小
        user_input = self.adaptation_entry.get()
        if user_input == '':
            return  # 如果用户输入为空，则不进行任何操作
        zoom_percentage = int(user_input)
        # 将百分比转换为缩放比例
        zoom_ratio = zoom_percentage / 100
        print(zoom_ratio)
        self.canvas_frame.set_zoom_ratio([zoom_ratio, zoom_ratio])
        # 失去焦点(其实是转移了焦点)
        self.master.focus_set()


