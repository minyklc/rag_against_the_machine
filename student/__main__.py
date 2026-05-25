#!/usr/bin/env python3
from .utils import evaluate, index, search, answer, search_ds, answer_ds
import fire


def main() -> None:
    """main program runned through Fire module"""
    fire.Fire(
        {
            "index": index,
            "search": search,
            "search_dataset": search_ds,
            "answer": answer,
            "answer_dataset": answer_ds,
            "evaluate": evaluate
        }
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("unexpected error:", e)
