import json
import os
import sys
from pydantic import (TypeAdapter, ValidationError,
                      BaseModel, Field, validate_call)
from typing import Any
from .func_schema import FunctionSchema, PromptSchema


class JsonParser(BaseModel):
    """
    A class to handle json file parsing.

    This file is responsable to handel all interaction with
    json files included in this project.
    """

    vocab_path: str | None = None
    function_def_file: str | None = None
    user_prompts_file: str | None = None
    ouput_file: str | None = None

    function_def_dir: str | None = Field(default=None, init=False)
    user_prompts_dir: str | None = Field(default=None, init=False)
    ouput_dir: str | None = Field(default=None, init=False)
    func_def_dict: dict[str, dict[str, Any]] | None = Field(
                        default=None,
                        init=False)
    prompts_list: list[str] | None = Field(default=None, init=False)
    vocab_dict: dict[str, int] | None = Field(default=None, init=False)

    def model_post_init(self, __context: Any) -> None:
        """
        Initializes internal dependencies after Pydantic validates
        the input arguments.

        This method automatically create all what needed to interact with
        the json files like propmt list, dict for function definition
        and more.
        """
        paths = self.init_file_paths(self.function_def_file,
                                     self.user_prompts_file, self.ouput_file)
        self.function_def_dir, self.user_prompts_dir, self.ouput_dir = paths
        try:
            with open(self.function_def_dir, "r") as f:
                func_adapter = TypeAdapter(list[FunctionSchema])
                funcstr = self.del_comment(f.read())
                try:
                    func_adapter.validate_json(funcstr)
                except ValidationError as e:
                    print(f"error: {e}")
                    print("please check you function definition file")
                    sys.exit()
                self.func_def_dict = self.map_by_name(json.loads(funcstr))
                self.func_def_dict["no_matched_function"] = {
                    "description": "this function called when no other \
function are matched or sutable for the user prompt",
                    "parameters": {"no_param_needs": {"type": "None"}}
                }
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit()
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            sys.exit()
        try:
            with open(self.user_prompts_dir, "r") as f:
                prompt_adapter = TypeAdapter(list[PromptSchema])
                prompts_str = self.del_comment(f.read())
                try:
                    prompt_adapter.validate_json(prompts_str)
                except ValidationError as e:
                    print(f"error: {e}")
                    print("please check you function definition file")
                    sys.exit()
                pompts_lst = self.extract_prompts(json.loads(prompts_str))
                self.prompts_list = pompts_lst
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit()
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            sys.exit()
        if self.vocab_path:
            try:
                with open(self.vocab_path, "r", encoding='utf-8') as f:
                    self.vocab_dict = self.clean_dict(json.load(f))
            except FileNotFoundError as e:
                print(f"Error: {e}")
                sys.exit()
            except json.JSONDecodeError as e:
                print(f"Error: {e}")
                sys.exit()

    @staticmethod
    @validate_call
    def extract_prompts(prompt_lst: list[dict[str, str]]) -> list[str]:
        """
        This function take the list of dict that represnet
        the user prompts and convert it into a lists of only
        the prompts

        Args:
            prompt_lst (list[dict[str, str]]): list containes the prompts dict.

        Returns:
            list[str] : list contain the prompts string.
        """
        res_lst = []
        for my_dict in prompt_lst:
            res_lst.append(my_dict["prompt"])
        return res_lst

    @validate_call
    def init_file_paths(self,
                        function_def_file: str | None,
                        user_prompts_file: str | None,
                        ouput_file: str | None) -> tuple[str, str, str]:
        """
        This func take the passed or default path of the json file
        and return the full path for each one.

        Args:
            function_def_file (str | None):the sub path of the func def file.
            user_prompts_file (str | None):the sub path of the prompts file.
            ouput_file (str | None): the desired path for the output file.

        Returns:
            tuple[str, str, str]: contain the final path for each one in order.
        """
        cmd = os.getcwd()

        if function_def_file is None:
            function_def_file = rf"{cmd}/data/input/functions_definition.json"
        else:
            function_def_file = os.path.join(cmd, function_def_file)
        if user_prompts_file is None:
            path = rf"{cmd}/data/input/function_calling_tests.json"
            user_prompts_file = path
        else:
            user_prompts_file = os.path.join(cmd, user_prompts_file)
        if ouput_file is None:
            ouput_file = rf"{cmd}/data/output/output_file.json"
        else:
            ouput_file = os.path.join(cmd, ouput_file)
        return function_def_file, user_prompts_file, ouput_file

    @validate_call
    def del_comment(self, json_str: str) -> str:
        """
        This function is responsible about clean the json str before loading
        it to avoid all error casses and delete the comments.

        Args:
            json_str (str): the json string

        Returns:
            str : the cleaned string.
        """
        cleand_str = ""
        lines_json = json_str.split("\n")
        for line in lines_json:
            if len(line.strip()) != 0:
                if not line.strip()[0] == "#":
                    for i in line.strip():
                        if i != "#":
                            cleand_str += i
                        else:
                            break
        return cleand_str

    @staticmethod
    @validate_call
    def map_by_name(lst: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """
        This function is convert the function definition dict
        to be sorted by the name of the function as a dict key.

        Args:
            lst (list[dict]): list containe the dict for each func definition.

        Returns:
            dict[str, dict]: a dict has a function name as a key and
                             it's attribute as a value (dict)
        """
        my_dict = {}
        for item in lst:
            sub_dict = {
                "description": item["description"],
                "parameters": item["parameters"],
                "returns": item["returns"]
            }
            my_dict[item["name"]] = sub_dict
        return my_dict

    @staticmethod
    @validate_call
    def clean_token(token: str) -> str:
        """
        each model represent some character by a special character
        instead of it's original one and this func return the token
        into it's original case.

        Args:
            token (str): the token str.

        Returns:
            str : the original case of the token.
        """
        token = token.replace("Ġ", " ")
        token = token.replace("\u2581", " ")
        return token

    @validate_call
    def clean_dict(self, vocab_dict: dict[str, int]) -> dict[str, int]:
        """
        This func take the vocab dict walk on it and clean each token
        inside it.

        Args:
            vocab_dict (dict[str, int]) :dict include the tokens and if of it.

        Retunrs:
            dict[str, int]: a clean dict of the vocab (cleand tokens).
        """
        cleand_vocab = {}
        for token, id in vocab_dict.items():
            cleand_vocab[self.clean_token(token)] = id
        return cleand_vocab
