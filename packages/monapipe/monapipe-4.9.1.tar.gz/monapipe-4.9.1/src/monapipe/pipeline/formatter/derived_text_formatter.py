# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import math
import random
from typing import Any, Callable, Dict, List, Union

from spacy.language import Language
from spacy.tokens import Doc, Token

from monapipe.pipeline.formatter.formatter import Formatter
from monapipe.pipeline.methods import (
    deserialize_config_param,
    serialize_config_param,
)


@Language.factory(
    "derived_text_formatter",
    assigns=Formatter.assigns,
    default_config={
        "column_names": [],
        "column_names_plus": [],
        "column_funcs": {},
        "column_delimiter": "\t",
        "text_operation": "replace",
        "text_level": "doc",
        "text_segment_length": 1000,
        "text_element": serialize_config_param({"text_element": lambda token: token.pos_}),
        "text_percentage": 0.1, # not used for 'replace' operation, see docstring documentation of `derived_text_formatter`
        "text_keep_start": 0.0, # not used for 'replace' operation, see docstring documentation of `derived_text_formatter`
    },
)

def derived_text_formatter(
    nlp: Language,
    name: str,
    column_names: List[str],
    column_names_plus: List[str],
    column_funcs: Union[str, Dict[str, Callable[[Token], Any]]],
    column_delimiter: str,
    text_operation: str,
    text_level: str,
    text_segment_length: int,
    text_element: str,
    text_percentage: float,
    text_keep_start: float,
) -> Any:
    r"""Spacy component implementation.
    Create a derived text representation of the document based on the specified columns.
    
    Args:
        nlp: Spacy object.
        name: Component name.
        column_names: Ignored. This parameter exists only for compatibility with `Formatter`.
        column_names_plus: Ignored. This parameter exists only for compatibility with `Formatter`.
        column_funcs: Ignored. This parameter exists only for compatibility with `Formatter`.
        column_delimiter: The column separator.
            If "\s+", a flexible number (at least 2) of spaces is inserted.
            Otherwise, the columns are concatenated using the given delimiter.
        text_operation: The operation to perform on the text (e.g., "replace", "randomize", "keep").
        text_level: The level at which the operation is applied (e.g., "doc", "sent", "clause", 
            "segment") in operation "replace" and "randomize".
        text_segment_length: The length of segments to be processed in the operation in operation 
            "replace" and "randomize" if `text_level` is "segment".
        text_element: A function that takes a token and returns the text element to be used in 
            the operation "replace".
        text_percentage: The percentage of the text to be affected by the operation "replace" 
            and "keep".
        text_keep_start: The starting point (as a fraction of the text length) for the 
            "keep" operation.

    Returns:
        `DerivedTextFormatter`: The initialized component instance.
    """
    return DerivedTextFormatter(
        nlp,
        column_names=column_names,
        column_names_plus=column_names_plus,
        column_funcs=column_funcs,
        column_delimiter=column_delimiter,
        text_operation=text_operation,
        text_level=text_level,
        text_segment_length=text_segment_length,
        text_element=text_element,
        text_percentage=text_percentage,
        text_keep_start=text_keep_start,
    )

class DerivedTextFormatter(Formatter):
    """The class `DerivedTextFormatter`."""

    def __init__(
        self,
        nlp: Language,
        column_names: List[str],
        column_names_plus: List[str],
        column_funcs: Union[str, Dict[str, Callable[[Token], Any]]],
        column_delimiter: str,
        text_operation: str,
        text_level: str,
        text_segment_length: int,
        text_element: Union[str, Dict[str, Callable[[Token], Any]]],
        text_percentage: float,
        text_keep_start: float,
    ):

        super().__init__(nlp, 
                         column_names=column_names,
                         column_names_plus=column_names_plus,
                         column_funcs=column_funcs,
                         column_delimiter=column_delimiter,
                         text_operation=text_operation,
                         text_level=text_level,
                         text_segment_length=text_segment_length,
                         text_element=text_element,
                         text_percentage=text_percentage,
                         text_keep_start=text_keep_start)
        self.text_operation = text_operation

        self.text_element = deserialize_config_param(text_element)["text_element"]

        # parameters for "replace", "keep"
        self.text_percentage = text_percentage
        # parameters for "replace", "randomize"
        self.text_level = text_level
        self.text_segment_length = text_segment_length
        # parameters for "keep"
        self.text_keep_start = text_keep_start

        # validate text_percentage as fraction in [0.0, 1.0]
        try:
            self.text_percentage = float(text_percentage)
        except (TypeError, ValueError):
            raise ValueError(f"text_percentage must be numeric (got {text_percentage!r})")
        if not (0.0 <= self.text_percentage <= 1.0):
            raise ValueError(f"text_percentage must be between 0.0 and 1.0 (got {self.text_percentage})")

        # validate and store text_segment_length: must be int >= 2
        try:
            self.text_segment_length = int(text_segment_length)
        except (TypeError, ValueError):
            raise ValueError(f"text_segment_length must be an integer >= 2 (got {text_segment_length!r})")
        if self.text_segment_length < 2:
            raise ValueError(f"text_segment_length must be >= 2 (got {self.text_segment_length})")

        # text_keep: start provided; compute end = start + percentage (capped at 1.0)
        try:
            self.text_keep_start = float(text_keep_start)
        except (TypeError, ValueError):
            raise ValueError(f"text_keep_start must be a float in [0.0, 1.0] (got {text_keep_start!r})")
        if not (0.0 <= self.text_keep_start <= 1.0):
            raise ValueError(f"text_keep_start must be between 0.0 and 1.0 (got {self.text_keep_start})")
        # compute keep end from start + percentage, cap at 1.0
        self.text_keep_end = min(1.0, self.text_keep_start + self.text_percentage)


    def __call__(self, doc: Doc) -> Doc:

        if self.text_operation == "replace":
        
            all_words = []
            if self.text_level == "doc":
                all_words = self._replace_tokens(doc)
            elif self.text_level == "sent":
                for sent in doc.sents:
                    all_words.extend(self._replace_tokens(sent))
            elif self.text_level == "clause":
                for clause in getattr(doc._, "clauses", []):
                    all_words.extend(self._replace_tokens(clause))
            elif self.text_level == "segment":
                for segment in self._iter_segments(doc):
                    all_words.extend(self._replace_tokens(segment))
            else:
                self._ensure_valid_text_level()
            output_text = ' '.join(all_words)
        
        elif self.text_operation == "randomize":
            all_words = []
            if self.text_level == "doc":
                all_words = self._randomize_tokens(doc)
            elif self.text_level == "sent":
                for sent in doc.sents:
                    all_words.extend(self._randomize_tokens(sent))
            elif self.text_level == "clause":
                for clause in getattr(doc._, "clauses", []):
                    all_words.extend(self._randomize_tokens(clause))
            elif self.text_level == "segment":
                for segment in self._iter_segments(doc):
                    all_words.extend(self._randomize_tokens(segment))
            else:
                self._ensure_valid_text_level()

            output_text = " ".join(all_words)


        elif self.text_operation == "keep":
            # keep uses computed self.text_keep_start and self.text_keep_end (start + percentage, capped at 1.0)
            tokens = [t.text for t in doc]
            n = len(tokens)
            if n == 0:
                output_text = ""
            else:
                start_idx = int(n * self.text_keep_start)
                end_idx = int(n * self.text_keep_end)
                # ensure at least one token if rounding causes equality
                if end_idx <= start_idx:
                    end_idx = min(start_idx + 1, n)
                kept = tokens[start_idx:end_idx]
                output_text = " ".join(kept)

        else:
            raise ValueError(f"Invalid text_operation {self.text_operation!r}. Allowed: 'replace', 'randomize', 'keep'.")

        doc._.format_str = output_text
        return doc


    def _replace_tokens(self, token_seq) -> List[Union[str, Any]]:
        """Replace tokens of the given span/sequence and return a list of token or their replacements.
        
        Returns:
            A list of token texts or their replacements.
        """
        replace_words_index = set(random.sample(range(0, len(token_seq)), int(len(token_seq) * self.text_percentage)))

        return [
            self.text_element(token_seq[i]) if i in replace_words_index else token_seq[i].text
            for i in range(len(token_seq))
        ]

    def _randomize_tokens(self, token_seq) -> List[str]:
        """Randomize tokens of the given span/sequence and return a list of token strings.

        Returns:
            A list of randomized token strings.
        """
        tokens = [t.text for t in token_seq]
        if not tokens:
            return []
        random.shuffle(tokens)
        return tokens

    def _iter_segments(self, token_seq):
        """Yield consecutive segments (spans) of token_seq of length self.text_segment_length.
        The last yielded segment may be shorter (contains the remainder).
        """
        for i in range(0, len(token_seq), self.text_segment_length):
            yield token_seq[i : i + self.text_segment_length]

    def _ensure_valid_text_level(self):
        """Raise ValueError if self.text_level is not one of the allowed values."""
        allowed = ("doc", "sent", "clause", "segment")
        if self.text_level not in allowed:
            raise ValueError(
                f"Invalid `text_level`: {self.text_level!r}. Allowed values: {', '.join(allowed)}. "
                "Use one of these in the component config (default: 'doc')."
            )