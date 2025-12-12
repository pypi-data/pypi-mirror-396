# criipto-signatures

A python SDK for Criipto Signatures.

Sign PAdeS-LTA documents using MitID, BankID or any other eID supported by Criipto.

[Examples](https://docs.criipto.com/signatures/graphql/examples/)

## Getting started

### Requirements

This library supports python 3.13 and later.

### Installation

The SDK is available on [PYPI](https://pypi.org/project/criipto-signatures/):

```
python3 -m pip install criipto-signatures
```

### Configure the SDK

The SDK is available in both a sync and an async version

```python
from criipto_signatures import (
  CriiptoSignaturesSDKAsync,
  CriiptoSignaturesSDKSync,
)
asyncClient = CriiptoSignaturesSDKAsync(
    '{YOUR_CRIIPTO_CLIENT_ID}',
    '{YOUR_CRIIPTO_CLIENT_SECRET}'
)
syncClient = CriiptoSignaturesSDKSync(
    '{YOUR_CRIIPTO_CLIENT_ID}',
    '{YOUR_CRIIPTO_CLIENT_SECRET}'
)
```

## Basic example

```python
from criipto_signatures import CriiptoSignaturesSDKAsync
from criipto_signatures.models import (
    CreateSignatureOrderInput,
    DocumentInput,
    PadesDocumentInput,
    DocumentStorageMode,
    AddSignatoryInput,
    CloseSignatureOrderInput,
)

client = CriiptoSignaturesSDKAsync(
    '{YOUR_CRIIPTO_CLIENT_ID}',
    '{YOUR_CRIIPTO_CLIENT_SECRET}'
)

# Create signature order
signatureOrder = await client.createSignatureOrder(
    CreateSignatureOrderInput(
        documents=[
            DocumentInput(
                pdf=PadesDocumentInput(
                    title="My document",
                    blob=data, # bytes object, or a base64 encoded string
                    storageMode=DocumentStorageMode.Temporary,
                )
            )
        ]
    )
)

# Add signatory to signature order
signatory = await client.addSignatory(
    AddSignatoryInput(
        signatureOrderId=signatureOrder.id
    )
)
print(signatory.href)

# ... Wait for the signatory to sign

# And close the order
await client.closeSignatureOrder(
    CloseSignatureOrderInput(
        signatureOrderId=signatureOrder.id,
        retainDocumentsForDays=1
    )
)
```

For a more complete example, see the [example project](https://github.com/criipto/criipto-signatures-sdk/tree/master/packages/python/example)
