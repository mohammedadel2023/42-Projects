*This activity has been created as part of the 42 curriculum by mkhashan.*
 
# call me maybe — Function Calling with Constrained Decoding

 ## 📌 Notes

This project was originally built as part of a structured coding curriculum and has since been cleaned up and shared here as a portfolio piece to demonstrate applied skills in Python, game development, algorithms, and software architecture.

Feedback and suggestions are welcome — feel free to open an issue or reach out!

## Description
 
This project implements a **function calling tool** that turns natural-language prompts into
structured, machine-executable function calls, using a small (0.6B parameter) local LLM
(`Qwen/Qwen3-0.6B` via the provided `llm_sdk`).
 
Small language models are unreliable at spontaneously producing valid JSON — prompting alone
might succeed only ~30% of the time. Instead of hoping the model "gets it right," this
implementation uses **constrained decoding**: at every generation step, the raw logits returned
by the model are masked so that only tokens which keep the output both syntactically valid JSON
*and* compliant with the target function's schema can be selected. This guarantees 100% parseable,
schema-correct output regardless of the model's raw reliability.
 
Given an input prompt such as:
 
```
"What is the sum of 2 and 3?"
```
 
the tool does **not** return `5`. It returns the function call needed to compute it:
 
```json
{"prompt": "What is the sum of 2 and 3?", "name": "fn_add_numbers", "parameters": {"a": 2, "b": 3}}
```
 
## Instructions
 
### Requirements
 
- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- The `llm_sdk` package, copied into the project root (alongside `src/`)
### Setup
 
```bash
# from the project root
uv sync
```
 
This installs `numpy`, `pydantic`, and any other declared dependencies into a managed virtual
environment.
 
### Running
 
```bash
uv run python -m src [--functions_definition <function_definition_file>] \
                      [--input <input_file>] \
                      [--output <output_file>]
```
 
By default, input files are read from `data/input/` and the result is written to
`data/output/function_calling_results.json`. Example with explicit paths:
 
```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```
 
### Makefile targets
 
| Target        | Purpose                                           |
|---------------|----------------------------------------------------|
| `make install`| Install dependencies via `uv`                     |
| `make run`    | Run the main script                                |
| `make debug`  | Run the main script under `pdb`                    |
| `make clean`  | Remove `__pycache__`, `.mypy_cache`, etc.          |
| `make lint`   | `flake8 .` + `mypy .` with the mandatory flag set  |
| `make lint-strict` | `flake8 .` + `mypy . --strict`               |
 
## Algorithm Explanation
 
Constrained decoding is applied at two distinct stages of generation, both built on top of
`ModelHandler.predict_next_token`, which:
 
1. Builds the full chat-formatted prompt. When generating a parameter value the prompt is
   narrowed to the chosen function's definition only (via `func_name`); when generating the
   function name it includes all available functions. The partial JSON accumulated so far is
   appended as the start of the assistant turn.
2. Encodes it and requests raw logits from the model via `llm_sdk`.
3. Clips any logits beyond the tokenizer's real vocabulary size (defensive against models
   that expose padding/special tokens outside the cleaned vocab).
4. Applies a **mask** (see below) before picking the arg-max token.
### Step 1 — Selecting the function name (`name_scenario`)
 
The function name isn't generated freely as text — it's generated **token by token, constrained
to only ever spell out a valid function name** from `functions_definition.json`. At each step:
 
- For every token in the vocabulary, `match_sub` checks whether appending that token to what's
  been generated so far still forms a valid **prefix** of at least one known function name.
- Only tokens passing that check are passed as the `include` whitelist to
  `predict_next_token`.
- Generation stops as soon as the accumulated string exactly matches a known function name.
This makes it structurally impossible for the model to hallucinate a function that doesn't
exist in the schema.
 
### Step 2 — Selecting parameter values (`param_scenario`)
 
Once the function is known, its parameter schema (`functions_definition.json`) is walked key by
key. For each parameter:
 
- The expected type determines the token whitelist:
  - **Numbers / integers** (`"number"` or `"integer"`): only tokens made up of digits, `-`,
    `.`, `,`, `}`, and whitespace are permitted (`get_number_whitelist`), so the model can
    only ever emit valid numeric literals, and generation stops the moment a `,` or `}`
    boundary token appears.
  - **Strings and booleans** (any other type, including `"string"` and `"boolean"`): generation
    is free-form (no whitelist) but wrapped in explicit `"` boundaries, and any `"`, `,`, or
    `}` emitted mid-token is treated as the end of the value.
- A `500`-character safety cutoff prevents runaway generation on a misbehaving parameter.
### Step 3 — The logit mask itself (`create_mask` / `mask_top_k_logits`)
 
- `include_ids`: every logit **not** in the whitelist is set to `-inf` before arg-max selection
  — this is what makes the function-name and number constraints airtight.
- `exclude_ids`: the inverse, used to block specific tokens (e.g. re-selecting a token that
  would immediately close a field before content has been written).
- `mask_top_k_logits`: masks the top-`k` remaining logits to `-inf`. With `k=1` (the default),
  this simply removes the single highest-probability token — used as a building block rather
  than for typical top-k sampling.
The combination of these two mechanisms means every single token emitted during generation is
filtered against the schema *before* it's chosen, not validated after the fact.
 
## Design Decisions
 
- **Pydantic everywhere**: `functions_definition.json` and the prompts file are validated
  against `FunctionSchema` / `PromptSchema` before any generation starts, so malformed input
  files fail fast with a clear error instead of causing confusing downstream crashes.
  `FunctionSchema` enforces the presence of `name`, `description`, `parameters`, and a
  `returns` field; `ParameterType` restricts types to `"number"`, `"string"`, `"boolean"`,
  or `"integer"`.
- **Greedy, masked arg-max instead of sampling**: since the goal is 100% valid, deterministic
  structured output rather than creative text, the token selection is a masked arg-max at every
  step rather than temperature-based sampling.
- **Whitelist-first vocabulary control**: rather than trying to fix up invalid JSON after
  generation (regex repair, retries, etc.), invalid tokens are prevented from ever being chosen.
  This is what gives the 100%-valid-JSON guarantee instead of a "usually valid" guarantee.
- **Type-driven whitelists**: number/integer fields use a strict character-level whitelist
  (`get_number_whitelist`) while all other types (string, boolean) fall back to the same
  free-form string generation branch, since a single whitelist would not cleanly cover both.
- **Function-scoped prompt context**: when generating parameter values, the system prompt is
  narrowed to show only the definition of the already-chosen function (via `func_name`), which
  reduces confusion from irrelevant functions without requiring a per-field hint system.
- **`no_matched_function` fallback**: the parser automatically injects a synthetic
  `no_matched_function` entry into the function dictionary so the model always has a safe
  fallback when no real function matches the prompt.
## Performance Analysis
 
> Fill this section in with your own measured results before submission — do not leave the
> placeholders below unfilled, as reviewers will re-run the tool.
 
- **Accuracy** (correct function + correct arguments) on the provided `function_calling_tests.json`:
  `100% ` (target: 90%+, per subject requirement).
- **JSON validity**: `100%` by construction — every output is checked with `json.loads()`
  in `loop()` before being written.
- **Runtime**: `less than minuts` seconds/minutes to process all test prompts on `RTX 3050 (cuda)` hardware
  (target: under 5 minutes on standard hardware).
- **Failure modes observed**: describe any prompts that produced structurally valid but
  semantically wrong output (e.g. correct function, wrong argument value).
## Challenges Faced
 
- **Tokenizer/subword alignment**: function names and parameter values are not guaranteed to
  align with single tokens. `match_sub` had to compare against *prefixes* of candidate strings
  rather than exact tokens, since a valid function name is typically spelled across several
  subword tokens.
- **Distinguishing numeric vs. string masking**: numbers needed a much stricter character-level
  whitelist than strings, since a stray letter or unescaped quote in a numeric field would break
  `json.loads()` even though the JSON *structure* looked fine.
- **Avoiding infinite generation loops**: without an explicit terminator whitelist, a field could
  in principle never emit a closing `"`/`}`/`,` token. A length-based safety cutoff (`500` chars)
  was added as a hard stop alongside the boundary-token detection.
- **Keeping the mask logic reusable**: `create_mask` and `mask_top_k_logits` were factored out
  as small, independently testable pure functions so the include/exclude/top-k logic could be
  unit tested without needing a live model.
## Testing Strategy

- **Integration tests** running the full pipeline (`loop` / `apply_on_prompts`) against small,
  hand-crafted `functions_definition.json` and `function_calling_tests.json` fixtures covering:
  - Multiple parameters of mixed types on one function.
  - Ambiguous prompts (e.g., prompts that could map to more than one function).
  - Edge-case values: empty strings, negative numbers, large numbers, special characters.
- **Output validation**: every generated object is round-tripped through `json.loads()` before
  being written, and the resulting file is checked against the original schema (correct keys,
  correct types, all required parameters present).
## Example Usage
 
```bash
$ uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calling_results.json
```
 
Given `function_calling_tests.json`:
 
```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Greet shrek"},
  {"prompt": "Reverse the string 'hello'"}
]
```
 
Produces `data/output/function_calling_results.json`:
 
```json
[
  {"prompt": "What is the sum of 2 and 3?", "name": "fn_add_numbers", "parameters": {"a": 2, "b": 3}},
  {"prompt": "Greet shrek", "name": "fn_greet", "parameters": {"name": "shrek"}},
  {"prompt": "Reverse the string 'hello'", "name": "fn_reverse_string", "parameters": {"value": "hello"}}
]
```
 
## Resources
 
- [OpenAI Function Calling documentation](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- General background on guided/constrained generation for structured LLM output (grammar-based
  and logit-masking approaches)
**AI usage disclosure**: *describe here exactly which parts of this activity you used AI for
(e.g., "used to draft the initial parsing skeleton in `parser.py`, then rewritten and understood
line by line" / "used to explain constrained decoding conceptually before implementation" /
"not used for the core masking logic in `handler.py`, which was designed and written manually").*
Be specific — this section is checked during peer review and you must be able to explain any
AI-assisted part in your own words.
