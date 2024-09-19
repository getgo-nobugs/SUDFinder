from collections import Counter
from PIL import Image


def get_top_colors(image_path, num_colors=2):
    # 打开图像
    image = Image.open(image_path)

    # 将图像转换为RGB模式
    image = image.convert('RGB')

    # 获取图像中的所有像素
    pixels = list(image.getdata())

    # 统计每种颜色出现的频率
    color_counter = Counter(pixels)

    # 获取出现频率最高的前 num_colors 种颜色
    top_colors = color_counter.most_common(num_colors)

    return top_colors


# 示例用法
image_path = '../cat.jpg'  # 替换为你的图像路径
top_colors = get_top_colors(image_path, 2)

for color, count in top_colors:
    print(f"Color: {color}, Count: {count}")