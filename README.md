_This project has been created as part of the 42 curriculum by msuizu_

### **--- Description ---**

RAG against the machine is a python project about Retrieval Augmented Generation. that’s it.

### **--- Instructions ---**

to check with flake8 and mypy:\
`make lint`

uv sync:\
`make install`

for indexing to create a searchable database:\
`uv run python -m student index --max_chunk_size 2000`

to answer a question with Qwen3-0.6B:\
`uv run python -m student answer "How to configure OpenAI server?" --k 10`

to create a dataset from json file containing questions:\
`uv run python -m student search_dataset --dataset_path data/datasets/public/UnansweredQuestions/dataset_code_public.json --k 10 --save_directory data/output/search_results`

to test the code with the moulinette provided:\
`./moulinette_pkg/moulinette-ubuntu evaluate_student_search_results --student_answer_path data/output/search_results/dataset_docs_public.json --dataset_path data/datasets/public/AnsweredQuestions/dataset_docs_public.json --k 10 --max_context_length 2000`

answer each question from the dataset created previously:\
`uv run python -m student answer_dataset --student_search_results_path data/output/search_results/dataset_docs_public.json --save_directory data/output/search_results_and_answer`

### **--- Resources ---**

[Qwen3-0.6B from Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)

[bm25s module](https://github.com/xhluca/bm25s)

[semchunk module](https://pypi.org/project/semchunk/)

AI was used for debugging, and helping understanding the concept.

### **--- System architecture ---**

RAG is organized in this pipeline:

* Chunking (see Chunking strategy part)
* Retrieving (see Retrieval method)
* Semantic search
* Answer generation

### **--- Chunking strategy ---**

all files from data/raw/vllm-0.10.1 are processed by creating chunks of 2000 characters max by default with a small overlaping to keep context.
the type of file is taken account in the process, for example, file code must be chunked by function definition, while markdown file are chunked by format.
this provides for the retrieving part better indexing.

### **--- Retrieval method ---**

BM25 or TF-IDF are ranking algorithm used to estimate the relevance of documents to a given search query.
BM25 is the ranking function used because 
it looks up for the recurrency of words (TF), the importance of them (IDF), which are the fundation of TF-IDF.
BM25, besides these parameters, takes also in count the documents length, which boosts the accuracy and this is why this method was prefered for this RAG

### **--- Performance analysis ---**

Recall@k: among chunks k returned, is the correct file inside ?
the subject's requirement is 5% of overlap between the returned chunk and the answer defined in `data/datasets/AnsweredQuestions`
by executing the moulinette, Recall@5 for docs is about 84%, while 55% is achieved for code.
the requirements for pass are 80% and 50% respectivly.

### **--- Design decisions ---**

* BM25 vs TF-IDF
BM25 was prefered for fiability concern

* Chunking
for text files, the function chunk() from semchunk module was choosed because it offers overlap possibility.
for code files, chunk() was associated with ast module to chunk by function and class definition

### **--- Challenges faced ---**

no real challenges were encountered, besides of course understand at first what the project is about, the main deal was how to make the AI answer properly without generating a full paragraph

### **--- Example usage ---**

#### **Files before**

`ls -l data/raw`\
total 11988\
drwxrwxr-x 15 student student 4096 Aug 19 00:27 vllm-0.10.1\
-rw-r--r-- 1 student student 12267696 Nov 2 22:21 vllm-0.10.1.zip\

#### **Indexing**

`uv run python -m student index --max_chunk_size 2000`\
Ingestion complete! Indices saved under data/processed/\
`ls -l data/processed`\
total 8\
drwxrwxr-x 4 student student 4096 Dec 9 10:09 bm25_index\
drwxrwxr-x 3 student student 4096 Dec 9 10:09 chunks

#### **Answer single query**

`uv run python -m student answer "How to configure OpenAI server?" --k 10`

#### **Showing datasets**

`ls -lR data/datasets/`\
data/datasets/:\
total 8\
drwxr-xr-x 2 student student 4096 Dec 8 22:38 AnsweredQuestions\
drwxr-xr-x 2 student student 4096 Dec 8 22:38 UnansweredQuestions\
data/datasets/AnsweredQuestions:\
total 132\
-rw-rw-r-- 1 student student 65238 Dec 8 22:38 dataset_code_public.json\
-rw-rw-r-- 1 student student 68817 Dec 8 22:38 dataset_docs_public.json\
data/datasets/UnansweredQuestions:\
total 40\
-rw-rw-r-- 1 student student 19217 Dec 8 22:38 dataset_code_public.json\
-rw-rw-r-- 1 student student 17525 Dec 8 22:38 dataset_docs_public.json

#### **Searching one dataset**

`uv run python -m student search_dataset
--dataset_path data/datasets/public/UnansweredQuestions/dataset_docs_public.json
--k 10
--save_directory data/output/search_results`\
Saved student_search_results to data/output/search_results/dataset_docs_public.json\
`ls -l data/output/search_results`\
total 4672\
-rw-rw-r-- 1 student student 4780742 Dec 9 10:14 dataset_docs_public.json

#### **Evaluate search results**

`./moulinette_pkg/moulinette-ubuntu evaluate_student_search_results
--student_answer_path data/output/search_results/dataset_docs_public.json
--dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
--k 10
--max_context_length 2000`\
Student data is valid: True\
Total number of questions: 100\
Total number of questions with sources: 100\
Total number of questions with student sources: 100\
Evaluation Results\
Questions evaluated: 100\
Recall@1: 0.450\
Recall@3: 0.590\
Recall@5: 0.650\
Recall@10: 0.720

#### **Answer the dataset**

`uv run python -m student answer_dataset
--student_search_results_path data/output/search_results/dataset_docs_public.json
--save_directory data/output/search_results_and_answer`\
Loaded 100 questions from data/output/search_results/dataset_docs_public.json\
Processed 100 of 100 questions\
Saved student_search_results_and_answer to data/output/search_results_and_answer/dataset_docs_public.json\
`ls -l data/output/search_results_and_answer`\
total 4688\
-rw-rw-r-- 1 student student 4798366 Dec 9 10:23 dataset_docs_public.json

### **--- Output ---**

#### **Search the dataset**

```"search_results": [
    {
        "question_id": "q1",
        "retrieved_sources": [
            {
                "file_path": "docs/serving/openai_compatible_server.md",
                "first_character_index": 9867,
                "last_character_index": 10100
            },
            {
                "file_path": "vllm/entrypoints/openai/api_server.py",
                "first_character_index": 267,
                "last_character_index": 400
            }
        ]
    }
],
"k": 10
```

#### **Answer the dataset**

```"search_results": [
    {
        "question_id": "q1",
        "retrieved_sources": [
            {
                "file_path": "docs/serving/openai_compatible_server.md",
                "first_character_index": 9867,
                "last_character_index": 10100
            },
            {
                "file_path": "vllm/entrypoints/openai/api_server.py",
                "first_character_index": 267,
                "last_character_index": 400
            }
        ],
        "answer": "To configure the OpenAI compatible server in vLLM..."
    }
],
"k": 10
```
