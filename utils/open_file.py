from tkinter.filedialog import askopenfilename


def open_file():
    # 设置文件类型过滤，只显示图像文件
    file_types = [("Image Files", "*.bmp;*.cur;*.gif;*.icns;*.ico;*.jpeg;*.jpg;"
                   "*.pbm;*.pgm;*.png;*tiff;*.wbmp;*.webp;*.xbm;*.xpm;*.json")]
    path = askopenfilename(title='选择图像或标签文件', filetypes=file_types)
    return path

