from abc import ABC
from typing import Type, List, cast

from pydantic import BaseModel
from pymultirole_plugins.v1.schema import Document, Sentence
from pymultirole_plugins.v1.segmenter import SegmenterParameters, SegmenterBase
from syntok import segmenter


class SyntokSegmenterParameters(SegmenterParameters, ABC):
    pass


class SyntokSegmenter(SegmenterBase, ABC):
    __doc__ = """Syntok segmenter [syntok](https://github.com/fnl/syntok)."""

    def segment(self, documents: List[Document], parameters: SegmenterParameters) \
            -> List[Document]:
        params: SyntokSegmenterParameters = \
            cast(SyntokSegmenterParameters, parameters)
        for document in documents:
            document.sentences = []
            for paragraph in segmenter.analyze(document.text):
                for sentence in paragraph:
                    first = sentence[0]
                    last = sentence[-1]
                    document.sentences.append(Sentence(start=first.offset, end=last.offset + len(last.value)))

        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return SyntokSegmenterParameters
