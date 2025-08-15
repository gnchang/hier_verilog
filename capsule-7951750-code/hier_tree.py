"""
File Name: hier_tree.py 

Contents

0. class TreeNode Definition
1. visualize_output_tree function
2. load_tree
3. save_tree
4. traverse_tree

"""
import networkx as nx
import matplotlib.pyplot as plt


class TreeNode:
    def __init__(self, module_spec):
        self.value = module_spec  # JSON-like dictionary stored as value
        self.name = module_spec.get("module_name", "Unnamed Module")  # Extract module_name for easy identification
        self.children = []  # List of child nodes
        self.parent = None  # Reference to parent node
        self.verilog = None
        self.testbench = None

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self  # Set current node as the parent of the child node

    def get_level(self):
        level = 0
        current_node = self.parent
        while current_node:
            level += 1
            current_node = current_node.parent
        return level

    def is_root(self):
        return self.parent is None

    def find_root(self):
        current_node = self
        while current_node.parent:  # Move upward if a parent node exists
            current_node = current_node.parent
        return current_node

    def to_dict(self):
        return {
            "module_spec": self.value,
            "children": [child.to_dict() for child in self.children]
        }

    def get_all_submodules(self):
            submodules = set()
            
            def traverse(node):
                for child in node.children:
                    submodules.add(child.name)  # Store module_name
                    traverse(child)

            traverse(self)
            return submodules


    def print_tree(self, level=0, output=None):
        if output is None:
            output = []

        indent = " " * (level * 4)  # Indentation of 4 spaces
        function_description = self.value.get('function_description')
        output.append(f"{indent}- {self.name}: {function_description}") 

        for child in self.children:
            child.print_tree(level + 1, output)

        return "\n".join(output)

    def __repr__(self):
        return f"TreeNode({self.name})"


def visualize_output_tree(root_node):

    graph = nx.DiGraph()  

    def add_edges(node, parent_name=None):
       
        node_name = f"{node.name}_{id(node)}"  
        graph.add_node(node_name, label=node.name)  

        if parent_name:
            graph.add_edge(parent_name, node_name)

        for child in node.children:
            add_edges(child, node_name)

    add_edges(root_node)

    pos = nx.spring_layout(graph, seed=42)

    def custom_layout(graph, root):
        pos = {}
        levels = {}  
        queue = [(root, 0)]  
        while queue:
            current, level = queue.pop(0)
            if current not in levels:
                levels[current] = level
                for neighbor in graph.successors(current):
                    queue.append((neighbor, level + 1))
        
        max_level = max(levels.values())
        x_pos = {}
        for node, level in levels.items():
            if level not in x_pos:
                x_pos[level] = 0
            pos[node] = (x_pos[level], -level)
            x_pos[level] += 1  

        return pos

    root_name = f"{root_node.name}_{id(root_node)}"
    pos = custom_layout(graph, root_name)

    plt.figure(figsize=(12, 8))
    labels = nx.get_node_attributes(graph, 'label')  # Display labels on nodes
    nx.draw(graph, pos, labels=labels, with_labels=True,
            node_size=3000, node_color="lightblue",
            font_size=10, font_weight="bold", arrowsize=15)
    plt.title("Tree Visualization")
    plt.show()


import os, pickle

def load_tree(save_dir, file_name, version=None):

    if (version):
        file_name = f"{tree.value['module_name']}_ver{version}.pkl"
        file_path = os.path.join(save_dir, file_name)
    else:    
        file_name = f"{file_name}.pkl"
        file_path = os.path.join(save_dir, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No tree found with module_name '{file_name}' in {save_dir}")

    # pickle로 불러오기
    with open(file_path, 'rb') as f:
        tree = pickle.load(f)

    print(f"Tree loaded from: {file_path}")
    return tree

import os, pickle

def save_tree(tree, save_dir, version=None):
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok = True)

    if (version):
        file_name = f"{tree.value['module_name']}_ver{version}.pkl"
        file_path = os.path.join(save_dir, file_name)
    else:
        file_name = f"{tree.value['module_name']}.pkl"
        file_path = os.path.join(save_dir, file_name)        


    with open(file_path, 'wb') as f:
        pickle.dump(tree, f)

    print(f"Tree saved to: {file_path}")


def traverse_tree(node, depth=0):
    """TreeNode를 순회하며 module 정보를 출력하는 함수"""
    indent = "          " * depth  # 들여쓰기 설정

    # 각 필드가 존재하는지 확인하고 출력
    module_name = node.value.get("module_name", "없음")
    module_header = node.value.get("module_header", "없음")
    function_description = node.value.get("function_description", "없음")

    print(f"{indent} [{module_name}]")
    print(f"{indent}  - module_name: {module_name}")
    print(f"{indent}  - module_header: {module_header}")
    print(f"{indent}  - function_description: {function_description}")

    # 자식 노드 순회
    for child in node.children:
        traverse_tree(child, depth + 1)