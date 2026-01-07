from tkinter.filedialog import askdirectory
import os
import re
from natsort import natsorted


def open_dir():
    # 设置文件类型过滤，只显示图像文件
    file_types = [("Image Files", "*.bmp;*.cur;*.gif;*.icns;*.ico;*.jpeg;*.jpg;"
                   "*.pbm;*.pgm;*.png;*tiff;*.wbmp;*.webp;*.xbm;*.xpm")]
    # 提取文件扩展名列表
    valid_extensions = [ext.strip('*') for ext in file_types[0][1].split(';')]
    path_list = []
    file_dir = askdirectory(title="选择文件夹")
    if not file_dir:
        return
    imgfiles = os.listdir(file_dir)  # 获取imgdir目录下的所有文件名
    sort_files = natsorted(imgfiles)  # 进行自然排序

    # 根据文件扩展名过滤文件
    for file in sort_files:
        if os.path.splitext(file)[1].lower() in valid_extensions:  # os.path.splitext(file)[1] 获取文件的扩展名
            path_list.append(os.path.join(file_dir, file))
    return path_list

