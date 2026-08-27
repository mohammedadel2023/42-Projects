from src.model import ModelHandler
from src.parser import JsonParser
import json
import sys
import os

if __name__ == "__main__":

    args = sys.argv[1:]
    cwd = os.getcwd()
    func_def_path = "data/input/functions_definition.json"
    user_prompts_path = "data/input/function_calling_tests.json"
    output_path = "data/output/function_calling_results.json"
    try:
        for arg_num in range(len(args)):
            if args[arg_num] == "--functions_definition":
                file_path = args[arg_num + 1]
                if not os.path.isfile(file_path):
                    file_path = f"data/input/{args[arg_num + 1]}"
                path = os.path.join(cwd, file_path)
                if os.path.exists(path):
                    func_def_path = path
                else:
                    raise FileNotFoundError(f"the path:{path} not found")

            elif args[arg_num] == "--input":
                file_path = args[arg_num + 1]
                if not os.path.isfile(file_path):
                    file_path = f"data/input/{args[arg_num + 1]}"
                path = os.path.join(cwd, file_path)
                if os.path.exists(path):
                    user_prompts_path = path
                else:
                    raise FileNotFoundError(f"the path:{path} not found")
            elif args[arg_num] == "--output":
                output_path = args[arg_num + 1]
    except ValueError as e:
        print(f"error: {e}")
    except FileNotFoundError as e:
        print(f"error: {e}")
    except Exception as e:
        print(f"error: {e}")

    parser = JsonParser()
    sys_prompt = "".join([
        "You are a precise tool selection agent. Your task is to analyze the ",
        "user request and select the correct function from the list of ",
        "available functions below.",
        "\n### Available Functions:\n",
        f"{json.dumps(parser.func_def_dict, indent=2)}",
        "\n### Response Instructions",
        "\n1. Select the function from the available functions whose ",
        "description best matches the user's intent.",
        "\n2. Output a JSON object containing the user prompt, function",
        " name, its required parameters, and the returned parameters.",
    ])
    try:
        model = ModelHandler(
                             fun_def_file=func_def_path,
                             user_input_file=user_prompts_path,
                             output_file=output_path)
        model.apply_on_prompts(save=True, output=True)
    except ValueError as e:
        print(f"error :{e}")
    except Exception as e:
        print(f"error : {e}")
