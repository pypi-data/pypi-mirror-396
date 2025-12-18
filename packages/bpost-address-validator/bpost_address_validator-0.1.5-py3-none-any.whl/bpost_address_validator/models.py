from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# General modeling approach:
# - Mirror the top-level envelopes exactly as exposed by the API
# - Keep inner structures flexible (extra = "allow") so the client remains
#   resilient to minor upstream changes without requiring immediate updates.


class _FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ----
# Request typing additions: AddressBlockLines and PostalAddress structures
# ----

class UnstructuredAddressLineItem(_FlexibleModel):
    body: Optional[str] = Field(default=None, alias="*body")
    locale: Optional[str] = Field(default=None, alias="@locale")


class AddressBlockLines(_FlexibleModel):
    unstructured_address_line: List[UnstructuredAddressLineItem] = Field(
        default_factory=list, alias="UnstructuredAddressLine"
    )


class StructuredDeliveryPointLocation(_FlexibleModel):
    street_name: Optional[str] = Field(default=None, alias="StreetName")
    box_number: Optional[str] = Field(default=None, alias="BoxNumber")
    street_number: Optional[str] = Field(default=None, alias="StreetNumber")
    country_name: Optional[str] = Field(default=None, alias="CountryName")


class DeliveryPointLocation(_FlexibleModel):
    unstructured_delivery_point_location: Optional[str] = Field(
        default=None, alias="UnstructuredDeliveryPointLocation"
    )
    structured_delivery_point_location: Optional[StructuredDeliveryPointLocation] = Field(
        default=None, alias="StructuredDeliveryPointLocation"
    )


class StructuredPostalCodeMunicipality(_FlexibleModel):
    postal_code: Optional[str] = Field(default=None, alias="PostalCode")
    municipality_name: Optional[str] = Field(default=None, alias="MunicipalityName")
    delivery_service_qualifier: Optional[str] = Field(
        default=None, alias="DeliveryServiceQualifier"
    )


class PostalCodeMunicipality(_FlexibleModel):
    unstructured_postal_code_municipality: Optional[str] = Field(
        default=None, alias="UnstructuredPostalCodeMunicipality"
    )
    structured_postal_code_municipality: Optional[StructuredPostalCodeMunicipality] = Field(
        default=None, alias="StructuredPostalCodeMunicipality"
    )


class StructuredOtherDeliveryInformation(_FlexibleModel):
    delivery_service_type: Optional[str] = Field(
        default=None, alias="DeliveryServiceType"
    )
    delivery_service_indicator: Optional[str] = Field(
        default=None, alias="DeliveryServiceIndicator"
    )


class OtherDeliveryInformation(_FlexibleModel):
    unstructured_other_delivery_information: Optional[str] = Field(
        default=None, alias="UnstructuredOtherDeliveryInformation"
    )
    structured_other_delivery_information: Optional[StructuredOtherDeliveryInformation] = Field(
        default=None, alias="StructuredOtherDeliveryInformation"
    )


class PostalAddress(_FlexibleModel):
    # Request-style nested groups
    delivery_point_location: Optional[DeliveryPointLocation] = Field(
        default=None, alias="DeliveryPointLocation"
    )
    postal_code_municipality: Optional[PostalCodeMunicipality] = Field(
        default=None, alias="PostalCodeMunicipality"
    )
    other_delivery_information: Optional[OtherDeliveryInformation] = Field(
        default=None, alias="OtherDeliveryInformation"
    )

    # Response-style direct structured fields (sometimes flattened)
    country_name: Optional[str] = Field(default=None, alias="CountryName")
    structured_delivery_point_location: Optional[StructuredDeliveryPointLocation] = Field(
        default=None, alias="StructuredDeliveryPointLocation"
    )
    structured_postal_code_municipality: Optional[StructuredPostalCodeMunicipality] = Field(
        default=None, alias="StructuredPostalCodeMunicipality"
    )
    structured_other_delivery_information: Optional[StructuredOtherDeliveryInformation] = Field(
        default=None, alias="StructuredOtherDeliveryInformation"
    )


class AddressToValidate(_FlexibleModel):
    id: Optional[str] = Field(default=None, alias="@id")
    dispatching_country_iso_code: Optional[str] = Field(
        default=None, alias="DispatchingCountryISOCode"
    )
    delivering_country_iso_code: Optional[str] = Field(
        default=None, alias="DeliveringCountryISOCode"
    )
    address_block_lines: Optional[AddressBlockLines] = Field(
        default=None, alias="AddressBlockLines"
    )
    postal_address: Optional[PostalAddress] = Field(default=None, alias="PostalAddress")
    mailee_and_addressee: Optional[Dict[str, Any]] = Field(
        default=None, alias="MaileeAndAddressee"
    )


class AddressToValidateList(_FlexibleModel):
    address_to_validate: List[AddressToValidate] = Field(alias="AddressToValidate")


class ValidateAddressOptions(_FlexibleModel):
    include_submitted_address: Optional[bool] = Field(
        default=None, alias="IncludeSubmittedAddress"
    )
    include_default_geo_location: Optional[bool] = Field(
        default=None, alias="IncludeDefaultGeoLocation"
    )
    include_suggestions: Optional[bool] = Field(default=None, alias="IncludeSuggestions")
    include_formatting: Optional[bool] = Field(default=None, alias="IncludeFormatting")
    include_default_geo_location_for_boxes: Optional[bool] = Field(
        default=None, alias="IncludeDefaultGeoLocationForBoxes"
    )
    include_suffix_list: Optional[bool] = Field(default=None, alias="IncludeSuffixList")
    include_number_of_boxes: Optional[bool] = Field(
        default=None, alias="IncludeNumberOfBoxes"
    )
    include_number_of_suffixes: Optional[bool] = Field(
        default=None, alias="IncludeNumberOfSuffixes"
    )
    include_list_of_boxes: Optional[bool] = Field(
        default=None, alias="IncludeListOfBoxes"
    )
    include_nis_code: Optional[bool] = Field(default=None, alias="IncludeNisCode")
    include_nis_hierarchy: Optional[bool] = Field(
        default=None, alias="IncludeNisHierarchy"
    )
    include_desired_address_language: Optional[str] = Field(
        default=None, alias="IncludeDesiredAddressLanguage"
    )


class CallerIdentification(_FlexibleModel):
    caller_name: Optional[str] = Field(default=None, alias="CallerName")


class ValidateAddressesRequestContent(_FlexibleModel):
    address_to_validate_list: AddressToValidateList = Field(
        alias="AddressToValidateList"
    )
    validate_address_options: Optional[ValidateAddressOptions] = Field(
        default=None, alias="ValidateAddressOptions"
    )
    caller_identification: Optional[CallerIdentification] = Field(
        default=None, alias="CallerIdentification"
    )


class ValidateAddressesRequest(_FlexibleModel):
    """Top-level request body wrapper required by the API."""

    validate_addresses_request: ValidateAddressesRequestContent = Field(
        alias="ValidateAddressesRequest"
    )


# Response models (kept flexible, but with helpful typed anchors)


class ValidatedAddress(_FlexibleModel):
    postal_address: Optional[PostalAddress] = Field(default=None, alias="PostalAddress")
    address_language: Optional[str] = Field(default=None, alias="AddressLanguage")
    score: Optional[str] = Field(default=None, alias="Score")
    number_of_suffix: Optional[str] = Field(default=None, alias="NumberOfSuffix")
    number_of_boxes: Optional[str] = Field(default=None, alias="NumberOfBoxes")
    label: Optional[Dict[str, Any]] = Field(default=None, alias="Label")
    service_point_box_list: Optional[Dict[str, Any]] = Field(
        default=None, alias="ServicePointBoxList"
    )
    service_point_detail: Optional[Dict[str, Any]] = Field(
        default=None, alias="ServicePointDetail"
    )
    nis_code: Optional[Dict[str, Any]] = Field(default=None, alias="NisCode")
    nis_hierarchy: Optional[Dict[str, Any]] = Field(default=None, alias="NisHierarchy")


class ValidatedAddressList(_FlexibleModel):
    validated_address: List[ValidatedAddress] = Field(
        default_factory=list, alias="ValidatedAddress"
    )


class ValidatedAddressResult(_FlexibleModel):
    validated_address_list: Optional[ValidatedAddressList] = Field(
        default=None, alias="ValidatedAddressList"
    )
    mailee_and_addressee: Optional[Dict[str, Any]] = Field(
        default=None, alias="MaileeAndAddressee"
    )
    id: Optional[str] = Field(default=None, alias="@id")
    error: Optional[List[ValidationErrorItem]] = Field(default_factory=list, alias="Error")
    detected_input_address_language: Optional[str] = Field(
        default=None, alias="DetectedInputAddressLanguage"
    )
    transaction_id: Optional[str] = Field(default=None, alias="TransactionID")


# ----
# Validation messages (Errors and Warnings)
# The official manual indicates both functional warnings and errors are returned
# and tied to impacted components. Because the exact upstream field names can
# vary, we keep models flexible while providing helpful, typed anchors.
# ----


class ValidationErrorItem(_FlexibleModel):
    component_ref: str = Field(alias="ComponentRef")
    error_code: Optional[str] = Field(default=None, alias="ErrorCode")
    error_severity: Optional[str] = Field(default=None, alias="ErrorSeverity")


# Rebuild to resolve forward refs for Pydantic v2
ValidatedAddressResult.model_rebuild()


class ValidatedAddressResultList(_FlexibleModel):
    validated_address_result: List[ValidatedAddressResult] = Field(
        default_factory=list, alias="ValidatedAddressResult"
    )


class ValidateAddressesResponseContent(_FlexibleModel):
    validated_address_result_list: Optional[ValidatedAddressResultList] = Field(
        default=None, alias="ValidatedAddressResultList"
    )


class ValidateAddressesResponse(_FlexibleModel):
    """Top-level response body wrapper returned by the API."""

    validate_addresses_response: Optional[ValidateAddressesResponseContent] = Field(
        default=None, alias="ValidateAddressesResponse"
    )
