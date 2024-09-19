from PIL import Image
from collections import Counter, defaultdict
import re
import os
import numpy as np


class Node:
    def __init__(self, line, indent):
        self.parse_line(line)
        self.children = []
        self.indent = indent

    def parse_line(self, line):
        match = re.match(r'(!*)([^{]+){([^}]+)}', line)
        self.indent = len(match.group(1))
        self.className = match.group(2).strip()
        details = match.group(3).split(' ')
        self.view_id = None
        self.layout_bounds = None
        for detail in details:
            if len(detail) == 7:
                self.view_id = detail
        match_final_numbers = re.findall(r'\d+', line)
        if len(match_final_numbers) >= 4:
            self.layout_bounds = ' '.join(match_final_numbers[-4:])
            self.x1 = self.layout_bounds.split(' ')[0]
            self.y1 = self.layout_bounds.split(' ')[1]
            self.x2 = self.layout_bounds.split(' ')[2]
            self.y2 = self.layout_bounds.split(' ')[3]

    def __repr__(self):
        return f"{'  ' * self.indent}{self.className} (id: {self.view_id}, bounds: {self.layout_bounds})"

    def get_class_name(self):
        return self.className

    def get_view_id(self):
        return self.view_id

    def get_layout_bounds(self):
        return self.layout_bounds


def build_tree(lines):
    if not lines:
        return None

    def compute_indent(line):
        return line.count('!')

    root_line = lines[0]
    root_indent = compute_indent(root_line)
    root_value = root_line.replace('!', '').strip()
    root = Node(root_value, root_indent)
    stack = [root]

    for line in lines[1:]:
        indent = compute_indent(line)
        value = line.replace('!', '').strip()
        node = Node(value, indent)
        while len(stack) > 1 and stack[-1].indent >= node.indent:
            stack.pop()
        if stack[-1].indent < node.indent:
            stack[-1].children.append(node)
            stack.append(node)
        else:
            raise ValueError("Invalid tree structure: indentation error.")

    return root


def print_tree(node, level=0):
    print(f"{'  ' * level}{node}")
    for child in node.children:
        print_tree(child, level + 1)


def find_leaf_nodes(node):
    leaf_nodes = []
    if not node.children:
        if node.x1 != node.x2 and node.y1 != node.y2:
            leaf_nodes.append(node)
    for child in node.children:
        leaf_nodes.extend(find_leaf_nodes(child))
    return leaf_nodes


def crop_image(image_path, coord1, coord2, output_path):
    with Image.open(image_path) as img:
        left = min(coord1[0], coord2[0])
        upper = min(coord1[1], coord2[1])
        right = max(coord1[0], coord2[0])
        lower = max(coord1[1], coord2[1])
        cropped_img = img.crop((left, upper, right, lower))
        print(f"Coordinates: {coord1}, {coord2}. Cropped image saved to {output_path}")
        cropped_img.save(output_path)


def get_top_colors(image_path, num_colors=2):
    image = Image.open(image_path)
    image = image.convert('RGB')
    pixels = list(image.getdata())
    color_counter = Counter(pixels)
    top_colors = color_counter.most_common(num_colors)
    top_colors_only = [color for color, count in top_colors]
    return top_colors_only


def read_view_tree_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def process_mode(view_tree_lines, image_path, mode_name):
    root = build_tree(view_tree_lines)
    leaf_nodes = find_leaf_nodes(root)
    print(f"\n{mode_name} Leaf Nodes:")
    for node in leaf_nodes:
        print(node)

    node_colors = {}  # 用于记录每个节点的颜色
    for i, node in enumerate(leaf_nodes):
        bounds = node.get_layout_bounds()
        if bounds:
            x1, y1, x2, y2 = map(int, bounds.split())
            output_path = os.path.join("test", f"{mode_name.lower()}_leaf_node_{i}.png")
            crop_image(image_path, (x1, y1), (x2, y2), output_path)
            top_colors = get_top_colors(output_path)
            print(f"Top colors for {output_path}: {top_colors}")
            node_colors[bounds] = {
                "class_name": node.get_class_name(),
                "view_id": node.get_view_id(),
                "layout_bounds": node.get_layout_bounds(),
                "top_colors": top_colors
            }
    return node_colors


def color_distance(c1, c2):
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))


def find_outliers(color_changes, threshold=2):
    changes = np.array(color_changes)
    mean = np.mean(changes)
    std_dev = np.std(changes)
    outliers = []
    for i, change in enumerate(changes):
        if np.abs(change - mean) > threshold * std_dev:
            outliers.append(i)
    return outliers


def compare_modes(day_colors, night_colors):
    print("\nComparison of Day Mode and Night Mode:")
    color_changes = []
    node_info = []

    for bounds, day_info in day_colors.items():
        night_info = night_colors.get(bounds)
        if night_info:
            change = color_distance(day_info['top_colors'][0], night_info['top_colors'][0])
            color_changes.append(change)
            node_info.append((day_info, night_info, change))
            print(f"UI Component: {day_info['class_name']} (id: {day_info['view_id']}, bounds: {day_info['layout_bounds']})")
            print(f"  Day Mode Colors: {day_info['top_colors']}")
            print(f"  Night Mode Colors: {night_info['top_colors']}")
            if day_info['top_colors'] != night_info['top_colors']:
                print(f"  Change Detected: {day_info['top_colors']} -> {night_info['top_colors']}")
        else:
            print(f"UI Component: {day_info['class_name']} (id: {day_info['view_id']}, bounds: {day_info['layout_bounds']}) only found in Day Mode")

    for bounds, night_info in night_colors.items():
        if bounds not in day_colors:
            print(f"UI Component: {night_info['class_name']} (id: {night_info['view_id']}, bounds: {night_info['layout_bounds']}) only found in Night Mode")

    outliers = find_outliers(color_changes)
    print("\nOutlier Color Changes:")
    for index in outliers:
        day_info, night_info, change = node_info[index]
        print(f"UI Component: {day_info['class_name']} (id: {day_info['view_id']}, bounds: {day_info['layout_bounds']})")
        print(f"  Day Mode Colors: {day_info['top_colors']}")
        print(f"  Night Mode Colors: {night_info['top_colors']}")
        print(f"  Change Detected: {day_info['top_colors']} -> {night_info['top_colors']} with distance {change}")


def main():
    os.makedirs("test", exist_ok=True)
    day_view_tree_file = os.path.join("test", "ltr_view_tree.txt")
    night_view_tree_file = os.path.join("test", "night_view_tree.txt")
    day_image_path = os.path.join("test", "ltr_screenshot.png")
    night_image_path = os.path.join("test", "night_screenshot.png")
    day_view_tree_lines = read_view_tree_from_file(day_view_tree_file)
    night_view_tree_lines = read_view_tree_from_file(night_view_tree_file)
    day_node_colors = process_mode(day_view_tree_lines, day_image_path, "Day Mode")
    night_node_colors = process_mode(night_view_tree_lines, night_image_path, "Night Mode")
    compare_modes(day_node_colors, night_node_colors)


if __name__ == "__main__":
    main()