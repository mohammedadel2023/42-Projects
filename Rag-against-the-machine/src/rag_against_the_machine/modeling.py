from pydantic import BaseModel, model_validator, Field
from typing import Any
from .helper import (MinimalSource, MinimalSearchResults,
                     StudentSearchResultsAndAnswer, MinimalAnswer,
                     llm_engin)
from tqdm import tqdm
import warnings

warnings.filterwarnings(action="ignore")


class LLM(BaseModel):
    """
    This class handle all interaction with the models

    Args:
        type (llm_engin): The type of engin to use.
        name (str): the name of the model.
        model (Any): the model
        tokenizer (Any): The tokenizer if needed.
        enable_thinking (bool): ture if enable thinking.
    """

    type: llm_engin = Field(default=llm_engin.llama)
    name: str | None = Field(default=None)
    model: Any = Field(default=None)
    tokenizer: Any = Field(default=None)
    enable_thinking: bool = False

    @model_validator(mode="after")
    def _run_post_init(self) -> "LLM":
        if self.type == llm_engin.transformers:
            self.name = "Qwen/Qwen3-0.6B"
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.model = AutoModelForCausalLM.from_pretrained(self.name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.name)
        else:
            from llama_cpp import Llama
            self.name = "mohammedkhas/Qwen3-0.6B-GGUF"
            self.model = Llama.from_pretrained(
                repo_id=self.name,
                filename="*q8_0.gguf",
                n_ctx=4000,
                n_threads=8,   # Utilizes the 8 physical P-cores on your i7
                n_batch=512,   # Evaluates prompt tokens in chunks of 512
                flash_attn=True,   # Reduces attention computation overhead
                verbose=False
            )

        return self

    def generate(self, searchResult: list[MinimalSearchResults],
                 k: int) -> StudentSearchResultsAndAnswer:
        """
        THis func walk on the searchResult and answer every qustion
        inside it based on the chunks

        Args:
            searchResult (list[MinimalSearchResults]): list of
                                                       MinimalSearchResults
            k (int): number of retrieved chunks.

        Returns:
            StudentSearchResultsAndAnswer: schema with answered question.
        """
        questions = []
        for i in range(len(searchResult)):
            questions.append(
                self.apply_prompt_sechema(searchResult[i].retrieved_sources,
                                          searchResult[i].question))
        responses = []
        for q in tqdm(questions, desc="processing quastion generation"):
            if self.type == llm_engin.llama:
                responses.append(self.llama_generate(q))
            else:
                responses.append(self.transformers_generate(q))
        answerResults = [MinimalAnswer(**s.model_dump(), answer=responses[i])
                         for i, s in enumerate(searchResult) if responses[i]]
        stAnswerResult = StudentSearchResultsAndAnswer(
            search_results=answerResults,
            k=k)
        return stAnswerResult

    def llama_generate(self, prompt: str) -> str:
        """
        this func used to run a llama engin on the provided prompt.

        Args:
            prompt (str): user prompt after apply the prompt sechema

        Returns:
            str: the response of the model.
        """
        rsponse = self.model(
            prompt,
            max_tokens=1864,
            temperature=0.7,
            echo=False,  # Print ONLY the generated answer
            stop=["<|im_end|>", "<|endoftext|>"]
        )
        return str(rsponse["choices"][0]["text"].strip())

    def transformers_generate(self, prompt: str) -> str:
        """
        this func used to run a transformers engin on the provided prompt.

        Args:
            prompt (str): user prompt after apply the prompt sechema

        Returns:
            str: the response of the model.
        """
        model_input = self.tokenizer([prompt], return_tensors="pt")
        generated_ids = self.model.generate(**model_input, max_length=5000)
        new_tokens = generated_ids[:, model_input.input_ids.shape[1]:]
        response = str(self.tokenizer.batch_decode(
            new_tokens,
            skip_special_tokens=True)[0])
        return response

    def apply_prompt_sechema(self, srcs: list[MinimalSource],
                             prompt: str) -> str:
        """
        This func apply the prompt schema on all user prompt with
        retrieved chunks

        Args:
            srcs (list[MinimalSource]): source of chunks.
            prompt (str): user prompt after apply the prompt sechema.

        Returns:
            str: the result full prompt.
        """
        text = [
                    {"role": "system", "content": "\n".join(
                        ["you are a RAG system build on a vllm codebases you",
                         " will prvided with a chunks of it (vllm source ",
                         "files) with a quastion and you must ",
                         "give a good answer using the chunks provided ",
                         "each chunk will contain a content and the resource",
                         " it extract from so answer based on this ",
                         f"{[(s.file_path, s.content) for s in srcs]}"])},
        ]
        full_prompt = (
                f"<|im_start|>system\n{text[0]["content"]}<|im_end|>\n"
                f"<|im_start|>user\n{prompt}<|im_end|>\n"
                f"<|im_start|>assistant\n<think>\n</think>"
            )
        return full_prompt
