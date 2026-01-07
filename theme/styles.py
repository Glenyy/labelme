import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def set_styles(style: ttk.Style):
    """main"""
    # 设置主题为 'light'
    style.theme_use('cosmo')
    style.configure('TLabel', font=('SimHei', 12))
    # 设置 TEntry 字体
    style.configure('TEntry', font=('SimHei', 12))
    # 设置 TButton 字体
    style.configure('TButton', font=('SimHei', 12))
    # 设置 TCombobox 的 Listbox 字体
    style.configure('TCombobox', font=('SimHei', 12))
    # 设置TFrame的背景颜色
    style.configure('TFrame', background='#f0f0f0')
    # 设置 TLabelframe.Label 的字体
    style.configure('TLabelframe.Label', font=('SimHei', 12))

    """tool_frame"""
    style.configure(style='frame.TFrame', background='#f0f0f0', relief=SOLID, borderwidth=0.5)

    """footer_tool_frame"""
    style.configure(style='labelme.TFrame', relief=FLAT, background='#f0f0f0', borderwidth=1)

    """tool_widget"""
    style.configure(style='tool.TButton', background='#f0f0f0', foreground='black', borderwidth=0, highlightthickness=0,
                    font=('等线', 10), height=2, widget=3)
    style.map('tool.TButton', background=[('hover', '#e5f3ff')])

    style.configure(style='selected.TButton', background='#cce8ff', foreground='black', borderwidth=0,
                    highlightthickness=0, font=('等线', 10), height=2, widget=3)
    style.map('selected.TButton', background=[('hover', '#cce8ff')])

    style.configure(style='tool.TLabel', background='#f0f0f0', font=('等线', 11, 'bold'))

    """canvas_widget"""

    """footer_widget"""
    style.configure(style='mouse.TLabel', background='#f0f0f0', foreground='black', font=('等线', 10))


