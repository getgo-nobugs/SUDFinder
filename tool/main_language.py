import os
import re
from PIL import Image
import cv_utils
import glob


class Node:
    def __init__(self, line):
        self.parse_line(line)
        self.children = []

    def parse_line(self, line):
        match = re.match(r'(!*)([^{]+){([^}]+)}', line)
        if match:
            self.indent = len(match.group(1))
            self.className = match.group(2).strip()
            details = match.group(3).split(' ')
            self.view_id = None
            self.layout_bounds = None
            for detail in details:
                if detail.startswith("app:id/") or detail.startswith("android:id"):
                    self.view_id = detail
                elif len(detail) == 7:
                    self.view_id = detail
            match_final_numbers = re.findall(r'\d+', line)
            if len(match_final_numbers) >= 4:
                self.layout_bounds = ' '.join(match_final_numbers[-4:])
                self.x1 = int(self.layout_bounds.split(' ')[0])
                self.y1 = int(self.layout_bounds.split(' ')[1])
                self.x2 = int(self.layout_bounds.split(' ')[2])
                self.y2 = int(self.layout_bounds.split(' ')[3])
            else:
                pass
        else:
            pass


    def __repr__(self):
        return f"Node(className={self.className}, view_id={self.view_id}, layout_bounds={self.layout_bounds})"

    def get_class_name(self):
        return self.className

    def get_view_id(self):
        return self.view_id

    def get_layout_bounds(self):
        return self.layout_bounds

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.view_id == other.view_id
        return False

    def __hash__(self):
        return hash(self.view_id)


def build_tree(lines):
    if not lines:
        return None

    def compute_indent(line):
        return line.count('!')

    root_line = lines[0]
    root = Node(root_line)
    stack = [root]

    for line in lines[1:]:
        node = Node(line)
        while len(stack) > 1 and stack[-1].indent >= node.indent:
            stack.pop()
        if stack[-1].indent < node.indent:
            stack[-1].children.append(node)
            stack.append(node)
        else:
            raise ValueError("Invalid tree structure: indentation error.")

    return root


def print_tree(node, level=0):
    print('  ' * level + repr(node))
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


def crop_image(image_path, coord1, coord2, output_path, node):
    with Image.open(image_path) as img:
        left = min(coord1[0], coord2[0])
        upper = min(coord1[1], coord2[1])
        right = max(coord1[0], coord2[0])
        lower = max(coord1[1], coord2[1])
        cropped_img = img.crop((left, upper, right, lower))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cropped_img.save(output_path)
        node.imagePath = output_path


def read_view_tree_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


def group_views(leaf_nodes, image_path):
    alignment_groups = {'left': [], 'right': [], 'center': [], 'justify': []}
    vertical_groups_left = {}
    vertical_groups_right = {}
    vertical_groups_center = {}

    for node in leaf_nodes:
        alignment = cv_utils.detect_text_alignment(node.imagePath)  # 传入必要的参数
        # 先判断居中对齐
        if alignment == 'center':
            alignment_groups['center'].append(node)
        # 然后判断右对齐
        elif alignment == 'right':
            alignment_groups['right'].append(node)
        # 默认是左对齐
        elif alignment == 'left':
            alignment_groups['left'].append(node)
        elif alignment == 'justify':
            alignment_groups['justify'].append(node)

        # 计算中心点
        x_center = (node.x1 + node.x2) // 2

        # 垂直分组，按左边界 x1
        if node.x1 not in vertical_groups_left:
            vertical_groups_left[node.x1] = []
        vertical_groups_left[node.x1].append(node)

        # 垂直分组，按右边界 x2
        if node.x2 not in vertical_groups_right:
            vertical_groups_right[node.x2] = []
        vertical_groups_right[node.x2].append(node)

        # 垂直分组，按中点 x_center
        if x_center not in vertical_groups_center:
            vertical_groups_center[x_center] = []
        vertical_groups_center[x_center].append(node)

    return alignment_groups, vertical_groups_left, vertical_groups_right, vertical_groups_center

def process_mode(view_tree_lines, image_path, mode_name):
    root = build_tree(view_tree_lines)
    leaf_nodes = find_leaf_nodes(root)

    for i, node in enumerate(leaf_nodes):
        bounds = node.get_layout_bounds()
        if bounds:
            x1, y1, x2, y2 = map(int, bounds.split())
            bounds_str = f"{x1}{y1}{x2}{y2}"
            output_path = os.path.join("test", f"{mode_name.lower()}leaf_node{i}_{bounds_str}.png")
            crop_image(image_path, (x1, y1), (x2, y2), output_path, node)

    alignment_groups, vertical_groups_left, vertical_groups_right, vertical_groups_center = group_views(
        leaf_nodes, image_path
    )

    def groups_are_equal(group1, group2):
        """Helper function to check if two groups contain the same elements."""
        return set(group1) == set(group2)

    # Filter vertical_groups_center to retain only 'center' and 'justify' alignments
    vertical_groups_center = {
        key: [node for node in nodes if (node in alignment_groups['center'] or node in alignment_groups['justify'])]
        for key, nodes in vertical_groups_center.items()
    }

    # Collect all nodes in vertical_groups_center to exclude from other groups
    center_nodes = {node for nodes in vertical_groups_center.values() for node in nodes}

    # Filter vertical_groups_left to retain only 'left' and 'justify' alignments and exclude center nodes
    vertical_groups_left = {
        key: [node for node in nodes if (node in alignment_groups['left'] or node in alignment_groups['justify']) and node not in center_nodes]
        for key, nodes in vertical_groups_left.items()
    }

    # Filter vertical_groups_right to retain only 'right' and 'justify' alignments and exclude center nodes
    vertical_groups_right = {
        key: [node for node in nodes if (node in alignment_groups['right'] or node in alignment_groups['justify']) and node not in center_nodes]
        for key, nodes in vertical_groups_right.items()
    }

    # Remove groups with size 0
    vertical_groups_left = {key: nodes for key, nodes in vertical_groups_left.items() if nodes}
    vertical_groups_right = {key: nodes for key, nodes in vertical_groups_right.items() if nodes}
    vertical_groups_center = {key: nodes for key, nodes in vertical_groups_center.items() if nodes}

    # print("\nVertical Groups Left:")
    # for key, nodes in vertical_groups_left.items():
    #     print(f"Group {key}:")
    #     for node in nodes:
    #         print(node)
    #
    # print("\nVertical Groups Right:")
    # for key, nodes in vertical_groups_right.items():
    #     print(f"Group {key}:")
    #     for node in nodes:
    #         print(node)
    #
    # print("\nVertical Groups Center:")
    # for key, nodes in vertical_groups_center.items():
    #     print(f"Group {key}:")
    #     for node in nodes:
    #         print(node)

    return leaf_nodes, alignment_groups, vertical_groups_left, vertical_groups_right, vertical_groups_center


def compare_groups(ltr_vertical_groups_left, rtl_vertical_groups_left, ltr_vertical_groups_right,
                   rtl_vertical_groups_right, ltr_vertical_groups_center, rtl_vertical_groups_center,
                   ltr_filename, rtl_filename):
    def collect_items(group_dict):
        items = []
        for key, nodes in group_dict.items():
            items.append(set(nodes))
        return items

    # Collect items from each group
    ltr_left_items = collect_items(ltr_vertical_groups_left)
    rtl_left_items = collect_items(rtl_vertical_groups_left)
    ltr_right_items = collect_items(ltr_vertical_groups_right)
    rtl_right_items = collect_items(rtl_vertical_groups_right)
    ltr_center_items = collect_items(ltr_vertical_groups_center)
    rtl_center_items = collect_items(rtl_vertical_groups_center)

    # Initialize a list to collect bug reports
    bug_reports = []

    # Check for bug: if any item in ltr_left_items is found in rtl_right_items or rtl_center_items
    for ltr_group in ltr_left_items:
        for item in ltr_group:
            if any(item in rtl_group for rtl_group in rtl_right_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR left group found in RTL right group.)"
                print(bug_message)
                bug_reports.append(bug_message)
            if any(item in rtl_group for rtl_group in rtl_center_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR left group found in RTL center group. "
                print(bug_message)
                bug_reports.append(bug_message)

    # Check for bug: if any item in ltr_right_items is found in rtl_left_items or rtl_center_items
    for ltr_group in ltr_right_items:
        for item in ltr_group:
            if any(item in rtl_group for rtl_group in rtl_left_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR right group found in RTL left group. (LTR: {ltr_filename}, RTL: {rtl_filename})"
                print(bug_message)
                bug_reports.append(bug_message)
            if any(item in rtl_group for rtl_group in rtl_center_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR right group found in RTL center group. (LTR: {ltr_filename}, RTL: {rtl_filename})"
                print(bug_message)
                bug_reports.append(bug_message)

    # Check for bug: if any item in ltr_center_items is found in rtl_left_items or rtl_right_items
    for ltr_group in ltr_center_items:
        for item in ltr_group:
            if any(item in rtl_group for rtl_group in rtl_left_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR center group found in RTL left group. (LTR: {ltr_filename}, RTL: {rtl_filename})"
                print(bug_message)
                bug_reports.append(bug_message)
            if any(item in rtl_group for rtl_group in rtl_right_items):
                bug_message = f"Bug detected: {ltr_filename.split('/')[-1]} Item '{item}' from LTR center group found in RTL right group. (LTR: {ltr_filename}, RTL: {rtl_filename})"
                print(bug_message)
                bug_reports.append(bug_message)

    if not bug_reports:
        print("No bugs detected.")
        bug_reports.append("No bugs detected.")

    # Save bug reports to a text file
    with open("bug_reports.txt", "w") as file:
        for report in bug_reports:
            file.write(report + "\n")


def main(prefix_ltr='1_', prefix_rtl='2.5_'):
    base_dir = '/Users/huanghuaxun/PycharmProjects/setdiff/v2/apk_utils/generated_data'
    os.makedirs("test", exist_ok=True)

    ltr_view_tree_files = sorted(glob.glob(os.path.join(base_dir, f'{prefix_ltr}*_view_tree.txt')))

    for ltr_view_tree_file in ltr_view_tree_files:
        common_part = ltr_view_tree_file.split(f'{prefix_ltr}')[1].split('_view_tree.txt')[0]

        rtl_view_tree_file = os.path.join(base_dir, f'{prefix_rtl}{common_part}_view_tree.txt')
        ltr_image_path = os.path.join(base_dir, f'{prefix_ltr}{common_part}_screenshot.png')
        rtl_image_path = os.path.join(base_dir, f'{prefix_rtl}{common_part}_screenshot.png')

        if os.path.exists(rtl_view_tree_file) and os.path.exists(ltr_image_path) and os.path.exists(rtl_image_path):
            ltr_view_tree_lines = read_view_tree_from_file(ltr_view_tree_file)
            rtl_view_tree_lines = read_view_tree_from_file(rtl_view_tree_file)

            ltr_leaf_nodes, ltr_alignment_groups, ltr_vertical_groups_left, ltr_vertical_groups_right, ltr_vertical_groups_center = process_mode(
                ltr_view_tree_lines, ltr_image_path, "LTR Mode")
            rtl_leaf_nodes, rtl_alignment_groups, rtl_vertical_groups_left, rtl_vertical_groups_right, rtl_vertical_groups_center = process_mode(
                rtl_view_tree_lines, rtl_image_path, "RTL Mode")

            compare_groups(
                ltr_vertical_groups_left, rtl_vertical_groups_left,
                ltr_vertical_groups_right, rtl_vertical_groups_right,
                ltr_vertical_groups_center, rtl_vertical_groups_center,
                ltr_view_tree_file, rtl_view_tree_file
            )

if __name__ == "__main__":
    main()