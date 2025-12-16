from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Translation:
    """ author semantha, this is a generated class do not change manually! """
    # Text to translate
    text: str
    # ISO-2 code; required
    target_language: str
    # ISO-2 code; optional. If omitted, auto-detect is used.
    source_language: Optional[str] = None

TranslationSchema = class_schema(Translation, base_schema=RestSchema)
