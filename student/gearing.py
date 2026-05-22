import bm25s
from .models import RagDataset, MinimalSource, MinimalAnswer
from .models import MinimalSearchResults, StudentSearchResults
from .models import AnsweredQuestion, StudentSearchResultsAndAnswer
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from typing import Any

MODEL_NAME = "Qwen/Qwen3-0.6B"


def searcher(query: str, k: int = 5) -> tuple[list[dict[str, Any]], list[Any]]:
    bmodel = bm25s.BM25.load("data/processed/bm25_index", load_corpus=True)

    query_tokens = bm25s.tokenize(query)
    results, scores = bmodel.retrieve(query_tokens, k=k)

    return [results[0, i] for i in range(k)], [scores[0, i] for i in range(k)]


def searcher_ds(unanswered: RagDataset, k: int) -> StudentSearchResults:
    answered = list()
    for q in tqdm(unanswered.rag_questions, "searching..."):
        tmp, _ = searcher(q.question, k)
        answered.append(
            MinimalSearchResults(
                question_id=q.question_id,
                question=q.question,
                retrieved_sources=[
                    MinimalSource(
                        file_path=t["filepath"],
                        first_character_index=t["first"],
                        last_character_index=t["last"],
                        text=t["text"],
                    )
                    for t in tmp
                ],
            )
        )
    return StudentSearchResults(search_results=answered, k=k)


def answerer(sources: dict[str, Any], query: str) -> Any:

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype="auto", device_map="auto"
    )

    prompt = f"""Sources: {sources}
        Query: {query}
        Answer in one sentence:"""
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(**model_inputs,  # type: ignore[misc]
                                   max_new_tokens=32768)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    # thinking_content = tokenizer.decode(output_ids[:index],
    # skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(
        output_ids[index:], skip_special_tokens=True
    )
    if isinstance(content, str):
        content.strip('\n')
    return content


def answerer_ds(answered: RagDataset, k: int
                ) -> StudentSearchResultsAndAnswer:
    minimal_list = list()
    for a in tqdm(answered.rag_questions, "answering..."):
        if isinstance(a, AnsweredQuestion):
            answer = answerer(a.sources, a.question)
            a.answer = answer
            minimal_list.append(
                MinimalAnswer(
                    question_id=a.question_id,
                    question=a.question,
                    retrieved_sources=a.sources,
                    answer=answer,
                )
            )
    return StudentSearchResultsAndAnswer(search_results=minimal_list, k=k)
