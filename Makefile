GOINFRE                        = $(HOME)/goinfre
export UV_CACHE_DIR            = $(GOINFRE)/.uv_cache
export UV_PROJECT_ENVIRONMENT  = $(GOINFRE)/.venv
export HF_HOME                 = $(GOINFRE)/.huggingface
export TORCH_HOME              = $(GOINFRE)/.torch
export XDG_CACHE_HOME          = $(GOINFRE)/.cache

PYTHON      = python3.10
VENV_DIR    = $(UV_PROJECT_ENVIRONMENT)
PIP         = $(VENV_DIR)/bin/pip
UV          = uv
UV_RUN      = $(UV) run python
MAIN        = -m student
MOULINETTE_BIN = ./moulinette/moulinette-ubuntu
EXAM_RETRIEVAL = ./exams_pkg/exams/scripts/exam_retrieval.sh
EXAM_ANSWER = ./exams_pkg/exams/scripts/exam_answer.sh
EXAM_EDGE = ./exams_pkg/exams/scripts/exam_edge_cases.sh

# Default single-query parameters (override: make answer Q="..." K=5)
Q   ?= What API endpoint does vLLM support for chat completions?
Q2  ?= How to configure OpenAI server?
Q3  ?= How do I enable prefix caching?
K   ?= 10

MODE                ?= bm25
MAX_CHUNK_SIZE      ?= 2000
MAX_CONTEXT_LENGTH  ?= 2000

# ── Datasets ─────────────────────────────────────────────────────────────────
UNANSWERED_DOCS = data/datasets/UnansweredQuestions/dataset_docs_public.json
UNANSWERED_CODE = data/datasets/UnansweredQuestions/dataset_code_public.json
ANSWERED_DOCS   = data/datasets/AnsweredQuestions/dataset_docs_public.json
ANSWERED_CODE   = data/datasets/AnsweredQuestions/dataset_code_public.json

SEARCH_OUT  = data/output/search_results
ANSWER_OUT  = data/output/search_results_and_answer

# ── Setup ────────────────────────────────────────────────────────────────────
install:
	mkdir -p $(GOINFRE)
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install uv
	$(UV) sync --python 3.10

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache"  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

fclean: clean
	rm -rf $(VENV_DIR)
	rm -rf $(UV_CACHE_DIR)
	rm -rf data/processed
	rm -rf data/output

lint:
	$(UV) run flake8
	$(UV) run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# ── Single-query commands ───────────────────────────────────────────────
index:
	$(UV_RUN) $(MAIN) index --max_chunk_size $(MAX_CHUNK_SIZE)

search:
	$(UV_RUN) $(MAIN) search "$(Q)" --k $(K)

answer:
	$(UV_RUN) $(MAIN) answer "$(Q)" --k $(K)

run: answer

debug:
	$(UV_RUN) -m pdb $(MAIN) answer "What is vLLM?"

# ── Dataset batch: search ────────────────────────────────────────────────────
search-docs:
	$(UV_RUN) $(MAIN) search_dataset \
		--dataset_path $(UNANSWERED_DOCS) \
		--k $(K) \
		--save_directory $(SEARCH_OUT)

search-code:
	$(UV_RUN) $(MAIN) search_dataset \
		--dataset_path $(UNANSWERED_CODE) \
		--k $(K) \
		--save_directory $(SEARCH_OUT)

search-dataset: search-docs search-code

# ── Dataset batch: answer ────────────────────────────────────────────────────

answer3:
	$(UV_RUN) $(MAIN) answer "$(Q)" --k $(K)
	$(UV_RUN) $(MAIN) answer "$(Q2)" --k $(K)
	$(UV_RUN) $(MAIN) answer "$(Q3)" --k $(K)
	
answer-docs:
	$(UV_RUN) $(MAIN) answer_dataset \
		--student_search_results_path $(SEARCH_OUT)/dataset_docs_public.json \
		--save_directory $(ANSWER_OUT)

answer-code:
	$(UV_RUN) $(MAIN) answer_dataset \
		--student_search_results_path $(SEARCH_OUT)/dataset_code_public.json \
		--save_directory $(ANSWER_OUT)

answer-dataset: answer-docs answer-code

# ── Local evaluation via student CLI (recall@1,3,5,10) ───────────────────────
evaluate-docs:
	$(UV_RUN) $(MAIN) evaluate --mode docs

evaluate-code:
	$(UV_RUN) $(MAIN) evaluate --mode code

evaluate: evaluate-docs evaluate-code

# ── Official moulinette evaluation (from moulinette README) ─────────────────
moulinette-docs:
	$(MOULINETTE_BIN) evaluate_student_search_results \
		$(SEARCH_OUT)/dataset_docs_public.json \
		$(ANSWERED_DOCS) \
		--k $(K) \
		--max_context_length $(MAX_CONTEXT_LENGTH)

moulinette-code:
	$(MOULINETTE_BIN) evaluate_student_search_results \
		$(SEARCH_OUT)/dataset_code_public.json \
		$(ANSWERED_CODE) \
		--k $(K) \
		--max_context_length $(MAX_CONTEXT_LENGTH)

moulinette: moulinette-docs moulinette-code

pipeline: index search-dataset moulinette

# ── Exam scripts (correction flow) ──────────────────────────────────────────
exam-retrieval:
	$(EXAM_RETRIEVAL) \
		--student-path . \
		--moulinette-path ./moulinette_pkg/moulinette-ubuntu \
		--module-name student

exam-answer:
	$(EXAM_ANSWER) \
		--student-path . \
		--moulinette-path ./moulinette_pkg/moulinette-ubuntu \
		--module-name student

exam-edge:
	$(EXAM_EDGE) --student-path . --module-name student

pipeline-exam: exam-retrieval

.PHONY: install clean fclean lint \
		index search answer run debug \
		search-docs search-code search-dataset \
		answer-docs answer-code answer-dataset \
		evaluate-docs evaluate-code evaluate \
		moulinette-docs moulinette-code moulinette \
		exam-retrieval exam-answer exam-edge \
		pipeline pipeline-exam pipeline-full
