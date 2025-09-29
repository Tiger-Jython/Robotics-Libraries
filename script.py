import os
import ast
import re
import python_minifier
import json
import sys
import subprocess

def getGlobalVariablesAndFunctions(content):
    astParsed = ast.parse(content)
    globalVariables = []
    globalFunctions = []

    for node in ast.walk(astParsed):
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                varName = node.targets[0].id
                if varName.startswith("_"):
                    if not any(isinstance(parent, (ast.FunctionDef, ast.ClassDef)) for parent in ast.walk(node)):
                        globalVariables.append(varName)
        elif isinstance(node, ast.FunctionDef):
            if node.name.startswith("_"):
                globalFunctions.append(node.name)

    return globalVariables, globalFunctions


def changeContent(content):
    globalVariables, globalFunctions = getGlobalVariablesAndFunctions(content)

    changedContent = content

    # Replace global variables
    for i, var in enumerate(globalVariables, start=1):
        replacement_var = f'_g{i}'
        changedContent = re.sub(rf'\b{var}\b', replacement_var, changedContent)

    # Replace function names, except for __init__
    for i, func in enumerate(globalFunctions, start=1):
        if func != "__init__":
            replacement_func = f'_f{i}'
            changedContent = re.sub(
                rf'\b{func}\b', replacement_func, changedContent)

    return changedContent


def minify_file(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Change global variables and function names in content
        changed_content = changeContent(content)

        # Minify the changed content
        minified_content = python_minifier.minify(changed_content)

        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, 'w') as file:
            file.write(minified_content)
        print(f"Minified file saved to {output_path}")

    except Exception as e:
        print(f"Error minifying file {file_path}: {e}")


def minify_directory(src_folder, dst_folder):
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith('.py') and file != 'script.py':
                file_path = os.path.join(root, file)

                relative_path = os.path.relpath(file_path, src_folder)
                minified_file_path = os.path.join(dst_folder, relative_path)

                os.makedirs(os.path.dirname(minified_file_path), exist_ok=True)

                minify_file(file_path, minified_file_path)
        # disable recursive minification
        break

    print(f"Minification complete. Minified files are in '{dst_folder}'.")




def create_json(src_folder):
    dict = {}
    for root, _, files in os.walk(os.path.join(src_folder,"min")):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root,file), 'r') as file:
                    content = file.read()
                    name = os.path.splitext(os.path.basename(file.name))[0]
                    dict[name] = content

        # disable recursive minification
        break
    # Convert and write JSON object to file
    outpath = os.path.join(src_folder, "libraries.json")
    with open(outpath, "w") as outfile: 
        json.dump(dict, outfile, indent=4)
    print(f"JSON file containing all libraries created in '{outpath}'.")


for item in os.listdir(os.getcwd()):
    if os.path.isdir(item):        
        minify_directory(item, os.path.join(item, "min"))
        create_json(item)

if len(sys.argv) > 1 and sys.argv[1]=="stage":
    print("staging minified files")
    subprocess.run(["git", "add", "*/libraries.json"])
    subprocess.run(["git", "add", "*/min/*"])
else:
    print("minified files not staged")