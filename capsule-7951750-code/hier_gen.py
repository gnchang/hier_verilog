"""

1. Ftn_Refine_API_call
2. Ftn_Integrate_API_call
3. Sub_List_API_call
4. Hier_API_call
5. Sub_Hier_JSON_API_call
6. find_node_by_name
7. add_sub_to_tree

8. Sub_Header_Check_API_call
9. update_sub_in_tree
10. Sub_Ftn_Check_API_call
11. update_sub_ftn_in_tree

12. sub_hier_loop
13. Hier_Gen_Loop

** Functions for ablation study: single-pass hierarchy generation **
14. API_call_base
15. add_sub_to_tree_base

"""

import json, re, time
from hier_tree import *
from prompts import *
from API_key import client


chat_history = []

def print_chat_history():
    print("\n=== Conversation with the LLM ===")
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "GPT"
        print(f"{role}: {msg['content']}\n")

########### 1.0 Function refinement ###########

def Ftn_Refine_API_call(top_module :TreeNode):
        user_message = FR_Q_prompt_gen(top_module)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
            temperature = 0.5,
            top_p = 0.9
        )
        
    
        text = response.choices[0].message.content.strip()

        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})

    
        return text


def Ftn_Integrate_API_call(top_module: TreeNode, previous_output, user_selected_options):
        user_message = FR_prompt_gen(top_module, previous_output, user_selected_options)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
            temperature = 0.5,
            top_p = 0.9
        )
        
        text = response.choices[0].message.content.strip()

        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})
        
        return text

########### 2.0 Submodule list generation ###########

def Sub_List_API_call(module: TreeNode):
        user_message = sub_list_gen(module)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
            temperature = 0.5,
            top_p=0.9
        )
        
        text = response.choices[0].message.content.strip()
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})
        
        return text

def Hier_API_call(module: TreeNode, sub_list):
        user_message = hier_gen(module, sub_list)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
            temperature = 0.5,
            top_p=0.9
        )
        
        text = response.choices[0].message.content.strip()
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})

        text = response.choices[0].message.content
        
        return text

########### 3.0 Sub-hierarchy generation in JSON format ###########

def Sub_Hier_JSON_API_call(module: TreeNode, sub_list):
        user_message = sub_hier_json_gen(module, sub_list)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
            temperature = 0.5,
            top_p=0.9
        )
        
        text = response.choices[0].message.content.strip()
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})

        text = response.choices[0].message.content
        print (text)
        pattern = r'```json(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            json_text = matches[0].strip()  
            json_output = json.loads(json_text)
            #print(json.dumps(decomposer_output, indent =4))
        else:
            #print("No JSON found.")
            json_output = json.loads(text)
            #print(json.dumps(decomposer_output, indent =4))
        return json_output

def find_node_by_name(root, target_name):
    
    stack = [root]

    while stack:
        current_node = stack.pop()

        if current_node.name == target_name:
            return current_node

        for child in current_node.children:
            stack.append(child)

    return None

def add_sub_to_tree(module_spec: TreeNode, JSON_output, root: TreeNode):
    existing_children = {child.name for child in module_spec.children}
    
    for submodule in JSON_output:
        child_name = submodule.get("module_name")  # Assuming "module_name" identifies a unique submodule
        if child_name in existing_children:
            print(f"Child node '{child_name}' already exists in parent '{module_spec.name}'. Skipping...")
            continue
        
        existing_node = find_node_by_name(root, child_name)
        if existing_node:
            submodule["module_header"] = existing_node.value["module_header"]
            
        # Add new child node
        child_node = TreeNode(submodule)
        module_spec.add_child(child_node)
        print(f"Added child node '{child_node.name}' to parent '{module_spec.name}'.")


########### 3.1 Sub-hierarchy refinement: module header ###########

def Sub_Header_Check_API_call(module: TreeNode):
        user_message = sub_header_check(module)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
        )
        
        text = response.choices[0].message.content.strip()
        print(text)
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})


        pattern = r'```json(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            json_text = matches[0].strip()
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                print("Invalid JSON format")
                return None
            
        else:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print("No valid JSON found.")
                return None  # If JSON is not found, return None

def update_sub_in_tree (module: TreeNode, modified_json):
    for child in module.children:
        child_name = child.value.get("module_name")
        if child_name and child_name in modified_json:
            child.value["module_header"] = modified_json[child_name][0]
            child.value["function_description"] = modified_json[child_name][1]


########### 3.2 Sub-hierarchy refinement: function description ###########

def Sub_Ftn_Check_API_call(module: TreeNode):
        user_message = sub_ftn_check(module)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o",
        )
        
        text = response.choices[0].message.content.strip()
        print(text)
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})


        pattern = r'```json(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            json_text = matches[0].strip()
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                print("Invalid JSON format")
                return None
            
        else:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print("No valid JSON found.")
                return None  # If JSON is not found, return None

def update_sub_ftn_in_tree (module: TreeNode, modified_json):
    for child in module.children:
        child_name = child.value.get("module_name")
        if child_name and child_name in modified_json:
            child.value["function_description"] = modified_json[child_name]

########### 3.0-3.2 Sub-hierarchy generation loop ###########

def sub_hier_loop(module :TreeNode, hierarchy_output, root: TreeNode, visited_nodes=None):
    if visited_nodes is None:
        visited_nodes = set()

    module_name = module.value["module_name"]
    module.value["module_name"] = module_name.replace(" ", "_")
    print(f"[{module_name}] Sub-hierarchy generation started.")
    
    #1. Generate submodule header, function description in JSON format
    print(f"[{module_name}] Generate submodule header and function description.")
    json_output = Sub_Hier_JSON_API_call(module, hierarchy_output)
    add_sub_to_tree(module, json_output, root) 
    

    if len(module.children) > 0:
        #2. Check sub-module header
        print(f"[{module_name}] Check submodule header.")
        modified_json = Sub_Header_Check_API_call(module)
    
        if (modified_json is None):
            print("Modification is skipped")
        else:
            print(f"This is modified JSON: {modified_json}")
            new_head_data = {key.replace(" ", "_"): value for key, value in modified_json.items()}
            update_sub_in_tree(module, new_head_data)

        #3. Check sub-module function description
        print(f"[{module_name}] Check submodule function description.")
        modified_json = Sub_Header_Check_API_call(module)
    
        if (modified_json is None):
            print("Modification is skipped")
        else:
            print(f"This is modified JSON: {modified_json}")
            new_ftn_data = {key.replace(" ", "_"): value for key, value in modified_json.items()}
            update_sub_ftn_in_tree(module, new_ftn_data)            

    # Recursively expand for child nodes
    for child in module.children:
        sub_hier_loop(child, hierarchy_output, root, visited_nodes)


########### 1.0-3.2 RTL hierarchy generation loop ###########

def Hier_Gen_Loop(top_module: TreeNode):

    #1. Function refinement
    text = Ftn_Refine_API_call(top_module)
    print(text)
    time.sleep(3)
    user_input = input("Please select the options: ")
    print(f"Selected options: {user_input}")
    refined_function_description = Ftn_Integrate_API_call(top_module, text, user_input)
    top_module.value["function_description"] = refined_function_description

    #2.0 Submodule list generation
    sub_list = Sub_List_API_call(top_module)
    print(sub_list)

    #2.1 Hierarchy outline generation
    hierarchy_output = Hier_API_call(top_module, sub_list)
    print(hierarchy_output)

    #2.2 Loop: sub-hierarchy generation and refinement
    sub_hier_loop(top_module, hierarchy_output, top_module)


########### Code for Ablation study ###########

def API_call_base(module: TreeNode):
        module_name = module.value["module_name"]
        module_header = module.value["module_header"]
        function_description = module.value["function_description"]

        user_message = f"""
top_module = {{
                "module_name": "{module_name}",
                "module_header": "{module_header}",
                "function_description": "{function_description}"
              }}

Please define all necessary submodules in top_module.
The output must follow the following format to represent the hierarchical structure of the design
You should only output the json hierarchy:

{{
  "module_name": "top_module",
  "module_header": "module top_module (...);",
  "function_description": "Top-level module",
  "submodule": [
    {{
      "module_name": "mid_module",
      "module_header": "module mid_module (...);",
      "function_description": "Intermediate module",
      "submodule": [
      ]
    }}
  ]
}}

"""

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="gpt-4o"
        )
        
        text = response.choices[0].message.content.strip()

        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": text})

        text = response.choices[0].message.content
        print (text)
        pattern = r'```json(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            json_text = matches[0].strip()  
            json_output = json.loads(json_text)
            print(json.dumps(json_output, indent =4))
        else:
            print("No JSON found.")
            json_output = json.loads(text)
            #print(json.dumps(decomposer_output, indent =4))
        return json_output
        

def add_sub_to_tree_base(module_spec: TreeNode, JSON_output, root: TreeNode):
    existing_children = {child.name for child in module_spec.children}
    
    for submodule in JSON_output.get("submodule", []):
        child_name = submodule.get("module_name")  # Assuming "module_name" identifies a unique submodule
        if child_name in existing_children:
            print(f"Child node '{child_name}' already exists in parent '{module_spec.name}'. Skipping...")
            continue
        
        existing_node = find_node_by_name(root, child_name)
        if existing_node:
            submodule["module_header"] = existing_node.value["module_header"]
            
        # Add new child node
        child_node = TreeNode(submodule)
        module_spec.add_child(child_node)
        print(f"Added child node '{child_node.name}' to parent '{module_spec.name}'.")

        add_sub_to_tree_base(child_node, submodule, root)


