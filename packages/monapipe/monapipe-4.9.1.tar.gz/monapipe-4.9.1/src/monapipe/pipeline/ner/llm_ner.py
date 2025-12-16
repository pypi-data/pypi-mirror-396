from typing import Union

from spacy.language import Language
from spacy.tokens import Doc
from spacy.util import filter_spans

from .llm_ner_methods.entity_annotator import EntityAnnotator
from .methods import merge_spans_into_doc_ents


class LLMNer:
    """The class `LLMNer` responsible for adding named entities to the Doc using an LLM-based approach"""

    assigns = {"doc.ents"}

    def __init__(
        self,
        nlp: Language,
        set_ents_mode: str,
        model_name: str,
        sentences_per_chunk: int,
        overlap_sentences: int,
        base_url: str,
        label_dict: Union[dict, None],
        info_logs: bool = False,
    ):

        self.set_ents_mode = set_ents_mode
        self.model_name = model_name
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
        self.info_logs = info_logs
        self.base_url = base_url

        # Default class descriptions if not provided
        # https://stackoverflow.com/questions/70835924/how-to-get-a-description-for-each-spacy-ner-entity
        self.label_dict = label_dict or {
            "PER": "A human individual's name.",
            "ORG": "An organization or company name.",
            "GPE": "Countries, cities, or states.",
            "LOC": "Non-political locations, e.g., mountains, rivers.",
            "FAC": "Buildings, airports, highways, bridges, etc.",
            "NORP": "Nationalities, religious or political groups.",
            "EVENT": "Named events, like sports events or historical events.",
            "PRODUCT": "Products, e.g., phones, cars.",
            "WORK_OF_ART": "Titles of works of art, books, music, etc.",
            "LAW": "Named legal documents or acts.",
            "LANG": "Languages, e.g., English, Spanish.",
            "DATE": "Specific dates like day, month, year.",
            "TIME": "Times of day, e.g., 3 PM.",
            "MONEY": "Monetary values, e.g., $100.",
            "PERCENT": "Percentages, e.g., 45%.",
            "QUANTITY": "Measurements, e.g., 10 km, 5 liters.",
            "ORDINAL": "Ordinal numbers, e.g., first, 2nd.",
            "CARDINAL": "Numbers not classified as other numeric types.",
        }

    def __call__(self, doc: Doc) -> Doc:
        annotator = EntityAnnotator(
            label_dict=self.label_dict,
            model_name=self.model_name,
            sentences_per_chunk=self.sentences_per_chunk,
            overlap_sentences=self.overlap_sentences,
            info_logs=self.info_logs,
            base_url=self.base_url,
        )

        at = annotator.annotate_text(doc.text)

        new_spans = []
        for ann in at.annotations:
            span = doc.char_span(ann.start, ann.end, label=ann.label, alignment_mode="contract")
            if span is None:
                span = doc.char_span(ann.start, ann.end, label=ann.label, alignment_mode="expand")
            new_spans.append(span)

        new_spans = filter_spans(new_spans)
        merge_spans_into_doc_ents(spans=new_spans, doc=doc, set_ents_mode=self.set_ents_mode)

        return doc

    def __repr__(self):
        """
        String representation of this Pipe showing the model and classes tagged by this instance
        """
        desc = ", ".join(self.label_dict.keys())
        return (
            f"<LLMNer(model_name={self.model_name}, set_ents_mode={self.set_ents_mode}, base_url={self.base_url}"
            f"classes=[{desc}])>"
        )

    def replace_label_dict(self, new_label_dict: dict) -> None:
        """
        Convenience method to overwrite this instance's `self.label_dict` to change the types of entities it tags.

        Args:
            new_label_dict: The dictionary containing label-description pairs to use from now on.

        Example:
            llm_ner.replace_label_dict({
                "ANIMAL": "Names of animals",
                "DISEASE": "Names of diseases"
            })
        """
        if not isinstance(new_label_dict, dict):
            raise ValueError("new_label_dict must be a dictionary")
        self.label_dict = new_label_dict

    def add_label(self, label: str, label_desc: str) -> None:
        """
        Convenience method to add a new `label` with the definition `label_desc` to tag

        Args:
            label (str): Name of the new label
            label_desc (str): Definition of the label to pass to the LLM.

        Raises:
            ValueError: If the `label` is already registered.
        """

        if label in self.label_dict:
            raise ValueError("Label already known.")
        self.label_dict[label] = label_desc


@Language.factory(
    "llm_ner",
    assigns=LLMNer.assigns,
    default_config={
        "set_ents_mode": "reset",
        "model_name": "openai-gpt-oss-120b",
        "sentences_per_chunk": 40,
        "overlap_sentences": 5,
        "base_url": "https://chat-ai.academiccloud.de/v1",
        "label_dict": {
            "PER": "A human individual's name.",
            "ORG": "An organization or company name.",
            "GPE": "Countries, cities, or states.",
            "LOC": "Non-political locations, e.g., mountains, rivers.",
            "FAC": "Buildings, airports, highways, bridges, etc.",
            "NORP": "Nationalities, religious or political groups.",
            "EVENT": "Named events, like sports events or historical events.",
            "PRODUCT": "Products, e.g., phones, cars.",
            "WORK_OF_ART": "Titles of works of art, books, music, etc.",
            "LAW": "Named legal documents or acts.",
            "LANG": "Languages, e.g., English, Spanish.",
            "DATE": "Specific dates like day, month, year.",
            "TIME": "Times of day, e.g., 3 PM.",
            "MONEY": "Monetary values, e.g., $100.",
            "PERCENT": "Percentages, e.g., 45%.",
            "QUANTITY": "Measurements, e.g., 10 km, 5 liters.",
            "ORDINAL": "Ordinal numbers, e.g., first, 2nd.",
            "CARDINAL": "Numbers not classified as other numeric types.",
        },
    },
)
def llm_ner(
    nlp: Language,
    name: str,
    set_ents_mode: str,
    model_name: str,
    sentences_per_chunk: int,
    overlap_sentences: int,
    base_url: str,
    label_dict: Union[dict, None],
):
    return LLMNer(
        nlp,
        set_ents_mode=set_ents_mode,
        model_name=model_name,
        sentences_per_chunk=sentences_per_chunk,
        overlap_sentences=overlap_sentences,
        base_url=base_url,
        label_dict=label_dict,
    )
