import numpy as np
from PIL import Image, ImageOps

def detect_text_alignment(image_path):
    # 读取图像
    image = Image.open(image_path).convert("L")

    # 检测背景颜色
    avg_pixel_value = np.mean(image)
    is_light_background = avg_pixel_value > 128

    # 二值化图像
    if is_light_background:
        binary_image = image.point(lambda p: p > 128 and 255)
        binary_image = ImageOps.invert(binary_image)
    else:
        binary_image = image.point(lambda p: p > 128 and 255)

    # 将图像转换为numpy数组
    binary_array = np.array(binary_image)

    # 获取每行的非零像素（即文本部分）
    row_sums = np.sum(binary_array, axis=1)
    text_rows = np.where(row_sums > 0)[0]

    left_margins = []
    right_margins = []

    # 计算每行的左边和右边边距
    for row in text_rows:
        cols = np.where(binary_array[row] > 0)[0]
        if len(cols) > 0:
            left_margins.append(cols[0])
            right_margins.append(binary_array.shape[1] - 1 - cols[-1])

    # 计算平均左边和右边边距
    avg_left_margin = np.mean(left_margins) if left_margins else 0
    avg_right_margin = np.mean(right_margins) if right_margins else 0

    # 确定对齐方式
    alignment = "other"
    # import numpy as np
    # from PIL import Image, ImageOps
    #
    # def detect_text_alignment(image_path):
    #     # 读取图像
    #     image = Image.open(image_path).convert("L")
    #
    #     # 检测背景颜色
    #     avg_pixel_value = np.mean(image)
    #     is_light_background = avg_pixel_value > 128
    #
    #     # 二值化图像
    #     if is_light_background:
    #         binary_image = image.point(lambda p: p > 128 and 255)
    #         binary_image = ImageOps.invert(binary_image)
    #     else:
    #         binary_image = image.point(lambda p: p > 128 and 255)
    #
    #     # 将图像转换为numpy数组
    #     binary_array = np.array(binary_image)
    #
    #     # 获取每行的非零像素（即文本部分）
    #     row_sums = np.sum(binary_array, axis=1)
    #     text_rows = np.where(row_sums > 0)[0]
    #
    #     left_margins = []
    #     right_margins = []
    #
    #     # 计算每行的左边和右边边距
    #     for row in text_rows:
    #         cols = np.where(binary_array[row] > 0)[0]
    #         if len(cols) > 0:
    #             left_margins.append(cols[0])
    #             right_margins.append(binary_array.shape[1] - 1 - cols[-1])
    #
    #     # 计算平均左边和右边边距
    #     avg_left_margin = np.mean(left_margins) if left_margins else 0
    #     avg_right_margin = np.mean(right_margins) if right_margins else 0
    #
    #     # 确定对齐方式
    #     alignment = "other"
    #     if avg_left_margin < binary_array.shape[1] * 0.1 and avg_right_margin < binary_array.shape[1] * 0.1:
    #         alignment = "justify"
    #     elif abs(avg_left_margin - avg_right_margin) < binary_array.shape[1] * 0.1:  # 调整后的中间对齐阈值
    #         alignment = "center"
    #     elif avg_left_margin < avg_right_margin * 0.5:
    #         alignment = "left"
    #     elif avg_right_margin < avg_left_margin * 0.5:
    #         alignment = "right"
    #
    #     return alignment

    if avg_left_margin < binary_array.shape[1] * 0.1 and avg_right_margin < binary_array.shape[1] * 0.1:
        alignment = "justify"
    elif abs(avg_left_margin - avg_right_margin) < binary_array.shape[1] * 0.1:  # 调整后的中间对齐阈值
        alignment = "center"
    elif avg_left_margin < avg_right_margin * 0.5:
        alignment = "left"
    elif avg_right_margin < avg_left_margin * 0.5:
        alignment = "right"

    return alignment


if __name__ == '__main__':
    align = detect_text_alignment('/Users/huanghuaxun/PycharmProjects/setdiff/v2/test/ltr modeleaf_node1_180138312601449.png')
    print(align)