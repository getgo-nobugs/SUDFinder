from collections import Counter
from PIL import Image


def crop_image(image_path, coord1, coord2, output_path):
    """
    Crop the image specified by the image_path from coord1 to coord2 and save it to output_path.

    :param image_path: Path to the input image.
    :param coord1: Tuple (x1, y1) for the top-left corner of the crop box.
    :param coord2: Tuple (x2, y2) for the bottom-right corner of the crop box.
    :param output_path: Path to save the cropped image.
    """
    # Open the image
    with Image.open(image_path) as img:
        # Define the crop box
        left = min(coord1[0], coord2[0])
        upper = min(coord1[1], coord2[1])
        right = max(coord1[0], coord2[0])
        lower = max(coord1[1], coord2[1])

        # Crop the image
        cropped_img = img.crop((left, upper, right, lower))

        # Save the cropped image
        cropped_img.save(output_path)
        print(f"Cropped image saved to {output_path}")

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

# Example usage
image_path = '../cat.jpg'
coord1 = (200, 100)
coord2 = (400, 400)
output_path = '../cropped_example.jpg'

crop_image(image_path, coord1, coord2, output_path)

top_colors = get_top_colors(output_path, 2)

for color, count in top_colors:
    print(f"Color: {color}, Count: {count}")