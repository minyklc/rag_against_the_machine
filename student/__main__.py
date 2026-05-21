#!/usr/bin/env python3
from .utils import index, search, answer, search_db
import fire


def main() -> None:
    fire.Fire({
            "index": index,
            "search": search,
            "search_database": search_db,
            "answer": answer
        })


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('unexpected error:', e)

# import bm25s # type: ignore
# # import Stemmer  # optional: for stemming

# # Create your corpus here
# corpus = [
#     "a cat is a feline and likes to purr",
#     "a dog is the human's best friend and loves to play",
#     "a bird is a beautiful animal that can fly",
#     "a fish is a creature that lives in water and swims",
# ]

# # Tokenize the corpus and only keep the ids (faster and saves memory)
# corpus_tokens = bm25s.tokenize(corpus, stopwords="en")

# # Create the BM25 model and index the corpus
# bmodel = bm25s.BM25()
# bmodel.index(corpus_tokens)

# # Query the corpus
# query = "does the fish purr like a cat?"
# query_tokens = bm25s.tokenize(query)

# # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k).
# # To return docs instead of IDs, set the `corpus=corpus` parameter.
# results, scores = bmodel.retrieve(query_tokens, k=2, corpus=corpus)

# for i in range(results.shape[1]):
#     doc, score = results[0, i], scores[0, i]
#     print(f"Rank {i+1} (score: {score:.2f}): {doc}")

# # You can save the arrays to a directory...
# bmodel.save("data_index")

# # You can save the corpus along with the model
# # bmodel.save("animal_index_bm25", corpus=corpus)

# # ...and load them when you need them
# # import bm25s
# # bmodel2 = bm25s.BM25.load("data_index", load_corpus=True)
# # result, score = bmodel2.retrieve(query_tokens, k=2, corpus=corpus)
# # for i in range(result.shape[1]):
# #     doc, scor = result[0, i], score[0, i]
# #     print(f"Rank {i+1} (score: {scor:.2f}): {doc}")
# # set load_corpus=False if you don't need the corpus