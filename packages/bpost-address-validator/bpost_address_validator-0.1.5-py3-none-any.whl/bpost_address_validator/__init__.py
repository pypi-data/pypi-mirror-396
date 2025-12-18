"""bpost_address_validator

Python wrapper for bpost External Mailing Address Proofing API.

Sync and async clients using httpx and Pydantic models.
"""

from .client import BpostClient, AsyncBpostClient
from .models import (
    AddressToValidate,
    AddressToValidateList,
    AddressBlockLines,
    UnstructuredAddressLineItem,
    PostalAddress,
    DeliveryPointLocation,
    StructuredDeliveryPointLocation,
    PostalCodeMunicipality,
    StructuredPostalCodeMunicipality,
    OtherDeliveryInformation,
    StructuredOtherDeliveryInformation,
    ValidateAddressesRequestContent,
    ValidateAddressOptions,
    CallerIdentification,
    ValidateAddressesRequest,
    ValidatedAddressResult,
    ValidatedAddressResultList,
    ValidateAddressesResponse,
    ValidationErrorItem,
)
from .errors import ApiError

__all__ = [
    "BpostClient",
    "AsyncBpostClient",
    "AddressToValidate",
    "AddressToValidateList",
    "AddressBlockLines",
    "UnstructuredAddressLineItem",
    "PostalAddress",
    "DeliveryPointLocation",
    "StructuredDeliveryPointLocation",
    "PostalCodeMunicipality",
    "StructuredPostalCodeMunicipality",
    "OtherDeliveryInformation",
    "StructuredOtherDeliveryInformation",
    "ValidateAddressesRequestContent",
    "ValidateAddressOptions",
    "CallerIdentification",
    "ValidateAddressesRequest",
    "ValidatedAddressResult",
    "ValidatedAddressResultList",
    "ValidateAddressesResponse",
    "ValidationErrorItem",
    "ApiError",
]
