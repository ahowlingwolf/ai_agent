import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file, creating or overwriting it in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base directory where the file will be created or overwritten.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The text content to write into the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    try:
        target_path = os.path.abspath(os.path.join(working_directory, file_path))
        working_path = os.path.abspath(working_directory)

        if not (target_path == working_path or target_path.startswith(working_path + os.sep)):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        dir_name = os.path.dirname(target_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(target_path, "w") as f:
                f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {str(e)}"


