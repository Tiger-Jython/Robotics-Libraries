import os
import ast
import re
import python_minifier


def getPath(path):
    with open(f"./{path}", "r") as file:
        content = file.read()
    return content


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
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                relative_path = os.path.relpath(file_path, src_folder)
                minified_file_path = os.path.join(dst_folder, relative_path)

                os.makedirs(os.path.dirname(minified_file_path), exist_ok=True)

                minify_file(file_path, minified_file_path)

    print(f"Minification complete. Minified files are in '{dst_folder}'.")


minify_directory(".", "./min")