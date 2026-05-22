from .chunking import chunking
import bm25s
import os
import json
from .models import UnansweredQuestion, AnsweredQuestion
from .models import RagDataset, MinimalSource
from .gearing import searcher, searcher_ds, answerer, answerer_ds


MODEL_NAME = "Qwen/Qwen3-0.6B"


def index(max_chunk_size: int = 2000) -> None:
    corpus, chunks = chunking(max_chunk_size, int(max_chunk_size / 5))

    corpus_tokens = bm25s.tokenize([c["text"] for c in corpus], stopwords="en")
    bmodel = bm25s.BM25(corpus=corpus)
    bmodel.index(corpus_tokens)

    bmodel.save("data/processed/bm25_index")
    os.makedirs("data/processed/chunks", exist_ok=True)
    with open("data/processed/chunks/all_chunks.json", "w") as f:
        json.dump([c.model_dump() for c in chunks], f, indent=4)
    print("Ingestion complete! Indices saved under data/processed/")


def search(query: str, k: int = 5) -> None:
    r, s = searcher(query, k)
    for i in range(k):
        print(
            f"Rank {i + 1} (score: {s[i]:.2f}): \
            {r[i]['filepath']} ({r[i]['first']} - {r[i]['last']})\n"
        )


def search_ds(
    dataset_path: str = "data/datasets/UnansweredQuestions\
/dataset_docs_public.json",
    k: int = 5,
    save_directory: str = "data/output/search_results",
) -> None:

    filename = dataset_path.split("/")[-1]
    with open(dataset_path, "r") as f:
        unanswered_data = json.load(f)["rag_questions"]

    rag_ds = RagDataset(
        rag_questions=[
            UnansweredQuestion(
                question_id=u["question_id"], question=u["question"]
            )
            for u in unanswered_data
        ]
    )
    unanswered = searcher_ds(rag_ds, k)

    os.makedirs(save_directory, exist_ok=True)
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += filename

    with open(save_directory, "w") as f:
        json.dump(unanswered.model_dump(mode="json"), f, indent=4)
    print(f"Saved student_search_results to {save_directory}")


def answer(query: str, k: int = 5) -> None:
    sources, _ = searcher(query, k)
    answer = answerer(sources, query)
    print(answer)


def answer_ds(
    student_search_results_path: str = "data/output/search_results\
/dataset_docs_public.json",
    save_directory: str = "data/output/search_results_and_answer",
) -> None:

    filename = student_search_results_path.split("/")[-1]
    with open(student_search_results_path, "r") as f:
        data = json.load(f)
        answered_data = data["search_results"]
        k = data["k"]

    rag_ds = RagDataset(
        rag_questions=[
            AnsweredQuestion(
                question_id=a["question_id"],
                question=a["question"],
                sources=[
                    MinimalSource(
                        file_path=s["file_path"],
                        first_character_index=s["first_character_index"],
                        last_character_index=s["last_character_index"],
                        text=s["text"],
                    )
                    for s in a["retrieved_sources"]
                ],
                answer="",
            )
            for a in answered_data
        ]
    )

    answered = answerer_ds(rag_ds, k)
    os.makedirs(save_directory, exist_ok=True)
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += filename

    with open(save_directory, "w") as f:
        json.dump(answered.model_dump(mode="json"), f, indent=4)
