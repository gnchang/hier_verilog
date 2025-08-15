"""
0. find_node_by_name

** Function for testbench generation (Correctbench) **

1. Correctbench_init
2. TB_v_SaveFile
3. TB_py_SaveFile
4. modify_tb_v
5. modify_tb_py

** Function for Verilog code generation and refinement **

6. VeriGen_API_call
7. VeriSaveFile
8. add_line_numbers_to_verilog
9. VerifyCode_proposed (proposed)
10. parse_compile_errors
11. save_simulation_result
12. Code_Gen_Loop (proposed)

** Functions for ablation study: no functional refinement in the loop **

13. VerifyCode_top
14. VerifyCode_sub
15. second_Loop_no_tb

* Functions for ablation study: functional refinement with verified testbench *

16. VerifyCode_golden_tb
17. second_Loop_verified_tb

20. second_Loop_no_feedback
"""

import json, os, re, subprocess

from hier_tree import *
from prompts import *
from API_key import client
from textwrap import dedent


def find_node_by_name(root, target_name):
    stack = [root] 

    while stack:
        current_node = stack.pop()

        if current_node.name == target_name:
            return current_node

        for child in current_node.children:
            stack.append(child)

    return None



########### 1.0 Testbench and test scenario generation ###########

def Correctbench_init (module_spec):
    task_id = module_spec.value["module_name"]
    task_number = 1 
    functionality = module_spec.value["function_description"]
    header = module_spec.value["module_header"]
    module_code = "  "
    testbench = "  "

    ## Set the directory containing all files required to run CorrectBench as the current working directory
    os.chdir("./CorrectBench")

    data = {
        "task_id": task_id,
        "task_number": task_number,
        "description": functionality,
        "header": header,
        "module_code": module_code,
        "testbench": testbench
    }

    jsonl_filename = "data/our_inputs.jsonl"
    with open(jsonl_filename, "w") as jsonl_file:
        jsonl_file.write(json.dumps(data) + "\n")

    print(f"JSONL file has been created at '{jsonl_filename}'.")


    os.system("python main.py")

    current_week = utils.get_week_range()
    directory = f"saves/{current_week}/Main_Results/CorrectBench"

    # Get list of folders
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]

    # Select the most recent folder
    latest_folder = max(
        folders, 
        key=lambda x: x.split("_")[1] + x.split("_")[2]  # Compare by date + time
    )

    print(f"The latest folder: {latest_folder}")
    latest_folder = os.path.join(directory, latest_folder)

    task_dir = None
    for subfolder in os.listdir(latest_folder):
        subfolder_path = os.path.join(latest_folder, subfolder)
        if os.path.isdir(subfolder_path) and subfolder == task_id:  
            task_dir = subfolder_path
            break

    # Find final_TB.py
    if task_dir:
        final_tb_v_path = os.path.join(task_dir, "final_TB.v")
        final_tb_py_path = os.path.join(task_dir, "final_TB.py")
        final_test_scenario_path = os.path.join(task_dir, "test_scenario.txt")


        if os.path.exists(final_tb_v_path):  
            print(f"final_TB.v directory: {final_tb_v_path}")
        else:
            print("final_TB.v file does not exist.")

        if os.path.exists(final_tb_py_path):  
            print(f"final_TB.py path: {final_tb_py_path}")
        else:
            print("final_TB.py file does not exist.")

        
        if os.path.exists(final_test_scenario_path):  
            print(f"test_scenario.txt path: {final_test_scenario_path}")
        else:
            print("test_scenario.txt file does not exist.")

        return {
        "test_scenario": final_test_scenario_path if os.path.exists(final_test_scenario_path) else None,
        "final_TB_v": final_tb_v_path if os.path.exists(final_tb_v_path) else None,
        "final_TB_py": final_tb_py_path if os.path.exists(final_tb_py_path) else None
        }



def TB_v_SaveFile(module_spec, tb_v_path, output_dir):
    module_name = module_spec.value['module_name']
    tb_v_dir = os.path.join (output_dir, "testbench_v")
    os.makedirs(tb_v_dir, exist_ok=True)

    if not os.path.exists(tb_v_path):
        print(f"Error: Testbench file '{tb_v_path}' does not exist.")
        return None

    with open(tb_v_path, "r", encoding="utf-8") as tb_file:
        tb_content = tb_file.read()

    tb_name = f"{module_name}_tb"
    print(f"Extracted Testbench Name: {tb_name}")

    os.makedirs(tb_v_dir, exist_ok=True)
    tb_v_file_path = os.path.join(tb_v_dir, f"{tb_name}.v")

    with open(tb_v_file_path, "w", encoding="utf-8") as new_tb_file:
        new_tb_file.write(tb_content)

    print(f"Testbench saved to: {tb_v_file_path}")
    return tb_v_file_path


def TB_py_SaveFile(module_spec, tb_py_path, output_dir):
    module_name = module_spec.value['module_name']
    tb_py_dir = os.path.join (output_dir, "testbench_py")
    os.makedirs(tb_py_dir, exist_ok=True)
    
    if not os.path.exists(tb_py_path):
        print(f"Error: Testbench file '{tb_py_path}' does not exist.")
        return None

    with open(tb_py_path, "r", encoding="utf-8") as tb_file:
        tb_content = tb_file.read()

    tb_name = f"{module_name}_tb" 
    print(f"Extracted Testbench Name: {tb_name}")

    tb_py_file_path = os.path.join(tb_py_dir, f"{tb_name}.py")

    with open(tb_py_file_path, "w", encoding="utf-8") as new_tb_file:
        new_tb_file.write(tb_content)

    print(f"Testbench saved to: {tb_py_file_path}")
    return tb_py_file_path


def modify_tb_v(module_spec, tb_v_path, output_dir):

    module_name = module_spec.value["module_name"]
    folder_name = f"testbench_v_out"
    tbout_name = f"{module_name}_out.txt"
    tbout_dir = os.path.join(output_dir, folder_name)
    os.makedirs(tbout_dir, exist_ok=True)
    
    tbout_path = os.path.join(tbout_dir, tbout_name)

    with open(tb_v_path, "r", encoding="utf-8") as file:
        tb_content = file.read()

    updated_tb_content = tb_content.replace('TBout.txt', tbout_path)

    with open(tb_v_path, "w", encoding="utf-8") as file:
        file.write(updated_tb_content)

    print(f"Testbench file updated. TBout.txt path is now: {tbout_path}")
    return tb_v_path


def modify_tb_py(module_spec, tb_py_path, output_dir):
    
    module_name = module_spec.value["module_name"]
    folder_name = f"testbench_v_out"
    tbout_name = f"{module_name}_out.txt"
    tbout_dir = os.path.join(output_dir, folder_name)
    os.makedirs(tbout_dir, exist_ok=True)
    
    tbout_path = os.path.join(tbout_dir, tbout_name)

    with open(tb_py_path, "r", encoding="utf-8") as file:
        tb_content = file.read()

    updated_tb_content = tb_content.replace('TBout.txt', tbout_path)

    with open(tb_py_path, "w", encoding="utf-8") as file:
        file.write(updated_tb_content)

    print(f"Python testbench file updated. TBout.txt path is now: {tbout_path}")
    return tb_py_path


########### 2.0 Verilog code generation ###########


def VeriGen_API_call(module: TreeNode, test_scenario_path, numbered_verilog_code=None, previous_verilog_errors=None):
    user_message = verilog_gen(module, test_scenario_path, numbered_verilog_code, previous_verilog_errors)
    response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": user_message}
                ],
                model="gpt-4o"
                )

    if response.choices:
            raw_code = response.choices[0].message.content
            verilog_code_match = re.search(r"'''verilog(.*?)'''", raw_code, re.DOTALL)
            
            if verilog_code_match:
                verilog_code = verilog_code_match.group(1).strip()
            else:
                verilog_code = raw_code 

    return verilog_code



def VeriSaveFile(verilog_code, output_dir):          
    verilog_dir = os.path.join(output_dir, "verilog")
    os.makedirs(verilog_dir, exist_ok=True)

    name_match = re.search(r'\bmodule\s+(\w+)', verilog_code)  
    code_match = re.search(r'module[\s\S]*?endmodule', verilog_code)
    
    if name_match:
        module_name = name_match.group(1)  
        print(f"Extracted module name: {module_name}")

        file_name = f"{module_name}.v"
        file_path = os.path.join(verilog_dir, file_name)
        print(f"Verilog code for {module_name} saved to {file_path}")

        if code_match:
            verilog_code = code_match.group(0)  
            with open(file_path, "w") as file:
                file.write(verilog_code)  
            print(f"Code for {module_name} saved to {file_name}")
            return file_path
        else:
            print(f"No matching Verilog code found in {module_name}.")
            return 
    else:
        print("No module name found.")
        return


def add_line_numbers_to_verilog(verilog_code):
    lines = verilog_code.splitlines()
    numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered_lines)


########### 2.1 Verilog code refinement ###########

def VerifyCode_proposed(module: TreeNode, output_dir, verilog_path, tb_v_path): 
    module_name = module.value['module_name']

    # Load sub-modules of target module
    submodule_names = module.get_all_submodules()
    submodule_names.add(module_name)

    all_verilog_dir = os.path.join(output_dir, "verilog")
    all_files = [
        os.path.join(all_verilog_dir, file)
        for file in os.listdir(all_verilog_dir)
        if file.endswith(".v") and file[:-2] in submodule_names
    ]

    verilog_file_name = os.path.basename(verilog_path)
    tb_file_name = os.path.basename(tb_v_path)

    iverilog_path = os.path.join(output_dir, "iverilog")
    os.makedirs(iverilog_path, exist_ok=True)

    compile_log_path = os.path.join(iverilog_path, f"{module_name}_compile_log.txt")
    sim_log_path = os.path.join(iverilog_path, f"{module_name}_sim_log.txt")
    simv_path = os.path.join(iverilog_path, f"{module_name}_simv")

    compile_cmd = ["iverilog","-o", simv_path, *all_files, tb_v_path]
    print(f"Verilog file to be verified: {verilog_file_name}")
    print(f"Simulation using Testbench: {tb_file_name}")
    print(f"iverilog command: {' '.join(compile_cmd)}")

    # Compilation
    compile_result = subprocess.run(compile_cmd, text=True, capture_output=True, timeout=60)
    if compile_result.returncode != 0:
        print(f"Compilation failed. Error: {compile_result.stderr.strip()}")
        with open(compile_log_path, "w") as compile_log_file:
            compile_log_file.write(compile_result.stderr)

        compile_errors = compile_result.stderr.splitlines()

        verilog_errors = [line for line in compile_errors if verilog_file_name in line and line not in tb_errors]

        return {
            "status": "compile_error",
            "verilog_errors": verilog_errors
        }
   
    print("Compilation successful..")


    # Simulation
    sim_result = subprocess.run(
        ["vvp", simv_path],
        text=True,
        capture_output=True,
        timeout=60,
    )

    stdout = sim_result.stdout.strip()
    stderr = sim_result.stderr.strip()

    print(f"Simulation stdout: {stdout}")
    print(f"Simulation stderr: {stderr}")

    # Log
    with open(sim_log_path, "w", encoding="utf-8") as sim_log_file:
        sim_log_file.write(stdout)
    return {
        "status": "simulation_success",
        "output_log": stdout,
        "log_path": sim_log_path
    }



def parse_compile_errors(compile_log):

    error_lines = []
    error_pattern = r"(\w+\.v):(\d+): (.+)"
    matches = re.findall(error_pattern, compile_log)
    
    for file_name, line_num, error_msg in matches:
        error_lines.append((int(line_num), error_msg))
    
    return error_lines


def save_simulation_result(target_node, tb_py_path, output_dir):
    # Get module name from target_node
    module_name = target_node.value["module_name"]

    # Set the output file path
    result_path = os.path.join(output_dir, "final_result")
    os.makedirs(result_path, exist_ok=True)

    result_file_path = os.path.join(result_path, f"{module_name}_final.txt")

    # Run the Python script and capture the output
    result = subprocess.run(["python", tb_py_path], text=True, capture_output=True)

    # Save the standard output (simulation results) to a file
    with open(result_file_path, "w", encoding="utf-8") as file:
        file.write(result.stdout)

    print(f"Simulation result saved to: {result_path}")

    return result_file_path


########### 1.0 - 2.1 Code generation loop ###########


def Code_Gen_Loop(module: TreeNode, output_dir):
    # Recursive call for child nodes
    for child in module.children:
        Code_Gen_Loop(child, output_dir)

    # Check if the module has already been processed
    module_name = module.value["module_name"]
    verilog_file_path = os.path.join(output_dir, "verilog", f"{module_name}.v")

    if os.path.exists(verilog_file_path):
        print(f"Module {module_name} already exists. Skipping...")
        return

    print(f"[{module_name}] 2nd stage starts")

    # 1.0 Generate test scenario, tb.v, tb.py
    print(f"[{module_name}] The testbench generation is starting.\n\n")
    path_dic = Correctbench_init(module)
    tb_v_path = TB_v_SaveFile(module, path_dic['final_TB_v'], output_dir)
    tb_py_path = TB_py_SaveFile(module, path_dic['final_TB_py'], output_dir)
    test_scenario_path = path_dic['test_scenario']
    
    print(f"[{module_name}] The testbench generation has been completed.\n\n")

    # Modify tb code
    tb_v_path = modify_tb_v(module, tb_v_path, output_dir)
    tb_py_path = modify_tb_py(module, tb_py_path, output_dir)

    # Initialize previous errors and Verilog code
    previous_verilog = None
    previous_errors = None

    # Retry limits
    max_retries = 5       
    max_reboots = 3       
    reboot_count = -1     

    while reboot_count < max_reboots:
        reboot_count += 1
        if reboot_count > 0:
            print(f"[{module_name}] Reboot attempt {reboot_count}/{max_reboots}")

        retry_count = 0       
        previous_verilog = None
        previous_errors = None

        while retry_count < max_retries:
            # 2.0 Generate Verilog code
            print(f"[{module_name}] Generating Verilog code... (Retry {retry_count}/{max_retries})")
            verilog_code = VeriGen_API_call(module, previous_verilog, previous_errors)
            verilog_path = VeriSaveFile(verilog_code, output_dir)
            if verilog_path is None:
                print(f"[{module_name}] Error: Verilog file could not be saved.") 
                return
            
            # 3.0 Verify Verilog code
            verification_result = VerifyCode_proposed(module, output_dir, verilog_path, tb_v_path)
        
            # Compilation error
            if verification_result['status'] == "compile_error":
                print(f"[{module_name}] Compilation failed.")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"[{module_name}] Max retries reached. Rebooting Verilog code generation...")
                    break  # Reboot 진행

                compile_errors = verification_result['verilog_errors']
                error_lines = parse_compile_errors("\n".join(compile_errors))
                previous_verilog = add_line_numbers_to_verilog(verilog_code)
                previous_errors = error_lines
                continue # Retry

            # Simulation
            elif verification_result['status'] == "simulation_success":
                    sim_result_path = save_simulation_result(module, tb_py_path, output_dir)

                    # Compare reference output signal vs. output signal
                    with open(sim_result_path, "r", encoding="utf-8") as sim_result_file:
                        sim_result = sim_result_file.read()

                    # Function error
                    if "Failed" in sim_result:
                        print(f"[{module_name}] Compilation failed.")
                        retry_count += 1
                        if retry_count > max_retries:
                            print(f"[{module_name}] Max retries reached. Rebooting Verilog code generation...")
                            break  # Reboot

                        failed_scenarios = [
                            line for line in sim_result.splitlines() if "Failed" in line
                        ]
                        failed_log_path = os.path.join(output_dir, f"{module_name}_failed_scenarios.txt")
                        with open(failed_log_path, "w", encoding="utf-8") as log_file:
                            log_file.write("\n".join(failed_scenarios))

                        print(f"Failed scenarios logged at: {failed_log_path}")
                        previous_errors = failed_scenarios
                        previous_verilog = verilog_code
                        continue  # Retry

                    # Function pass
                    else:
                        print(f"[{module_name}] Simulation passed successfully {retry_count+1}/{max_retries} with {reboot_count}/{max_reboots}!")
                        return  # Exit simulation loop
                
        # Fail to generate correct Verilog code
        if reboot_count >= max_reboots:
            print(f"[{module_name}]  Max reboots reached. Could not fix all issues.")
            return



def VerifyCode_sub(module: TreeNode, output_dir, verilog_path): 
    module_name = module.value['module_name']
    
    all_verilog_dir = os.path.join(output_dir, "verilog")
    all_files = [os.path.join(all_verilog_dir, file) for file in os.listdir(all_verilog_dir)]

    verilog_file_name = os.path.basename(verilog_path)

    iverilog_path = os.path.join(output_dir, "iverilog")
    os.makedirs(iverilog_path, exist_ok=True)

    compile_log_path = os.path.join(iverilog_path, f"{module_name}_compile_log.txt")
    sim_log_path = os.path.join(iverilog_path, f"{module_name}_sim_log.txt")
    simv_path = os.path.join(iverilog_path, f"{module_name}_simv")

    compile_cmd = ["iverilog", "-o", simv_path, *all_files]
    print(f"Verilog file to be verified: {verilog_file_name}")
    print(f"iverilog command: {' '.join(compile_cmd)}")

    # 컴파일
    compile_result = subprocess.run(compile_cmd, text=True, capture_output=True, timeout=60)
    if compile_result.returncode != 0:
        print(f"Compilation failed. Error: {compile_result.stderr.strip()}")
        with open(compile_log_path, "w") as compile_log_file:
            compile_log_file.write(compile_result.stderr)

        compile_errors = compile_result.stderr.splitlines()
       
        verilog_errors = [ line  for line in compile_errors if verilog_file_name in line]
        print(verilog_errors)

        if (verilog_errors):
            return {
                "status": "compile_error",
                "verilog_errors": verilog_errors,
            }
        
        else:
            print("Compilation successful..")
            return {
            "status": "compile_success",
                }
    
    else:
        print("Compilation successful..")
        return {
        "status": "compile_success",
            }



def VerifyCode_top(module_spec, output_dir, verilog_path, top_tb_path): 
    module_name = module_spec.value['module_name']

    all_verilog_dir = os.path.join(output_dir, "verilog")
    all_files = [os.path.join(all_verilog_dir, file) for file in os.listdir(all_verilog_dir)]

    verilog_file_name = os.path.basename(verilog_path)
    tb_file_name = os.path.basename(top_tb_path)

    iverilog_path = os.path.join(output_dir, "iverilog")
    os.makedirs(iverilog_path, exist_ok=True)

    compile_log_path = os.path.join(iverilog_path, f"{module_name}_compile_log.txt")
    sim_log_path = os.path.join(iverilog_path, f"{module_name}_sim_log.txt")
    simv_path = os.path.join(iverilog_path, f"{module_name}_simv")

    compile_cmd = ["iverilog", "-o", simv_path, *all_files, top_tb_path]
    print(f"Verilog file to be verified: {verilog_file_name}")
    print(f"Simulation using Testbench: {tb_file_name}")
    print(f"iverilog command: {' '.join(compile_cmd)}")

    compile_result = subprocess.run(compile_cmd, text=True, capture_output=True, timeout=60)
    if compile_result.returncode != 0:
        print(f"Compilation failed. Error: {compile_result.stderr.strip()}")
        with open(compile_log_path, "w") as compile_log_file:
            compile_log_file.write(compile_result.stderr)

        compile_errors = compile_result.stderr.splitlines()

        tb_errors = [line for line in compile_errors if tb_file_name in line]

        verilog_errors = [line for line in compile_errors if verilog_file_name in line and line not in tb_errors]

        if (verilog_errors):
            return {
                "status": "compile_error",
                "tb_errors": tb_errors,
                "verilog_errors": verilog_errors,
            }
        
        else:
            print("Compilation successful..")
            return {
            "status": "compile_success",
                }

    else:
        print("Compilation successful..")


    sim_result = subprocess.run(
        ["vvp", simv_path],
        text=True,
        capture_output=True,
        timeout=60,
    )

    stdout = sim_result.stdout.strip()
    stderr = sim_result.stderr.strip()

    print(f"Simulation stdout: {stdout}")
    print(f"Simulation stderr: {stderr}")

    with open(sim_log_path, "w", encoding="utf-8") as sim_log_file:
        sim_log_file.write(stdout)
    return {
        "status": "simulation_success",
        "output_log": stdout,
        "log_path": sim_log_path
    }

       
### Functions for ablation study: code generation with no functional refinement ###


def second_Loop_no_tb(module: TreeNode, output_dir, top_tb_path):
    # Recursive call for child nodes
    for child in module.children:
        second_Loop_no_tb(child, output_dir, top_tb_path)

    # Check if the module has already been processed
    module_name = module.value["module_name"]
    verilog_file_path = os.path.join(output_dir, "verilog", f"{module_name}.v")

    if os.path.exists(verilog_file_path):
        print(f"Module {module_name} already exists. Skipping...")
        return

    print(f"[{module_name}] 2nd stage starts")

    parent = module.parent
    has_parent = bool(parent)

    #submodule일 때 --> simulation 안함
    if has_parent:     
        print(f"[{module_name}] The testbench generation has been skipped.\n\n")

        previous_verilog = None
        previous_errors = None

        # Retry limits
        max_compile_retries = 5
        compile_retry_count = 0

        while compile_retry_count < max_compile_retries:
            # Generate prompts and Verilog code
            print(f"[{module_name}] The Verilog code generation is starting.\n\n")
            verilog_code = VeriGen_API_call(module, previous_verilog, previous_errors)
            if verilog_code == None:
                print(f"Nothing to deal with {module_name} module. Skip to next step")
                break
                
            print(f"[{module_name}] The Verilog code generation has been completed. The Verilog code verification is starting.\n\n")
            verilog_path = VeriSaveFile(verilog_code, output_dir)
            # Verify code
            verification_result = VerifyCode_sub(module, output_dir, verilog_path)

            if verification_result['status'] == "compile_error":
                print(f"[{module_name}] Compilation failed. Fixing errors...")

                # Parse compile errors
                compile_errors = verification_result['verilog_errors']
                error_lines = parse_compile_errors("\n".join(compile_errors))

                previous_verilog = add_line_numbers_to_verilog(verilog_code)  # Update with line numbers
                previous_errors = error_lines  # Update with errors
                
                compile_retry_count += 1
                if compile_retry_count == max_compile_retries:
                    print(f"[{module_name}]Max compilation retries reached. Could not fix all issues.")
                    break  # Exit compile loop
                
                continue  # Retry compile
            
            else:
                print(f"[{module_name}]Compilation succeeded.")
                break

    #topmodule일 때 --> simulation 함
    else:
        print(f"[{module_name}] The testbench generation has been skipped.\n\n")
        previous_verilog = None
        previous_errors = None

        # Retry limits
        max_compile_retries = 5
        compile_retry_count = 0
        # Code generation 추가
        while compile_retry_count < max_compile_retries:
            # Generate prompts and Verilog code
            print(f"[{module_name}] The Verilog code generation is starting.\n\n")
            verilog_code = VeriGen_API_call(module, previous_verilog, previous_errors)
            if verilog_code == None:
                print(f"Nothing to deal with {module_name} module. Skip to next step")
                break
            
            print(f"[{module_name}] The Verilog code generation has been completed. The Verilog code verification is starting.\n\n")
            verilog_path = VeriSaveFile(verilog_code, output_dir)
            # Verify code
            verification_result = VerifyCode_sub(module, output_dir, verilog_path)

            if verification_result['status'] == "compile_error":
                print(f"[{module_name}] Compilation failed. Fixing errors...")

                # Parse compile errors
                compile_errors = verification_result['verilog_errors']
                error_lines = parse_compile_errors("\n".join(compile_errors))

                previous_verilog = add_line_numbers_to_verilog(verilog_code)  # Update with line numbers
                previous_errors = error_lines  # Update with errors
                
                compile_retry_count += 1
                if compile_retry_count == max_compile_retries:
                    print(f"[{module_name}]Max compilation retries reached. Could not fix all issues.")
                    break  # Exit compile loop
                
                continue  # Retry compile
            
            else:
                print(f"[{module_name}]Compilation succeeded.")
                break

        #simul
        all_verilog_dir = os.path.join(output_dir, "verilog")
        all_files = [os.path.join(all_verilog_dir, file) for file in os.listdir(all_verilog_dir)]

        verilog_file_name = os.path.basename(verilog_file_path)
        tb_file_name = os.path.basename(top_tb_path)

        iverilog_path = os.path.join(output_dir, "iverilog")
        os.makedirs(iverilog_path, exist_ok=True)

        compile_log_path = os.path.join(iverilog_path, f"{module_name}_compile_log.txt")
        sim_log_path = os.path.join(iverilog_path, f"{module_name}_sim_log.txt")
        simv_path = os.path.join(iverilog_path, f"{module_name}_simv")

        #compile_cmd = ["iverilog", "-g2005-sv","-o", simv_path, *all_files, top_tb_path]
        compile_cmd = ["iverilog", "-o", simv_path, *all_files, top_tb_path]
        print(f"Verilog file to be verified: {verilog_file_name}")
        print(f"Simulation using Testbench: {tb_file_name}")
        print(f"iverilog command: {' '.join(compile_cmd)}")

        # 컴파일
        compile_result = subprocess.run(compile_cmd, text=True, capture_output=True, timeout=60)
        if compile_result.returncode != 0:
            print(f"Compilation failed. Error: {compile_result.stderr.strip()}")
            with open(compile_log_path, "w") as compile_log_file:
                compile_log_file.write(compile_result.stderr)

            compile_errors = compile_result.stderr.splitlines()

            # tb_file_name에서 발생한 에러만 tb_errors에 저장
            tb_errors = [line for line in compile_errors if tb_file_name in line]

            # verilog_file_name에서 발생한 에러만 verilog_errors에 저장
            verilog_errors = [line for line in compile_errors if verilog_file_name in line and line not in tb_errors]

            return {
                "status": "compile_error",
                "tb_errors": tb_errors,
                "verilog_errors": verilog_errors,
            }
        else:
            print("Compilation successful..")


        #이제 시뮬레이션
        sim_result = subprocess.run(
            ["vvp", simv_path],
            text=True,
            capture_output=True,
            timeout=60,
        )

        stdout = sim_result.stdout.strip()
        stderr = sim_result.stderr.strip()

        print(f"Simulation stdout: {stdout}")
        print(f"Simulation stderr: {stderr}")

        # 시뮬레이션 결과 로그 저장
        with open(sim_log_path, "w", encoding="utf-8") as sim_log_file:
            sim_log_file.write(stdout)
        return {
            "status": "simulation_success",
            "output_log": stdout,
            "log_path": sim_log_path
        }

       
### Functions for ablation study: code generation with golden functional refinement ###


def VerifyCode_golden_tb (module: TreeNode, output_dir, verilog_path, tb_path):  
    module_name = module.value['module_name']
    
    submodule_names = module.get_all_submodules()
    submodule_names.add(module_name)  

    all_verilog_dir = os.path.join(output_dir, "verilog")
    all_files = [
        os.path.join(all_verilog_dir, file)
        for file in os.listdir(all_verilog_dir)
        if file.endswith(".v") and file[:-2] in submodule_names
    ]

    verilog_file_name = os.path.basename(verilog_path)

    iverilog_path = os.path.join(output_dir, "iverilog")
    os.makedirs(iverilog_path, exist_ok=True)

    compile_log_path = os.path.join(iverilog_path, f"{module_name}_compile_log.txt")
    sim_log_path = os.path.join(iverilog_path, f"{module_name}_sim_log.txt")
    simv_path = os.path.join(iverilog_path, f"{module_name}_simv")

    tb_file_name = f"{module_name}_tb.v"
    tb_file_path = os.path.join(tb_path, tb_file_name)

    if os.path.exists(tb_file_path):
        print(f"Testbench file found: {tb_file_path}")
        all_files.append(tb_file_path)
    else:
        print(f"Warning: Testbench file {tb_file_name} not found in {tb_path}")

    compile_cmd = ["iverilog", "-o", simv_path, *all_files]
    
    print(f"Verilog file to be verified: {verilog_file_name}")
    print(f"iverilog command: {' '.join(compile_cmd)}")

    compile_result = subprocess.run(compile_cmd, text=True, capture_output=True, timeout=60)
    if compile_result.returncode != 0:
        print(f"Compilation failed. Error: {compile_result.stderr.strip()}")
        with open(compile_log_path, "w") as compile_log_file:
            compile_log_file.write(compile_result.stderr)

        compile_errors = compile_result.stderr.splitlines()
       
        verilog_errors = [
            line
            for line in compile_errors
            if verilog_file_name in line
        ]

        return {
            "status": "compile_error",
            "verilog_errors": verilog_errors,
        }
    
    print("Compilation successful..")

    sim_cmd = ["vvp", simv_path]
    print(f"Running simulation: {' '.join(sim_cmd)}")

    sim_result = subprocess.run(sim_cmd, text=True, capture_output=True, timeout=60)
    stdout = sim_result.stdout.strip()

    with open(sim_log_path, "w", encoding="utf-8") as sim_log_file:
        sim_log_file.write(stdout)

    if "PASS" in stdout:
        print("Simulation passed!")
        return {
            "status": "simulation_success",
            "output_log": stdout,
            "log_path": sim_log_path
        }
    elif "FAIL" in stdout:
        print("Simulation failed!")
        return {
            "status": "simulation_fail",
            "output_log": stdout,
            "log_path": sim_log_path
        }
    else:
        print("Simulation completed with unknown status.")
        return {
            "status": "simulation_unknown",
            "output_log": stdout,
            "log_path": sim_log_path
        }

import os

def second_Loop_verified_tb(module: TreeNode, output_dir, tb_path):
    # Recursive call for child nodes
    for child in module.children:
        second_Loop_verified_tb(child, output_dir, tb_path)

    module_name = module.value["module_name"]
    verilog_file_path = os.path.join(output_dir, "verilog", f"{module_name}.v")

    if os.path.exists(verilog_file_path):
        print(f"Module {module_name} already exists. Skipping...")
        return

    print(f"[{module_name}] 2nd stage starts")

    max_retries = 5       # Number of retries per round (compile + simulation)
    max_reboots = 4       # Maximum number of full reboots from scratch
    reboot_count = -1     # Current reboot count

    while reboot_count < max_reboots:
        reboot_count += 1
        if reboot_count > 0:
            print(f"[{module_name}] Reboot attempt {reboot_count}/{max_reboots}")
        
        
        retry_count = 0       # Reset retry_count after each reboot
        previous_verilog = None
        previous_errors = None

        while retry_count < max_retries:
            # Generate Verilog code
            print(f"[{module_name}] Generating Verilog code... (Retry {retry_count}/{max_retries})")
            verilog_code = VeriGen_API_call(module, previous_verilog, previous_errors)
            verilog_path = VeriSaveFile(verilog_code, output_dir)
            if verilog_path is None:
                print(f"[{module_name}] Error: Verilog file could not be saved.") 
                return
            
            # Verify Verilog code
            verification_result = VerifyCode_golden_tb(module, output_dir, verilog_path, tb_path)

            # Compilation error
            if verification_result['status'] == "compile_error":
                print(f"[{module_name}] Compilation failed.")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"[{module_name}] Max retries reached. Rebooting Verilog code generation...")
                    break  # Reboot 

                #print(f"[{module_name}] Fixing errors... (Retry {retry_count}/{max_retries})") 
                compile_errors = verification_result['verilog_errors']
                error_lines = parse_compile_errors("\n".join(compile_errors))
                previous_verilog = add_line_numbers_to_verilog(verilog_code)
                previous_errors = error_lines
                continue  # Proceed to the next retry attempt

            
            # Simulation error
            elif verification_result['status'] == "simulation_fail":
                print(f"[{module_name}] Simulation failed.")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"[{module_name}] Max retries reached. Rebooting Verilog code generation...")
                    break  # Reboot

                #print(f"[{module_name}] Fixing errors... (Retry {retry_count}/{max_retries})") 
                previous_errors = "Simulation error: the Verilog Code fails to function as intended."
                previous_verilog = verilog_code
                continue

            # Simulation success
            elif verification_result['status'] == "simulation_success":
                print(f"[{module_name}] Simulation passed successfully on attempt {retry_count+1}/{max_retries} with {reboot_count}/{max_reboots}!")
                return  # Exit the entire loop
            
            # Unknown error
            else:
                print(f"[{module_name}] Simulation completed with unknown status. (Reboot)")
                break  # Reboot
        
        # Still failed after all reboot attempts
        if reboot_count >= max_reboots:
            print(f"[{module_name}]  Max reboots reached. Could not fix all issues.")
            return  # Final failure


def second_Loop_no_feedback(module: TreeNode, output_dir):
    # Recursive call for child nodes
    for child in module.children:
        second_Loop_no_feedback(child, output_dir)

    module_name = module.value["module_name"]
    verilog_file_path = os.path.join(output_dir, "verilog", f"{module_name}.v")

    if os.path.exists(verilog_file_path):
        print(f"Module {module_name} already exists. Skipping...")
        return

    print(f"[{module_name}] Generating Verilog code...")

    # Generate Verilog code once
    # 수정 후 (정의에 맞게 호출)
    verilog_code = VeriGen_API_call(module, test_scenario_path=None, numbered_verilog_code=None, previous_verilog_errors=None)


    if verilog_code is None:
        print(f"No Verilog code generated for {module_name}. Skipping.")
        return

    # Save the generated Verilog code
    VeriSaveFile(verilog_code, output_dir)

    print(f"[{module_name}] Verilog code generation completed. No verification performed.\n")