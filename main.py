from PIL import Image, ImageTk
import tkinter as tk
from pathlib import Path
from labelme_app import LabelmeApp
import ttkbootstrap as ttk
from theme.styles import set_styles


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        set_styles(ttk.Style())

        self.title("AI标注工具")
        # 获取屏幕宽高
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # 窗口默认大小
        window_width = 1250
        window_height = 600

        # 计算窗口的新位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2 - 100
        # 设置窗口的布局和大小
        self.geometry("%dx%d+%d+%d" % (window_width, window_height, x, y))
        # 设置窗口的logo
        logo_img_path = Path(__file__).parent / 'icons/logo_36px.png'
        logo_img = Image.open(logo_img_path)
        logo_photo_img = ImageTk.PhotoImage(logo_img)
        self.iconphoto(True, logo_photo_img)

        self.labelme_app = LabelmeApp(self)
        self.labelme_app.pack()

    def show_mouse_position(self, x, y):
        self.labelme_app.footer_frame.show_mouse_position(x, y)

    def show_mouse_in_button(self, tip):
        self.labelme_app.footer_frame.show_mouse_in_button(tip)


if __name__ == '__main__':
    app = MainApp()
    app.mainloop()

# 仍需优化
# 1. 图片适应窗口有小瑕疵，没有完全适应，因为滚动条可用
# 2. 分辨率较高的图片适应窗口 或者 放大缩小时，会有明显的卡顿
