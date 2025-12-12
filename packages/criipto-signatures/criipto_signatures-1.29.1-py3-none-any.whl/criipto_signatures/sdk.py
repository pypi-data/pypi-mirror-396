from typing import Optional
from criipto_signatures.models import (
  IntScalarInput,
  SignatureOrderStatus,
  StringScalarInput,
)
from .operations import (
  CriiptoSignaturesSDKAsync as CriiptoSignaturesSDKAsyncInternal,
  CriiptoSignaturesSDKSync as CriiptoSignaturesSDKSyncInternal,
  QuerySignatureOrders_Viewer_Application,
  QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder,
)


class CriiptoSignaturesSDKAsync(CriiptoSignaturesSDKAsyncInternal):
  async def querySignatureOrders(  # pyright: ignore[reportIncompatibleMethodOverride]
    self,
    first: IntScalarInput,
    status: Optional[SignatureOrderStatus] = None,
    after: Optional[StringScalarInput] = None,
  ) -> list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder
  ]:
    result = await super().querySignatureOrders(first, status, after)
    assert isinstance(result, QuerySignatureOrders_Viewer_Application)
    return list(map(lambda edge: edge.node, result.signatureOrders.edges))


class CriiptoSignaturesSDKSync(CriiptoSignaturesSDKSyncInternal):
  def querySignatureOrders(  # pyright: ignore[reportIncompatibleMethodOverride]
    self,
    first: IntScalarInput,
    status: Optional[SignatureOrderStatus] = None,
    after: Optional[StringScalarInput] = None,
  ) -> list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder
  ]:
    result = super().querySignatureOrders(first, status, after)
    assert isinstance(result, QuerySignatureOrders_Viewer_Application)
    return list(map(lambda edge: edge.node, result.signatureOrders.edges))
