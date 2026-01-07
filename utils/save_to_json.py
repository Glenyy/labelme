import json
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox


def save_to_json(shapes, image_path, image_width, image_height, json_path=None):
    data = {
        "shapes": shapes,
        "image_path": image_path,
        "image_width": image_width,
        "image_height": image_height
    }

    # 如果有指定json_path，则保存到该文件
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:  # "w" 模式的作用：如果文件不存在，则创建新文件；如果文件已存在，则清空原有内容，从头写入新数据
            json.dump(data, f, ensure_ascii=False, indent=2)  # 中文字符不转义 缩进2个空格
            # 保存成功后弹出提示框提示保存成功
            messagebox.showinfo("提示", "保存成功")
    else:
        # 如果没有指定json_path，则打开窗口选择保存路径
        # 打开窗口选择保存路径
        save_path = asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)  # 中文字符不转义 缩进2个空格
            # 保存成功后弹出提示框提示保存成功
            messagebox.showinfo("提示", "保存成功")
        else:  # 如果直接将选择文件窗口关闭则不提示保存成功
            return


