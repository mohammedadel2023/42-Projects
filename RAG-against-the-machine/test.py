# from langchain_unstructured import UnstructuredLoader
# from unstructured.cleaners.core import clean_extra_whitespace
# from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PythonLoader
import pickle
import bm25s

# file_path = "./disagg_overhead_benchmark.sh"
# file_path = "./source.py"
# loader = UnstructuredLoader(file_path,
#                            chunking_strategy="basic",
#                            post_processors=[clean_extra_whitespace],
#                            max_characters=500,
#                            include_orig_elements=True)
#
# docs = loader.load()


# print(type(docs[1]))
# for id, doc in enumerate(docs):
#    print(f"The content of {id} doc is:\n")
#    print(f"The content: {doc.page_content}")
#    print("\n\n=====================================\n\n")
# loader = PythonLoader(
#     file_path=file_path,
# )
#
# docs = loader.load()
# python_splitter = RecursiveCharacterTextSplitter.from_language(
#     language=Language.PYTHON,
#     chunk_size=500)
#
#
# docs = python_splitter.split_documents(docs)
# print(len(docs))  # list[langchain_document]
# print(docs[3])
# print(docs[5].page_content)
# print(docs[5].metadata["source"])

with open("data/processed/retriever.pkl", "rb") as f:
    ret_saver = pickle.load(f)
with open("data/processed/chunks_lookup.pkl", "rb") as f:
    chunks_lookup = pickle.load(f)

retriever = ret_saver["bm25_model"]
query = "What activation formats does the fused batched MoE layer return in vLLM?"

results, scores = retriever.retrieve(bm25s.tokenize(query), k=10)
print("the result")
print(results)
print(f"the result type is :{type(results)}")
print("the scores")
print(scores)
print(f"the scores type is :{type(scores)}")
for i in results[0]:
    print(f"the rang {i} chunk source  is: {chunks_lookup[i].metadata}")
    print(f"the content of it is: {chunks_lookup[i].page_content}")
