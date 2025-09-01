import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = dict(function_call_part.args or {})

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
    }

    function_args["working_directory"] = "./calculator"

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )   
    
    func = function_map[function_name]
    function_result = func(**function_args)

    return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                name=function_name,
                    response={"result": function_result},
                )
            ],
    )




def main():
    print("Hello from agent!")

    if len(sys.argv) < 2:
        print("Error: No prompt provided.")
        sys.exit(1)
    
    prompt = sys.argv[1]
    verbose = "--verbose" in sys.argv

    

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    for _ in range(20):
        response = client.models.generate_content(
            model='gemini-2.0-flash-001', 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], 
                system_instruction=system_prompt
            ),
        )

        for c in response.candidates:
            messages.append(c.content)

        if response.function_calls:
            for function_call_part in response.function_calls:
                result_content = call_function(function_call_part, verbose)
                messages.append(
                    types.Content(role="user", parts=result_content.parts)
                )

            try:
                resp = result_content.parts[0].function_response.response
            except Exception as e:
                raise RuntimeError("Function call did not return a function_response.response") from e
            
            if verbose:
                print(f"-> {resp}")
            
            continue

        if response.text:
            print("Final response:")
            print(response.text)
            break

        if verbose and response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    


if __name__ == "__main__":
    main()
