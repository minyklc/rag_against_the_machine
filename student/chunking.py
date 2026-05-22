#!/usr/bin/env python3
from glob import glob
from .models import MinimalSource
import os
from semchunk import chunk
import ast
from typing import Any
from tqdm import tqdm


def chunking(
    size: int, overlap: int
) -> tuple[list[dict[str, Any]], list[MinimalSource]]:
    corpus = list()
    chunks = list()
    for thing in tqdm(
        glob("data/raw/vllm-0.10.1/**", recursive=True), "chunking..."
    ):
        # print(thing)
        if os.path.isfile(thing):
            if thing.endswith(".md") or thing.endswith(".txt"):
                with open(thing, "r") as f:
                    text = f.read()
                    tmp = chunk(text, size, len, overlap=overlap)
                    balise = 0
                    for t in tmp:
                        new_chunk, new_corp, balise = create_obj(
                            thing, text, t, balise
                        )
                        chunks.append(new_chunk)
                        corpus.append(new_corp)

            elif thing.endswith(".py"):
                with open(thing, "r") as f:
                    text = f.read()
                    lines = text.splitlines()
                    covered: set[Any] = set()
                    aster = ast.parse(text)
                    for node in ast.walk(aster):
                        if isinstance(node, (ast.ClassDef)):
                            if isinstance(node.end_lineno, int):
                                node.end_lineno -= 1
                            node_text = "\n".join(
                                lines[node.lineno - 1:node.end_lineno]
                            )
                            tmp = chunk(node_text, size, len, overlap=overlap)
                            balise = 0
                            for t in tmp:
                                new_chunk, new_corp, balise = create_obj(
                                    thing, text, t, balise
                                )
                                chunks.append(new_chunk)
                                corpus.append(new_corp)
                            if node.end_lineno:
                                if isinstance(node.end_lineno, int):
                                    node.end_lineno += 1
                                covered.update(
                                    range(node.lineno - 1, node.end_lineno)
                                )
                    for node in ast.walk(aster):
                        if (
                            isinstance(
                                node, (ast.FunctionDef, ast.AsyncFunctionDef)
                            )
                            and lines[node.lineno] != "#"
                        ):
                            if isinstance(node.end_lineno, int):
                                node.end_lineno -= 1
                            node_text = "\n".join(
                                lines[node.lineno - 1:node.end_lineno]
                            )
                            tmp = chunk(node_text, size, len, overlap=overlap)
                            balise = 0
                            for t in tmp:
                                new_chunk, new_corp, balise = create_obj(
                                    thing, text, t, balise
                                )
                                chunks.append(new_chunk)
                                corpus.append(new_corp)
                            if isinstance(node.end_lineno, int):
                                node.end_lineno += 1
                            if node.end_lineno:
                                covered.update(
                                    range(node.lineno - 1, node.end_lineno)
                                )

                    lines_left = [
                        line
                        for i, line in enumerate(lines)
                        if i not in covered
                    ]
                    if lines_left:
                        part = str()
                        for li in lines:
                            if li != "#":
                                part += li
                                part += '\n'
                            elif part and li == "#":
                                tmp = chunk(part, size, len, overlap=overlap)
                                balise = 0
                                for t in tmp:
                                    new_chunk, new_corp, balise = create_obj(
                                        thing, text, t, balise
                                    )
                                    chunks.append(new_chunk)
                                    corpus.append(new_corp)
                                part = str()
                        if part:
                            tmp = chunk(part, size, len, overlap=overlap)
                            balise = 0
                            for t in tmp:
                                new_chunk, new_corp, balise = create_obj(
                                    thing, text, t, balise
                                )
                                chunks.append(new_chunk)
                                corpus.append(new_corp)
    return corpus, chunks


def create_obj(
    filepath: str, src: str, text: Any, balise: int
) -> tuple[MinimalSource, dict[str, Any], int]:
    if not src.endswith('\n'):
        src += '\n'
    start = src.find(text)
    end = start + len(text)
    chunk = MinimalSource(
        file_path=filepath,
        first_character_index=start,
        last_character_index=end,
        text=text,
    )
    corp = {
        "filepath": filepath,
        "first": chunk.first_character_index,
        "last": chunk.last_character_index,
        "text": text,
    }
    return chunk, corp, start + 1
