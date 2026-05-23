#!/usr/bin/env python3
from pydantic import BaseModel, Field, computed_field
import uuid
from typing import List


class MinimalSource(BaseModel):
    """MinimalSource model represents a minimal source of information"""
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str


class UnansweredQuestion(BaseModel):
    """UnansweredQuestion model represent an unanswered question"""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """AnsweredQuestion model represent an answered question"""
    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """The RagDataset model represents a dataset of RAG questions:"""
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """The MinimalSearchResults model represent the search results"""
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]

    @computed_field
    def question_str(self) -> str:
        return self.question


class MinimalAnswer(MinimalSearchResults):
    """The MinimalAnswer model represent the search results and an answer"""
    answer: str


class StudentSearchResults(BaseModel):
    """The StudentSearchResults model represent search results"""
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    """The StudentSearchResultsAndAnswer model represent
    search results with answers"""
    search_results: List[MinimalAnswer]  # type: ignore[assignment]
