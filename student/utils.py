from .chunking import chunking
import bm25s # type: ignore
import os
import json
from llm_sdk import Small_LLM_Model
import numpy as np
from typing import Any
from tqdm import tqdm


def index(max_chunk_size: int = 2000) -> None:
    corpus, chunks = chunking(max_chunk_size, int(max_chunk_size / 5))

    corpus_tokens = bm25s.tokenize([c["text"] for c in corpus], stopwords="en")
    bmodel = bm25s.BM25(corpus=corpus)
    bmodel.index(corpus_tokens)

    bmodel.save("data/processed/bm25_index")
    os.makedirs("data/processed/chunks", exist_ok=True)
    with open("data/processed/chunks/all_chunks.json", 'w') as f:
        json.dump([c.model_dump() for c in chunks], f, indent=4)
    print("Ingestion complete! Indices saved under data/processed/")


def search(query: str, k: int = 5, answer=False) -> None | list[dict[str, Any]]:
    bmodel = bm25s.BM25.load("data/processed/bm25_index", load_corpus=True)

    print(query)
    query_tokens = bm25s.tokenize(query)

    results, scores = bmodel.retrieve(query_tokens, k=k)

    for i in range(results.shape[1]):
        doc, score = results[0, i], scores[0, i]
        if not answer:
            print(f"Rank {i+1} (score: {score:.2f}): {doc['filepath']} ({doc['first']} - {doc['last']})\n")
    if answer:
        return [results[0, i] for i in range(k)]


def search_db():
    ...


def answer(query: str, k: int = 5) -> None:
    sources = search(query, k, True)
    sources_text = str()
    if sources:
        for s in sources:
            sources_text += s["text"]
            if s != sources[-1]:
                sources_text += '\n'
    # print(sources_text)
    if not sources:
        return

    llm = Small_LLM_Model(device="cpu")
    tokens = llm.encode(f"""Sources: {sources_text}
        Query: {query}
        Answer:"""
    ).cpu().detach().numpy()[0].tolist()

    res = str()
    for _ in tqdm(range(35), "generating..."):
        logits = llm.get_logits_from_input_ids(tokens)
        token_id = int(np.argmax(logits))
        if '\n' in llm.decode(token_id):
            break
        tokens.append(token_id)
        res += llm.decode(token_id)
    print(res)
