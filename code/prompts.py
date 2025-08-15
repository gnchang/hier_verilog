"""

File Name: prompts_hier_250209.py 
Date Created: Mar. 12, 2025

Contents
0. class TreeNode Definition

1. Spec_Prompt: prompt for SpecOption_Prompt_Gen

2.1 Hier_Prompt_root: prompt for Hier_Prompt_Gen (Root module) 
2.2 Hier_Prompt_sub: prompt for Hier_Prompt_Gen (submodule)

3. Json_Prompt_Gen

3.1 Verilog code generation

"""

from hier_tree import * 


# 1 Function refinement

# 1.1 Question generation

def FR_Q_prompt_gen(module: TreeNode):
            
    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]

    FR_Q_prompt= f"""
Describe missing details in the "top-module function description", taking the following considerations into account.
And provide potential options to compensate for each missing detail with labels.

Considerations:
    - Are all input and output ports properly described?
    - Are the roles of control signals clearly explained?
    - Is the timing of each operation clear?
    

Top-module description:
Module name: "{module_name}",
Module header: "{module_header}",
Function description: "{function_description}"
    """
    return FR_Q_prompt


# 1.2 Function description refinement

def FR_prompt_gen(module: TreeNode, previous_output, user_selected_options):
    function_description = module.value["function_description"]

    FR_prompt= f"""
Refine the original function description by integrating the user-selected design options.
Only incorporate the selected options and ignore any questions without user input.
Ensure the refined function description is coherent and concise, aligning with the provided selections.
Output only the refined function description without any headers or labels.

Design options:
{previous_output}

User-selected options:
{user_selected_options}

Original module description:
{function_description}
    """
    return FR_prompt


# 2. RTL Hierarchy Generation

# 2-0. Sub-module list generation

def sub_list_gen(module: TreeNode): 
    
    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]

    sub_list_prompt = f"""
Top-module description:
    Module name: "{module_name}",
    Module header: "{module_header}",
    Function description: "{function_description}"
    
Produce a list of sub-modules with their function descriptions to design {module_name}.
Each sub-module must follow this format:
```json
{{ 
    "module_name": "<module name>", 
    "function_description": "<function description>"  

}}
```

- If multiple submodules logically belong to a higher-level sub-module, create a higher-level submodule to encapsulate them, while also listing all its submodules independently.
- Make sure to assign distinct names to submodules that perform different functions.
"""

    return sub_list_prompt

# 2-1. Hierarchy outline generation

def hier_gen(module: TreeNode, previous_response):
    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]

    hier_prompt = f"""
Top-module description:
    Module name: "{module_name}",
    Module header: "{module_header}",
    Function description: "{function_description}"
    
Submodule list:
########
{previous_response}
########

Top-module description and a list of sub-modules are provided.
From the sub-module list, generate the function description and module header of "immediate submodules" for each module.
Immediate submodules are the submodules (child) that are directly instantiated by the module (parent).
If some submodules are omitted in the list, you can add additinal immediate submodules.
Do not include any deepper-level submodules of each module.

Output format for "each module":
<Module Name>
    - **immediate submodule list**:
        - <Submodule Name> x #instance
        - <Submodule Name> x #instance
        - ...
    - **Brief Description of Data Flow**:
        - Explain how data moves between submodules or between the module and its submodules.
        - Highlight any key dependencies or interactions.

"""
    return hier_prompt

# 2-2. Sub-hierarchy generation in JSON Format

def sub_hier_json_gen(module: TreeNode, hierarchy_output):
    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]


    sub_hier_json_prompt = f"""
Hierarchy:
########
{hierarchy_output}
########

Description of parent module:
########
    Module name: "{module_name}",
    Module header: "{module_header}",
    Function description: "{function_description}"
########    

From the given hierarchy, please generate the function description and module header of submodule which is directly instantiated by {module_name}.
Even if the hierarchy says that there are no immediate submodules of {module_name}, you can add them if you decide that you need additional submodules.
For each submodule, provide a JSON object containing module_name, module_header, function_description and #instance.

The final output must be a single valid JSON array containing all submodule objects.
Do not output anything else other than JSON array.
If the {module_name} has no submodules, output an empty list.
Ensure the output is structured as follows:
```json
[
    {{
        "module_name": "<module_name>",
        "module_header": "<module_header>",
        "function_description": "<function_description>", 
    }},
    ...
]
```
"""
    return sub_hier_json_prompt


# 2-3. Sub-hierarchy refinement: header checker


def get_tree_info(node, depth=0):
    """Function that traverses the TreeNode and converts module information into a string"""
    indent = "              " * depth  
    module_name = node.value.get("module_name", "None")
    module_header = node.value.get("module_header", "None")
    function_description = node.value.get("function_description", "None")

    info = f"{indent}[{module_name}]\n"
    info += f"{indent}  - module_name: {module_name}\n"
    info += f"{indent}  - module_header: {module_header}\n"
    info += f"{indent}  - function_description: {function_description}\n\n"

    for child in node.children:
        info += get_tree_info(child, depth + 1)

    return info

def sub_header_check(module: TreeNode):

    module_name = module.value["module_name"]
    module_header = module.value["module_header"]

    tree_info = get_tree_info(module)

    header_checker_prompt = f"""

######################
{tree_info}  
######################

You are given the {module_name} module, which consists of multiple submodules.
For each submodule:
1. Verify the Verilog header and explain the verification results:
 - Ensure that all required ports are properly defined, while taking account the {module_name}'s header.
 - Check that each port's bit width is correct.
 - Confirm that Verilog syntax is correct.

2. If modifications are needed, provide the corrected header in the following JSON format:
    key: submodule name
    value: an array containing two strings; (1) modified module header (2) modified function description 
        ```json
        {{
            "module_name": [
                "<modified module header>",
                "<modified function description>"
            ],
            ...
        }}
        ```
"""
    return header_checker_prompt
    

# 2-4. Sub-hierarchy refinement: function description checker

def sub_ftn_check(module: TreeNode): 

    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]

    tree_info = get_tree_info(module)

    ftn_checker_prompt = f"""

######################
{tree_info}  
######################

You are given the {module_name} module, which consists of multiple submodules.
Identify the missing details in the function description for each module,
and refine them while the following considerations are taken into account.

Considerations:
    - Are all input and output ports properly described?
    - Are the roles of control signals clearly explained?
    - Is the timing of each operation clear?
    
Provide the updated function description in the following JSON format:
    key: submodule name
    value: modified function description 
        ```json
        {{
            "submodule_name": "<modified function description>",
            ...
        }}
        ```
"""
    return ftn_checker_prompt



# 3.1 Verilog code generation
import os, re
def verilog_gen(module: TreeNode, test_scenario_path, numbered_verilog_code=None, previous_verilog_errors=None):
    module_name = module.value["module_name"]
    module_header = module.value["module_header"]
    function_description = module.value["function_description"]
    
    children = module.children
    has_children = bool(children)

    # Load sub-modules
    if has_children:
        submodules = []

        for child in module.children:
            #child_name = child.value["module_name"]
            child_header = child.value["module_header"]
            child_function = child.value["function_description"]
            formatted_submodule = f"""
            - Submodule header:
            {child_header}
            - Function_description: {child_function}
            """
            
            submodules.append(formatted_submodule)
        
        submodules_str = "\n".join(submodules)

    # Load test scenarios
    if test_scenario_path and os.path.exists(test_scenario_path): 
        with open(test_scenario_path, "r", encoding="utf-8") as file:
            test_scenario = file.read()

        vectors = re.findall(r"vector: (\{.*?\})", test_scenario)
        test_scenario = "\n".join(vectors)

    else:
        test_scenario = "No test scenario provided."


    ## 1. Prompt to generate Verilog code
    if (numbered_verilog_code == None):
            if has_children: 
                # 1-1. module which has any sub-module
                verilog_prompt = f"""
Please generate Verilog code for the follwoing {module_name}.
Write the complete Verilog code M according to the given module header, while the module signals and submodule instantiation lines are taken into account.
- Do not omit any Verilog code
- Write Verilog code without using any SystemVerilog features.
- Strictly follow the signal names and port names exactly as provided.
- Do not include anything else: only output Verilog code for **one** module.

** Below is information about {module_name}:
- Module header:
{module_header}
- Function description: {function_description}

** Submodule list:
{submodules_str}

** The Verilog code should pass the following test scenarios:
{test_scenario}
            """
               
            else:
                verilog_prompt = f"""
Please generate Verilog code for the following {module_name} design.
Write the complete Verilog module according to the given module header.
Do not include anything else, only Verilog code for one module.
Write Verilog code without using any SystemVerilog features.

** Below is information about {module_name}:
- Module header:
{module_header}
- Function description: {function_description}

** The Verilog code should pass the following test scenarios:
{test_scenario}
            """

            
    # 2. Prompt to fix the Verilog code
    else:
        if has_children:
                verilog_prompt = f"""
Please fix the errors of Verilog code generated earlier.
Check if the previous Verilog code followsthe signal names and port names exactly as provided.
Do not indclude anything else, only Verilog code for one module.
Write Verilog code without using any SystemVerilog features.

**Below is information about {module_name}:
- Module header:
{module_header}
- Function description: {function_description}

**Submodule list:
{submodules_str}

**Below is the code you generated earlier:
{numbered_verilog_code}

**The code has follwoing errors:
{previous_verilog_errors}
"""
               
                       
        else:
            verilog_prompt = f"""
Please fix the errors of Verilog code generated earlier.
Do not indclude anything else, only Verilog code for one module.
- Write Verilog code without using any SystemVerilog features.

** Below is information about {module_name}:
- Function description: {function_description}
- Module header:
{module_header}

** Below is the code you generated earlier:
{numbered_verilog_code}

** The code has follwoing error:
{previous_verilog_errors}
"""
    return verilog_prompt




    

