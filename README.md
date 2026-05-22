uv run python -m student index --max_chunk_size 2000

uv run python -m student answer "How to configure OpenAI server?" --k 10

uv run python -m student search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory data/output/search_results

uv run python -m moulinette evaluate_student_search_results --student_answer_path data/output/search_results/dataset_docs_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json --k 10 --max_context_length 2000

uv run python -m student answer_dataset --student_search_results_path data/output/search_results/dataset_docs_public.json --save_directory data/output/search_results_and_answer