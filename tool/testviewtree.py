class Node:
    def __init__(self, value, indent):
        self.value = value
        self.children = []
        self.indent = indent

def build_tree(lines):
    if not lines:
        return None

    def compute_indent(line):
        return line.count('-')

    root_line = lines[0]
    root_indent = compute_indent(root_line)
    root_value = root_line.replace('-', '').strip()
    root = Node(root_value, root_indent)
    stack = [root]

    for line in lines[1:]:
        indent = compute_indent(line)
        value = line.replace('-', '').strip()
        node = Node(value, indent)
        while len(stack) > 1 and stack[-1].indent >= node.indent:
            stack.pop()
        if stack[-1].indent < node.indent:
            stack[-1].children.append(node)
            stack.append(node)
        else:
            raise ValueError("Invalid tree structure: indentation error.")

    return root

# 示例调用
lines = [
    "root",
    "- child1",
    "-- grandchild1",
    "-- grandchild2",
    "- child2",
    "-- grandchild3"
]

root = build_tree(lines)

# 简单的打印树结构函数
def print_tree(node, level=0):
    print("*" * level + node.value)
    for child in node.children:
        print_tree(child, level + 1)

print_tree(root)