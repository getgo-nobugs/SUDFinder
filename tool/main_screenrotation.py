import re
import os
from math import sqrt


class Node:
    def __init__(self, line, indent):
        self.parse_line(line)
        self.children = []
        self.indent = indent

    def parse_line(self, line):
        # 匹配并解析行
        match = re.match(r'(!*)([^{]+){([^}]+)}', line)
        self.indent = len(match.group(1))
        self.className = match.group(2).strip()
        details = match.group(3).split(' ')
        # 解析 view id 和 layout bounds
        self.view_id = None
        self.layout_bounds = None
        for detail in details:
            if len(detail) == 7:
                self.view_id = detail
        # 提取最后四个数字作为 layout_bounds
        match_final_numbers = re.findall(r'\d+', line)
        if len(match_final_numbers) >= 4:
            self.layout_bounds = ' '.join(match_final_numbers[-4:])
            self.x1 = int(self.layout_bounds.split(' ')[0])
            self.y1 = int(self.layout_bounds.split(' ')[1])
            self.x2 = int(self.layout_bounds.split(' ')[2])
            self.y2 = int(self.layout_bounds.split(' ')[3])

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


def read_view_tree_from_file(file_path):
    """
    Read the view tree lines from a file.

    :param file_path: Path to the file containing the view tree lines.
    :return: List of view tree lines.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def distance(node1, node2):
    """
    Calculate the Euclidean distance between two nodes based on their bounds.
    """
    center_x1 = (node1.x1 + node1.x2) / 2
    center_y1 = (node1.y1 + node1.y2) / 2
    center_x2 = (node2.x1 + node2.x2) / 2
    center_y2 = (node2.y1 + node2.y2) / 2
    return sqrt((center_x1 - center_x2) ** 2 + (center_y1 - center_y2) ** 2)


def find_close_nodes(base_nodes, all_nodes, threshold):
    """
    Find nodes that are close to the base nodes within a given threshold.
    """
    close_nodes = set(base_nodes)
    for base_node in base_nodes:
        for node in all_nodes:
            if node not in close_nodes and distance(base_node, node) <= threshold:
                close_nodes.add(node)
    return list(close_nodes)


def process_mode(view_tree_lines, mode_name, screen_width):
    # 构建视图树
    root = build_tree(view_tree_lines)

    # 查找所有的叶节点
    leaf_nodes = find_leaf_nodes(root)
    print(f"\n{mode_name} Leaf Nodes:")
    for node in leaf_nodes:
        print(node)

    # 定义一个靠近边缘的距离阈值
    edge_threshold = 200
    close_threshold = 100  # 定义非常接近的距离阈值

    # 查找靠近左边缘和右边缘的叶节点
    left_edge_nodes = [node for node in leaf_nodes if node.x1 <= edge_threshold]
    right_edge_nodes = [node for node in leaf_nodes if node.x2 >= screen_width - edge_threshold]

    # 找到与这些节点非常接近的结点
    left_edge_and_close_nodes = find_close_nodes(left_edge_nodes, leaf_nodes, close_threshold)
    right_edge_and_close_nodes = find_close_nodes(right_edge_nodes, leaf_nodes, close_threshold)

    print(f"\n{mode_name} Left Edge and Close Nodes (within {close_threshold} pixels):")
    for node in left_edge_and_close_nodes:
        print(node)

    print(f"\n{mode_name} Right Edge and Close Nodes (within {close_threshold} pixels):")
    for node in right_edge_and_close_nodes:
        print(node)

    return left_edge_and_close_nodes, right_edge_and_close_nodes


def compare_nodes(before_nodes, after_nodes, edge):
    before_ids = {node.get_view_id() for node in before_nodes}
    after_ids = {node.get_view_id() for node in after_nodes}

    still_on_edge = before_ids.intersection(after_ids)
    moved_off_edge = before_ids.difference(after_ids)

    print(f"\nNodes still on {edge} edge after rotation:")
    for view_id in still_on_edge:
        print(view_id)

    print(f"\nNodes moved off the {edge} edge after rotation:")
    for view_id in moved_off_edge:
        print(view_id)


def main():
    # 确保test文件夹存在
    os.makedirs("test", exist_ok=True)

    # 白天模式视图树文件路径
    day_view_tree_file = os.path.join("test", "day_view_tree.txt")
    rotated_view_tree_file = os.path.join("test", "night_view_tree.txt")

    # 从文件中读取白天模式视图树
    day_view_tree_lines = read_view_tree_from_file(day_view_tree_file)
    rotated_view_tree_lines = read_view_tree_from_file(rotated_view_tree_file)

    # 处理普通模式
    screen_width = 1080  # 假设屏幕宽度为1080像素
    day_left_nodes, day_right_nodes = process_mode(day_view_tree_lines, "Default", screen_width)
    rotated_left_nodes, rotated_right_nodes = process_mode(rotated_view_tree_lines, "Rotated", screen_width)

    # 比较旋转前后的节点位置
    compare_nodes(day_left_nodes, rotated_left_nodes, "left")
    compare_nodes(day_right_nodes, rotated_right_nodes, "right")


if __name__ == '__main__':
    main()