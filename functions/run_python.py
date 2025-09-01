import subprocess
import os
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file with optional command-line arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base directory where the Python file is located.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of command-line arguments to pass to the Python file.",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=[]):
    working_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not target_path.startswith(working_path):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(target_path):
        return f'Error: File "{file_path}" not found.'
    
    if not target_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        result = subprocess.run(
            ["python", file_path] + args,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30
        )

        if not result.stdout and not result.stderr:
            return "No output produced."
        
        return (
            (f"STDOUT: {result.stdout}\n" if result.stdout else "") +
            (f"STDERR: {result.stderr}\n" if result.stderr else "") +
            (f"Process exited with code {result.returncode}" if result.returncode != 0 else "")
        )
    except Exception as e:
        return f"Error: executing Python file: {e}"
