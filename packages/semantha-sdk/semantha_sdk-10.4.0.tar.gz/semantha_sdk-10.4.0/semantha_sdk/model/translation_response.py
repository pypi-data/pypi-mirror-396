from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class TranslationResponse:
    """ author semantha, this is a generated class do not change manually! """
    translation: Optional[str] = None
    score: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

TranslationResponseSchema = class_schema(TranslationResponse, base_schema=RestSchema)
