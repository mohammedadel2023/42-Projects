install:
	uv sync

run_index:
	uv run python -m src index 2000

run_search_dataset:
	uv run python -m src search_dataset --dataset_path data/datasets/public/UnansweredQuestions/dataset_docs_public.json --k 5 --save_directory data/output/search_results/UnansweredQuestions
	uv run python -m src search_dataset --dataset_path data/datasets/public/UnansweredQuestions/dataset_code_public.json --k 5 --save_directory data/output/search_results/UnansweredQuestions

run_answer_dataset:
	uv run python -m src answer_dataset --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_code_public.json --save_directory data/output/answer_results/AnsweredQuestions --engin llama
	uv run python -m src answer_dataset --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json --save_directory data/output/answer_results/AnsweredQuestions --engin llama
	
run_my_evaluate:
	uv run python -m src evaluate data/output/search_results/UnansweredQuestions/dataset_code_public.json data/datasets/public/AnsweredQuestions/dataset_code_public.json
	uv run python -m src evaluate data/output/search_results/UnansweredQuestions/dataset_docs_public.json data/datasets/public/AnsweredQuestions/dataset_docs_public.json

run_evaluate:
	cd moulinette_pkg && ./moulinette-fedora evaluate_student_search_results ../data/output/search_results/UnansweredQuestions/dataset_code_public.json  ../data/datasets/public/AnsweredQuestions/dataset_code_public.json --k 5 --max_context_length 2000
	cd moulinette_pkg && ./moulinette-fedora evaluate_student_search_results ../data/output/search_results/UnansweredQuestions/dataset_docs_public.json  ../data/datasets/public/AnsweredQuestions/dataset_docs_public.json --k 5 --max_context_length 2000

pipeline:
	uv run python -m src pipline --dataset_path data/datasets/public/UnansweredQuestions/dataset_code_public.json --save_directory data/output/search_results/UnansweredQuestions --truth_dataset data/datasets/public/AnsweredQuestions/dataset_code_public.json --k 5 --chunk_size 2000
	uv run python -m src pipline --dataset_path data/datasets/public/UnansweredQuestions/dataset_docs_public.json --save_directory data/output/search_results/UnansweredQuestions --truth_dataset data/datasets/public/AnsweredQuestions/dataset_docs_public.json --k 5 --chunk_size 2000

full_pipeline:
	uv run python -m src full_pipeline data/datasets/private/UnansweredQuestions/dataset_code_private.json data/datasets/private/UnansweredQuestions/dataset_docs_private.json data/output/search_results2 data/datasets/private/AnsweredQuestions/dataset_code_private.json data/datasets/private/AnsweredQuestions/dataset_docs_private.json 5 2000

run: run_index run_search_dataset  run_answer_dataset run_my_evaluate run_evaluate

init:
	tar -xf data+moulinette.tar.xz
	unzip datasets_public.zip
	unzip moulinette.zip
	unzip vllm-0.10.1.zip
	mkdir data
	mkdir data/processed   
	mkdir data/datasets
	mkdir data/raw
	mkdir data/output

	mv ./public ./data/datasets/
	mv ./vllm-0.10.1 data/raw/

debug:
	uv run python -m pdb -m src \
		--functions_definition $(FUNCTIONS_DEFINITION) \
		--input $(INPUT) \
		--output $(OUTPUT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm *.zip
	rm -rf .mypy_cache

lint:
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --explicit-package-bases

lint-strict:
	uv run flake8 src/
	uv run mypy src/ --strict