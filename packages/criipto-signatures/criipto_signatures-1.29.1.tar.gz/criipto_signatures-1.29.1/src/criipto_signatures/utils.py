from typing import Annotated
from pydantic import PlainSerializer, PlainValidator
from base64 import b64encode, b64decode


def serializeBlob(blob: str | bytes) -> str:
  if isinstance(
    blob,
    bytes,
  ):
    base64_encoded_data = b64encode(blob)
    return base64_encoded_data.decode("utf-8")
  else:
    return blob


type CustomBlobInput = Annotated[str | bytes, PlainSerializer(serializeBlob)]


type CustomBlobOutput = Annotated[bytes, PlainValidator(b64decode)]
