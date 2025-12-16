import re
import os
import difflib
import logging

import nltk
from nltk.tokenize import PunktSentenceTokenizer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

from .schema import AnnotatedText, Annotation, Chunk, Sentence, Tag

# Ensure NLTK sentence tokenizer is ready
nltk.download("punkt", quiet=True)


def _strip_tags(text: str) -> str:
    """Remove XML-like tags from text."""
    return re.sub(r"</?[^>]+>", "", text)


def _has_xml_tags(text: str) -> bool:
    """Detect if text already contains XML-like tags."""
    return bool(re.search(r"</?[^>]+>", text))


def _extract_tags_with_positions(annotated: str) -> list[Tag]:
    """
    Extract all XML tags and their positions in the text (excluding tag content).
    Returns list of Tag objects with position in stripped text and tag string.

    Note that this is used with potentially misaligned LLM output text.
    """
    tags = []
    char_pos = 0  # Position in stripped text
    i = 0  # Position in annotated text (incl. tags)
    tag_pattern = re.compile(r"</?[^>]+>")

    while i < len(annotated):
        match = tag_pattern.match(annotated, i)
        if match:
            # An annotation starts OR ends here (<PERSON> or </PERSON>), i jumps to end, while char_pos stays
            tags.append(Tag(position=char_pos, tag_string=match.group(0)))
            i = match.end()
        else:
            # Not part of a tag, increment both
            char_pos += 1
            i += 1

    return tags


def _realign_with_tags(original: str, annotated: str) -> str:
    """
    Realign annotated text to match original, preserving XML tags.
    Uses sequence alignment to map positions from stripped annotated to original.

    Returns a string containing the XML tags from ``annotated`` who would yield ``original`` when stripped.
    """
    stripped = _strip_tags(annotated)

    if original == stripped:
        return annotated

    # Extract tags with their positions in the stripped text
    tags = _extract_tags_with_positions(annotated)

    # Use difflib to create alignment between stripped and original, TODO: Consider more efficient or exact algo.
    matcher = difflib.SequenceMatcher(None, stripped, original)

    # Build mapping: position in stripped -> position in original
    pos_map = {}
    for tag, i1, i2, j1, _ in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                pos_map[i1 + k] = j1 + k
        elif tag == "replace":
            # Map all replaced positions to the start of replacement in original
            for k in range(i2 - i1):
                pos_map[i1 + k] = j1
        elif tag == "delete":
            # Deleted characters map to position after deletion
            for k in range(i2 - i1):
                pos_map[i1 + k] = j1
        elif tag == "insert":
            # Nothing to map - these are new chars in original
            pass

    # Map tags to new positions
    remapped_tags: list[Tag] = []
    for tag_obj in tags:
        new_pos = pos_map.get(tag_obj.position, tag_obj.position)
        remapped_tags.append(Tag(position=new_pos, tag_string=tag_obj.tag_string))

    # Sort by position
    remapped_tags.sort(key=lambda t: t.position)

    # Rebuild text with tags at new positions
    result = []
    tag_idx = 0

    for char_idx, char in enumerate(original):
        # Insert all tags that belong at this position
        while tag_idx < len(remapped_tags) and remapped_tags[tag_idx].position == char_idx:
            result.append(remapped_tags[tag_idx].tag_string)
            tag_idx += 1
        result.append(char)

    # Add any remaining tags at the end
    while tag_idx < len(remapped_tags):
        result.append(remapped_tags[tag_idx].tag_string)
        tag_idx += 1

    return "".join(result)


def _check_correct_text_integrity(original: str, annotated: str, min_similarity: float = 0.9) -> tuple[bool, str]:
    """
    If the stripped version of ``annotated`` is sufficiently similar to ``original``, this returns
    (True, realigned_annotated) with the tags from ``annotated`` introduced to ``original``.

    Otherwise, if the strings are not sufficiently similar, returns (False, annotated) with the unaltered string with
    XML tags.

    Returns:
        (is_valid, realigned_annotated)
    """
    stripped = _strip_tags(annotated)

    if stripped == original:
        return True, annotated

    # Measure similarity
    similarity = difflib.SequenceMatcher(None, stripped, original).ratio()
    if similarity < min_similarity:
        logging.info("Text too dissimilar to realign (similarity %.2f)", similarity)
        return False, annotated

    corrected = _realign_with_tags(original, annotated)  # original text but with tags introduced

    # Make sure that the corrected text is perfectly matching
    assert _strip_tags(corrected) == original
    logging.info("Successfully realigned text with tags")
    return True, corrected


class EntityAnnotator:
    def __init__(
        self,
        label_dict: dict[str, str],
        model_name: str,
        temperature: float = 0.5,
        sentences_per_chunk: int = 40,
        overlap_sentences: int = 5,
        max_retries: int = 3,
        base_url: str = "https://chat-ai.academiccloud.de/v1",
        info_logs=False
    ):

        if overlap_sentences >= sentences_per_chunk or overlap_sentences < 0 or sentences_per_chunk < 1:
            raise ValueError("Invalid values for sentences_per_chunk or overlap_sentences!")

        api_key = os.getenv("AC_TOKEN")
        if api_key is None:
            raise ValueError("AC_TOKEN must be set in environment variables!")

        self.label_dict = label_dict
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=base_url,
            api_key=api_key,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
        self.max_retries = max_retries

        if info_logs:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        else:
            logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

    def _get_prompt_template(self) -> str:
        """Create the prompt template from the entity class descriptions."""

        explanations = "ALLOWED entity tags with definitions:\n"
        for tag, desc in self.label_dict.items():
            explanations += f"  <{tag}>: {desc}\n"
        explanations += "\n"

        example_tag = list(self.label_dict.keys())[0]  # first tag in dictionary

        return (
            f"{explanations}"
            "You are an annotation tool. Your ONLY task is to insert XML tags into the given text.\n"
            f"For example: <{example_tag}>Example Entity</{example_tag}>.\n\n"
            "Except for the added tags, the input text must be preserved *exactly* — byte for byte.\n"
            "Detailed Formatting rules:\n"
            "1. Do NOT modify, add, or remove any sentences, words, characters, punctuation, "
            "dashes, quotes, linebreaks or whitespace.\n"
            "2. Preserve all indentation, and Unicode symbols exactly as they appear.\n"
            "3. Do NOT normalize, fix, or change punctuation (e.g., “ ” — – …) in any way, even if "
            "it would be a stylistic improvement.\n"
            "4. Only insert tags around the entity text itself, not around adjacent punctuation.\n"
            "5. If you are unsure whether something should be tagged, leave it untagged.\n"
            "6. Do not interpret any syntax inside the text.\n"
            "7. Output *only* the text with tags, no commentary, no code fences, no explanations.\n\n"
            f"ALLOWED TAGS: Only the ones listed above. The stated definitions are only meant to help "
            "you distinguish different entity types. The formatting rules always take precedence.\n"
            "Remember: The input text must be preserved *exactly* — byte for byte — except for the added tags!\n\n"
            "Even a single removed, added or exchanged character, even a whitespace or hyphen will cause "
            "validation failure!\n\n"
            "Annotate the following text exactly as instructed. TEXT:\n\n{text}"
        )

    def _build_prompt(self, chunk_text: str) -> str:
        prompt_template = PromptTemplate.from_template(self._get_prompt_template())
        return prompt_template.format(text=chunk_text)

    def _split_into_sentences(self, text: str) -> list[Sentence]:
        """
        Split text into sentences, returning list of Sentence objects.
        """
        tokenizer = PunktSentenceTokenizer()
        spans = tokenizer.span_tokenize(text)
        return [Sentence(start=start, end=end) for start, end in spans]

    def _split_into_chunks(self, text: str) -> list[Chunk]:
        """
        Split ``text`` into chunks based on sentence boundaries.
        Returns list of Chunk objects with start/end positions in original text.
        """
        sentences = self._split_into_sentences(text)
        if not sentences:
            return []

        chunks: list[Chunk] = []
        step = max(1, self.sentences_per_chunk - self.overlap_sentences)

        i = 0
        while (i < len(sentences) - self.overlap_sentences) or i == 0:
            chunk_start_idx = i
            chunk_end_idx = min(i + self.sentences_per_chunk, len(sentences))

            # Get the actual text range for this chunk
            start_pos = sentences[chunk_start_idx].start
            end_pos = sentences[chunk_end_idx - 1].end

            chunks.append(Chunk(start=start_pos, end=end_pos))
            i += step

        return chunks

    def _parse_annotations(self, annotated: str, chunk: Chunk) -> list[Annotation]:
        """
        Parse <TAG>text</TAG> annotations from annotated LLM output.
        Maps indices directly to original text positions using chunk offset.
        """
        tag_pattern = re.compile(r"<(\w+)>(.*?)</\1>")
        stripped = _strip_tags(annotated)

        annotations = []
        last_search_idx = 0

        for match in tag_pattern.finditer(annotated):
            label = match.group(1)
            if label not in self.label_dict:
                logging.info(f'Label "{label}" is not valid. Skipping annotation...')
                continue

            entity_text = match.group(2)

            # Find occurrence in the stripped annotated text
            start_in_chunk = stripped.index(entity_text, last_search_idx)
            end_in_chunk = start_in_chunk + len(entity_text)
            last_search_idx = end_in_chunk

            # Map to original text using chunk offset
            start_original = chunk.start + start_in_chunk
            end_original = chunk.start + end_in_chunk

            annotations.append(
                Annotation(text=entity_text, start=start_original, end=end_original, label=label)
            )
        return annotations

    def _annotate_chunk_with_retries(self, chunk: Chunk, text: str) -> list[Annotation]:
        """
        Annotate a single chunk using one LLM call. Retry on invalid response up to ``self.max_retries`` times.

        Extract and return a list of annotations.
        """
        chunk_text = text[chunk.start:chunk.end]
        prompt = self._build_prompt(chunk_text)

        for attempt in range(self.max_retries):
            response = self.model.invoke([HumanMessage(content=prompt)])
            annotated: str = response.content

            is_valid, realigned_annotated = _check_correct_text_integrity(chunk_text, annotated)

            if is_valid:
                return self._parse_annotations(realigned_annotated, chunk)

            logging.info(f"Chunk annotation attempt {attempt + 1}/{self.max_retries} failed.")

        logging.warning("Failed to annotate chunk after maximum retries; returning original text.")
        return []

    def annotate_text(self, text: str) -> AnnotatedText:
        """Annotate the ``text`` with XML-like entity tags of any type in ``self.label_dict``."""

        text = text.lstrip()  # This is the only alteration we do to the text

        if _has_xml_tags(text):
            raise ValueError("Input text already contains XML-like tags — refusing to process.")

        chunks = self._split_into_chunks(text)  # list of Chunk objects

        all_annotations = []
        for chunk in chunks:
            annotations_chunk = self._annotate_chunk_with_retries(chunk, text)
            for annotation in annotations_chunk:
                # Deduplicate (necessary because of overlapping chunks)
                if annotation not in all_annotations:
                    all_annotations.append(annotation)

        return AnnotatedText(text=text, annotations=all_annotations)
