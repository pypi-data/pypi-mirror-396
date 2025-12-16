from dataclasses import dataclass


@dataclass
class Sentence:
    start: int  # Start position in original text
    end: int    # End position in original text


@dataclass
class Tag:
    position: int  # Position in stripped text where this tag is inserted
    tag_string: str  # The XML tag (e.g., "<PERSON>" or "</PERSON>")


@dataclass
class Chunk:
    start: int  # Start position in original text
    end: int    # End position in original text


@dataclass
class Annotation:
    text: str
    start: int
    end: int
    label: str  # e.g. PERSON


@dataclass
class AnnotatedText:
    text: str
    annotations: list[Annotation]
