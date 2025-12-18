#
# ContextGem
#
# Copyright 2025 Shcherbak AI AS. All rights reserved. Developed by Sergii Shcherbak.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from tashan_core.public.aspects import Aspect
from tashan_core.public.concepts import (
    BooleanConcept,
    DateConcept,
    JsonObjectConcept,
    LabelConcept,
    ListConcept,
    NumericalConcept,
    PaperSelectionConcept,
    RatingConcept,
    StringConcept,
)
from tashan_core.public.converters import DocxConverter
from tashan_core.public.data_models import LLMPricing, RatingScale
from tashan_core.public.decorators import register_tool
from tashan_core.public.documents import Document
from tashan_core.public.examples import JsonObjectExample, StringExample
from tashan_core.public.images import Image
from tashan_core.public.llms import ChatSession, DocumentLLM, DocumentLLMGroup
from tashan_core.public.paragraphs import Paragraph
from tashan_core.public.pipelines import DocumentPipeline, ExtractionPipeline
from tashan_core.public.sentences import Sentence
from tashan_core.public.utils import (
    JsonObjectClassStruct,
    create_image,
    image_to_base64,
    reload_logger_settings,
)

__all__ = (
    # Aspects
    "Aspect",
    # Concepts
    "StringConcept",
    "BooleanConcept",
    "NumericalConcept",
    "RatingConcept",
    "JsonObjectConcept",
    "DateConcept",
    "LabelConcept",
    "ListConcept",
    "PaperSelectionConcept",
    # Documents
    "Document",
    # Pipelines
    "ExtractionPipeline",
    "DocumentPipeline",  # deprecated, will be removed in v1.0.0
    # Paragraphs
    "Paragraph",
    # Sentences
    "Sentence",
    # Images
    "Image",
    # Examples
    "StringExample",
    "JsonObjectExample",
    # LLMs
    "DocumentLLM",
    "DocumentLLMGroup",
    "ChatSession",
    # Data models
    "LLMPricing",
    "RatingScale",  # deprecated, will be removed in v1.0.0
    # Utils
    "create_image",
    "image_to_base64",
    "reload_logger_settings",
    "JsonObjectClassStruct",
    # Converters
    "DocxConverter",
    # Decorators
    "register_tool",
)
