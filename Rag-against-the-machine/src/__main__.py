from rag_against_the_machine import (
    do_index_handler, do_search_handler, do_search_dataset_handler,
    answer_handler, answer_dataset_handler, evaluate_handler, pipeline,
    full_pipeline
)


if __name__ == "__main__":
    try:
        import fire
        fire.Fire({
            "index": do_index_handler,
            "search": do_search_handler,
            "search_dataset": do_search_dataset_handler,
            "answer": answer_handler,
            "answer_dataset": answer_dataset_handler,
            "evaluate": evaluate_handler,
            "pipeline": pipeline,
            "full_pipeline": full_pipeline})
    except Exception as e:
        print(e)
