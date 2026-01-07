# 根据图片大小和画布大小，计算图片适应画布的比例
# def adaptation_image(original_width, original_height, canvas_width, canvas_height):
#     if canvas_width/canvas_height > original_width/original_height:
#         new_height = canvas_height
#         new_width = original_width * new_height / original_height
#     elif canvas_width/canvas_height < original_width/original_height:
#         new_width = canvas_width
#         new_height = original_height * new_width / original_width
#     else:
#         new_width = canvas_width
#         new_height = canvas_height
#
#     zoom_ratio = [new_width/original_width, new_height/original_height]
#     # print('适应画布后的比例', zoom_ratio)
#     return zoom_ratio

def adaptation_image(original_width, original_height, canvas_width, canvas_height):
    # 使用整数运算提高计算速度
    if canvas_width * original_height > original_width * canvas_height:
        new_height = canvas_height
        new_width = (original_width * new_height) // original_height
    elif canvas_width * original_height < original_width * canvas_height:
        new_width = canvas_width
        new_height = (original_height * new_width) // original_width
    else:
        new_width = canvas_width
        new_height = canvas_height

    # 直接返回整数比例，减少浮点运算
    return [new_width / original_width, new_height / original_height]


# from fractions import Fraction
#
#
# def adaptation_image(original_width, original_height, canvas_width, canvas_height):
#     # 将宽高转换为 Fraction 类型进行精确计算
#     cw = Fraction(canvas_width)
#     ch = Fraction(canvas_height)
#     ow = Fraction(original_width)
#     oh = Fraction(original_height)
#
#     canvas_ratio = cw / ch
#     image_ratio = ow / oh
#
#     if canvas_ratio > image_ratio:
#         new_height = ch
#         new_width = ow * new_height / oh
#     elif canvas_ratio < image_ratio:
#         new_width = cw
#         new_height = oh * new_width / ow
#     else:
#         new_width = cw
#         new_height = ch
#
#     zoom_ratio = [new_width / ow, new_height / oh]
#     print('适应画布后的比例', zoom_ratio)
#     return zoom_ratio
