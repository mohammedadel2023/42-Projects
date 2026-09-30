# from transformers import AutoModelForCausalLM, AutoTokenizer
# import time
# from llama_cpp import Llama
# import warnings
#
# warnings.filterwarnings("ignore")
#
#
# name = "Qwen/Qwen3-0.6B"
#
# tr_start_load = time.time()
# model = AutoModelForCausalLM.from_pretrained(name)
# tokenizer = AutoTokenizer.from_pretrained(name)
# tr_end_load = time.time()
# #
# # prompt = [
# #      {"role": "system", "content": "you are a father of some one
# so be too frindly when you child talk to you"},
# #      {"role": "user", "content": "hi father!"},
# #      {"role": "assistent", "content": "reponse:<think></think>"}
# #  ]
# tr_start_inf = time.time()
# full_prompt = (
#                 f"<|im_start|>system\nyou are a father of some one so be too
#  frindly when you child talk to you<|im_end|>\n"
#                 f"<|im_start|>user\nhi father!, how are you, there are some
#  boys force me to do bad things how to stop them?pls help me
#  dady<|im_end|>\n"
#                 f"<|im_start|>assistant\n<think>\n</think>{your response}"
#             )
# print(type(full_prompt))
#
# # print(input)
# # print("=========================================")
# model_input = tokenizer([full_prompt], return_tensors="pt")
# #
# # print("====================================================")
# generated_ids = model.generate(**model_input, max_length=2000)
# # print(len(model_input.input_ids[0]))
# # print(model_input.input_ids.shape[1])
# # print(generated_ids)
# new_tokens = generated_ids[:, model_input.input_ids.shape[1]:]
# print(tokenizer.batch_decode(new_tokens, skip_special_tokens=True)[0])
#
# tr_end_inf = time.time()
# print(f"the time for laoding {tr_end_load - tr_start_load}")
# print(f"the time for inference {tr_end_inf - tr_start_inf}")
# # string = ""
# #
# # for key in prompt[0].keys():
# #     string += f"{key}: {prompt[0][key]}\n"
#
# load_start = time.time()
# llm = Llama.from_pretrained(
#     repo_id="mohammedkhas/Qwen3-0.6B-GGUF",
#     filename="*q8_0.gguf",
#     n_ctx=2000,          # Allocates buffer for 3000+ context + generation
#     n_threads=8,         # Utilizes the 8 physical P-cores on your i7
#     n_batch=512,         # Evaluates prompt tokens in chunks of 512
#     flash_attn=True,     # Reduces attention computation overhead
#     verbose=False
# )
#
# load_end = time.time()
#
#
# # 2. Inference Benchmark
# eval_start = time.time()
#
# output = llm(
#     full_prompt,
#     max_tokens=500,
#     temperature=0.7,
#     echo=False,                                # Print ONLY the
#  generated answer
#     stop=["<|im_end|>", "<|endoftext|>"]      # Stop generation cleanly
# )
#
# evl_end = time.time()
# elapsed = eval_end - eval_start
#
# # 3. Output & Performance Metrics
# result_text = output["choices"][0]["text"]
# completion_tokens = output["usage"]["completion_tokens"]
# prompt_tokens = output["usage"]["prompt_tokens"]
#
# print("=================== OUTPUT ===================")
# print(f"Model loaded in: {load_end - load_start}")
# print(result_text.strip())
# print("==============================================")
# print(f"inference: {elapsed}")
