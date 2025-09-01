import os
from functions.config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of a specified file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base directory where the file is located.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to be read, relative to the working directory.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    try:
        working_path = os.path.abspath(working_directory)
        target_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not target_path.startswith(working_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
    
        with open(target_path, "r") as f:
            file_content = f.read(MAX_CHARS)

        if len(file_content) > MAX_CHARS:
            return file_content[:MAX_CHARS] + f'[...File {file_path} truncated at 10000 characters]'
    
        else:
            return file_content
    
    except Exception as e:
        return f"Error: {str(e)}"