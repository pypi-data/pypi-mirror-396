from __future__ import annotations
from .utils import CustomBlobInput, CustomBlobOutput
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
from warnings import deprecated
from pydantic import RootModel
from .models import (
  CreateSignatureOrderInput,
  CleanupSignatureOrderInput,
  AddSignatoryInput,
  AddSignatoriesInput,
  ChangeSignatoryInput,
  CloseSignatureOrderInput,
  CancelSignatureOrderInput,
  SignActingAsInput,
  ValidateDocumentInput,
  ExtendSignatureOrderInput,
  DeleteSignatoryInput,
  CreateBatchSignatoryInput,
  ChangeSignatureOrderInput,
)
from .models import (
  IDScalarInput,
  IDScalarOutput,
  StringScalarInput,
  StringScalarOutput,
  IntScalarInput,
  IntScalarOutput,
  BooleanScalarInput,
  BooleanScalarOutput,
  BlobScalarInput,
  BlobScalarOutput,
  DateScalarInput,
  DateScalarOutput,
  DateTimeScalarInput,
  DateTimeScalarOutput,
  FloatScalarInput,
  FloatScalarOutput,
  URIScalarInput,
  URIScalarOutput,
)
from .models import (
  ApplicationApiKeyMode,
  CriiptoVerifyEvidenceProviderVersion,
  DeviceOperatingSystem,
  DocumentIDLocation,
  DocumentStorageMode,
  EvidenceValidationStage,
  Language,
  SignatoryDocumentStatus,
  SignatoryFrontendEvent,
  SignatoryRole,
  SignatoryStatus,
  SignatureOrderStatus,
  VerifyApplicationEnvironment,
  WebhookInvocationEvent,
)
from gql import Client, gql
from httpx import BasicAuth
from gql.transport.httpx import HTTPXAsyncTransport, HTTPXTransport

BasicDocumentFragment = """fragment BasicDocument on Document {
  __typename
  id
  title
  reference
  ... on PdfDocument {
    documentID
    form {
      enabled
    }
  }
}"""
SingleSignatureFragment = """fragment SingleSignature on SingleSignature {
  ... on JWTSignature {
    jwt
    jwks
    claims {
      name
      value
    }
  }
  ... on DrawableSignature {
    name
    image
  }
  ... on NorwegianBankIdSignature {
    claims {
      name
      value
    }
    signingCertificate {
      raw
      issuer
      subject
    }
  }
}"""
SignedDocumentFragment = """fragment SignedDocument on Document {
  id
  title
  blob
  signatures {
    __typename
    signatory {
      id
    }
    timestampToken {
      timestamp
    }
    ...SingleSignature
    ... on CompositeSignature {
      signatures {
        ...SingleSignature
      }
    }
  }
}"""
BasicSignatoryFragment = """fragment BasicSignatory on Signatory {
  id
  status
  statusReason
  href
  downloadHref
  token
  reference
  role
  signingAs
  signatoryRole
  signatureOrder {
    id
    status
    closedAt
    expiresAt
  }
  evidenceProviders {
    __typename
    id
  }
  documents {
    edges {
      status
      node {
        __typename
        id
      }
    }
  }
  signingSequence {
    initialNumber
  }
}"""
BasicSignatureOrderFragment = """fragment BasicSignatureOrder on SignatureOrder {
  id
  status
  title
  closedAt
  expiresAt
  maxSignatories
  signatories {
    ...BasicSignatory
  }
  evidenceProviders {
    __typename
    id
  }
}"""
BasicBatchSignatoryFragment = """fragment BasicBatchSignatory on BatchSignatory {
  id
  token
  href
}"""


class CreateSignatureOrder_CreateSignatureOrderOutput(BaseModel):
  signatureOrder: CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document
  ]
  evidenceProviders: list[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document = (
  CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument
  | CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_XmlDocument
)


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory(
  BaseModel
):
  documents: CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument(
  BaseModel
):
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_XmlDocument(
  BaseModel
):
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


createSignatureOrderDocument = f"""mutation createSignatureOrder($input: CreateSignatureOrderInput!) {{
  createSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
      documents {{
        ...BasicDocument
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}"""


class CleanupSignatureOrder_CleanupSignatureOrderOutput(BaseModel):
  signatureOrder: CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document
  ]
  evidenceProviders: list[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document = (
  CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument
  | CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_XmlDocument
)


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory(
  BaseModel
):
  documents: CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument(
  BaseModel
):
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_XmlDocument(
  BaseModel
):
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


cleanupSignatureOrderDocument = f"""mutation cleanupSignatureOrder($input: CleanupSignatureOrderInput!) {{
  cleanupSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
      documents {{
        ...BasicDocument
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}"""


class AddSignatory_AddSignatoryOutput(BaseModel):
  signatory: AddSignatory_AddSignatoryOutput_Signatory


class AddSignatory_AddSignatoryOutput_Signatory(BaseModel):
  documents: AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    AddSignatory_AddSignatoryOutput_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: AddSignatory_AddSignatoryOutput_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: AddSignatory_AddSignatoryOutput_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection(BaseModel):
  edges: list[
    AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class AddSignatory_AddSignatoryOutput_Signatory_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class AddSignatory_AddSignatoryOutput_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class AddSignatory_AddSignatoryOutput_Signatory_SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


addSignatoryDocument = f"""mutation addSignatory($input: AddSignatoryInput!) {{
  addSignatory(input: $input) {{
    signatory {{
      ...BasicSignatory
    }}
  }}
}}
{BasicSignatoryFragment}"""


class AddSignatories_AddSignatoriesOutput(BaseModel):
  signatories: list[AddSignatories_AddSignatoriesOutput_Signatory]


class AddSignatories_AddSignatoriesOutput_Signatory(BaseModel):
  documents: AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    AddSignatories_AddSignatoriesOutput_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: AddSignatories_AddSignatoriesOutput_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: (
    AddSignatories_AddSignatoriesOutput_Signatory_SignatorySigningSequence
  )
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class AddSignatories_AddSignatoriesOutput_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class AddSignatories_AddSignatoriesOutput_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class AddSignatories_AddSignatoriesOutput_Signatory_SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


addSignatoriesDocument = f"""mutation addSignatories($input: AddSignatoriesInput!) {{
  addSignatories(input: $input) {{
    signatories {{
      ...BasicSignatory
    }}
  }}
}}
{BasicSignatoryFragment}"""


class ChangeSignatory_ChangeSignatoryOutput(BaseModel):
  signatory: ChangeSignatory_ChangeSignatoryOutput_Signatory


class ChangeSignatory_ChangeSignatoryOutput_Signatory(BaseModel):
  documents: ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: (
    ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatorySigningSequence
  )
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


changeSignatoryDocument = f"""mutation changeSignatory($input: ChangeSignatoryInput!) {{
  changeSignatory(input: $input) {{
    signatory {{
      ...BasicSignatory
    }}
  }}
}}
{BasicSignatoryFragment}"""


class CloseSignatureOrder_CloseSignatureOrderOutput(BaseModel):
  signatureOrder: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document]
  evidenceProviders: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document = (
  CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument
)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory(BaseModel):
  documents: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument(
  BaseModel
):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatures: Optional[
    list[
      CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature
    ]
  ] = Field(default=None)
  title: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument(
  BaseModel
):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatures: Optional[
    list[
      CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature
    ]
  ] = Field(default=None)
  title: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


type CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature = (
  CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature
)

type CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature = (
  CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature
)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature(
  BaseModel
):
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory
  ] = Field(default=None)
  signatures: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature
  ]
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature(
  BaseModel
):
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim
  ]
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory
  ] = Field(default=None)
  signingCertificate: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature(
  BaseModel
):
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory
  ] = Field(default=None)
  signatures: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature
  ]
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature(
  BaseModel
):
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory
  ] = Field(default=None)
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim
  ]
  signatory: Optional[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory
  ] = Field(default=None)
  signingCertificate: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate
  timestampToken: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


type CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature = (
  CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature
)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


type CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature = (
  CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature
  | CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature
)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature(
  BaseModel
):
  pass


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim
  ]
  signingCertificate: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature(
  BaseModel
):
  pass


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim
  ]
  signingCertificate: CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


closeSignatureOrderDocument = f"""mutation closeSignatureOrder($input: CloseSignatureOrderInput!) {{
  closeSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
      documents {{
        ...BasicDocument
        ...SignedDocument
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}
{SignedDocumentFragment}
{SingleSignatureFragment}"""


class CancelSignatureOrder_CancelSignatureOrderOutput(BaseModel):
  signatureOrder: CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document
  ]
  evidenceProviders: list[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document = (
  CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument
  | CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_XmlDocument
)


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory(
  BaseModel
):
  documents: CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument(
  BaseModel
):
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_XmlDocument(
  BaseModel
):
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


cancelSignatureOrderDocument = f"""mutation cancelSignatureOrder($input: CancelSignatureOrderInput!) {{
  cancelSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
      documents {{
        ...BasicDocument
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}"""


class SignActingAs_SignActingAsOutput(BaseModel):
  signatory: SignActingAs_SignActingAsOutput_Signatory


class SignActingAs_SignActingAsOutput_Signatory(BaseModel):
  documents: SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    SignActingAs_SignActingAsOutput_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: SignActingAs_SignActingAsOutput_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: SignActingAs_SignActingAsOutput_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection(BaseModel):
  edges: list[
    SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class SignActingAs_SignActingAsOutput_Signatory_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class SignActingAs_SignActingAsOutput_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class SignActingAs_SignActingAsOutput_Signatory_SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


signActingAsDocument = f"""mutation signActingAs($input: SignActingAsInput!) {{
  signActingAs(input: $input) {{
    signatory {{
      ...BasicSignatory
    }}
  }}
}}
{BasicSignatoryFragment}"""


class ValidateDocument_ValidateDocumentOutput(BaseModel):
  errors: Optional[list[StringScalarOutput]] = Field(default=None)
  # Whether or not the errors are fixable using 'fixDocumentFormattingErrors'
  fixable: Optional[BooleanScalarOutput] = Field(default=None)
  valid: BooleanScalarOutput


validateDocumentDocument = """mutation validateDocument($input: ValidateDocumentInput!) {
  validateDocument(input: $input) {
    valid
    errors
    fixable
  }
}"""


class ExtendSignatureOrder_ExtendSignatureOrderOutput(BaseModel):
  signatureOrder: ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document
  ]
  evidenceProviders: list[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document = (
  ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument
  | ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_XmlDocument
)


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory(
  BaseModel
):
  documents: ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument(
  BaseModel
):
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_XmlDocument(
  BaseModel
):
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  title: StringScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


extendSignatureOrderDocument = f"""mutation extendSignatureOrder($input: ExtendSignatureOrderInput!) {{
  extendSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
      documents {{
        ...BasicDocument
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}"""


class DeleteSignatory_DeleteSignatoryOutput(BaseModel):
  signatureOrder: DeleteSignatory_DeleteSignatoryOutput_SignatureOrder


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory(BaseModel):
  documents: DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: (
    DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureOrder
  )
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


deleteSignatoryDocument = f"""mutation deleteSignatory($input: DeleteSignatoryInput!) {{
  deleteSignatory(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class CreateBatchSignatory_CreateBatchSignatoryOutput(BaseModel):
  batchSignatory: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory(BaseModel):
  href: StringScalarOutput
  id: IDScalarOutput
  items: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem
  ]
  # The authentication token required for performing batch operations.
  token: StringScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem(
  BaseModel
):
  signatory: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory
  signatureOrder: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory(
  BaseModel
):
  documents: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory(
  BaseModel
):
  documents: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


createBatchSignatoryDocument = f"""mutation createBatchSignatory($input: CreateBatchSignatoryInput!) {{
  createBatchSignatory(input: $input) {{
    batchSignatory {{
      ...BasicBatchSignatory
      items {{
        signatureOrder {{
          ...BasicSignatureOrder
        }}
        signatory {{
          ...BasicSignatory
        }}
      }}
    }}
  }}
}}
{BasicBatchSignatoryFragment}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class ChangeSignatureOrder_ChangeSignatureOrderOutput(BaseModel):
  signatureOrder: ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory(
  BaseModel
):
  documents: ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


changeSignatureOrderDocument = f"""mutation changeSignatureOrder($input: ChangeSignatureOrderInput!) {{
  changeSignatureOrder(input: $input) {{
    signatureOrder {{
      ...BasicSignatureOrder
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class QuerySignatureOrder_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[QuerySignatureOrder_SignatureOrder_SignatureEvidenceProvider]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[QuerySignatureOrder_SignatureOrder_Signatory]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class QuerySignatureOrder_SignatureOrder_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class QuerySignatureOrder_SignatureOrder_Signatory(BaseModel):
  documents: QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatureOrder_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: QuerySignatureOrder_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: QuerySignatureOrder_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QuerySignatureOrder_SignatureOrder_Signatory_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class QuerySignatureOrder_SignatureOrder_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QuerySignatureOrder_SignatureOrder_Signatory_SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


querySignatureOrderDocument = f"""query signatureOrder($id: ID!) {{
  signatureOrder(id: $id) {{
    ...BasicSignatureOrder
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class QuerySignatureOrderWithDocuments_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  documents: list[QuerySignatureOrderWithDocuments_SignatureOrder_Document]
  evidenceProviders: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[QuerySignatureOrderWithDocuments_SignatureOrder_Signatory]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


type QuerySignatureOrderWithDocuments_SignatureOrder_Document = (
  QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument
)


class QuerySignatureOrderWithDocuments_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory(BaseModel):
  documents: QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: (
    QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureOrder
  )
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: (
    QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatorySigningSequence
  )
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument(BaseModel):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_PdfDocumentForm
  ] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatures: Optional[
    list[QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature]
  ] = Field(default=None)
  title: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument(BaseModel):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatures: Optional[
    list[QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature]
  ] = Field(default=None)
  title: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_PdfDocumentForm(
  BaseModel
):
  enabled: BooleanScalarOutput


type QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature = (
  QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature
)

type QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature = (
  QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature
)


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature(
  BaseModel
):
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory
  ] = Field(default=None)
  signatures: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature
  ]
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature(
  BaseModel
):
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim
  ]
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory
  ] = Field(default=None)
  signingCertificate: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature(
  BaseModel
):
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory
  ] = Field(default=None)
  signatures: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature
  ]
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature(
  BaseModel
):
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory
  ] = Field(default=None)
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim
  ]
  signatory: Optional[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory
  ] = Field(default=None)
  signingCertificate: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate
  timestampToken: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken


class QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


type QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature = (
  QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature
)


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


type QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature = (
  QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature
  | QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature
)


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken(
  BaseModel
):
  timestamp: DateScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature(
  BaseModel
):
  pass


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim
  ]
  signingCertificate: QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature(
  BaseModel
):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature(
  BaseModel
):
  pass


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim
  ]
  jwks: StringScalarOutput
  jwt: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature(
  BaseModel
):
  claims: list[
    QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim
  ]
  signingCertificate: QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim(
  BaseModel
):
  name: StringScalarOutput
  value: StringScalarOutput


class QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate(
  BaseModel
):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


querySignatureOrderWithDocumentsDocument = f"""query signatureOrderWithDocuments($id: ID!) {{
  signatureOrder(id: $id) {{
    ...BasicSignatureOrder
    documents {{
      ...BasicDocument
      ...SignedDocument
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}
{BasicDocumentFragment}
{SignedDocumentFragment}
{SingleSignatureFragment}"""


class QuerySignatory_Signatory(BaseModel):
  documents: QuerySignatory_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[QuerySignatory_Signatory_SignatureEvidenceProvider]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: QuerySignatory_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: QuerySignatory_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QuerySignatory_Signatory_SignatoryDocumentConnection(BaseModel):
  edges: list[
    QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QuerySignatory_Signatory_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class QuerySignatory_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatory_Signatory_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[QuerySignatory_Signatory_SignatureOrder_Signatory]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class QuerySignatory_Signatory_SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: (
    QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  )
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QuerySignatory_Signatory_SignatureOrder_SignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput


class QuerySignatory_Signatory_SignatureOrder_Signatory(BaseModel):
  documents: (
    QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection
  )
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: (
    QuerySignatory_Signatory_SignatureOrder_Signatory_SignatorySigningSequence
  )
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


querySignatoryDocument = f"""query signatory($id: ID!) {{
  signatory(id: $id) {{
    signatureOrder {{
      ...BasicSignatureOrder
    }}
    ...BasicSignatory
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""
type QuerySignatureOrders_Viewer = (
  QuerySignatureOrders_Viewer_AnonymousViewer
  | QuerySignatureOrders_Viewer_Application
  | QuerySignatureOrders_Viewer_BatchSignatoryViewer
  | QuerySignatureOrders_Viewer_SignatoryViewer
  | QuerySignatureOrders_Viewer_UnvalidatedSignatoryViewer
  | QuerySignatureOrders_Viewer_UserViewer
)


class QuerySignatureOrders_Viewer_AnonymousViewer(BaseModel):
  pass


class QuerySignatureOrders_Viewer_Application(BaseModel):
  signatureOrders: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection


class QuerySignatureOrders_Viewer_BatchSignatoryViewer(BaseModel):
  pass


class QuerySignatureOrders_Viewer_SignatoryViewer(BaseModel):
  pass


class QuerySignatureOrders_Viewer_UnvalidatedSignatoryViewer(BaseModel):
  pass


class QuerySignatureOrders_Viewer_UserViewer(BaseModel):
  pass


# A connection from an object to a list of objects of type SignatureOrder
class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection(BaseModel):
  # Information to aid in pagination.
  edges: list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge
  ]


# An edge in a connection from an object to another object of type SignatureOrder
class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge(
  BaseModel
):
  # The item at the end of the edge. Must NOT be an enumerable collection.
  node: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory(
  BaseModel
):
  documents: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


querySignatureOrdersDocument = f"""query signatureOrders($status: SignatureOrderStatus, $first: Int!, $after: String) {{
  viewer {{
    __typename
    ... on Application {{
      signatureOrders(status: $status, first: $first, after: $after) {{
        edges {{
          node {{
            ...BasicSignatureOrder
          }}
        }}
      }}
    }}
  }}
}}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class QueryBatchSignatory_BatchSignatory(BaseModel):
  href: StringScalarOutput
  id: IDScalarOutput
  items: list[QueryBatchSignatory_BatchSignatory_BatchSignatoryItem]
  # The authentication token required for performing batch operations.
  token: StringScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem(BaseModel):
  signatory: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory
  signatureOrder: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory(BaseModel):
  documents: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: (
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder
  )
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder(BaseModel):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider
  ]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory
  ]
  status: SignatureOrderStatus
  title: Optional[StringScalarOutput] = Field(default=None)


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory(
  BaseModel
):
  documents: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider
  ]
  # A link to the signatures frontend, you can send this link to your users to enable them to sign your documents.
  href: StringScalarOutput
  id: IDScalarOutput
  reference: Optional[StringScalarOutput] = Field(default=None)
  roleDeprecated: Optional[StringScalarOutput] = Field(
    alias="role",
    deprecated=deprecated("Deprecated in favor of signingAs"),
    default=None,
  )

  @property
  @deprecated("Deprecated in favor of signingAs")
  def role(self) -> Optional[StringScalarOutput]:
    return self.model_dump().get("roleDeprecated")

  signatoryRole: SignatoryRole
  # Signature order for the signatory.
  signatureOrder: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection(
  BaseModel
):
  edges: list[
    QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge
  ]


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider(
  BaseModel
):
  id: IDScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder(
  BaseModel
):
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  status: SignatureOrderStatus


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence(
  BaseModel
):
  initialNumber: IntScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge(
  BaseModel
):
  node: QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document(
  BaseModel
):
  id: IDScalarOutput


queryBatchSignatoryDocument = f"""query batchSignatory($id: ID!) {{
  batchSignatory(id: $id) {{
    ...BasicBatchSignatory
    items {{
      signatureOrder {{
        ...BasicSignatureOrder
      }}
      signatory {{
        ...BasicSignatory
      }}
    }}
  }}
}}
{BasicBatchSignatoryFragment}
{BasicSignatureOrderFragment}
{BasicSignatoryFragment}"""


class CriiptoSignaturesSDKAsync:
  def __init__(self, clientId: str, clientSecret: str):
    auth = BasicAuth(username=clientId, password=clientSecret)
    headers = {"Criipto-Sdk": "criipto-signatures-python"}
    transport = HTTPXAsyncTransport(
      url="https://signatures-api.criipto.com/v1/graphql", auth=auth, headers=headers
    )
    self.client = Client(transport=transport, fetch_schema_from_transport=False)

  async def createSignatureOrder(
    self, input: CreateSignatureOrderInput
  ) -> CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder:
    query = gql(createSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[CreateSignatureOrder_CreateSignatureOrderOutput]
      .model_validate(result.get("createSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def cleanupSignatureOrder(
    self, input: CleanupSignatureOrderInput
  ) -> CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder:
    query = gql(cleanupSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[CleanupSignatureOrder_CleanupSignatureOrderOutput]
      .model_validate(result.get("cleanupSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def addSignatory(
    self, input: AddSignatoryInput
  ) -> AddSignatory_AddSignatoryOutput_Signatory:
    query = gql(addSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[AddSignatory_AddSignatoryOutput]
      .model_validate(result.get("addSignatory"))
      .root.signatory
    )
    return parsed

  async def addSignatories(
    self, input: AddSignatoriesInput
  ) -> list[AddSignatories_AddSignatoriesOutput_Signatory]:
    query = gql(addSignatoriesDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[AddSignatories_AddSignatoriesOutput]
      .model_validate(result.get("addSignatories"))
      .root.signatories
    )
    return parsed

  async def changeSignatory(
    self, input: ChangeSignatoryInput
  ) -> ChangeSignatory_ChangeSignatoryOutput_Signatory:
    query = gql(changeSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[ChangeSignatory_ChangeSignatoryOutput]
      .model_validate(result.get("changeSignatory"))
      .root.signatory
    )
    return parsed

  async def closeSignatureOrder(
    self, input: CloseSignatureOrderInput
  ) -> CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder:
    query = gql(closeSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[CloseSignatureOrder_CloseSignatureOrderOutput]
      .model_validate(result.get("closeSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def cancelSignatureOrder(
    self, input: CancelSignatureOrderInput
  ) -> CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder:
    query = gql(cancelSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[CancelSignatureOrder_CancelSignatureOrderOutput]
      .model_validate(result.get("cancelSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def signActingAs(
    self, input: SignActingAsInput
  ) -> SignActingAs_SignActingAsOutput_Signatory:
    query = gql(signActingAsDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[SignActingAs_SignActingAsOutput]
      .model_validate(result.get("signActingAs"))
      .root.signatory
    )
    return parsed

  async def validateDocument(
    self, input: ValidateDocumentInput
  ) -> ValidateDocument_ValidateDocumentOutput:
    query = gql(validateDocumentDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[ValidateDocument_ValidateDocumentOutput]
      .model_validate(result.get("validateDocument"))
      .root
    )
    return parsed

  async def extendSignatureOrder(
    self, input: ExtendSignatureOrderInput
  ) -> ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder:
    query = gql(extendSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[ExtendSignatureOrder_ExtendSignatureOrderOutput]
      .model_validate(result.get("extendSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def deleteSignatory(
    self, input: DeleteSignatoryInput
  ) -> DeleteSignatory_DeleteSignatoryOutput_SignatureOrder:
    query = gql(deleteSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[DeleteSignatory_DeleteSignatoryOutput]
      .model_validate(result.get("deleteSignatory"))
      .root.signatureOrder
    )
    return parsed

  async def createBatchSignatory(
    self, input: CreateBatchSignatoryInput
  ) -> CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory:
    query = gql(createBatchSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[CreateBatchSignatory_CreateBatchSignatoryOutput]
      .model_validate(result.get("createBatchSignatory"))
      .root.batchSignatory
    )
    return parsed

  async def changeSignatureOrder(
    self, input: ChangeSignatureOrderInput
  ) -> ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder:
    query = gql(changeSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[ChangeSignatureOrder_ChangeSignatureOrderOutput]
      .model_validate(result.get("changeSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  async def querySignatureOrder(
    self, id: IDScalarInput
  ) -> QuerySignatureOrder_SignatureOrder:
    query = gql(querySignatureOrderDocument)
    query.variable_values = {"id": id}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[QuerySignatureOrder_SignatureOrder]
      .model_validate(result.get("signatureOrder"))
      .root
    )
    return parsed

  async def querySignatureOrderWithDocuments(
    self, id: IDScalarInput
  ) -> QuerySignatureOrderWithDocuments_SignatureOrder:
    query = gql(querySignatureOrderWithDocumentsDocument)
    query.variable_values = {"id": id}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[QuerySignatureOrderWithDocuments_SignatureOrder]
      .model_validate(result.get("signatureOrder"))
      .root
    )
    return parsed

  async def querySignatory(self, id: IDScalarInput) -> QuerySignatory_Signatory:
    query = gql(querySignatoryDocument)
    query.variable_values = {"id": id}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[QuerySignatory_Signatory].model_validate(result.get("signatory")).root
    )
    return parsed

  async def querySignatureOrders(
    self,
    first: IntScalarInput,
    status: Optional[SignatureOrderStatus] = None,
    after: Optional[StringScalarInput] = None,
  ) -> QuerySignatureOrders_Viewer:
    query = gql(querySignatureOrdersDocument)
    query.variable_values = {
      "first": first,
      "status": status if status is not None else "",
      "after": after,
    }
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[QuerySignatureOrders_Viewer].model_validate(result.get("viewer")).root
    )
    return parsed

  async def queryBatchSignatory(
    self, id: IDScalarInput
  ) -> QueryBatchSignatory_BatchSignatory:
    query = gql(queryBatchSignatoryDocument)
    query.variable_values = {"id": id}
    result = await self.client.execute_async(query)
    parsed = (
      RootModel[QueryBatchSignatory_BatchSignatory]
      .model_validate(result.get("batchSignatory"))
      .root
    )
    return parsed


class CriiptoSignaturesSDKSync:
  def __init__(self, clientId: str, clientSecret: str):
    auth = BasicAuth(username=clientId, password=clientSecret)
    headers = {"Criipto-Sdk": "criipto-signatures-python"}
    transport = HTTPXTransport(
      url="https://signatures-api.criipto.com/v1/graphql", auth=auth, headers=headers
    )
    self.client = Client(transport=transport, fetch_schema_from_transport=False)

  def createSignatureOrder(
    self, input: CreateSignatureOrderInput
  ) -> CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder:
    query = gql(createSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[CreateSignatureOrder_CreateSignatureOrderOutput]
      .model_validate(result.get("createSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def cleanupSignatureOrder(
    self, input: CleanupSignatureOrderInput
  ) -> CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder:
    query = gql(cleanupSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[CleanupSignatureOrder_CleanupSignatureOrderOutput]
      .model_validate(result.get("cleanupSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def addSignatory(
    self, input: AddSignatoryInput
  ) -> AddSignatory_AddSignatoryOutput_Signatory:
    query = gql(addSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[AddSignatory_AddSignatoryOutput]
      .model_validate(result.get("addSignatory"))
      .root.signatory
    )
    return parsed

  def addSignatories(
    self, input: AddSignatoriesInput
  ) -> list[AddSignatories_AddSignatoriesOutput_Signatory]:
    query = gql(addSignatoriesDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[AddSignatories_AddSignatoriesOutput]
      .model_validate(result.get("addSignatories"))
      .root.signatories
    )
    return parsed

  def changeSignatory(
    self, input: ChangeSignatoryInput
  ) -> ChangeSignatory_ChangeSignatoryOutput_Signatory:
    query = gql(changeSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[ChangeSignatory_ChangeSignatoryOutput]
      .model_validate(result.get("changeSignatory"))
      .root.signatory
    )
    return parsed

  def closeSignatureOrder(
    self, input: CloseSignatureOrderInput
  ) -> CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder:
    query = gql(closeSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[CloseSignatureOrder_CloseSignatureOrderOutput]
      .model_validate(result.get("closeSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def cancelSignatureOrder(
    self, input: CancelSignatureOrderInput
  ) -> CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder:
    query = gql(cancelSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[CancelSignatureOrder_CancelSignatureOrderOutput]
      .model_validate(result.get("cancelSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def signActingAs(
    self, input: SignActingAsInput
  ) -> SignActingAs_SignActingAsOutput_Signatory:
    query = gql(signActingAsDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[SignActingAs_SignActingAsOutput]
      .model_validate(result.get("signActingAs"))
      .root.signatory
    )
    return parsed

  def validateDocument(
    self, input: ValidateDocumentInput
  ) -> ValidateDocument_ValidateDocumentOutput:
    query = gql(validateDocumentDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[ValidateDocument_ValidateDocumentOutput]
      .model_validate(result.get("validateDocument"))
      .root
    )
    return parsed

  def extendSignatureOrder(
    self, input: ExtendSignatureOrderInput
  ) -> ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder:
    query = gql(extendSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[ExtendSignatureOrder_ExtendSignatureOrderOutput]
      .model_validate(result.get("extendSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def deleteSignatory(
    self, input: DeleteSignatoryInput
  ) -> DeleteSignatory_DeleteSignatoryOutput_SignatureOrder:
    query = gql(deleteSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[DeleteSignatory_DeleteSignatoryOutput]
      .model_validate(result.get("deleteSignatory"))
      .root.signatureOrder
    )
    return parsed

  def createBatchSignatory(
    self, input: CreateBatchSignatoryInput
  ) -> CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory:
    query = gql(createBatchSignatoryDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[CreateBatchSignatory_CreateBatchSignatoryOutput]
      .model_validate(result.get("createBatchSignatory"))
      .root.batchSignatory
    )
    return parsed

  def changeSignatureOrder(
    self, input: ChangeSignatureOrderInput
  ) -> ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder:
    query = gql(changeSignatureOrderDocument)
    query.variable_values = {"input": input.model_dump()}
    result = self.client.execute(query)
    parsed = (
      RootModel[ChangeSignatureOrder_ChangeSignatureOrderOutput]
      .model_validate(result.get("changeSignatureOrder"))
      .root.signatureOrder
    )
    return parsed

  def querySignatureOrder(
    self, id: IDScalarInput
  ) -> QuerySignatureOrder_SignatureOrder:
    query = gql(querySignatureOrderDocument)
    query.variable_values = {"id": id}
    result = self.client.execute(query)
    parsed = (
      RootModel[QuerySignatureOrder_SignatureOrder]
      .model_validate(result.get("signatureOrder"))
      .root
    )
    return parsed

  def querySignatureOrderWithDocuments(
    self, id: IDScalarInput
  ) -> QuerySignatureOrderWithDocuments_SignatureOrder:
    query = gql(querySignatureOrderWithDocumentsDocument)
    query.variable_values = {"id": id}
    result = self.client.execute(query)
    parsed = (
      RootModel[QuerySignatureOrderWithDocuments_SignatureOrder]
      .model_validate(result.get("signatureOrder"))
      .root
    )
    return parsed

  def querySignatory(self, id: IDScalarInput) -> QuerySignatory_Signatory:
    query = gql(querySignatoryDocument)
    query.variable_values = {"id": id}
    result = self.client.execute(query)
    parsed = (
      RootModel[QuerySignatory_Signatory].model_validate(result.get("signatory")).root
    )
    return parsed

  def querySignatureOrders(
    self,
    first: IntScalarInput,
    status: Optional[SignatureOrderStatus] = None,
    after: Optional[StringScalarInput] = None,
  ) -> QuerySignatureOrders_Viewer:
    query = gql(querySignatureOrdersDocument)
    query.variable_values = {
      "first": first,
      "status": status if status is not None else "",
      "after": after,
    }
    result = self.client.execute(query)
    parsed = (
      RootModel[QuerySignatureOrders_Viewer].model_validate(result.get("viewer")).root
    )
    return parsed

  def queryBatchSignatory(
    self, id: IDScalarInput
  ) -> QueryBatchSignatory_BatchSignatory:
    query = gql(queryBatchSignatoryDocument)
    query.variable_values = {"id": id}
    result = self.client.execute(query)
    parsed = (
      RootModel[QueryBatchSignatory_BatchSignatory]
      .model_validate(result.get("batchSignatory"))
      .root
    )
    return parsed


CreateSignatureOrder_CreateSignatureOrderOutput.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_XmlDocument.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CreateSignatureOrder_CreateSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_XmlDocument.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CleanupSignatureOrder_CleanupSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
AddSignatory_AddSignatoryOutput.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatureEvidenceProvider.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatureOrder.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatorySigningSequence.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
AddSignatory_AddSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
AddSignatories_AddSignatoriesOutput.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatureEvidenceProvider.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatureOrder.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatorySigningSequence.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
AddSignatories_AddSignatoriesOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureEvidenceProvider.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatureOrder.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatorySigningSequence.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
ChangeSignatory_ChangeSignatoryOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
CloseSignatureOrder_CloseSignatureOrderOutput_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_XmlDocument.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CancelSignatureOrder_CancelSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
SignActingAs_SignActingAsOutput.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatureEvidenceProvider.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatureOrder.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatorySigningSequence.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
SignActingAs_SignActingAsOutput_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
ValidateDocument_ValidateDocumentOutput.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_XmlDocument.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
ExtendSignatureOrder_ExtendSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
DeleteSignatory_DeleteSignatoryOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
CreateBatchSignatory_CreateBatchSignatoryOutput_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
ChangeSignatureOrder_ChangeSignatureOrderOutput_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QuerySignatureOrder_SignatureOrder.model_rebuild()
QuerySignatureOrder_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QuerySignatureOrder_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_PdfDocumentForm.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_DrawableSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_EmptySignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_JWTSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_Certificate.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_NorwegianBankIdSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_DrawableSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_EmptySignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_JWTSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Signatory.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_Certificate.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_NorwegianBankIdSignature_TimestampToken.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_EmptySignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_DrawableSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_EmptySignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_PdfDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_JWTSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_JWTClaim.model_rebuild()
QuerySignatureOrderWithDocuments_SignatureOrder_Document_XmlDocument_Signature_CompositeSignature_SingleSignature_NorwegianBankIdSignature_Certificate.model_rebuild()
QuerySignatory_Signatory.model_rebuild()
QuerySignatory_Signatory_SignatoryDocumentConnection.model_rebuild()
QuerySignatory_Signatory_SignatureEvidenceProvider.model_rebuild()
QuerySignatory_Signatory_SignatureOrder.model_rebuild()
QuerySignatory_Signatory_SignatorySigningSequence.model_rebuild()
QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory.model_rebuild()
QuerySignatory_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QuerySignatory_Signatory_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QuerySignatureOrders_Viewer_AnonymousViewer.model_rebuild()
QuerySignatureOrders_Viewer_Application.model_rebuild()
QuerySignatureOrders_Viewer_BatchSignatoryViewer.model_rebuild()
QuerySignatureOrders_Viewer_SignatoryViewer.model_rebuild()
QuerySignatureOrders_Viewer_UnvalidatedSignatoryViewer.model_rebuild()
QuerySignatureOrders_Viewer_UserViewer.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QuerySignatureOrders_Viewer_Application_SignatureOrderConnection_SignatureOrderEdge_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QueryBatchSignatory_BatchSignatory.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureEvidenceProvider.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatureOrder.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatorySigningSequence.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_SignatureEvidenceProvider.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureEvidenceProvider.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatureOrder.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatorySigningSequence.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge.model_rebuild()
QueryBatchSignatory_BatchSignatory_BatchSignatoryItem_SignatureOrder_Signatory_SignatoryDocumentConnection_SignatoryDocumentEdge_Document.model_rebuild()
