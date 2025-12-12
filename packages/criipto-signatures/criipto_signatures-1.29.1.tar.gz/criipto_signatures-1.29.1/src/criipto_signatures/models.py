from __future__ import annotations
from .utils import CustomBlobInput, CustomBlobOutput
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
from warnings import deprecated

type IDScalarInput = str
type IDScalarOutput = str
type StringScalarInput = str
type StringScalarOutput = str
type IntScalarInput = int
type IntScalarOutput = int
type FloatScalarInput = float
type FloatScalarOutput = float
type BooleanScalarInput = bool
type BooleanScalarOutput = bool
type BlobScalarInput = CustomBlobInput
type BlobScalarOutput = CustomBlobOutput
type DateScalarInput = str
type DateScalarOutput = str
type DateTimeScalarInput = str
type DateTimeScalarOutput = str
type URIScalarInput = str
type URIScalarOutput = str


class AddSignatoriesInput(BaseModel):
  signatories: list[CreateSignatureOrderSignatoryInput]
  signatureOrderId: IDScalarInput


class AddSignatoriesOutput(BaseModel):
  signatories: list[Signatory]
  signatureOrder: SignatureOrder


class AddSignatoryInput(BaseModel):
  # Define a subset of documents for the signatory. Must be a non-empty list. Leave null for all documents.
  documents: Optional[list[SignatoryDocumentInput]] = Field(default=None)
  # Selectively enable evidence providers for this signatory.
  evidenceProviders: Optional[list[SignatoryEvidenceProviderInput]] = Field(
    default=None
  )
  evidenceValidation: Optional[list[SignatoryEvidenceValidationInput]] = Field(
    default=None
  )
  # Will not be displayed to signatories, can be used as a reference to your own system.
  reference: Optional[StringScalarInput] = Field(default=None)
  # Deprecated in favor of 'signingAs'. Define a role for the signatory, i.e. 'Chairman'. Will be visible in the document output.
  role: Optional[StringScalarInput] = Field(default=None)
  # Denotes the signatory role, e.g. SIGNER or VIEWER. Defaults to SIGNER.
  signatoryRole: Optional[SignatoryRole] = Field(default=None)
  signatureAppearance: Optional[SignatureAppearanceInput] = Field(default=None)
  signatureOrderId: IDScalarInput
  # Define the who signatory is signing as, i.e., 'Chairman'. Will be visible in the document output.
  signingAs: Optional[StringScalarInput] = Field(default=None)
  # Defines signing sequence order for sequential signing. If two signatories have the same number they can sign in parallel. Default: 2147483647
  signingSequence: Optional[IntScalarInput] = Field(default=None)
  # Override UI settings for signatory, defaults to UI settings for signature order
  ui: Optional[SignatoryUIInput] = Field(default=None)


class AddSignatoryOutput(BaseModel):
  signatory: Signatory
  signatureOrder: SignatureOrder


class AllOfEvidenceProviderInput(BaseModel):
  providers: list[SingleEvidenceProviderInput]


class AllOfSignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput
  providers: list[SingleSignatureEvidenceProvider]


class AnonymousViewer(BaseModel):
  authenticated: BooleanScalarOutput
  id: IDScalarOutput


class Application(BaseModel):
  apiKeys: list[ApplicationApiKey]
  id: IDScalarOutput
  name: StringScalarOutput
  signatureOrders: SignatureOrderConnection
  # Tenants are only accessable from user viewers
  tenant: Optional[Tenant] = Field(default=None)
  verifyApplication: VerifyApplication
  webhookLogs: list[WebhookInvocation]


class ApplicationApiKey(BaseModel):
  clientId: StringScalarOutput
  clientSecret: Optional[StringScalarOutput] = Field(default=None)
  id: IDScalarOutput
  mode: ApplicationApiKeyMode
  note: Optional[StringScalarOutput] = Field(default=None)


class ApplicationApiKeyMode(StrEnum):
  READ_ONLY = "READ_ONLY"
  READ_WRITE = "READ_WRITE"


class BatchSignatory(BaseModel):
  href: StringScalarOutput
  id: IDScalarOutput
  items: list[BatchSignatoryItem]
  # The authentication token required for performing batch operations.
  token: StringScalarOutput
  traceId: StringScalarOutput
  ui: SignatureOrderUI


class BatchSignatoryItem(BaseModel):
  signatory: Signatory
  signatureOrder: SignatureOrder


class BatchSignatoryItemInput(BaseModel):
  signatoryId: StringScalarInput
  signatureOrderId: StringScalarInput


class BatchSignatoryViewer(BaseModel):
  authenticated: BooleanScalarOutput
  batchSignatoryId: IDScalarOutput
  documents: SignatoryDocumentConnection
  evidenceProviders: list[SignatureEvidenceProvider]
  id: IDScalarOutput
  signer: BooleanScalarOutput
  status: SignatoryStatus
  traceId: StringScalarOutput
  ui: SignatureOrderUI


class CancelSignatureOrderInput(BaseModel):
  signatureOrderId: IDScalarInput


class CancelSignatureOrderOutput(BaseModel):
  signatureOrder: SignatureOrder


class Certificate(BaseModel):
  issuer: StringScalarOutput
  raw: BlobScalarOutput
  subject: StringScalarOutput


class ChangeSignatoryInput(BaseModel):
  # Define a subset of documents for the signatory. Must be a non-empty list. Leave null for all documents.
  documents: Optional[list[SignatoryDocumentInput]] = Field(default=None)
  # Selectively enable evidence providers for this signatory.
  evidenceProviders: Optional[list[SignatoryEvidenceProviderInput]] = Field(
    default=None
  )
  evidenceValidation: Optional[list[SignatoryEvidenceValidationInput]] = Field(
    default=None
  )
  # Will not be displayed to signatories, can be used as a reference to your own system.
  reference: Optional[StringScalarInput] = Field(default=None)
  # Deprecated in favor of 'signingAs'. Define a role for the signatory, i.e. 'Chairman'. Will be visible in the document output.
  role: Optional[StringScalarInput] = Field(default=None)
  signatoryId: IDScalarInput
  signatureAppearance: Optional[SignatureAppearanceInput] = Field(default=None)
  # Define the who signatory is signing as, i.e., 'Chairman'. Will be visible in the document output.
  signingAs: Optional[StringScalarInput] = Field(default=None)
  # Defines signing sequence order for sequential signing. If two signatories have the same number they can sign in parallel. Default: 2147483647
  signingSequence: Optional[IntScalarInput] = Field(default=None)
  # Override UI settings for signatory, defaults to UI settings for signature order
  ui: Optional[SignatoryUIInput] = Field(default=None)


class ChangeSignatoryOutput(BaseModel):
  signatory: Signatory
  signatureOrder: SignatureOrder


class ChangeSignatureOrderInput(BaseModel):
  # Max allowed signatories (as it influences pages needed for seals). Cannot be changed after first signer.
  maxSignatories: Optional[IntScalarInput] = Field(default=None)
  signatureOrderId: IDScalarInput
  # Signature order webhook settings
  webhook: Optional[CreateSignatureOrderWebhookInput] = Field(default=None)


class ChangeSignatureOrderOutput(BaseModel):
  signatureOrder: SignatureOrder


class CleanupSignatureOrderInput(BaseModel):
  signatureOrderId: IDScalarInput


class CleanupSignatureOrderOutput(BaseModel):
  signatureOrder: SignatureOrder


class CloseSignatureOrderInput(BaseModel):
  # Retains documents on Criipto servers after closing a signature order. You MUST manually call the cleanupSignatureOrder mutation when you are sure you have downloaded the blobs. Maximum value is 7 days.
  retainDocumentsForDays: Optional[IntScalarInput] = Field(default=None)
  signatureOrderId: IDScalarInput


class CloseSignatureOrderOutput(BaseModel):
  signatureOrder: SignatureOrder


class CompleteCriiptoVerifyEvidenceProviderInput(BaseModel):
  code: StringScalarInput
  state: StringScalarInput


class CompleteCriiptoVerifyEvidenceProviderOutput(BaseModel):
  jwt: StringScalarOutput


class CompositeSignature(BaseModel):
  signatory: Optional[Signatory] = Field(default=None)
  signatures: list[SingleSignature]
  timestampToken: TimestampToken


class CreateApplicationApiKeyInput(BaseModel):
  applicationId: IDScalarInput
  mode: Optional[ApplicationApiKeyMode] = Field(default=None)
  note: Optional[StringScalarInput] = Field(default=None)


class CreateApplicationApiKeyOutput(BaseModel):
  apiKey: ApplicationApiKey
  application: Application


class CreateApplicationInput(BaseModel):
  name: StringScalarInput
  tenantId: IDScalarInput
  verifyApplicationDomain: StringScalarInput
  verifyApplicationEnvironment: VerifyApplicationEnvironment
  verifyApplicationRealm: StringScalarInput


class CreateApplicationOutput(BaseModel):
  apiKey: ApplicationApiKey
  application: Application
  tenant: Tenant


class CreateBatchSignatoryInput(BaseModel):
  items: list[BatchSignatoryItemInput]
  # UI settings for batch signatory, will use defaults otherwise (will not use UI settings from sub signatories)
  ui: Optional[SignatoryUIInput] = Field(default=None)


class CreateBatchSignatoryOutput(BaseModel):
  batchSignatory: BatchSignatory


class CreateSignatureOrderInput(BaseModel):
  # By default signatories will be prompted to sign with a Criipto Verify based e-ID, this setting disables it.
  disableVerifyEvidenceProvider: Optional[BooleanScalarInput] = Field(default=None)
  documents: list[DocumentInput]
  # Define evidence providers for signature order if not using built-in Criipto Verify for e-IDs
  evidenceProviders: Optional[list[EvidenceProviderInput]] = Field(default=None)
  # Defines when a signatory must be validated, default is when signing, but can be expanded to also be required when viewing documents.
  evidenceValidationStages: Optional[list[EvidenceValidationStage]] = Field(
    default=None
  )
  # When this signature order will auto-close/expire at exactly in one of the following ISO-8601 formats: yyyy-MM-ddTHH:mm:ssZ, yyyy-MM-ddTHH:mm:ss.ffZ, yyyy-MM-ddTHH:mm:ss.fffZ, yyyy-MM-ddTHH:mm:ssK, yyyy-MM-ddTHH:mm:ss.ffK, yyyy-MM-ddTHH:mm:ss.fffK. Cannot be provided with `expiresInDays`.
  expiresAt: Optional[StringScalarInput] = Field(default=None)
  # When this signature order will auto-close/expire. Default 90 days. Cannot be provided with `expiresAt`
  expiresInDays: Optional[IntScalarInput] = Field(default=None)
  # Attempt to automatically fix document formatting errors if possible. Default 'true'.
  fixDocumentFormattingErrors: Optional[BooleanScalarInput] = Field(default=None)
  # Max allowed signatories (as it influences pages needed for seals). Default 14.
  maxSignatories: Optional[IntScalarInput] = Field(default=None)
  signatories: Optional[list[CreateSignatureOrderSignatoryInput]] = Field(default=None)
  # Configure appearance of signatures inside documents
  signatureAppearance: Optional[SignatureAppearanceInput] = Field(default=None)
  # Timezone to render signature seals in, default UTC.
  timezone: Optional[StringScalarInput] = Field(default=None)
  title: Optional[StringScalarInput] = Field(default=None)
  # Various settings for how the UI is presented to the signatory.
  ui: Optional[CreateSignatureOrderUIInput] = Field(default=None)
  # Signature order webhook settings
  webhook: Optional[CreateSignatureOrderWebhookInput] = Field(default=None)


class CreateSignatureOrderOutput(BaseModel):
  application: Application
  signatureOrder: SignatureOrder


class CreateSignatureOrderSignatoryInput(BaseModel):
  # Define a subset of documents for the signatory. Must be a non-empty list. Leave null for all documents.
  documents: Optional[list[SignatoryDocumentInput]] = Field(default=None)
  # Selectively enable evidence providers for this signatory.
  evidenceProviders: Optional[list[SignatoryEvidenceProviderInput]] = Field(
    default=None
  )
  evidenceValidation: Optional[list[SignatoryEvidenceValidationInput]] = Field(
    default=None
  )
  # Will not be displayed to signatories, can be used as a reference to your own system.
  reference: Optional[StringScalarInput] = Field(default=None)
  # Deprecated in favor of 'signingAs'. Define a role for the signatory, i.e. 'Chairman'. Will be visible in the document output.
  role: Optional[StringScalarInput] = Field(default=None)
  # Denotes the signatory role, e.g. SIGNER or VIEWER. Defaults to SIGNER.
  signatoryRole: Optional[SignatoryRole] = Field(default=None)
  signatureAppearance: Optional[SignatureAppearanceInput] = Field(default=None)
  # Define the who signatory is signing as, i.e., 'Chairman'. Will be visible in the document output.
  signingAs: Optional[StringScalarInput] = Field(default=None)
  # Defines signing sequence order for sequential signing. If two signatories have the same number they can sign in parallel. Default: 2147483647
  signingSequence: Optional[IntScalarInput] = Field(default=None)
  # Override UI settings for signatory, defaults to UI settings for signature order
  ui: Optional[SignatoryUIInput] = Field(default=None)


class CreateSignatureOrderUIInput(BaseModel):
  # Removes the UI options to reject a document or signature order.
  disableRejection: Optional[BooleanScalarInput] = Field(default=None)
  # Adds an UI option for the signatory to cancel, will return to 'signatoryRedirectUri' if defined.
  enableCancel: Optional[BooleanScalarInput] = Field(default=None)
  # The language of texts rendered to the signatory.
  language: Optional[Language] = Field(default=None)
  # Define a logo to be shown in the signatory UI.
  logo: Optional[SignatureOrderUILogoInput] = Field(default=None)
  # Renders a UI layer for PDF annotations, such as links, making them interactive in the UI/browser
  renderPdfAnnotationLayer: Optional[BooleanScalarInput] = Field(default=None)
  # The signatory will be redirected to this URL after signing or rejected the signature order.
  signatoryRedirectUri: Optional[StringScalarInput] = Field(default=None)
  # Add stylesheet/css via an absolute HTTPS URL.
  stylesheet: Optional[StringScalarInput] = Field(default=None)


class CreateSignatureOrderWebhookInput(BaseModel):
  # If defined, webhook invocations will have a X-Criipto-Signature header containing a HMAC-SHA256 signature (as a base64 string) of the webhook request body (utf-8). The secret should be between 256 and 512 bits.
  secret: Optional[BlobScalarInput] = Field(default=None)
  # Webhook url. POST requests will be executed towards this URL on certain signatory events.
  url: StringScalarInput
  # Validates webhook connectivity by triggering a WEBHOOK_VALIDATION event, your webhook must respond within 5 seconds with 200/OK or the signature order creation will fail.
  validateConnectivity: Optional[BooleanScalarInput] = Field(default=None)


class CriiptoVerifyEvidenceProviderRedirect(BaseModel):
  redirectUri: StringScalarOutput
  state: StringScalarOutput


class CriiptoVerifyEvidenceProviderVersion(StrEnum):
  V1 = "V1"
  V2 = "V2"


# Criipto Verify based evidence for signatures.
class CriiptoVerifyProviderInput(BaseModel):
  acrValues: Optional[list[StringScalarInput]] = Field(default=None)
  alwaysRedirect: Optional[BooleanScalarInput] = Field(default=None)
  # Define additional valid audiences (besides the main client_id) for the Criipto Verify domain/issuer underlying the application.
  audiences: Optional[list[StringScalarInput]] = Field(default=None)
  # Set a custom login_hint for the underlying authentication request.
  loginHint: Optional[StringScalarInput] = Field(default=None)
  # Messages displayed when performing authentication (only supported by DKMitID currently).
  message: Optional[StringScalarInput] = Field(default=None)
  # Set a custom scope for the underlying authentication request.
  scope: Optional[StringScalarInput] = Field(default=None)
  # Enforces that signatories sign by unique evidence by comparing the values of previous evidence on the key you define. For Criipto Verify you likely want to use `sub` which is a unique pseudonym value present in all e-ID tokens issued.
  uniqueEvidenceKey: Optional[StringScalarInput] = Field(default=None)
  version: Optional[CriiptoVerifyEvidenceProviderVersion] = Field(default=None)


class CriiptoVerifySignatureEvidenceProvider(BaseModel):
  acrValues: list[StringScalarOutput]
  alwaysRedirect: BooleanScalarOutput
  audience: StringScalarOutput
  audiences: list[StringScalarOutput]
  clientID: StringScalarOutput
  domain: StringScalarOutput
  environment: Optional[VerifyApplicationEnvironment] = Field(default=None)
  id: IDScalarOutput
  loginHint: Optional[StringScalarOutput] = Field(default=None)
  message: Optional[StringScalarOutput] = Field(default=None)
  name: StringScalarOutput
  scope: Optional[StringScalarOutput] = Field(default=None)
  version: CriiptoVerifyEvidenceProviderVersion


class DeleteApplicationApiKeyInput(BaseModel):
  apiKeyId: IDScalarInput
  applicationId: IDScalarInput


class DeleteApplicationApiKeyOutput(BaseModel):
  application: Application


class DeleteSignatoryInput(BaseModel):
  signatoryId: IDScalarInput
  signatureOrderId: IDScalarInput


class DeleteSignatoryOutput(BaseModel):
  signatureOrder: SignatureOrder


class DeviceInput(BaseModel):
  os: Optional[DeviceOperatingSystem] = Field(default=None)


class DeviceOperatingSystem(StrEnum):
  ANDROID = "ANDROID"
  IOS = "IOS"


type Document = PdfDocument | XmlDocument


class DocumentIDLocation(StrEnum):
  BOTTOM = "BOTTOM"
  LEFT = "LEFT"
  RIGHT = "RIGHT"
  TOP = "TOP"


class DocumentInput(BaseModel):
  pdf: Optional[PadesDocumentInput] = Field(default=None)
  # When enabled, will remove any existing signatures from the document before storing. (PDF only)
  removePreviousSignatures: Optional[BooleanScalarInput] = Field(default=None)
  # XML signing is coming soon, reach out to learn more.
  xml: Optional[XadesDocumentInput] = Field(default=None)


# Document storage mode. Temporary documents will be deleted once completed.
class DocumentStorageMode(StrEnum):
  Temporary = "Temporary"


class DownloadVerificationCriiptoVerifyInput(BaseModel):
  jwt: StringScalarInput


class DownloadVerificationInput(BaseModel):
  criiptoVerify: Optional[DownloadVerificationCriiptoVerifyInput] = Field(default=None)
  oidc: Optional[DownloadVerificationOidcInput] = Field(default=None)


class DownloadVerificationOidcInput(BaseModel):
  jwt: StringScalarInput


# Hand drawn signature evidence for signatures.
class DrawableEvidenceProviderInput(BaseModel):
  # Required minimum height of drawed area in pixels.
  minimumHeight: Optional[IntScalarInput] = Field(default=None)
  # Required minimum width of drawed area in pixels.
  minimumWidth: Optional[IntScalarInput] = Field(default=None)
  requireName: Optional[BooleanScalarInput] = Field(default=None)


class DrawableSignature(BaseModel):
  image: BlobScalarOutput
  name: Optional[StringScalarOutput] = Field(default=None)
  signatory: Optional[Signatory] = Field(default=None)
  timestampToken: TimestampToken


class DrawableSignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput
  minimumHeight: Optional[IntScalarOutput] = Field(default=None)
  minimumWidth: Optional[IntScalarOutput] = Field(default=None)
  requireName: BooleanScalarOutput


class EmptySignature(BaseModel):
  signatory: Optional[Signatory] = Field(default=None)
  timestampToken: TimestampToken


# Must define a evidence provider subsection.
class EvidenceProviderInput(BaseModel):
  allOf: Optional[AllOfEvidenceProviderInput] = Field(default=None)
  # Criipto Verify based evidence for signatures.
  criiptoVerify: Optional[CriiptoVerifyProviderInput] = Field(default=None)
  # Hand drawn signature evidence for signatures.
  drawable: Optional[DrawableEvidenceProviderInput] = Field(default=None)
  # Determined if this evidence provider should be enabled by signatories by default. Default true
  enabledByDefault: Optional[BooleanScalarInput] = Field(default=None)
  # TEST environment only. Does not manipulate the PDF, use for integration or webhook testing.
  noop: Optional[NoopEvidenceProviderInput] = Field(default=None)
  # Deprecated
  oidc: Optional[OidcEvidenceProviderInput] = Field(default=None)


class EvidenceValidationStage(StrEnum):
  SIGN = "SIGN"
  VIEW = "VIEW"


class ExtendSignatureOrderInput(BaseModel):
  # Expiration to add to order, in days, max 30.
  additionalExpirationInDays: IntScalarInput
  signatureOrderId: IDScalarInput


class ExtendSignatureOrderOutput(BaseModel):
  signatureOrder: SignatureOrder


class JWTClaim(BaseModel):
  name: StringScalarOutput
  value: StringScalarOutput


class JWTSignature(BaseModel):
  claims: list[JWTClaim]
  jwks: StringScalarOutput
  jwt: StringScalarOutput
  signatory: Optional[Signatory] = Field(default=None)
  timestampToken: TimestampToken


class Language(StrEnum):
  DA_DK = "DA_DK"
  EN_US = "EN_US"
  NB_NO = "NB_NO"
  SV_SE = "SV_SE"


class Mutation(BaseModel):
  # Add multiple signatures to your signature order.
  addSignatories: Optional[AddSignatoriesOutput] = Field(default=None)
  # Add a signatory to your signature order.
  addSignatory: Optional[AddSignatoryOutput] = Field(default=None)
  # Cancels the signature order without closing it, use if you no longer need a signature order. Documents are deleted from storage after cancelling.
  cancelSignatureOrder: Optional[CancelSignatureOrderOutput] = Field(default=None)
  # Change an existing signatory
  changeSignatory: Optional[ChangeSignatoryOutput] = Field(default=None)
  # Change an existing signature order
  changeSignatureOrder: Optional[ChangeSignatureOrderOutput] = Field(default=None)
  # Cleans up the signature order and removes any saved documents from the servers.
  cleanupSignatureOrder: Optional[CleanupSignatureOrderOutput] = Field(default=None)
  # Finalizes the documents in the signature order and returns them to you as blobs. Documents are deleted from storage after closing.
  closeSignatureOrder: Optional[CloseSignatureOrderOutput] = Field(default=None)
  completeCriiptoVerifyEvidenceProvider: Optional[
    CompleteCriiptoVerifyEvidenceProviderOutput
  ] = Field(default=None)
  # Creates a signature application for a given tenant.
  createApplication: Optional[CreateApplicationOutput] = Field(default=None)
  # Creates a new set of api credentials for an existing application.
  createApplicationApiKey: Optional[CreateApplicationApiKeyOutput] = Field(default=None)
  createBatchSignatory: Optional[CreateBatchSignatoryOutput] = Field(default=None)
  # Creates a signature order to be signed.
  createSignatureOrder: Optional[CreateSignatureOrderOutput] = Field(default=None)
  # Deletes a set of API credentials for an application.
  deleteApplicationApiKey: Optional[DeleteApplicationApiKeyOutput] = Field(default=None)
  # Delete a signatory from a signature order
  deleteSignatory: Optional[DeleteSignatoryOutput] = Field(default=None)
  # Extends the expiration of the signature order.
  extendSignatureOrder: Optional[ExtendSignatureOrderOutput] = Field(default=None)
  # Refreshes the client secret for an existing set of API credentials. Warning: The old client secret will stop working immediately.
  refreshApplicationApiKey: Optional[RefreshApplicationApiKeyOutput] = Field(
    default=None
  )
  # Used by Signatory frontends to reject a signature order in full.
  rejectSignatureOrder: Optional[RejectSignatureOrderOutput] = Field(default=None)
  retrySignatureOrderWebhook: Optional[RetrySignatureOrderWebhookOutput] = Field(
    default=None
  )
  # Used by Signatory frontends to sign the documents in a signature order.
  sign: Optional[SignOutput] = Field(default=None)
  # Sign with API credentials acting as a specific signatory. The signatory MUST be preapproved in this case.
  signActingAs: Optional[SignActingAsOutput] = Field(default=None)
  # Signatory frontend use only.
  signatoryBeacon: Optional[SignatoryBeaconOutput] = Field(default=None)
  # Signatory frontend use only.
  startCriiptoVerifyEvidenceProvider: Optional[
    StartCriiptoVerifyEvidenceProviderOutput
  ] = Field(default=None)
  # Signatory frontend use only.
  trackSignatory: Optional[TrackSignatoryOutput] = Field(default=None)
  # Used by Signatory frontends to mark documents as opened, approved or rejected.
  updateSignatoryDocumentStatus: Optional[UpdateSignatoryDocumentStatusOutput] = Field(
    default=None
  )
  validateDocument: Optional[ValidateDocumentOutput] = Field(default=None)


# TEST only. Allows empty signatures for testing.
class NoopEvidenceProviderInput(BaseModel):
  name: StringScalarInput


class NoopSignatureEvidenceProvider(BaseModel):
  id: IDScalarOutput
  name: StringScalarOutput


class NorwegianBankIdSignature(BaseModel):
  claims: list[JWTClaim]
  signatory: Optional[Signatory] = Field(default=None)
  signingCertificate: Certificate
  timestampToken: TimestampToken


# OIDC/JWT based evidence for signatures.
class OidcEvidenceProviderInput(BaseModel):
  acrValues: Optional[list[StringScalarInput]] = Field(default=None)
  alwaysRedirect: Optional[BooleanScalarInput] = Field(default=None)
  audience: StringScalarInput
  clientID: StringScalarInput
  domain: StringScalarInput
  name: StringScalarInput
  # Enforces that signatories sign by unique evidence by comparing the values of previous evidence on the key you define.
  uniqueEvidenceKey: Optional[StringScalarInput] = Field(default=None)


class OidcJWTSignatureEvidenceProvider(BaseModel):
  acrValues: list[StringScalarOutput]
  alwaysRedirect: BooleanScalarOutput
  clientID: StringScalarOutput
  domain: StringScalarOutput
  id: IDScalarOutput
  name: StringScalarOutput


class PadesDocumentFormInput(BaseModel):
  enabled: BooleanScalarInput


class PadesDocumentInput(BaseModel):
  blob: BlobScalarInput
  # Will add a unique identifier for the document to the specified margin of each page. Useful when printing signed documents.
  displayDocumentID: Optional[DocumentIDLocation] = Field(default=None)
  form: Optional[PadesDocumentFormInput] = Field(default=None)
  # Will not be displayed to signatories, can be used as a reference to your own system.
  reference: Optional[StringScalarInput] = Field(default=None)
  sealsPageTemplate: Optional[PadesDocumentSealsPageTemplateInput] = Field(default=None)
  storageMode: DocumentStorageMode
  title: StringScalarInput


class PadesDocumentSealsPageTemplateInput(BaseModel):
  # Using the PDF coordinate system, with (x1, y1) being bottom-left
  area: PdfBoundingBoxInput
  # Must be a PDF containing a SINGLE page
  blob: BlobScalarInput
  # Validate that the defined seal area produces the expected number of columns, will error if expectation is not met
  expectedColumns: Optional[IntScalarInput] = Field(default=None)
  # Validate that the defined seal area produces the expected number of rows, will error if expectation is not met
  expectedRows: Optional[IntScalarInput] = Field(default=None)


# Information about pagination in a connection.
class PageInfo(BaseModel):
  # When paginating forwards, the cursor to continue.
  endCursor: Optional[StringScalarOutput] = Field(default=None)
  # When paginating forwards, are there more items?
  hasNextPage: BooleanScalarOutput
  # When paginating backwards, are there more items?
  hasPreviousPage: BooleanScalarOutput
  # When paginating backwards, the cursor to continue.
  startCursor: Optional[StringScalarOutput] = Field(default=None)


class PdfBoundingBoxInput(BaseModel):
  x1: FloatScalarInput
  x2: FloatScalarInput
  y1: FloatScalarInput
  y2: FloatScalarInput


class PdfDocument(BaseModel):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  # Same value as stamped on document when using displayDocumentID
  documentID: StringScalarOutput
  form: Optional[PdfDocumentForm] = Field(default=None)
  id: IDScalarOutput
  originalBlob: Optional[BlobScalarOutput] = Field(default=None)
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatoryViewerStatus: Optional[SignatoryDocumentStatus] = Field(default=None)
  signatures: Optional[list[Signature]] = Field(default=None)
  title: StringScalarOutput


class PdfDocumentForm(BaseModel):
  enabled: BooleanScalarOutput


class PdfSealPosition(BaseModel):
  page: IntScalarInput
  x: FloatScalarInput
  y: FloatScalarInput


class Query(BaseModel):
  application: Optional[Application] = Field(default=None)
  batchSignatory: Optional[BatchSignatory] = Field(default=None)
  document: Optional[Document] = Field(default=None)
  # Query a signatory by id. Useful when using webhooks.
  signatory: Optional[Signatory] = Field(default=None)
  signatureOrder: Optional[SignatureOrder] = Field(default=None)
  # Tenants are only accessable from user viewers
  tenant: Optional[Tenant] = Field(default=None)
  timezones: list[StringScalarOutput]
  viewer: Viewer


class RefreshApplicationApiKeyInput(BaseModel):
  apiKeyId: IDScalarInput
  applicationId: IDScalarInput


class RefreshApplicationApiKeyOutput(BaseModel):
  apiKey: ApplicationApiKey
  application: Application


class RejectSignatureOrderInput(BaseModel):
  dummy: BooleanScalarInput
  reason: Optional[StringScalarInput] = Field(default=None)


class RejectSignatureOrderOutput(BaseModel):
  viewer: Viewer


class RetrySignatureOrderWebhookInput(BaseModel):
  retryPayload: StringScalarInput
  signatureOrderId: IDScalarInput


class RetrySignatureOrderWebhookOutput(BaseModel):
  invocation: WebhookInvocation


class SignActingAsInput(BaseModel):
  evidence: SignInput
  signatoryId: IDScalarInput


class SignActingAsOutput(BaseModel):
  signatory: Signatory
  signatureOrder: SignatureOrder


class SignAllOfInput(BaseModel):
  criiptoVerify: Optional[SignCriiptoVerifyInput] = Field(default=None)
  criiptoVerifyV2: Optional[SignCriiptoVerifyV2Input] = Field(default=None)
  drawable: Optional[SignDrawableInput] = Field(default=None)
  noop: Optional[BooleanScalarInput] = Field(default=None)
  oidc: Optional[SignOidcInput] = Field(default=None)


class SignCriiptoVerifyInput(BaseModel):
  jwt: StringScalarInput


class SignCriiptoVerifyV2Input(BaseModel):
  code: StringScalarInput
  state: StringScalarInput


class SignDocumentFormFieldInput(BaseModel):
  field: StringScalarInput
  value: StringScalarInput


class SignDocumentFormInput(BaseModel):
  fields: list[SignDocumentFormFieldInput]


class SignDocumentInput(BaseModel):
  form: Optional[SignDocumentFormInput] = Field(default=None)
  id: IDScalarInput


class SignDrawableInput(BaseModel):
  image: BlobScalarInput
  name: Optional[StringScalarInput] = Field(default=None)


class SignInput(BaseModel):
  allOf: Optional[SignAllOfInput] = Field(default=None)
  criiptoVerify: Optional[SignCriiptoVerifyInput] = Field(default=None)
  criiptoVerifyV2: Optional[SignCriiptoVerifyV2Input] = Field(default=None)
  documents: Optional[list[SignDocumentInput]] = Field(default=None)
  drawable: Optional[SignDrawableInput] = Field(default=None)
  # EvidenceProvider id
  id: IDScalarInput
  noop: Optional[BooleanScalarInput] = Field(default=None)
  oidc: Optional[SignOidcInput] = Field(default=None)


class SignOidcInput(BaseModel):
  jwt: StringScalarInput


class SignOutput(BaseModel):
  viewer: Viewer


class Signatory(BaseModel):
  documents: SignatoryDocumentConnection
  # A download link for signatories to download their signed documents. Signatories must verify their identity before downloading. Can be used when signature order is closed with document retention.
  downloadHref: Optional[StringScalarOutput] = Field(default=None)
  evidenceProviders: list[SignatureEvidenceProvider]
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
  signatureOrder: SignatureOrder
  signingAs: Optional[StringScalarOutput] = Field(default=None)
  signingSequence: SignatorySigningSequence
  spanId: StringScalarOutput
  # The current status of the signatory.
  status: SignatoryStatus
  # The reason for the signatory status (rejection reason when rejected).
  statusReason: Optional[StringScalarOutput] = Field(default=None)
  # The signature frontend authentication token, only required if you need to build a custom url.
  token: StringScalarOutput
  traceId: StringScalarOutput
  ui: SignatureOrderUI


class SignatoryBeaconInput(BaseModel):
  lastActionAt: DateTimeScalarInput


class SignatoryBeaconOutput(BaseModel):
  viewer: Viewer


class SignatoryDocumentConnection(BaseModel):
  edges: list[SignatoryDocumentEdge]


class SignatoryDocumentEdge(BaseModel):
  node: Document
  status: Optional[SignatoryDocumentStatus] = Field(default=None)


class SignatoryDocumentInput(BaseModel):
  id: IDScalarInput
  # Deprecated in favor of `pdfSealPositions`. Define custom position for PDF seal. Uses PDF coordinate system (bottom-left as 0,0). If defined for one signatory/document, must be defined for all.
  pdfSealPosition: Optional[PdfSealPosition] = Field(default=None)
  # Define custom positions for PDF seals. Uses PDF coordinate system (bottom-left as 0,0). If defined for one signatory/document, must be defined for all.
  pdfSealPositions: Optional[list[PdfSealPosition]] = Field(default=None)
  preapproved: Optional[BooleanScalarInput] = Field(default=None)


class SignatoryDocumentStatus(StrEnum):
  APPROVED = "APPROVED"
  OPENED = "OPENED"
  PREAPPROVED = "PREAPPROVED"
  REJECTED = "REJECTED"
  SIGNED = "SIGNED"


class SignatoryEvidenceProviderInput(BaseModel):
  allOf: Optional[AllOfEvidenceProviderInput] = Field(default=None)
  # Criipto Verify based evidence for signatures.
  criiptoVerify: Optional[CriiptoVerifyProviderInput] = Field(default=None)
  # Hand drawn signature evidence for signatures.
  drawable: Optional[DrawableEvidenceProviderInput] = Field(default=None)
  id: IDScalarInput
  # TEST environment only. Does not manipulate the PDF, use for integration or webhook testing.
  noop: Optional[NoopEvidenceProviderInput] = Field(default=None)
  # Deprecated
  oidc: Optional[OidcEvidenceProviderInput] = Field(default=None)


class SignatoryEvidenceValidationInput(BaseModel):
  boolean: Optional[BooleanScalarInput] = Field(default=None)
  key: StringScalarInput
  value: Optional[StringScalarInput] = Field(default=None)


class SignatoryFrontendEvent(StrEnum):
  DOWNLOAD_LINK_OPENED = "DOWNLOAD_LINK_OPENED"
  SIGN_LINK_OPENED = "SIGN_LINK_OPENED"


class SignatoryRole(StrEnum):
  APPROVER = "APPROVER"
  SIGNER = "SIGNER"
  VIEWER = "VIEWER"


class SignatorySigningSequence(BaseModel):
  initialNumber: IntScalarOutput


class SignatoryStatus(StrEnum):
  APPROVED = "APPROVED"
  DELETED = "DELETED"
  ERROR = "ERROR"
  OPEN = "OPEN"
  REJECTED = "REJECTED"
  SIGNED = "SIGNED"


class SignatoryUIInput(BaseModel):
  # Removes the UI options to reject a document or signature order.
  disableRejection: Optional[BooleanScalarInput] = Field(default=None)
  # Adds an UI option for the signatory to cancel, will return to 'signatoryRedirectUri' if defined.
  enableCancel: Optional[BooleanScalarInput] = Field(default=None)
  # The language of texts rendered to the signatory.
  language: Optional[Language] = Field(default=None)
  # Define a logo to be shown in the signatory UI.
  logo: Optional[SignatureOrderUILogoInput] = Field(default=None)
  # Renders a UI layer for PDF annotations, such as links, making them interactive in the UI/browser
  renderPdfAnnotationLayer: Optional[BooleanScalarInput] = Field(default=None)
  # The signatory will be redirected to this URL after signing or rejected the signature order.
  signatoryRedirectUri: Optional[StringScalarInput] = Field(default=None)
  # Add stylesheet/css via an absolute HTTPS URL.
  stylesheet: Optional[StringScalarInput] = Field(default=None)


class SignatoryViewer(BaseModel):
  authenticated: BooleanScalarOutput
  documents: SignatoryDocumentConnection
  download: Optional[SignatoryViewerDownload] = Field(default=None)
  evidenceProviders: list[SignatureEvidenceProvider]
  id: IDScalarOutput
  role: SignatoryRole
  signatoryId: IDScalarOutput
  signatureOrderStatus: SignatureOrderStatus
  signer: BooleanScalarOutput
  status: SignatoryStatus
  traceId: StringScalarOutput
  ui: SignatureOrderUI


class SignatoryViewerDownload(BaseModel):
  documents: Optional[SignatoryDocumentConnection] = Field(default=None)
  expired: BooleanScalarOutput
  verificationEvidenceProvider: Optional[SignatureEvidenceProvider] = Field(
    default=None
  )
  verificationRequired: BooleanScalarOutput


# Represents a signature on a document.
type Signature = (
  CompositeSignature
  | DrawableSignature
  | EmptySignature
  | JWTSignature
  | NorwegianBankIdSignature
)


class SignatureAppearanceInput(BaseModel):
  displayName: Optional[list[SignatureAppearanceTemplateInput]] = Field(default=None)
  footer: Optional[list[SignatureAppearanceTemplateInput]] = Field(default=None)
  headerLeft: Optional[list[SignatureAppearanceTemplateInput]] = Field(default=None)
  # Render evidence claim as identifier in the signature appearance inside the document. You can supply multiple keys and they will be tried in order. If no key is found a GUID will be rendered.
  identifierFromEvidence: list[StringScalarInput]


class SignatureAppearanceTemplateInput(BaseModel):
  replacements: Optional[list[SignatureAppearanceTemplateReplacementInput]] = Field(
    default=None
  )
  template: StringScalarInput


class SignatureAppearanceTemplateReplacementInput(BaseModel):
  fromEvidence: list[StringScalarInput]
  placeholder: StringScalarInput


type SignatureEvidenceProvider = (
  AllOfSignatureEvidenceProvider
  | CriiptoVerifySignatureEvidenceProvider
  | DrawableSignatureEvidenceProvider
  | NoopSignatureEvidenceProvider
  | OidcJWTSignatureEvidenceProvider
)


class SignatureOrder(BaseModel):
  application: Optional[Application] = Field(default=None)
  closedAt: Optional[DateTimeScalarOutput] = Field(default=None)
  createdAt: DateTimeScalarOutput
  documents: list[Document]
  evidenceProviders: list[SignatureEvidenceProvider]
  expiresAt: DateTimeScalarOutput
  id: IDScalarOutput
  # Number of max signatories for the signature order
  maxSignatories: IntScalarOutput
  # List of signatories for the signature order.
  signatories: list[Signatory]
  status: SignatureOrderStatus
  # Tenants are only accessable from user viewers
  tenant: Optional[Tenant] = Field(default=None)
  timezone: StringScalarOutput
  title: Optional[StringScalarOutput] = Field(default=None)
  traceId: StringScalarOutput
  ui: SignatureOrderUI
  webhook: Optional[SignatureOrderWebhook] = Field(default=None)


# A connection from an object to a list of objects of type SignatureOrder
class SignatureOrderConnection(BaseModel):
  # Information to aid in pagination.
  edges: list[SignatureOrderEdge]
  # Information to aid in pagination.
  pageInfo: PageInfo
  # A count of the total number of objects in this connection, ignoring pagination. This allows a client to fetch the first five objects by passing \"5\" as the argument to `first`, then fetch the total count so it could display \"5 of 83\", for example. In cases where we employ infinite scrolling or don't have an exact count of entries, this field will return `null`.
  totalCount: Optional[IntScalarOutput] = Field(default=None)


# An edge in a connection from an object to another object of type SignatureOrder
class SignatureOrderEdge(BaseModel):
  # A cursor for use in pagination
  cursor: StringScalarOutput
  # The item at the end of the edge. Must NOT be an enumerable collection.
  node: SignatureOrder


class SignatureOrderStatus(StrEnum):
  CANCELLED = "CANCELLED"
  CLOSED = "CLOSED"
  EXPIRED = "EXPIRED"
  OPEN = "OPEN"


class SignatureOrderUI(BaseModel):
  disableRejection: BooleanScalarOutput
  enableCancel: BooleanScalarOutput
  language: Language
  logo: Optional[SignatureOrderUILogo] = Field(default=None)
  renderPdfAnnotationLayer: BooleanScalarOutput
  signatoryRedirectUri: Optional[StringScalarOutput] = Field(default=None)
  stylesheet: Optional[StringScalarOutput] = Field(default=None)


class SignatureOrderUILogo(BaseModel):
  href: Optional[StringScalarOutput] = Field(default=None)
  src: StringScalarOutput


class SignatureOrderUILogoInput(BaseModel):
  # Turns your logo into a link with the defined href.
  href: Optional[StringScalarInput] = Field(default=None)
  # The image source for the logo. Must be an absolute HTTPS URL or a valid data: url
  src: StringScalarInput


class SignatureOrderWebhook(BaseModel):
  logs: list[WebhookInvocation]
  url: StringScalarOutput


# Must define a evidence provider subsection.
class SingleEvidenceProviderInput(BaseModel):
  # Criipto Verify based evidence for signatures.
  criiptoVerify: Optional[CriiptoVerifyProviderInput] = Field(default=None)
  # Hand drawn signature evidence for signatures.
  drawable: Optional[DrawableEvidenceProviderInput] = Field(default=None)
  # TEST environment only. Does not manipulate the PDF, use for integration or webhook testing.
  noop: Optional[NoopEvidenceProviderInput] = Field(default=None)
  # Deprecated
  oidc: Optional[OidcEvidenceProviderInput] = Field(default=None)


type SingleSignature = (
  DrawableSignature | EmptySignature | JWTSignature | NorwegianBankIdSignature
)

type SingleSignatureEvidenceProvider = (
  CriiptoVerifySignatureEvidenceProvider
  | DrawableSignatureEvidenceProvider
  | NoopSignatureEvidenceProvider
  | OidcJWTSignatureEvidenceProvider
)


class StartCriiptoVerifyEvidenceProviderInput(BaseModel):
  acrValue: StringScalarInput
  device: Optional[DeviceInput] = Field(default=None)
  id: IDScalarInput
  # Use the id_token of a previous login to infer, for instance, reauthentication or other hints for the next login.
  idTokenHint: Optional[StringScalarInput] = Field(default=None)
  redirectUri: StringScalarInput
  stage: EvidenceValidationStage


type StartCriiptoVerifyEvidenceProviderOutput = CriiptoVerifyEvidenceProviderRedirect


class Tenant(BaseModel):
  applications: list[Application]
  id: IDScalarOutput
  webhookLogs: list[WebhookInvocation]


class TimestampToken(BaseModel):
  timestamp: DateScalarOutput


class TrackSignatoryInput(BaseModel):
  event: SignatoryFrontendEvent


class TrackSignatoryOutput(BaseModel):
  viewer: Viewer


class UnvalidatedSignatoryViewer(BaseModel):
  authenticated: BooleanScalarOutput
  download: Optional[SignatoryViewerDownload] = Field(default=None)
  evidenceProviders: list[SignatureEvidenceProvider]
  id: IDScalarOutput
  signatoryId: IDScalarOutput
  ui: SignatureOrderUI


class UpdateSignatoryDocumentStatusInput(BaseModel):
  documentId: IDScalarInput
  status: SignatoryDocumentStatus


class UpdateSignatoryDocumentStatusOutput(BaseModel):
  documentEdge: SignatoryDocumentEdge
  viewer: Viewer


class UserViewer(BaseModel):
  authenticated: BooleanScalarOutput
  id: IDScalarOutput
  tenants: list[Tenant]


class ValidateDocumentInput(BaseModel):
  pdf: Optional[BlobScalarInput] = Field(default=None)
  xml: Optional[BlobScalarInput] = Field(default=None)


class ValidateDocumentOutput(BaseModel):
  errors: Optional[list[StringScalarOutput]] = Field(default=None)
  # Whether or not the errors are fixable using 'fixDocumentFormattingErrors'
  fixable: Optional[BooleanScalarOutput] = Field(default=None)
  # `true` if the document contains signatures. If value is `null`, we were unable to determine whether the document has been previously signed.
  previouslySigned: Optional[BooleanScalarOutput] = Field(default=None)
  valid: BooleanScalarOutput


class VerifyApplication(BaseModel):
  domain: StringScalarOutput
  environment: VerifyApplicationEnvironment
  realm: StringScalarOutput


class VerifyApplicationEnvironment(StrEnum):
  PRODUCTION = "PRODUCTION"
  TEST = "TEST"


class VerifyApplicationQueryInput(BaseModel):
  domain: StringScalarInput
  realm: StringScalarInput
  tenantId: IDScalarInput


type Viewer = (
  AnonymousViewer
  | Application
  | BatchSignatoryViewer
  | SignatoryViewer
  | UnvalidatedSignatoryViewer
  | UserViewer
)


class WebhookExceptionInvocation(BaseModel):
  correlationId: StringScalarOutput
  event: Optional[WebhookInvocationEvent] = Field(default=None)
  exception: StringScalarOutput
  requestBody: StringScalarOutput
  responseBody: Optional[StringScalarOutput] = Field(default=None)
  retryPayload: StringScalarOutput
  retryingAt: Optional[StringScalarOutput] = Field(default=None)
  signatureOrderId: Optional[StringScalarOutput] = Field(default=None)
  timestamp: StringScalarOutput
  url: StringScalarOutput


class WebhookHttpErrorInvocation(BaseModel):
  correlationId: StringScalarOutput
  event: Optional[WebhookInvocationEvent] = Field(default=None)
  requestBody: StringScalarOutput
  responseBody: Optional[StringScalarOutput] = Field(default=None)
  responseStatusCode: IntScalarOutput
  retryPayload: StringScalarOutput
  retryingAt: Optional[StringScalarOutput] = Field(default=None)
  signatureOrderId: Optional[StringScalarOutput] = Field(default=None)
  timestamp: StringScalarOutput
  url: StringScalarOutput


type WebhookInvocation = (
  WebhookExceptionInvocation
  | WebhookHttpErrorInvocation
  | WebhookSuccessfulInvocation
  | WebhookTimeoutInvocation
)


class WebhookInvocationEvent(StrEnum):
  SIGNATORY_APPROVED = "SIGNATORY_APPROVED"
  SIGNATORY_DOCUMENT_STATUS_CHANGED = "SIGNATORY_DOCUMENT_STATUS_CHANGED"
  SIGNATORY_DOWNLOAD_LINK_OPENED = "SIGNATORY_DOWNLOAD_LINK_OPENED"
  SIGNATORY_REJECTED = "SIGNATORY_REJECTED"
  SIGNATORY_SIGNED = "SIGNATORY_SIGNED"
  SIGNATORY_SIGN_ERROR = "SIGNATORY_SIGN_ERROR"
  SIGNATORY_SIGN_LINK_OPENED = "SIGNATORY_SIGN_LINK_OPENED"
  SIGNATURE_ORDER_EXPIRED = "SIGNATURE_ORDER_EXPIRED"


class WebhookSuccessfulInvocation(BaseModel):
  correlationId: StringScalarOutput
  event: Optional[WebhookInvocationEvent] = Field(default=None)
  requestBody: StringScalarOutput
  responseBody: Optional[StringScalarOutput] = Field(default=None)
  responseStatusCode: IntScalarOutput
  signatureOrderId: Optional[StringScalarOutput] = Field(default=None)
  timestamp: StringScalarOutput
  url: StringScalarOutput


class WebhookTimeoutInvocation(BaseModel):
  correlationId: StringScalarOutput
  event: Optional[WebhookInvocationEvent] = Field(default=None)
  requestBody: StringScalarOutput
  responseBody: Optional[StringScalarOutput] = Field(default=None)
  responseTimeout: IntScalarOutput
  retryPayload: StringScalarOutput
  retryingAt: Optional[StringScalarOutput] = Field(default=None)
  signatureOrderId: Optional[StringScalarOutput] = Field(default=None)
  timestamp: StringScalarOutput
  url: StringScalarOutput


class XadesDocumentInput(BaseModel):
  blob: BlobScalarInput
  # Will not be displayed to signatories, can be used as a reference to your own system.
  reference: Optional[StringScalarInput] = Field(default=None)
  storageMode: DocumentStorageMode
  title: StringScalarInput


class XmlDocument(BaseModel):
  blob: Optional[BlobScalarOutput] = Field(default=None)
  id: IDScalarOutput
  originalBlob: Optional[BlobScalarOutput] = Field(default=None)
  reference: Optional[StringScalarOutput] = Field(default=None)
  signatoryViewerStatus: Optional[SignatoryDocumentStatus] = Field(default=None)
  signatures: Optional[list[Signature]] = Field(default=None)
  title: StringScalarOutput


AddSignatoriesInput.model_rebuild()
AddSignatoriesOutput.model_rebuild()
AddSignatoryInput.model_rebuild()
AddSignatoryOutput.model_rebuild()
AllOfEvidenceProviderInput.model_rebuild()
AllOfSignatureEvidenceProvider.model_rebuild()
AnonymousViewer.model_rebuild()
Application.model_rebuild()
ApplicationApiKey.model_rebuild()
BatchSignatory.model_rebuild()
BatchSignatoryItem.model_rebuild()
BatchSignatoryItemInput.model_rebuild()
BatchSignatoryViewer.model_rebuild()
CancelSignatureOrderInput.model_rebuild()
CancelSignatureOrderOutput.model_rebuild()
Certificate.model_rebuild()
ChangeSignatoryInput.model_rebuild()
ChangeSignatoryOutput.model_rebuild()
ChangeSignatureOrderInput.model_rebuild()
ChangeSignatureOrderOutput.model_rebuild()
CleanupSignatureOrderInput.model_rebuild()
CleanupSignatureOrderOutput.model_rebuild()
CloseSignatureOrderInput.model_rebuild()
CloseSignatureOrderOutput.model_rebuild()
CompleteCriiptoVerifyEvidenceProviderInput.model_rebuild()
CompleteCriiptoVerifyEvidenceProviderOutput.model_rebuild()
CompositeSignature.model_rebuild()
CreateApplicationApiKeyInput.model_rebuild()
CreateApplicationApiKeyOutput.model_rebuild()
CreateApplicationInput.model_rebuild()
CreateApplicationOutput.model_rebuild()
CreateBatchSignatoryInput.model_rebuild()
CreateBatchSignatoryOutput.model_rebuild()
CreateSignatureOrderInput.model_rebuild()
CreateSignatureOrderOutput.model_rebuild()
CreateSignatureOrderSignatoryInput.model_rebuild()
CreateSignatureOrderUIInput.model_rebuild()
CreateSignatureOrderWebhookInput.model_rebuild()
CriiptoVerifyEvidenceProviderRedirect.model_rebuild()
CriiptoVerifyProviderInput.model_rebuild()
CriiptoVerifySignatureEvidenceProvider.model_rebuild()
DeleteApplicationApiKeyInput.model_rebuild()
DeleteApplicationApiKeyOutput.model_rebuild()
DeleteSignatoryInput.model_rebuild()
DeleteSignatoryOutput.model_rebuild()
DeviceInput.model_rebuild()
DocumentInput.model_rebuild()
DownloadVerificationCriiptoVerifyInput.model_rebuild()
DownloadVerificationInput.model_rebuild()
DownloadVerificationOidcInput.model_rebuild()
DrawableEvidenceProviderInput.model_rebuild()
DrawableSignature.model_rebuild()
DrawableSignatureEvidenceProvider.model_rebuild()
EmptySignature.model_rebuild()
EvidenceProviderInput.model_rebuild()
ExtendSignatureOrderInput.model_rebuild()
ExtendSignatureOrderOutput.model_rebuild()
JWTClaim.model_rebuild()
JWTSignature.model_rebuild()
Mutation.model_rebuild()
NoopEvidenceProviderInput.model_rebuild()
NoopSignatureEvidenceProvider.model_rebuild()
NorwegianBankIdSignature.model_rebuild()
OidcEvidenceProviderInput.model_rebuild()
OidcJWTSignatureEvidenceProvider.model_rebuild()
PadesDocumentFormInput.model_rebuild()
PadesDocumentInput.model_rebuild()
PadesDocumentSealsPageTemplateInput.model_rebuild()
PageInfo.model_rebuild()
PdfBoundingBoxInput.model_rebuild()
PdfDocument.model_rebuild()
PdfDocumentForm.model_rebuild()
PdfSealPosition.model_rebuild()
Query.model_rebuild()
RefreshApplicationApiKeyInput.model_rebuild()
RefreshApplicationApiKeyOutput.model_rebuild()
RejectSignatureOrderInput.model_rebuild()
RejectSignatureOrderOutput.model_rebuild()
RetrySignatureOrderWebhookInput.model_rebuild()
RetrySignatureOrderWebhookOutput.model_rebuild()
SignActingAsInput.model_rebuild()
SignActingAsOutput.model_rebuild()
SignAllOfInput.model_rebuild()
SignCriiptoVerifyInput.model_rebuild()
SignCriiptoVerifyV2Input.model_rebuild()
SignDocumentFormFieldInput.model_rebuild()
SignDocumentFormInput.model_rebuild()
SignDocumentInput.model_rebuild()
SignDrawableInput.model_rebuild()
SignInput.model_rebuild()
SignOidcInput.model_rebuild()
SignOutput.model_rebuild()
Signatory.model_rebuild()
SignatoryBeaconInput.model_rebuild()
SignatoryBeaconOutput.model_rebuild()
SignatoryDocumentConnection.model_rebuild()
SignatoryDocumentEdge.model_rebuild()
SignatoryDocumentInput.model_rebuild()
SignatoryEvidenceProviderInput.model_rebuild()
SignatoryEvidenceValidationInput.model_rebuild()
SignatorySigningSequence.model_rebuild()
SignatoryUIInput.model_rebuild()
SignatoryViewer.model_rebuild()
SignatoryViewerDownload.model_rebuild()
SignatureAppearanceInput.model_rebuild()
SignatureAppearanceTemplateInput.model_rebuild()
SignatureAppearanceTemplateReplacementInput.model_rebuild()
SignatureOrder.model_rebuild()
SignatureOrderConnection.model_rebuild()
SignatureOrderEdge.model_rebuild()
SignatureOrderUI.model_rebuild()
SignatureOrderUILogo.model_rebuild()
SignatureOrderUILogoInput.model_rebuild()
SignatureOrderWebhook.model_rebuild()
SingleEvidenceProviderInput.model_rebuild()
StartCriiptoVerifyEvidenceProviderInput.model_rebuild()
Tenant.model_rebuild()
TimestampToken.model_rebuild()
TrackSignatoryInput.model_rebuild()
TrackSignatoryOutput.model_rebuild()
UnvalidatedSignatoryViewer.model_rebuild()
UpdateSignatoryDocumentStatusInput.model_rebuild()
UpdateSignatoryDocumentStatusOutput.model_rebuild()
UserViewer.model_rebuild()
ValidateDocumentInput.model_rebuild()
ValidateDocumentOutput.model_rebuild()
VerifyApplication.model_rebuild()
VerifyApplicationQueryInput.model_rebuild()
WebhookExceptionInvocation.model_rebuild()
WebhookHttpErrorInvocation.model_rebuild()
WebhookSuccessfulInvocation.model_rebuild()
WebhookTimeoutInvocation.model_rebuild()
XadesDocumentInput.model_rebuild()
XmlDocument.model_rebuild()
