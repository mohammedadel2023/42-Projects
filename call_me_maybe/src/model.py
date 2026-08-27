from llm_sdk import Small_LLM_Model
from .parser import JsonParser
from pydantic import BaseModel, Field, ConfigDict, validate_call
from typing import Any
import numpy as np
import numpy.typing as npt
import json
import os
import sys


class ModelHandler(BaseModel):
    """
    An orchestration class to handle interactions between a
    small LLM and JSON parsing logic.

    This class manages prompt construction, token prediction,
    and strict output formatting
    to ensure the language model generates valid JSON corresponding
    to predefined function schemas.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_prompts: list[str] | str | None = None
    fun_def_file: str | None = None
    user_input_file: str | None = None
    output_file: str | None = None

    model: Small_LLM_Model | None = Field(default=None, init=False)
    parser: JsonParser | None = Field(default=None, init=False)

    def model_post_init(self, __context: Any) -> None:
        """
        Initializes internal dependencies after Pydantic validates
        the input arguments.

        This method automatically instantiates the language model,
        retrieves the vocabulary, and sets up the JsonParser.
        It also normalizes `user_prompts` into a list format.
        """
        self.model = Small_LLM_Model()
        vocab_path = self.model.get_path_to_vocab_file()

        self.parser = JsonParser(
            vocab_path=vocab_path,
            function_def_file=self.fun_def_file,
            user_prompts_file=self.user_input_file,
            ouput_file=self.output_file
        )

        if self.user_prompts:
            if isinstance(self.user_prompts, str):
                self.user_prompts = [self.user_prompts]
        else:
            self.user_prompts = self.parser.prompts_list

    @validate_call()
    def create_prompt(self, func_name: str | None = None) -> str:
        """
        This function create the prompt based on the scenario we are in
        so if we in func name scenario we provide all func def with prompt
        instead we just pass the choosen func def.

        Args:
            func_name (str | None): func name
        Returns:
            str: the full prompt
        """
        if self.parser:
            if func_name:
                if self.parser.func_def_dict:
                    func_def: str | Any = self.parser.func_def_dict[func_name]
                    func_def = f"the function name is {func_name} and the \
definition is {func_def}"
            else:
                func_def = f"{json.dumps(self.parser.func_def_dict, indent=2)}"
            sys_prompt = "".join([
                "You are a precise tool selection agent. Your task is to ",
                "analyze the user request and select the correct ",
                "function from the list of available functions below.",
                "\n### Available Functions:\n",
                f"{func_def}",
                "\n### Response Instructions",
                "\n1. Select the function from the available functions whose ",
                "description best matches the user's intent.",
                "\n2. Output a JSON object containing ",
                "the user prompt, function",
                " name, its required parameters, and the returned parameters.",
            ])
            return sys_prompt
        return ""

    @staticmethod
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def mask_top_k_logits(logits: npt.NDArray[Any],
                          k: int) -> npt.NDArray[Any]:
        """
        Finds the highest `k` values in a 1D logit array and masks them with
        -inf.

        Args:
            logits: A 1D numpy array of floating point scores.
            k: The number of top scores to mask.

        Returns:
            A new numpy array with the top `k` logits set to -inf.
        """
        logits_array = np.array(logits, dtype=np.float32)

        if k <= 0:
            return logits_array.copy()
        if k >= len(logits_array):
            return np.full(logits_array.shape, -np.inf, dtype=np.float32)

        masked_logits = logits_array.copy()
        partitioned_indices = np.argpartition(masked_logits, -k)
        top_k_indices = partitioned_indices[-k:]

        masked_logits[top_k_indices] = -np.inf
        return masked_logits

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def create_mask(self, logits: npt.NDArray[Any],
                    include_ids: list[int] | None = None,
                    exclude_ids: list[int] | None = None,
                    mask_first_k: int = 1) -> npt.NDArray[Any] | None:
        """
        Applies inclusion, exclusion, and top-k masking constraints
        to a set of token logits.

        Args:
            logits: The raw logit distribution from the language model.
            include_ids: A list of token IDs to exclusively permit
                         (all others become -inf).
            exclude_ids: A list of token IDs to explicitly ban (set to -inf).
            mask_first_k: The number of top probable tokens to ignore.

        Returns:
            A processed numpy array of logits with the specified masking
            rules applied.
        """
        if include_ids:
            masked_logits = np.full(logits.shape, -np.inf, dtype=np.float32)
            masked_logits[include_ids] = logits[include_ids]
            arr: npt.NDArray[Any] = self.mask_top_k_logits(masked_logits,
                                                           mask_first_k)
            return arr
        elif exclude_ids:
            masked_logits = logits.copy()
            masked_logits[exclude_ids] = -np.inf
            arr = self.mask_top_k_logits(masked_logits, mask_first_k)
            return arr
        arr = self.mask_top_k_logits(logits, mask_first_k)
        return arr

    @validate_call
    def token_to_ids(self, tokens: str | list[str]) -> list[int]:
        """
        Converts human-readable text tokens into their corresponding
        numerical vocabulary IDs.

        Args:
            tokens: A single token string or a list of token strings.

        Returns:
            A list of integer IDs mapped directly from the model's
            vocabulary dictionary.
        """
        if self.parser:
            tokens_list = []
            vocab = self.parser.vocab_dict
            if isinstance(tokens, str):
                tokens_list.append(tokens)
            else:
                tokens_list = tokens
            ids = []
            if vocab:
                for token in tokens_list:
                    ids.append(vocab[token])
            return ids
        else:
            print("error: self.parser is None")
            sys.exit()

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def predict_next_token(self, response: str = "",
                           mask_first_k: int = 0,
                           include: list[str] | None = None,
                           exclude: list[str] | None = None,
                           user_prompt_id: int = 1,
                           func_name: str | None = None) -> str:
        """
        Constructs a prompt context, queries the LLM, and predicts the
        single most likely next token.

        Args:
            response: The current accumulated generation string from the model.
            mask_first_k: Number of highest-probability tokens to suppress.
            include: An optional list of specific text tokens to restrict the
                     generation to.
            exclude: An optional list of specific text tokens to ban from
                     generation.
            user_prompt_id: The 1-based index identifying which user prompt
                         to evaluate.

        Returns:
            The decoded text string of the single selected next token.
        """
        user_prompt_id -= 1
        if self.user_prompts:
            user_prompt = self.user_prompts[user_prompt_id]
        sys_prompt = self.create_prompt(func_name=func_name)
        full_prompt = (
                f"<|im_start|>system\n{sys_prompt}<|im_end|>\n"
                f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
                f"<|im_start|>assistant\n<think>\n</think>\n{response}"
            )
        if self.model and self.parser:
            ids = self.model.encode(full_prompt)[0].tolist()
            raw_logits = self.model.get_logits_from_input_ids(ids)
            logits = np.array(raw_logits, dtype=np.float32)
            if self.parser.vocab_dict:
                base_vocab_size = len(self.parser.vocab_dict)
            if len(logits) > base_vocab_size:
                logits[base_vocab_size:] = -np.inf

            include_ids = None
            exclude_ids = None
            if include:
                include_ids = self.token_to_ids(include)
            if exclude:
                exclude_ids = self.token_to_ids(exclude)

            masked_logits = self.create_mask(logits, include_ids, exclude_ids,
                                             mask_first_k)
            if masked_logits is not None:
                next_token_id = int(np.argmax(masked_logits))
            return self.model.decode([next_token_id])
        else:
            print("The self.parser or self.model is None")
            sys.exit()

    @staticmethod
    @validate_call
    def match_sub(sub: str, lst: list[str]) -> bool:
        """
        Checks if a given substring prefix matches the beginning of any
        string within a list.

        Args:
            sub: The prefix substring to search for.
            lst: The list of valid full strings to check against.

        Returns:
            True if the substring matches the start of at least one item,
            False otherwise.
        """
        length = len(sub)
        for item in lst:
            if len(item) >= length:
                if sub == item[:length]:
                    return True
        return False

    @validate_call
    def name_scenario(self, prompt_id: int) -> tuple[str, str]:
        """
        Generates the function name portion of the JSON output,
        enforcing alignment with the allowed function names
        defined in the parser.

        Args:
            prompt_id: The 1-based index of the current user
            prompt being evaluated.

        Returns:
            A tuple containing:
            1. The accumulated JSON string constructed so far.
            2. The specific function name string successfully
               predicted by the model.

        Raises:
            ValueError: If the model enters a state where no valid
            next tokens exist to complete an allowed function name.
        """
        if self.parser:
            response = '{"prompt":"'
            if self.user_prompts:
                response += self.user_prompts[prompt_id - 1].replace('"', "'")
            else:
                print("the prompt does not exist")
                sys.exit()
            response += '","name": "'
            if self.parser.func_def_dict:
                func_names = list(self.parser.func_def_dict.keys())
            func_name_response = ""

            while not (func_name_response in func_names):
                valid_next_tokens = []
                if self.parser.vocab_dict:
                    for token_str in self.parser.vocab_dict.keys():
                        potential_name = func_name_response + token_str
                        if self.match_sub(sub=potential_name, lst=func_names):
                            valid_next_tokens.append(token_str)

                if not valid_next_tokens:
                    raise ValueError("No valid tokens found" +
                                     f"to continue: {func_name_response}")

                token = self.predict_next_token(
                    user_prompt_id=prompt_id,
                    response=response,
                    include=valid_next_tokens,
                )
                func_name_response += token
                response += token
            return response + '", "parameters": {', func_name_response
        else:
            print("self.parser is None")
            sys.exit()

    @validate_call
    def param_scenario(self, response: str, param_name: str,
                       func_name: str, expected_type: str,
                       prompt_id: int = 1,) -> str:
        """
        Generates the parameter value for a specific function
        argument, constraining the generation based on the expected
        data type (e.g., number vs string).

        Args:
            response: The currently accumulated JSON string to append to.
            param_name: The name of the parameter being filled.
            func_name: The name of the parent function being utilized.
            expected_type: The data type expected for this parameter
            (e.g., 'number', 'string').
            prompt_id: The index of the prompt being processed.

        Returns:
            The updated JSON response string with the populated
            parameter key-value pair.
        """
        if not response.endswith("{"):
            response += ", "
        response += f'"{param_name}":'

        if expected_type == "number" or expected_type == "integer":
            whitelist = self.get_number_whitelist()
            while True:
                token = self.predict_next_token(
                    user_prompt_id=prompt_id,
                    response=response,
                    include=whitelist,
                    func_name=func_name
                )
                if "," in token or "}" in token:
                    clean_token = token.replace(",", "").replace("}", "")
                    response += clean_token
                    break
                response += token
                if len(response) > 500:
                    break

        else:
            response += '"'
            while True:
                token = self.predict_next_token(
                    user_prompt_id=prompt_id,
                    response=response,
                    func_name=func_name
                )
                token = token.replace("\n", "").replace("\r", "")
                if '"' in token or "}" in token or "," in token:
                    clean_token = token.replace('"', "").replace("}", "")
                    clean_token = clean_token.replace(",", "")
                    response += clean_token
                    break
                response += token
                if len(response) > 500:
                    break
            if not response.endswith('"'):
                response += '"'
        return response

    @validate_call
    def loop(self, prompt_id: int = 1) -> str:
        """
        Orchestrates the end-to-end generation sequence for
        a single prompt, predicting the target function name and
        populating all required parameters dynamically.

        Args:
            prompt_id: The index of the user prompt to process.

        Returns:
            A fully constructed JSON string representing the
            prompt, selected function, and populated parameters.
        """
        if self.parser:
            llm_response: str
            llm_response, func_name = self.name_scenario(prompt_id=prompt_id)
            if self.parser.func_def_dict:
                param_blk = self.parser.func_def_dict[func_name]["parameters"]
                param_keys = list(param_blk.keys())
            for key in param_keys:
                expected_type = param_blk[key].get("type", "string")
                llm_response = self.param_scenario(llm_response, key,
                                                   func_name, expected_type,
                                                   prompt_id)
            llm_response += '}}'
            try:
                _ = json.loads(llm_response)
            except json.JSONDecodeError:
                print("Warning: LLM generated invalid JSON.")
            return llm_response
        else:
            print("parser is None")
            sys.exit()

    @validate_call
    def get_number_whitelist(self) -> list[str]:
        """
        Analyzes the vocabulary dictionary to filter and return
        only tokens composed  of valid numeric
        and structural characters.

        Returns:
            A list of token strings that contain
            exclusively numbers, decimals, negative
            signs, JSON structural brackets, or whitespace characters.
        """
        if self.parser:
            valid_tokens = []
            allowed_chars = set("0123456789-.,} \n\r\t")
            if self.parser.vocab_dict:
                for tkn_str in self.parser.vocab_dict.keys():
                    cln_str = tkn_str.replace("Ġ", " ").replace("\u2581", " ")
                    if (all(char in allowed_chars for char in cln_str)
                       and len(cln_str) > 0):
                        valid_tokens.append(tkn_str)
            return valid_tokens
        else:
            print("parser is None")
            sys.exit()

    @validate_call
    def apply_on_prompts(self, save: bool = False,
                         output: bool = False) -> bool:
        """
        Executes the JSON generation loop across all configured
        user prompts sequentially  and writes the collective results
        to the specified output file.

        Args:
            save: A boolean flag indicating whether the output
                  should be persistently saved.
            output: A boolean flag; if True, prints the result of
                    each prompt to standard output.

        Returns:
            True upon successful completion of the loop and file writing.
        """
        cmd = os.getcwd()
        def_path = "data/output/output.json"
        file_path_str = self.output_file if self.output_file else def_path
        file_path = os.path.join(cmd, file_path_str)

        parent_folder = os.path.dirname(file_path)
        if not (os.path.exists(parent_folder)
                and os.path.isdir(parent_folder)):
            os.mkdir(parent_folder)
        dict_list = []
        if self.user_prompts:
            for prompt_id in range(1, len(self.user_prompts) + 1):
                if self.user_prompts[prompt_id - 1] == "":
                    continue
                res = self.loop(prompt_id=prompt_id)
                if output:
                    print(f"the result of {prompt_id} is :\n{res}")
                try:
                    dict_list.append(json.loads(res))
                except Exception:
                    pass
        if save:
            try:
                if self.output_file:
                    with open(self.output_file, "w") as f:
                        json.dump(dict_list, f, indent=4)
                    return True
            except Exception as e:
                print(f"error: {e}")
            return False
        return False
