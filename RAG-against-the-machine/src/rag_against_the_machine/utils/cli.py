from ..indexing import indexer
from ..helper import (chunk_types, TruthQuestionNotFound, StudentSearchResults,
                      llm_engin, Truth_question,
                      MinimalSource, retrieval_type)
from ..retrieving import retriever
from ..modeling import LLM
from .json_handling import json_handler
from pathlib import Path
from pydantic import Field


def do_index_handler(max_chunk_size: int = 2000,
                     faiss_index: bool = False) -> None:
    """
    THis func run the logic of chunking all file and storing them
    using pickle

    Args:
        chunk_size (int): The size of chunks to create
        faiss_index (bool): Whether to build a FAISS index
    """

    indexer_obj = indexer(chunk_size=max_chunk_size)
    indexer_obj.start(t=chunk_types.Code)
    indexer_obj.start(t=chunk_types.Doc)
    if faiss_index:
        indexer_obj.do_save(faiss_index=True)
    else:
        indexer_obj.do_save()


def do_search_handler(query: str = Field(min_length=5),
                      k: int = Field(default=5, ge=1),
                      type: retrieval_type = retrieval_type.Bm25) -> None:
    """
    This function apply the logic of retrieving on the provided query

    Returns:
        query (str): the query used to search based on.
        k (int): number of retrieved chunks
    """

    retriever_obj = retriever()
    res = retriever_obj.query(query, k=k)
    sum_scores = sum(res.scores)
    if sum_scores == 0:
        print("-The query is unsensible or use unreqular way to ask about the")
        print("topic pls try again with different query")
    else:
        for i in range(k):
            st_index = res.retrieved_sources[i].first_character_index
            end_index = res.retrieved_sources[i].last_character_index
            print(res.retrieved_sources[i].file_path, end="")
            print(f" [s:{st_index},e:{end_index}] score: {res.scores[i]:.2f}")


def do_search_dataset_handler(dataset_path: str, save_directory: str,
                              k: int = Field(default=5, ge=1),
                              t: retrieval_type = retrieval_type.Bm25) -> None:
    """
    This function apply the logic of retrieving on the provided files

    Retruns:
        dataset_path (str): the file for the student search dataset path
        save_directory (str): the dir to save the data in.
        k (int): number of retrieved chunks
    """
    handler = json_handler()
    data = handler.read_RagDataset(dataset_path).rag_questions
    search_results = []
    retriever_obj = retriever(t=t)
    name = Path(dataset_path).name
    unsensible = []
    for q in data:
        if len(q.question) > 5:
            res = retriever_obj.query(
                                  q.question, q.question_id,
                                  k,
                                  t)
            if sum(res.scores) == 0:
                unsensible.append(res.question_id)
            else:
                search_results.append(res)
    stSearchResults = StudentSearchResults(search_results=search_results,
                                           k=k)
    handler.write_searchResult(stSearchResults,
                               save_directory,
                               name)
    if len(unsensible) > 0:

        print(f"- Note that unsensible Q's with id's {unsensible}\
 are ignored")
        print("- Unsensible question: when the query is unsensible or\
 use unreqular way to ask about the topic")


def answer_handler(query: str = Field(min_length=5),
                   engin: llm_engin = llm_engin.transformers,
                   k: int = Field(default=5, ge=1)) -> None:
    """
    This func apply the full logic index (if needed) -> retrieving ->
    generation on the provided query.

    Args:
        query (str):the query used to answer based on.
        engin (llm_engin.llama): engin type to use during inferencing.
        k (int): number of retrieved chunks
    """
    retriever_obj = retriever()
    ret_Res = retriever_obj.query(query, k=k)
    sum_scores = sum(ret_Res.scores)
    if sum_scores == 0:
        print("-The query is unsensible or use unreqular way to ask about the")
        print("topic pls try again with different query")
    else:
        model = LLM(type=engin)
        output = model.generate([ret_Res], k=k)
        print(output.search_results[0].answer)


def answer_dataset_handler(student_search_results_path: str,
                           save_directory: str,
                           engin: llm_engin = llm_engin.transformers) -> None:
    """
    This func apply the full logic index (if needed) -> retrieving ->
    generation on the file provided.

    Args:
        results_path (str): the path for the result StudentSearchResults
        save_directory (str): the dir where to save the result.
        engin (llm_engin.llama): engin type to use during inferencing.
    """
    handler = json_handler()
    data = handler.read_search_results(student_search_results_path)
    search_results = data.search_results
    k = data.k
    model = LLM(type=engin)
    output = model.generate(search_results, k=k)
    name = "answer" + Path(student_search_results_path).name
    handler.write_answerResult(output, path=save_directory,
                               name=name)


def get_true_q(true_q: list[Truth_question], q_id: str) -> Truth_question:
    """
    This func return the true question with rhe same id provided.

    Args:
        true_q (list[Truth_question]): list of posible true questions.
        q_id (str): id provided.

    Returns:
        Truth_question: the turth qustion
    """
    for q in true_q:
        if q.question_id == q_id:
            return q
    raise TruthQuestionNotFound(f"The question with id {q_id} does not exist")


# def matched(srcs: list[MinimalSource], true_q: Truth_question) -> bool:
#     """
#     This function check if there are any retrieved chunk matched the correct
#     one include the data needed.
#
#     Args:
#         srcs (list[MinimalSource]): list of MinimalSource format.
#         true_q (Truth_question): The truth question to checked based on.
#
#     Returns:
#         bool: true if matched other wise false
#     """
#     for src in srcs:
#         t_source = true_q.sources[0]
#         if src.file_path == t_source.file_path:
#             a_len = src.last_character_index - src.first_character_index
#             b_len = (t_source.last_character_index -
#                      t_source.first_character_index)
#             intersection = (min(src.last_character_index,
#                                 t_source.last_character_index) -
#                             max(src.first_character_index,
#                                 t_source.first_character_index))
#             union = a_len + b_len - intersection
#             iou = intersection / union
#             if iou >= 0.05:
#                 return True
#     return False
#
#
# def evaluate_handler(student_search_results_path: str,
#                      dataset_path: str) -> None:
#     """
#     This function take the StudentSearchResults and fine the Recall@k.
#
#     Args:
#         search_results_path (str): the path to StudentSearchResults file.
#         dataset_path (str): path for the truth dataset.
#     """
#     handler = json_handler()
#     data = handler.read_search_results(student_search_results_path)
#     search_results = data.search_results
#     k = data.k
#     truth = handler.read_truth(dataset_path)
#     counter = 0
#     com = 0
#     for q in search_results:
#         true_q = get_true_q(truth.rag_questions, q.question_id)
#         com += 1 if matched(q.retrieved_sources, true_q) else 0
#         counter += 1
#     print(f"Recall{k}k:\n{com/counter}")


def normalize_path(p: str) -> str:
    """Converts Windows paths to POSIX and removes leading relative symbols."""
    # Convert \ to / and strip leading ./ if present
    clean_p = Path(p).as_posix().lstrip("./")
    return clean_p


def matched(srcs: list[MinimalSource], true_q: Truth_question) -> bool:
    """
    Checks if any retrieved chunk matches any ground truth source
    by file path and character offset IoU >= 0.05.
    """
    for src in srcs:
        src_path = normalize_path(src.file_path)

        for t_source in true_q.sources:
            truth_path = normalize_path(t_source.file_path)

            if (src_path == truth_path or
                    src_path.endswith(truth_path) or
                    truth_path.endswith(src_path)):
                a_len = src.last_character_index - src.first_character_index
                b_len = (t_source.last_character_index -
                         t_source.first_character_index)

                inter_start = max(src.first_character_index,
                                  t_source.first_character_index)
                inter_end = min(src.last_character_index,
                                t_source.last_character_index)
                intersection = max(0, inter_end - inter_start)

                union = a_len + b_len - intersection
                if union > 0:
                    iou = intersection / union
                    if iou >= 0.05:
                        return True
    return False


def evaluate_handler(student_search_results_path: str,
                     dataset_path: str) -> None:
    handler = json_handler()
    data = handler.read_search_results(student_search_results_path)
    search_results = data.search_results
    k = data.k
    truth = handler.read_truth(dataset_path)

    counter = 0
    com = 0
    for q in search_results:
        true_q = get_true_q(truth.rag_questions, q.question_id)
        if matched(q.retrieved_sources, true_q):
            com += 1
        counter += 1

    recall = com / counter if counter > 0 else 0.0
    print(f"Recall@{k}: {recall:.4f}")


def pipeline(
            dataset_path: str, save_directory: str,
            truth_dataset: str,
            k: int = Field(default=5, ge=5),
            chunk_size: int = 2000,
            ) -> None:
    """
    This function run the full pipline from index -> search -> evaluate.

    Args:
        chunk_size (int): the size of the chunk.
        dataset_path (str): The path where dataset want to be used to retrieve
                            based on.
        save_directory (str): where to save the result output.
        k (int): numbrt pf retrieved chunks.
    """
    do_index_handler(chunk_size)
    do_search_dataset_handler(dataset_path, save_directory, k)
    name = Path(dataset_path).name
    save_dir = Path(save_directory)
    file_path = save_dir / name
    evaluate_handler(str(file_path), truth_dataset)


def full_pipeline(
            dataset_path1: str, dataset_path2: str,
            save_directory: str,
            truth_dataset1: str, truth_dataset2: str,
            k: int = Field(default=5, ge=5),
            chunk_size: int = 2000,
            ) -> None:
    """
    This function run the full pipline from index -> search -> evaluate.

    Args:
        chunk_size (int): the size of the chunk.
        dataset_path (str): The path where dataset want to be used to retrieve
                            based on.
        save_directory (str): where to save the result output.
        k (int): numbrt pf retrieved chunks.
    """
    pipeline(dataset_path1, save_directory, truth_dataset1, k, chunk_size)
    pipeline(dataset_path2, save_directory, truth_dataset2, k, chunk_size)
