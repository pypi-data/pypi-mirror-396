from .models import CreateSignatureOrderInput


def test_create_signature_order_input_dump():
  model = CreateSignatureOrderInput(documents=[])
  assert (
    model.model_dump_json()
    == '{"disableVerifyEvidenceProvider":null,"documents":[],"evidenceProviders":null,"evidenceValidationStages":null,"expiresAt":null,"expiresInDays":null,"fixDocumentFormattingErrors":null,"maxSignatories":null,"signatories":null,"signatureAppearance":null,"timezone":null,"title":null,"ui":null,"webhook":null}'
  )
