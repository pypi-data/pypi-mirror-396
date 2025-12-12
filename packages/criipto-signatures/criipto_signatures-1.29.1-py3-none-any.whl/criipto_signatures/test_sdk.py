import os
from datetime import datetime
from .sdk import (
  CriiptoSignaturesSDKAsync,
  CriiptoSignaturesSDKSync,
)
from .operations import (
  CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument,
)
from .models import (
  AddSignatoryInput,
  CancelSignatureOrderInput,
  ChangeSignatureOrderInput,
  CreateSignatureOrderInput,
  DocumentInput,
  PadesDocumentInput,
  PadesDocumentFormInput,
  DocumentStorageMode,
  SignatureOrderStatus,
)
import pytest
import inspect
from typing import Any, cast, Coroutine

dir_path = os.path.dirname(os.path.realpath(__file__))


def getFileBytes(filename: str) -> bytes:
  with open(dir_path + os.sep + filename, "rb") as sample_file:
    return sample_file.read()


documentFixture = DocumentInput(
  pdf=PadesDocumentInput(
    title="Python sample document",
    blob=getFileBytes("sample.pdf"),
    storageMode=DocumentStorageMode.Temporary,
  )
)


async def unwrapResult[T](maybeCoroutine: T | Coroutine[Any, Any, T]) -> T:
  if inspect.iscoroutine(maybeCoroutine):
    return await maybeCoroutine
  return cast(T, maybeCoroutine)


@pytest.mark.parametrize(
  ("sdk"),
  [
    (
      CriiptoSignaturesSDKAsync(
        os.environ["CRIIPTO_SIGNATURES_CLIENT_ID"],
        os.environ["CRIIPTO_SIGNATURES_CLIENT_SECRET"],
      )
    ),
    (
      CriiptoSignaturesSDKSync(
        os.environ["CRIIPTO_SIGNATURES_CLIENT_ID"],
        os.environ["CRIIPTO_SIGNATURES_CLIENT_SECRET"],
      )
    ),
  ],
)
class TestClass:
  @pytest.mark.asyncio
  async def test_create_signature_order_add_signatory(
    self, sdk: CriiptoSignaturesSDKAsync | CriiptoSignaturesSDKSync
  ):
    signatureOrder = await unwrapResult(
      sdk.createSignatureOrder(
        CreateSignatureOrderInput(
          title="Python sample signature order",
          expiresInDays=1,
          documents=[documentFixture],
        )
      )
    )

    assert signatureOrder.id

    signatory = await unwrapResult(
      sdk.addSignatory(AddSignatoryInput(signatureOrderId=signatureOrder.id))
    )

    assert signatory.href

    await unwrapResult(
      sdk.cancelSignatureOrder(
        CancelSignatureOrderInput(signatureOrderId=signatureOrder.id)
      )
    )

  @pytest.mark.asyncio
  async def test_create_signature_order_with_form(
    self, sdk: CriiptoSignaturesSDKAsync | CriiptoSignaturesSDKSync
  ):
    signatureOrder = await unwrapResult(
      sdk.createSignatureOrder(
        CreateSignatureOrderInput(
          title="Python sample signature order",
          expiresInDays=1,
          documents=[
            DocumentInput(
              pdf=PadesDocumentInput(
                title="Python sample document",
                blob=getFileBytes("sample-form.pdf"),
                storageMode=DocumentStorageMode.Temporary,
                form=PadesDocumentFormInput(enabled=True),
              )
            )
          ],
        )
      )
    )

    document = signatureOrder.documents[0]
    # TODO: This should use an auto-generated type guard, instead of an instanceof check.
    assert isinstance(
      document,
      CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument,
    )

    assert document.form is not None
    assert document.form.enabled

    await unwrapResult(
      sdk.cancelSignatureOrder(
        CancelSignatureOrderInput(signatureOrderId=signatureOrder.id)
      )
    )

  @pytest.mark.asyncio
  async def test_change_max_signatories(
    self, sdk: CriiptoSignaturesSDKAsync | CriiptoSignaturesSDKSync
  ):
    signatureOrder = await unwrapResult(
      sdk.createSignatureOrder(
        CreateSignatureOrderInput(
          title="Python sample signature order",
          expiresInDays=1,
          maxSignatories=10,
          documents=[documentFixture],
        )
      )
    )

    assert signatureOrder.id

    changedSignatureOrder = await unwrapResult(
      sdk.changeSignatureOrder(
        ChangeSignatureOrderInput(signatureOrderId=signatureOrder.id, maxSignatories=20)
      )
    )

    assert changedSignatureOrder.maxSignatories == 20

    await unwrapResult(
      sdk.cancelSignatureOrder(
        CancelSignatureOrderInput(signatureOrderId=signatureOrder.id)
      )
    )

  @pytest.mark.asyncio
  async def test_query_signature_orders(
    self, sdk: CriiptoSignaturesSDKAsync | CriiptoSignaturesSDKSync
  ):
    title = "Python sample signature order" + str(datetime.now())

    signatureOrder = await unwrapResult(
      sdk.createSignatureOrder(
        CreateSignatureOrderInput(
          title=title,
          expiresInDays=1,
          documents=[documentFixture],
        )
      )
    )

    signatureOrders = await unwrapResult(
      sdk.querySignatureOrders(first=1000, status=SignatureOrderStatus.OPEN)
    )

    createdSignatureOrder = next(
      _signatureOrder
      for _signatureOrder in signatureOrders
      if _signatureOrder.id == signatureOrder.id
    )

    assert createdSignatureOrder is not None
    assert createdSignatureOrder.title == title

    await unwrapResult(
      sdk.cancelSignatureOrder(
        CancelSignatureOrderInput(signatureOrderId=signatureOrder.id)
      )
    )

  @pytest.mark.asyncio
  async def test_signature_order_role(
    self, sdk: CriiptoSignaturesSDKAsync | CriiptoSignaturesSDKSync
  ):
    role = "CEO"

    signatureOrder = await unwrapResult(
      sdk.createSignatureOrder(
        CreateSignatureOrderInput(
          title="Python sample signature order",
          expiresInDays=1,
          documents=[documentFixture],
        )
      )
    )

    signatory = await unwrapResult(
      sdk.addSignatory(AddSignatoryInput(signatureOrderId=signatureOrder.id, role=role))
    )

    assert signatory.role == role

    await unwrapResult(
      sdk.cancelSignatureOrder(
        CancelSignatureOrderInput(signatureOrderId=signatureOrder.id)
      )
    )
