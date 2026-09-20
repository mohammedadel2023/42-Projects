*This activity has been created as part of the 42 curriculum by mkhashan.*

# RAG Against the Machine

This project builds a lightweight retrieval-augmented generation (RAG) pipeline for answering questions over a codebase and documentation corpus. It scans source files, chunks them into searchable units, retrieves the most relevant chunks with BM25, and then generates answers with an LLM.

The system is designed around the following flow:

- Index raw source files and documentation
- Split content into manageable chunks
- Retrieve top-k relevant chunks for a query
- Feed context into a local LLM
- Save search and answer results for evaluation

## What this repository does

The project provides:

- File traversal and filtering for code/document sources
- Chunking logic for large source files
- BM25-based indexing and retrieval
- A question-answering pipeline using either llama.cpp or Hugging Face transformers
- Dataset-oriented search and answer generation workflows
- Recall-based evaluation against a ground-truth dataset

## Architecture

The main logic is implemented in the `src/rag_against_the_machine` package:

- `indexing.py`: builds the searchable index from files under `data/raw`
- `retrieving.py`: loads the BM25 index and retrieves relevant chunks
- `modeling.py`: runs the LLM for answer generation
- `controler.py`: exposes the CLI handlers for search, answer, and evaluation
- `utils/`: file traversal, chunking, JSON dataset handling, and CLI helpers

### System architecture and data flow

The pipeline is composed of four stages:

1. **File discovery**: the traversal utilities scan `data/raw` and separate supported
   code and documentation files.
2. **Indexing**: the indexer loads each file, creates chunks, assigns source metadata
   such as the file path and character offsets, and stores a chunk lookup table.
3. **Retrieval**: the retriever tokenizes the user question and uses the persisted
   BM25 model to rank chunks by lexical relevance. It returns the top `k` chunks and
   their scores.
4. **Generation**: the selected chunks and the question are placed in a prompt and
   sent to the selected local language-model backend. The answer, retrieved sources,
   and scores can be serialized for later evaluation.

The persisted files connect the stages: `chunks_lookup.pkl` maps BM25 result IDs back
to source chunks, while `retriever.pkl` contains the indexed BM25 model. A normal
single-question request therefore follows this path:

```text
raw files -> traversal -> chunker -> BM25 index
                                  -> chunk lookup
question -> BM25 retrieval -> top-k source chunks -> LLM prompt -> answer
```

## Chunking strategy

The chunker uses `RecursiveCharacterTextSplitter` with a maximum chunk size of
**2,000 characters** by default. The size can be changed through the index command,
but the current implementation caps it at 2,000 characters.

- Markdown files use the Markdown-aware splitter.
- Plain-text files use the generic recursive character splitter.
- Python files use the Python-aware splitter so that code boundaries are preserved
  where possible.
- Each chunk stores its starting character index and source path.
- Documentation chunks use a **200-character overlap** to preserve context across
  boundaries.
- Code chunks currently use the language-aware splitter without overlap.

This approach balances retrieval granularity against prompt size: smaller chunks
improve source precision, while larger chunks preserve more context. Chunk size is
therefore an important tuning parameter for both Recall@k and generation quality.

## Retrieval method

Retrieval uses **BM25**, a sparse lexical ranking algorithm. During indexing, the
content of every chunk is tokenized and added to a BM25 index. At query time, the
question is tokenized using the same tokenizer and the index returns the highest
scoring chunk IDs.

The retriever then:

1. Requests the configured number of results (`k`).
2. Maps each returned ID through `chunks_lookup.pkl`.
3. Preserves the BM25 score for each result.
4. Returns the source path, character offsets, content, and score.

BM25 favors terms that occur frequently in the query and are distinctive across the
corpus. It is fast, local, and does not require embedding generation, but it is
lexical: paraphrases and queries using vocabulary absent from the source may be
ranked less effectively than with a semantic vector retriever.

## Performance analysis

The project evaluates retrieval using Recall@k. A result is counted as relevant when
the retrieved chunk belongs to the expected source file and overlaps the reference
source span by at least the implementation's IoU threshold. The built-in evaluator
prints the recall for the `k` stored in the search-results file.

Run an evaluation with:

```bash
uv run python -m src evaluate \
  data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  data/datasets/public/AnsweredQuestions/dataset_docs_public.json
```

| Dataset | k | Recall@k | Index time | Search time | Answer time (llama) | Answer time (transformers)
|---|---:|---:|---:|---:|---:|---:|
| Documents | 5 | 84% | None | None | 6s | 37s
| Code | 5 | 55% | None | None | 6s | 37s

Indexing is performed once and persisted, so later searches avoid reprocessing the
source files. Search is generally cheaper than answer generation; generation time
depends on the selected model, CPU/GPU availability, model download status, and the
number of questions in the dataset. Increasing `k` can improve context coverage but
also increases prompt size and generation cost.

## Design decisions

- **BM25 instead of embeddings**: BM25 is simple to run locally, has no vector
  database requirement, and works well for exact identifiers, function names, and
  technical terms in source code.
- **Persisted pickle artifacts**: saving the chunk lookup and BM25 model separates the
  expensive indexing phase from repeated query and answer runs.
- **Language-aware splitting**: Markdown and Python splitters preserve more useful
  structural boundaries than splitting every file as arbitrary text.
- **Source metadata preservation**: file paths and character offsets make retrieved
  results inspectable and allow overlap-based evaluation against reference sources.
- **Two local generation backends**: llama.cpp provides a local GGUF workflow, while
  Transformers provides an alternative Hugging Face implementation.
- **Separate search and answer commands**: retrieval results can be inspected,
  evaluated, cached, and regenerated without repeating the search phase.

## Challenges and limitations

Several practical challenges shaped the implementation:

- **Long files exceed the model context window**: recursive chunking limits the
  amount of text passed to retrieval and generation.
- **Boundary loss between chunks**: documentation overlap helps retain context when
  a relevant passage crosses a chunk boundary.
- **Code and prose have different structure**: separate language-aware splitters are
  used instead of applying one generic strategy to every file type.
- **Local model inference can be slow**: the pipeline caches retrieval results and
  supports both llama.cpp and Transformers so users can select the backend that fits
  their hardware.
- **Lexical retrieval misses some paraphrases**: BM25 depends on shared terms between
  the question and source. Queries using different wording may require better query
  formulation or a future semantic/hybrid retriever.
- **Results depend on corpus preparation**: unsupported extensions, missing datasets,
  or an incorrectly populated `data/raw` directory reduce index coverage and can
  lower Recall@k.

## Requirements

- Python 3.13+
- `uv` package manager
- Access to a local model backend
 - `llama.cpp` model via `llama-cpp-python`
 - or Hugging Face transformer model support
- Dataset files and source corpus extracted into the `data/` folder

## Installation

From the project root:

```bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and creates the project virtual environment.

## Initial data setup

The project expects a prepared source tree and evaluation datasets under `data/`.

You can use the provided Makefile target:

```bash
make init
```

This unpacks the bundled archive and creates the expected working folders:

- `data/raw/`
- `data/datasets/`
- `data/processed/`
- `data/output/`

If you prefer to do it manually, ensure that:

- the source codebase is placed under `data/raw`
- the public datasets are available under `data/datasets/public`
- `data/processed` exists for serialized index files

## Project folders

```text
.
├── src/
│   └── rag_against_the_machine/
│       ├── indexing.py
│       ├── retrieving.py
│       ├── modeling.py
│       ├── controler.py
│       └── utils/
├── data/
│   ├── raw/
│   ├── datasets/
│   ├── processed/
│   └── output/
├── Makefile
├── pyproject.toml
├── README.md
└── data+moulinette.tar.xz
```

## Running the pipeline

### 1) Build the index

This scans files in the raw source tree and saves the BM25 index and chunk lookup.

```bash
uv run python -m src index --chunk_size 2000
```

You can also use the Makefile shortcut:

```bash
make run_index
```

### 2) Search a single query

```bash
uv run python -m src search "How is the model loaded?" --k 5
```

This returns the top-k matching chunks along with their file paths and character ranges.

### 3) Search an entire dataset

```bash
uv run python -m src search_dataset \
 data/datasets/public/UnansweredQuestions/dataset_docs_public.json \
 data/output/search_results/UnansweredQuestions \
 --k 5
```

This runs the retriever over every question in the dataset and saves the search result JSON to the output directory.

### 4) Answer a single query

```bash
uv run python -m src answer "What does this function do?" --k 5 --engin llama
```

Supported engine values are defined by the project enum and include:

- `llama`
- `transformers`

#### Example with the Transformers backend

```bash
uv run python -m src answer "What does this function do?" --k 5 --engin transformers
```

### 5) Answer a full dataset

Run answers against search results previously saved for a dataset.

#### For document dataset

```bash
uv run python -m src answer_dataset \
 data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
 data/output/answer_results/UnansweredQuestions \
 --engin llama
```

#### For code dataset

```bash
uv run python -m src answer_dataset \
 data/output/search_results/UnansweredQuestions/dataset_code_public.json \
 data/output/answer_results/UnansweredQuestions \
 --engin llama
```

Note: this step can be slow depending on the model and dataset size. The project comments note that answer generation may take several minutes with the local LLM backend.

### 6) Evaluate retrieval quality

The project includes a Recall@k evaluator that compares retrieved sources against the dataset truth set.

```bash
uv run python -m src evaluate \
 data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
 data/datasets/public/AnsweredQuestions/dataset_docs_public.json
```

This computes a recall metric for the stored retrieval results.

### Optional external benchmark runner

If the bundled evaluation tool was extracted during setup, you can also invoke the dataset benchmark directly:

```bash
cd moulinette_pkg
./moulinette-fedora evaluate_student_search_results \
  ../data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  ../data/datasets/public/AnsweredQuestions/dataset_docs_public.json \
  --k 5 \
  --max_context_length 2000
```

This is the same workflow referenced by the project Makefile and is useful when you want to compare the project output against the external evaluator provided with the dataset bundle.

## Makefile shortcuts

The repository ships with helper commands:

```bash
make install
make init
make run_index
make run_search_dataset
make run_evaluate
```

You can also run linting checks:

```bash
make lint
make lint-strict
```

## Typical workflow

A standard end-to-end pipeline is:

```bash
uv sync
make init
uv run python -m src index --chunk_size 2000
uv run python -m src search_dataset \
 data/datasets/public/UnansweredQuestions/dataset_docs_public.json \
 data/output/search_results/UnansweredQuestions \
 --k 5
uv run python -m src answer_dataset \
 data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
 data/output/answer_results/UnansweredQuestions \
 --engin llama
uv run python -m src evaluate \
 data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
 data/datasets/public/AnsweredQuestions/dataset_docs_public.json
```

## Notes

- The index is stored in `data/processed/chunks_lookup.pkl` and `data/processed/retriever.pkl`.
- Retrieval uses BM25, meaning the result quality depends heavily on chunk size and the content quality of the raw corpus.
- Large local LLM models may require substantial disk space and time to download and run.
- For best results, make sure the raw corpus and datasets are present before running the indexing and evaluation commands.

## License

This project is distributed as-is for research and local experimentation. Check the repository status and any project-specific policies before using it in production or shared environments.
