"""
Scenarios SDK for BrynQ.

This module provides the `Scenarios` class for fetching, parsing, and applying
data transformation scenarios from the BrynQ API. It handles field renaming,
value mapping, and structure validation based on configured scenarios.

This module also contains parsed scenario models (ParsedScenario, Record, FieldProperties)
and parsing logic that transforms raw API responses into usable business logic models.
"""
# imports
from __future__ import annotations

import re
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union, Literal

import pandas as pd
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from pandera.typing import Series, String  # type: ignore[attr-defined]
from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import AwareDatetime

from .schemas.scenarios import (
    Scenario,
    ScenarioDetail,
    SourceOrTargetField,
    ScenarioMappingConfiguration,
    FieldType,
    SystemType,
    RelationType,
    CustomSourceOrTargetField,
    LibrarySourceOrTargetField,
    ConfigurationSourceOrTargetField,
    LibraryFieldValues,
    MappingValue,
    ConfigurationType,
    ConfigFieldValues,
    Template,
)

# ============================================================================
# Type Aliases for Parsed Models
# ============================================================================
FieldName = str
PythonicName = str
FieldPropertiesMap = Dict[FieldName, "FieldProperties"]
SourceToTargetMap = Dict[FieldName, List[FieldName]]
TargetToSourceMap = Dict[FieldName, Union[FieldName, List[FieldName]]]


# ============================================================================
# Extraction Helpers
# ============================================================================

def _sanitize_alias(alias: str) -> str:
    """Converts a raw string into a valid Python variable name.

    Converts names like "User ID" or "1st_Name" to "user_id" and "field_1st_name" to fix
    Python syntax issues (spaces, special characters, leading digits). Used in
    `_build_field_properties` and `_build_record` to create Python-safe aliases.

    Args:
        alias: The raw string to sanitize.

    Returns:
        A snake_case string safe for use as a class attribute.
    """
    # Replace non-word characters and leading digits with underscores to create a valid Python variable name
    pythonic_name = re.sub(r"\W|^(?=\d)", "_", alias)
    pythonic_name = re.sub(r"_+", "_", pythonic_name).strip("_").lower()
    if not pythonic_name:
        pythonic_name = "field"
    if pythonic_name[0].isdigit(): #double check if regex failed
        pythonic_name = f"field_{pythonic_name}"
    return pythonic_name

def _extract_names_from_fields(fields: SourceOrTargetField) -> List[str]:
    """Extracts a list of field names from a field object, preserving order.

    The API stores names in different places by field type (technical_name for CUSTOM,
    field/uuid for LIBRARY). This provides a single way to get names regardless of structure.
    Used during scenario parsing to build mapping dictionaries. Order is preserved from the API response.

    Args:
        fields: The SourceOrTargetField object to extract names from.

    Returns:
        List of field names (technical_name for CUSTOM, field/uuid for LIBRARY, uuid for CONFIGURATION) in API order.
        Empty list for FIXED/EMPTY fields.
    """
    if isinstance(fields, CustomSourceOrTargetField):
        names: List[str] = []
        seen = set()  # Track seen names to avoid duplicates while preserving order
        for item in fields.data:
            if item.technical_name and item.technical_name not in seen:
                names.append(item.technical_name)
                seen.add(item.technical_name)
        if not names:
            for item in fields.data:
                uuid = getattr(item, "uuid", None)
                if uuid and uuid not in seen:
                    names.append(str(uuid))
                    seen.add(str(uuid))
        return names

    if isinstance(fields, LibrarySourceOrTargetField):
        names: List[str] = []
        seen = set()  # Track seen names to avoid duplicates while preserving order
        for entry in fields.data:
            # Handle different formats the API may return:
            # - as a plain string: the string itself IS the field name/identifier
            # - as a LibraryFieldValues object: the field name is in the 'field' attribute (preferred)
            #   or 'uuid' attribute (fallback if 'field' is missing)
            if isinstance(entry, str):
                # String entry is the field name itself
                if entry not in seen:
                    names.append(entry)
                    seen.add(entry)
            elif isinstance(entry, LibraryFieldValues):
                if entry.field and entry.field not in seen:
                    names.append(entry.field)
                    seen.add(entry.field)
                elif entry.uuid and entry.uuid not in seen:
                    names.append(str(entry.uuid))
                    seen.add(str(entry.uuid))
        return names

    if isinstance(fields, ConfigurationSourceOrTargetField):
        names: List[str] = []
        seen = set()  # Track seen names to avoid duplicates while preserving order
        for config_item in fields.data:
            # Configuration fields use UUID as identifier
            uuid_str = str(config_item.uuid)
            if uuid_str not in seen:
                names.append(uuid_str)
                seen.add(uuid_str)
        return names

    return []

def _extract_label_from_fields(
    fields: SourceOrTargetField,
    field_name: str
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extracts human-readable labels for customer-facing communication.

    CUSTOM fields use 'name' directly; LIBRARY fields have multi-language 'field_label'
    dictionaries. Prioritizes English, then falls back to any available value. Used in
    `_build_field_properties` and `_build_record`.

    Args:
        fields: The SourceOrTargetField object to extract from.
        field_name: The field name to look up.

    Returns:
        Tuple of (Preferred Label, English Label, Dutch Label).
    """
    if isinstance(fields, CustomSourceOrTargetField):
        for item in fields.data:
            # Custom fields don't have multi-language field_label like library fields,
            # so we use 'name' directly as the label (this is what shows up in BrynQ)
            if item.technical_name == field_name or item.uuid == field_name:
                return (item.name, None, None)

    if isinstance(fields, LibrarySourceOrTargetField):
        for entry in fields.data:
            # Handle different formats the API may return:
            # - as a plain string: no label available (skip)
            # - as a LibraryFieldValues object: check field/uuid and extract field_label
            if not isinstance(entry, str) and (entry.field == field_name or entry.uuid == field_name) and entry.field_label:
                if isinstance(entry.field_label, dict):
                    l_en = entry.field_label.get("en")
                    # Return EN if present, else the first available value
                    return (l_en or next(iter(entry.field_label.values()), None), l_en, entry.field_label.get("nl"))

    return (None, None, None)

def _extract_uuid_from_fields(fields: SourceOrTargetField, field_name: str) -> Optional[str]:
    """Extracts UUID from fields for a given field name.

    The API's mappingValues reference fields by UUID. This extracts UUIDs so
    `UuidToFieldNameMapper` can convert UUID-based references to field names.

    Args:
        fields: SourceOrTargetField object to extract from.
        field_name: The field name to look up.

    Returns:
        UUID string if found, None otherwise.
    """
    if isinstance(fields, CustomSourceOrTargetField):
        for item in fields.data:
            if item.technical_name == field_name or item.uuid == field_name:
                return item.uuid

    if isinstance(fields, LibrarySourceOrTargetField):
        for entry in fields.data:
            if not isinstance(entry, str) and (entry.field == field_name or entry.uuid == field_name):
                return entry.uuid
    return None


def _extract_schema_from_fields(fields: SourceOrTargetField, field_name: str) -> Optional[str]:
    """Extracts schema name identifying the source system or category.

    Used when building field properties to store metadata (not used in transformation logic).

    Args:
        fields: SourceOrTargetField object to extract from.
        field_name: The field name to look up.

    Returns:
        Schema name string if found, None otherwise.
        - For CUSTOM fields: returns CustomDataValues.source
        - For LIBRARY fields: returns category.technicalName
    """
    if isinstance(fields, CustomSourceOrTargetField):
        for item in fields.data:
            if item.technical_name == field_name or item.uuid == field_name:
                return item.source

    if isinstance(fields, LibrarySourceOrTargetField):
        for entry in fields.data:
            if not isinstance(entry, str) and (entry.field == field_name or entry.uuid == field_name):
                return entry.category.get("technicalName") if entry.category else None
    return None

def _extract_technical_name_from_fields(fields: SourceOrTargetField, field_name: str) -> Optional[str]:
    """Extracts technical_name from fields for a given field name.

    Technical names are system-specific identifiers (often numeric/encoded) that differ from
    human-readable names. Used by `UuidToFieldNameMapper` to convert UUID/schema pattern keys to field names and as a
    fallback alias in Pandera field definitions. Only CUSTOM fields have technical names.

    Args:
        fields: SourceOrTargetField object to extract from.
        field_name: The field name to look up (should be the technical_name for CUSTOM fields).

    Returns:
        Technical name string if found, None otherwise.
        - For CUSTOM fields: returns the technical field ID needed for API calls to the system
          (often not human-readable, e.g., "custom_field_2839471293")
        - For LIBRARY fields: returns None (they use schema names instead, not technical identifiers)
    """
    if isinstance(fields, CustomSourceOrTargetField):
        for item in fields.data:
            # Match by technical_name (primary) or uuid (fallback)
            # field_name should be the technical_name extracted by _extract_names_from_fields
            # Ensure technical_name exists and matches, or fall back to uuid match
            if item.technical_name and item.technical_name == field_name:
                return item.technical_name
            elif item.uuid == field_name:
                # If matched by uuid, return the technical_name if it exists
                return item.technical_name if item.technical_name else None
    return None

def _extract_description_from_fields(fields: SourceOrTargetField, field_name: str) -> Optional[str]:
    """Extracts description explaining what a field represents.

    Used when building field properties to store metadata for documentation.
    Only CUSTOM fields have descriptions.

    Args:
        fields: SourceOrTargetField object to extract from.
        field_name: The field name to look up.

    Returns:
        Description string for CUSTOM fields, None otherwise.
    """
    if isinstance(fields, CustomSourceOrTargetField):
        for item in fields.data:
            if item.technical_name == field_name or item.uuid == field_name:
                return item.description
    return None


def _extract_config_props(fields: SourceOrTargetField, field_name: str) -> Dict[str, Any]:
    """Extracts configuration field properties (question, type, value).

    Used when building field properties for CONFIGURATION field types.
    Extracts question (as dict, en, nl, and preferred string), config_type, and config_value.

    Args:
        fields: SourceOrTargetField object to extract from.
        field_name: The field name to look up (UUID for CONFIGURATION fields).

    Returns:
        Dictionary with config properties: question, question_dict, question_en, question_nl, config_type, config_value.
        Returns empty dict with None values if not a CONFIGURATION field or not found.
    """
    if isinstance(fields, ConfigurationSourceOrTargetField):
        for config_item in fields.data:
            # Match by UUID (configuration fields use UUID as identifier)
            # Convert UUID to string for comparison
            config_uuid_str = str(config_item.uuid)
            if config_uuid_str == field_name or config_item.uuid == field_name:
                question_dict = config_item.question
                question_en = question_dict.get("en") if question_dict else None
                question_nl = question_dict.get("nl") if question_dict else None
                # Preferred question: English if available, else first available, else None
                question = question_en or (next(iter(question_dict.values()), None) if question_dict else None)

                # Get config_type value (handle both enum and string)
                config_type_value = config_item.type.value if hasattr(config_item.type, 'value') else str(config_item.type)

                return {
                    "question": question,
                    "question_dict": question_dict,
                    "question_en": question_en,
                    "question_nl": question_nl,
                    "config_type": config_type_value,
                    "config_value": config_item.value,
                }

    # Return empty dict with None values for non-configuration fields
    return {
        "question": None,
        "question_dict": None,
        "question_en": None,
        "question_nl": None,
        "config_type": None,
        "config_value": None,
    }


def _parse_config_value(config_item: ConfigFieldValues) -> Optional[str]:
    """Convert a ConfigFieldValues object into a normalized string representation."""
    cfg_type = getattr(config_item.type, "value", str(config_item.type))
    value = config_item.value

    # Attachment: explicitly suppressed
    if cfg_type == ConfigurationType.ATTACHMENT.value:
        return None

    # Selection: extract English labels if the payload is a list of dicts
    if cfg_type == ConfigurationType.SELECTION.value:
        if isinstance(value, list):
            labels = [v.get("en", "") for v in value if isinstance(v, dict) and "en" in v]
            return ", ".join(labels) if labels else str(value)
        return str(value)

    # Datepicker: normalize single or range
    if cfg_type == ConfigurationType.DATEPICKER.value:
        def fmt(dt):
            return dt.isoformat() if isinstance(dt, (datetime, AwareDatetime)) else str(dt)

        if isinstance(value, list):
            parts = [fmt(v) for v in value]
            return " - ".join(parts) if parts else None
        return fmt(value) if value is not None else None

    # Simple scalar types: TEXT, EMAIL, NUMBER, RICHTEXT
    if cfg_type in {
        ConfigurationType.TEXT.value,
        ConfigurationType.EMAIL.value,
        ConfigurationType.NUMBER.value,
        ConfigurationType.RICHTEXT.value,
    }:
        return str(value) if value is not None else None

    # Fallback
    return str(value) if value is not None else None


# ============================================================================
# Internal Schema Models (The "Useful" Objects)
# ============================================================================

class SourceTargetFields(BaseModel):
    """Nested structure for source or target field metadata.

    Provides organized access to field information for either source or target fields
    in a scenario. Access via `scenario.source` or `scenario.target`.

    Example:
        >>> scenario.source.field_names
        ['employee_id', 'first_name', 'last_name']
        >>> scenario.source.unique_fields
        ['employee_id']
        >>> scenario.source.field_properties[0].alias
        'employee_id'
        >>> scenario.target.custom_fields
        ['custom_field_1', 'custom_field_2']
        >>> len(scenario.source)
        3
        >>> print(scenario.source)
        SourceTargetFields(type='source', fields=3)
        employee_id
        first_name
        last_name

    Attributes:
        type: Either 'source' or 'target' indicating the system type
        field_names: List of all field names for this system type (source or target)
        unique_fields: List of field names that are part of unique constraints
        required_fields: List of field names that are required
        field_properties: List of FieldProperties objects containing full metadata for all fields
        custom_fields: List of field names that are custom fields (field_type='CUSTOM')
        library_fields: List of field names that are library fields (field_type='LIBRARY')
        fields_with_logic: List of field names that have transformation logic defined
    """
    type: Literal["source", "target"]
    field_names: List[str]
    unique_fields: List[str]
    required_fields: List[str]
    field_properties: List[FieldProperties]
    custom_fields: List[str]
    library_fields: List[str]
    fields_with_logic: List[str]

    def __iter__(self) -> Iterator[FieldProperties]:
        """Make SourceTargetFields iterable, yielding FieldProperties objects.

        Allows direct iteration: `for field in scenario.source:`

        Example:
            >>> for field in scenario.source:
            ...     print(f"{field.alias} (required: {field.required})")
            employee_id (required: True)
            first_name (required: False)

        Yields:
            FieldProperties objects for each field
        """
        return iter(self.field_properties)

    def __len__(self) -> int:
        """Return the number of fields.

        Example:
            >>> len(scenario.source)
            3

        Returns:
            Number of field names
        """
        return len(self.field_names)

    def __str__(self) -> str:
        """Return a string representation for print().

        Example:
            >>> print(scenario.source)
            SourceTargetFields(type='source', fields=3)

        Returns:
            String representation showing type and field count
        """
        return f"SourceTargetFields(type={self.type!r}, fields={len(self.field_names)})"

    def __repr__(self) -> str:
        """Return a string representation of SourceTargetFields.

        Example:
            >>> repr(scenario.source)
            "SourceTargetFields(type='source', fields=3)"

        Returns:
            String representation showing type and field count
        """
        return f"SourceTargetFields(type={self.type!r}, fields={len(self.field_names)})"


class FieldProperties(BaseModel):
    """Metadata for a single field in a mapping.

    How to use:
        Access this via `scenario.field_name`. It provides details on
        validation (unique, required) and origins (schema, uuid).

    Example:
        >>> scenario = ParsedScenario(...)
        >>> scenario.customer_id.required
        True
        >>> scenario.customer_id.unique
        False
        >>> scenario['customer_id'].label
        'Customer ID'

    Attributes:
        logic: Transformation logic string as defined in the BrynQ template
        unique: Whether this field is part of the unique key constraint
        required: Whether this field is required (cannot be empty/null)
        mapping: Value mapping dictionary (empty for individual fields, actual mapping is at Record level)
        system_type: Indicates whether this is a 'source' or 'target' field
        field_type: Indicates the field origin type: 'CUSTOM' or 'LIBRARY'
        alias: The technical field name/identifier (pythonic name for the field)
        uuid: The UUID identifier used in mapping values
        schema_name: For LIBRARY fields: category.technicalName. For CUSTOM fields: CustomDataValues.source
        technical_name: For CUSTOM fields: CustomDataValues.technical_name. Not populated for LIBRARY fields
        label: Human-readable field name displayed in BrynQ
        label_en: English human-readable field name
        label_nl: Dutch human-readable field name
        description: Business description/purpose of the field (for custom fields)
    """
    model_config = ConfigDict(extra="allow", frozen=True)

    # Core Mapping Properties, straight from api
    logic: Optional[str] = None
    unique: bool = False
    required: bool = False
    mapping: Dict[str, Any] = Field(default_factory=dict)

    # Identification
    system_type: Optional[str] = None  # 'source' or 'target'
    field_type: Optional[str] = None   # 'CUSTOM' or 'LIBRARY'
    alias: Optional[str] = None        # Python variable name
    uuid: Optional[str] = None         # API ID

    # Context
    schema_name: Optional[str] = Field(default=None, alias="schema")
    technical_name: Optional[str] = None
    label: Optional[str] = None
    label_dict: Optional[Dict[str,str]] = None
    label_en: Optional[str] = None
    label_nl: Optional[str] = None
    description: Optional[str] = None

    # config related optional fields
    question: Optional[str] = None
    question_dict: Optional[Dict[str,str]] = None
    question_en: Optional[str] = None
    question_nl: Optional[str] = None
    config_type: Optional[str] = None
    config_value: Optional[Any] = None

    def __repr__(self) -> str:
        """A human-friendly string representation.

        Example:
            >>> repr(field_props)
            "<FieldProperties alias='customer_id' system_type='source' field_type='CUSTOM'>"

        Returns:
            String representation showing the pythonic field name/alias, system type, and field type
        """
        alias_str = self.alias if self.alias else 'unnamed'
        system_type_str = self.system_type if self.system_type else 'unknown'
        field_type_str = self.field_type if self.field_type else 'unknown'
        return f"<FieldProperties alias='{alias_str}' system_type='{system_type_str}' field_type='{field_type_str}'>"

    def __str__(self) -> str:
        """String representation (used by print()). Delegates to __repr__."""
        return self.__repr__()


class Record(BaseModel):
    """Represents a relationship between Source and Target fields. It's the unit of the Scenarios, and Scenario is a collection of records.

    How to use:
        Iterate over `scenario.records`. Each record can tell:
        "Take these source fields, apply this logic/mapping, and put result in these target fields."

    Example:
        >>> scenario = ParsedScenario(...)
        >>> for record in scenario.records:
        ...     print(f"Source: {record.source.field_names} -> Target: {record.target.field_names}")
        Source: ['first_name'] -> Target: ['firstname']
        >>> record = scenario.records[0]
        >>> for field in record.source:
        ...     print(f"{field.alias} (required: {field.required})")
        first_name (required: True)
        >>> record.source.unique_fields
        ['first_name']
        >>> record.target.required_fields
        ['firstname']

    Attributes:
        logic: Transformation logic string as defined in the BrynQ template
        unique: Whether this mapping is part of the unique key constraint
        required: Whether this mapping is required (cannot be empty/null)
        source: SourceTargetFields object containing source field metadata (field_names, unique_fields, required_fields, field_properties, etc.)
        target: SourceTargetFields object containing target field metadata (field_names, unique_fields, required_fields, field_properties, etc.)
        source_field_types: Maps source field name to its type (CUSTOM, LIBRARY, FIXED, EMPTY)
        target_field_types: Maps target field name to its type (CUSTOM, LIBRARY, FIXED, EMPTY)
        relation_type: Type of mapping relationship: 'one_to_one', 'one_to_many', 'many_to_one', or 'many_to_many'
        mapping: Value mapping configuration for translating source values to target values. Set to False when mapping has empty values list
        id: Unique identifier for this mapping record
        fixed_source_value: If source type is FIXED, this contains the fixed literal value to use for all target fields
    """
    model_config = ConfigDict(extra="allow", frozen=True)

    # Inherited properties applied to the whole group
    logic: Optional[str] = None
    unique: bool = False
    required: bool = False
    mapping: Union["ScenarioMappingConfiguration", bool, None] = None
    id: Optional[str] = None
    fixed_source_value: Optional[str] = None

    # The fields involved in this relationship
    source: SourceTargetFields
    target: SourceTargetFields
    source_field_types: Dict[str, str] = Field(default_factory=dict)
    target_field_types: Dict[str, str] = Field(default_factory=dict)

    # inferred
    relation_type: Literal["one_to_one", "one_to_many", "many_to_one", "many_to_many"]

    # Record dunders
    def __iter__(self):
        """Enable iteration over all fields (both source and target).

        Uses `source` and `target` attributes internally.

        Example:
            >>> for field in record:
            ...     print(field.label)
            First Name
            Last Name
            >>> list(record)
            [FieldProperties(...), FieldProperties(...)]

        """
        return iter(list(self.source.field_properties) + list(self.target.field_properties))


    def __repr__(self) -> str:
        """A human-friendly string representation.

        Example:
            >>> repr(record)
            "<Record id='rec_123' relation_type='one_to_one' source=[<FieldProperties alias='first_name'>, ...] -> target=[<FieldProperties alias='firstname'>, ...]>"

        Returns:
            String representation of the Record
        """
        # Build source field representation using FieldProperties
        source_repr = [repr(field) for field in self.source.field_properties]
        source_str = f"[{', '.join(source_repr)}]" if source_repr else "[]"

        # Build target field representation using FieldProperties
        target_repr = [repr(field) for field in self.target.field_properties]
        target_str = f"[{', '.join(target_repr)}]" if target_repr else "[]"

        # Build the representation string
        id_str = f"id='{self.id}' " if self.id else ""
        return (
            f"<Record {id_str}relation_type='{self.relation_type}' "
            f"source={source_str} -> target={target_str}>"
        )

    def __str__(self) -> str:
        """String representation (used by print()). Delegates to __repr__."""
        return self.__repr__()


# ============================================================================
# Parsing Logic (The Engine)
# ============================================================================

@dataclass
class UuidToFieldNameConverter:
    """Bundles all data needed to convert value mapping keys from UUIDs/schema patterns to field names.

    The API returns value mappings where BOTH input and output dictionaries use field identifier
    keys (UUIDs like "ea06ce9f-e10e-484e-bdf0-ec58087f15c5" or schema.name patterns like "work_schema-title").
    We MUST convert these identifier keys to readable field names (like {"title": "CEO"}) because
    the rest of the code expects field names, not UUIDs or schema patterns. This dataclass groups
    all the lookup data needed for that conversion, avoiding passing 5+ separate arguments.

    Created in ScenarioParser.parse() and passed to UuidToFieldNameMapper.__init__().

    Attributes:
        uuid_keyed_value_mappings: The value mappings that currently use field identifier keys (UUIDs/schema patterns)
            and need conversion to field names. Both input and output dictionaries have identifier keys.
        source_names: List of source field names (used to resolve UUIDs and validate keys), preserving API order.
        target_names: List of target field names (used to resolve UUIDs and validate keys), preserving API order.
        props: Dictionary mapping field names to FieldProperties (contains UUID-to-name lookups).
        detail_model: The scenario detail model with source/target field definitions.
    """
    uuid_keyed_value_mappings: Optional[ScenarioMappingConfiguration]
    source_names: List[str]
    target_names: List[str]
    props: FieldPropertiesMap
    detail_model: ScenarioDetail


class UuidToFieldNameMapper:
    """Converts value mapping keys from UUIDs/schema patterns to readable field names.

    The API returns value mappings where BOTH input and output dictionaries use field identifier
    keys (UUIDs like "ea06ce9f-e10e-484e-bdf0-ec58087f15c5" or schema.name patterns like "work_schema-title").
    This class converts those identifier keys to field names (like {"title": "CEO"}) because
    the rest of the codebase expects field names, not UUIDs or schema patterns. Uses multiple
    lookup strategies to handle API inconsistencies.
    """

    def __init__(self, uuid_converter: UuidToFieldNameConverter):
        """Initialize the converter with all data needed to convert UUID/schema pattern keys to field names.

        Args:
            uuid_converter: Contains UUID-keyed value mappings, field names, properties, and detail model.
                Created in ScenarioParser.parse() and provides all lookup data needed to convert
                field identifier keys (UUIDs like "ea06ce9f..." or schema patterns like "work_schema-title")
                to readable field names (like "title"). Used to convert keys in BOTH input and output dictionaries.
        """
        # Store all data needed to convert UUID/schema pattern keys in value mappings to field names
        self.uuid_converter = uuid_converter
        self.source_uuid_to_field: Dict[str, str] = {}
        self.target_uuid_to_field: Dict[str, str] = {}
        self.source_technical_to_pythonic: Dict[str, str] = {}
        self.target_technical_to_pythonic: Dict[str, str] = {}
        self._build_mappings()

    def _build_mappings(self) -> None:
        """Builds the lookup dictionaries needed for translation.

        Strategies:
        1. Technical Names -> Python Aliases (for CUSTOM fields).
        2. UUIDs -> Python Aliases (for all fields using props as source of truth).
        """
        # Strategy 1: Map Technical Names -> Python Aliases
        self._map_technical_names(
            model=self.uuid_converter.detail_model.source,
            names=self.uuid_converter.source_names,
            mapping=self.source_technical_to_pythonic,
            system_type=SystemType.SOURCE
        )
        self._map_technical_names(
            model=self.uuid_converter.detail_model.target,
            names=self.uuid_converter.target_names,
            mapping=self.target_technical_to_pythonic,
            system_type=SystemType.TARGET
        )

        # Strategy 2: Map UUIDs -> Python Aliases
        self._map_uuids(
            names=self.uuid_converter.source_names,
            tech_map=self.source_technical_to_pythonic,
            uuid_map=self.source_uuid_to_field
        )
        self._map_uuids(
            names=self.uuid_converter.target_names,
            tech_map=self.target_technical_to_pythonic,
            uuid_map=self.target_uuid_to_field
        )

    def _map_technical_names(
        self,
        model: SourceOrTargetField,
        names: List[str],
        mapping: Dict[str, str],
        system_type: SystemType
    ) -> None:
        """Maps technical names to python aliases for custom fields."""
        if not isinstance(model, CustomSourceOrTargetField):
            return

        names_set = set(names)  # Convert to set for fast lookup
        for item in model.data:
            if item.technical_name not in names_set:
                continue

            # Find matching pythonic name in props via UUID
            for py_name, props in self.uuid_converter.props.items():
                if props.system_type == system_type.value and props.uuid == item.uuid:
                    mapping[item.technical_name] = py_name
                    break

    def _map_uuids(
        self,
        names: List[str],
        tech_map: Dict[str, str],
        uuid_map: Dict[str, str]
    ) -> None:
        """Maps UUIDs to python aliases using props."""
        for name in names:
            py_name = tech_map.get(name, name)
            props = self.uuid_converter.props.get(py_name)
            if props and props.uuid:
                uuid_map[props.uuid] = py_name

    def convert_key(self, key: str, direction: Literal["source", "target"]) -> str:
        """Converts a single API mapping key to a pythonic field name.

        This helper method handles API inconsistency by trying multiple fallback strategies:
        1. UUID lookup (most reliable - direct match)
        2. Name lookup (handles technical names and pythonic names)
        3. Pattern matching (handles schema.name or schema-name patterns)

        Uses internal lookup maps (`source_uuid_to_field`, etc.) populated during initialization.

        Example:
            >>> mapper.convert_key('be3a4c1e...', 'source')
            'gender'

        Args:
            key: The raw key from the API (could be UUID, Name, or Schema.Name).
            direction: 'source' or 'target'.

        Returns:
            The best matching Pythonic field name.
        """
        if direction == "source":
            uuid_map = self.source_uuid_to_field
            tech_map = self.source_technical_to_pythonic
            valid_names = self.uuid_converter.source_names
        else:
            uuid_map = self.target_uuid_to_field
            tech_map = self.target_technical_to_pythonic
            valid_names = self.uuid_converter.target_names

        # Strategy 1: Direct UUID Lookup (Most reliable)
        if key in uuid_map:
            return uuid_map[key]

        # Strategy 2: Direct Name Lookup
        if key in valid_names:
            return tech_map.get(key, key)
        if key in tech_map.values():
            return key

        # Strategy 3: Pattern Matching (Heuristic)
        # Handles keys like 'schema_name.email' by checking suffixes
        all_names = set(tech_map.values()) | set(valid_names)
        for fname in all_names:
            if key.endswith(f'.{fname}') or key.endswith(f'-{fname}'):
                return tech_map.get(fname, fname)

        # Fallback: Return original key
        return key

    def convert_mapping_config(self) -> Optional[ScenarioMappingConfiguration]:
        """Converts value mapping keys from field identifiers to field names.

        The API returns value mappings where BOTH input and output dictionaries use field identifier
        keys (UUIDs like "ea06ce9f-e10e-484e-bdf0-ec58087f15c5" or schema.name patterns like "work_schema-title").
        This method converts all identifier keys to readable field names (like {"title": "CEO"})
        because the rest of the codebase expects field names, not UUIDs or schema patterns.

        Example:
            >>> converted = mapper.convert_mapping_config()
            >>> converted.values[0].input
            {'title': 'CEO'}  # Field identifier key converted to field name
            >>> converted.values[0].output
            {'job_code': '96'}  # UUID key converted to field name

        Returns:
            ScenarioMappingConfiguration with field name keys (not UUIDs or schema patterns),
            or None if no mapping config exists.
        """
        if not self.uuid_converter.uuid_keyed_value_mappings or not self.uuid_converter.uuid_keyed_value_mappings.values:
            return self.uuid_converter.uuid_keyed_value_mappings

        # Convert UUID/schema pattern keys to field names in each value mapping
        converted_values = []
        for val in self.uuid_converter.uuid_keyed_value_mappings.values:
            # Convert source field identifier keys (UUIDs/schema patterns) to field names
            new_in = {
                self.convert_key(key=k, direction="source"): v
                for k, v in val.input.items()
            }
            # Convert target field identifier keys (UUIDs/schema patterns) to field names
            new_out = {
                self.convert_key(key=k, direction="target"): v
                for k, v in val.output.items()
            }
            converted_values.append(MappingValue(input=new_in, output=new_out))

        return ScenarioMappingConfiguration(
            values=converted_values,
            default_value=self.uuid_converter.uuid_keyed_value_mappings.default_value
        )


class ScenarioParser:
    """Orchestrates the parsing of a Raw Scenario Dictionary.

    This class breaks the logic into three distinct phases:
    1. Extraction: Get raw names from the polymorphic API response.
    2. Property Building: Create metadata objects (`FieldProperties`) for every field.
    3. Linking: Create `Record` objects that link Sources to Targets.
    """

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse(self, scenario: Dict[str, Any]) -> "ParsedScenario":
        """Parse a raw API scenario dictionary into a ParsedScenario object.

        Args:
            scenario: Raw scenario dictionary from the BrynQ API

        Returns:
            ParsedScenario object with all parsed data
        """
        details = scenario.get("details", [])

        # Accumulators
        source_to_target = defaultdict(set)
        target_to_source = defaultdict(set)
        props: FieldPropertiesMap = {}
        value_mappings = defaultdict(list)
        aliases = set()
        alias_order = []

        records = []

        # details is the 'raw' api name for what is essentially called 'records' here.
        for detail in details:
            detail_model = ScenarioDetail.model_validate(detail)

            # Phase 1: extract names
            source_names = _extract_names_from_fields(detail_model.source)
            target_names = _extract_names_from_fields(detail_model.target)

            for source_name in source_names:
                source_to_target[source_name].update(target_names)
            for target_name in target_names:
                target_to_source[target_name].update(source_names)

            # Phase 2: Property Building
            # We use the same method for source and target to avoid code duplication, just need sepperate types

            # Identify reserved keys from target (Library fields) to avoid collisions with Source Custom fields
            reserved_keys = set()
            if detail_model.target.type == FieldType.LIBRARY.value:
                reserved_keys = set(target_names)  # Convert list to set for fast lookup

            base_props = FieldProperties.model_validate(detail)
            self._build_field_properties(
                fields=detail_model.source,
                names=source_names,
                sys_type=SystemType.SOURCE,
                base=base_props,
                props=props,
                aliases=aliases,
                alias_order=alias_order,
                reserved=reserved_keys
            )
            self._build_field_properties(
                fields=detail_model.target,
                names=target_names,
                sys_type=SystemType.TARGET,
                base=base_props,
                props=props,
                aliases=aliases,
                alias_order=alias_order
            )

            # Phase 3: Linking & Mapping Conversion
            # Convert value mapping keys from UUIDs/schema patterns to field names (API uses UUIDs/schema patterns, code expects field names)
            uuid_converter = UuidToFieldNameConverter(
                uuid_keyed_value_mappings=detail_model.mapping,
                source_names=source_names,
                target_names=target_names,
                props=props,
                detail_model=detail_model
            )
            converted_map = UuidToFieldNameMapper(uuid_converter).convert_mapping_config()

            if converted_map:
                # If values exist, store them in the lookup map
                if converted_map.values:
                    # Preserve order from API, but sort for consistent key generation
                    key = '|'.join(sorted(source_names)) if source_names else detail_model.id
                    value_mappings[key].append(converted_map)
                # If map exists but is empty, treat as False
                else:
                    converted_map = False

            records.append(
                self._build_record(
                    detail=detail_model,
                    source_names=source_names,
                    target_names=target_names,
                    base=base_props,
                    props=props,
                    mapping_cfg=converted_map
                )
            )

        # Final Phase: Assembly
        return self._build_parsed_scenario(
            raw=scenario,
            records=records,
            source_to_target_map=source_to_target,
            target_to_source_map=target_to_source,
            props=props,
            source_to_value_mappings=value_mappings
        )

    def _build_field_properties(
        self,
        fields: SourceOrTargetField,
        names: List[str],
        sys_type: SystemType,
        base: FieldProperties,
        props: FieldPropertiesMap,
        aliases: Set[str],
        alias_order: List[str],
        reserved: Optional[Set[str]] = None
    ) -> None:
        """Creates FieldProperties for a set of fields and registers them.

        Args:
            fields:      SourceOrTargetField object containing field definitions
            names:       Set of field names to process
            sys_type:    Either SystemType.SOURCE or SystemType.TARGET
            base:        Base FieldProperties shared across fields in this mapping
            props:       Dictionary to store field properties (modified in place)
            aliases:     Set to track custom field aliases (modified in place)
            alias_order: List to maintain custom alias order (modified in place)
            reserved:    Set of reserved keys to avoid collisions (e.g. target library names)
        """
        for name in names:
            label, l_en, l_nl = _extract_label_from_fields(fields, name) #only returned for library/custom

            # Determine Python Alias
            f_type_str = fields.type.value if isinstance(fields.type, FieldType) else fields.type
            is_custom = (f_type_str == FieldType.CUSTOM.value)

            # Only sanitize custom fields; libraries use fixed keys
            alias = _sanitize_alias(label or name) if is_custom else name
            key = alias if is_custom else name

            # Handle collisions for Custom fields if key is reserved (e.g. used by Target Library field)
            if is_custom and reserved and key in reserved:
                alias = f"{alias}_{sys_type.value}"
                key = alias

            config_props = _extract_config_props(fields, name)

            props[key] = base.model_copy(update={
                "system_type": sys_type.value,
                "field_type": f_type_str,
                "alias": alias,
                "uuid": _extract_uuid_from_fields(fields, name),
                "schema_name": _extract_schema_from_fields(fields, name),
                "technical_name": _extract_technical_name_from_fields(fields, name),
                "label": label,
                "label_en": l_en,
                "label_nl": l_nl,
                "description": _extract_description_from_fields(fields, name),
                "mapping": {},  # Mappings are stored at Record level, not Field level
                #config fields
                **config_props
            })

            if is_custom and key not in aliases:
                aliases.add(key)
                alias_order.append(key)

    def _build_record(
        self,
        detail: ScenarioDetail,
        source_names: List[str],
        target_names: List[str],
        base: FieldProperties,
        props: FieldPropertiesMap,
        mapping_cfg
    ) -> Record:
        """Creates a Record object representing the relationship.

        Args:
            detail: Validated ScenarioDetail object
            source_names: List of source field names (preserving API order)
            target_names: List of target field names (preserving API order)
            base: Base FieldProperties for this mapping
            props: Dictionary of field properties
            mapping_cfg: Converted mapping configuration

        Returns:
            Record object representing this mapping
        """
        # Helper to retrieve the correct prop keys, preserving order
        def _get_keys(names, field_obj, sys_type: SystemType):
            keys = []
            is_custom = (field_obj.type == FieldType.CUSTOM.value)
            for n in names:  # Iterate in order
                if is_custom:
                    # For custom fields, look up the actual key from props
                    uuid = _extract_uuid_from_fields(field_obj, n)
                    technical_name = _extract_technical_name_from_fields(field_obj, n)

                    # First try
                    lbl, _, _ = _extract_label_from_fields(field_obj, n)
                    sanitized_alias = _sanitize_alias(lbl or n)
                    if sanitized_alias in props:
                        prop = props[sanitized_alias]
                        if prop.system_type == sys_type.value and prop.field_type == FieldType.CUSTOM.value:
                            # Verify it's the same field by UUID or technical_name
                            if (uuid and prop.uuid == uuid) or (technical_name and prop.technical_name == technical_name):
                                keys.append(sanitized_alias)
                                continue

                    # Second try: find matching key in props by UUID or technical_name
                    found_key = None
                    for key, prop in props.items():
                        if prop.system_type == sys_type.value and prop.field_type == FieldType.CUSTOM.value:
                            if (uuid and prop.uuid == uuid) or (technical_name and prop.technical_name == technical_name):
                                found_key = key
                                break

                    if found_key:
                        keys.append(found_key)
                    else:
                        # Fallback: use sanitized alias (shouldn't happen if props were built correctly)
                        keys.append(sanitized_alias)
                else:
                    # For library/configuration fields, the name itself is the key
                    keys.append(n)
            return keys

        source_keys = _get_keys(source_names, detail.source, SystemType.SOURCE)
        target_keys = _get_keys(target_names, detail.target, SystemType.TARGET)

        # Determine Cardinality
        rel = RelationType.ONE_TO_ONE.value
        if len(source_names) > 1 and len(target_names) > 1:
            rel = RelationType.MANY_TO_MANY.value
        elif len(source_names) > 1:
            rel = RelationType.MANY_TO_ONE.value
        elif len(target_names) > 1:
            rel = RelationType.ONE_TO_MANY.value

        # Extract fixed_source_value based on source type
        fixed_source_value = None
        if detail.source.type == "FIXED":
            # For FIXED type, use the data directly (it's a string)
            fixed_source_value = detail.source.data
        elif detail.source.type == "CONFIGURATION":
            # For CONFIGURATION type, parse the config value according to its type
            if isinstance(detail.source, ConfigurationSourceOrTargetField) and detail.source.data:
                # Get the first config item (for one_to_one/one_to_many, there's typically one)
                config_item = detail.source.data[0]
                fixed_source_value = _parse_config_value(config_item)

        # Build FieldProperties lists
        source_field_props = [props[k] for k in source_keys if k in props]
        target_field_props = [props[k] for k in target_keys if k in props]

        # Build SourceTargetFields instances
        source_unique_fields = [k for k in source_keys if k in props and props[k].unique]
        source_required_fields = [k for k in source_keys if k in props and props[k].required]
        source_custom_fields = [k for k in source_keys if k in props and props[k].field_type == FieldType.CUSTOM.value]
        source_library_fields = [k for k in source_keys if k in props and props[k].field_type == FieldType.LIBRARY.value]
        source_fields_with_logic = [k for k in source_keys if k in props and props[k].logic is not None]

        target_unique_fields = [k for k in target_keys if k in props and props[k].unique]
        target_required_fields = [k for k in target_keys if k in props and props[k].required]
        target_custom_fields = [k for k in target_keys if k in props and props[k].field_type == FieldType.CUSTOM.value]
        target_library_fields = [k for k in target_keys if k in props and props[k].field_type == FieldType.LIBRARY.value]
        target_fields_with_logic = [k for k in target_keys if k in props and props[k].logic is not None]

        source_stf = SourceTargetFields(
            type="source",
            field_names=source_keys,
            unique_fields=source_unique_fields,
            required_fields=source_required_fields,
            field_properties=source_field_props,
            custom_fields=source_custom_fields,
            library_fields=source_library_fields,
            fields_with_logic=source_fields_with_logic
        )

        target_stf = SourceTargetFields(
            type="target",
            field_names=target_keys,
            unique_fields=target_unique_fields,
            required_fields=target_required_fields,
            field_properties=target_field_props,
            custom_fields=target_custom_fields,
            library_fields=target_library_fields,
            fields_with_logic=target_fields_with_logic
        )

        return Record(
            logic=base.logic,
            unique=base.unique,
            required=base.required,
            source_field_types={k: detail.source.type for k in source_keys},
            target_field_types={k: detail.target.type for k in target_keys},
            source=source_stf,
            target=target_stf,
            relation_type=rel,
            mapping=mapping_cfg,
            id=detail.id,
            fixed_source_value=fixed_source_value
        )

    def _build_parsed_scenario(
        self,
        raw,
        records,
        source_to_target_map,
        target_to_source_map,
        props,
        source_to_value_mappings
    ):
        """Constructs the final immutable ParsedScenario object.

        Args:
            raw: Original scenario dictionary
            records: List of Record objects
            source_to_target_map: Source to target mapping dictionary
            target_to_source_map: Target to source mapping dictionary
            props: Field properties dictionary
            source_to_value_mappings: Source field to value mappings dictionary

        Returns:
            ParsedScenario object
        """
        # Sort maps for deterministic behavior
        s_to_t = {k: sorted(v) for k, v in source_to_target_map.items()}
        t_to_s = {k: sorted(v) for k, v in target_to_source_map.items()}

        # Only include custom fields that are source fields (based on system_type)
        custom_fields = {k: v for k, v in props.items()
                        if v.field_type == FieldType.CUSTOM.value
                        and v.system_type == SystemType.SOURCE.value}
        custom_model = ParsedScenario._build_custom_field_model(custom_fields) if custom_fields else None

        # Build unique and required fields (all fields, regardless of source/target)
        unique_fields = [fid for fid, props in props.items() if props.unique]
        required_fields = [fid for fid, props in props.items() if props.required]

        # Build source and target unique/required fields separately
        source_field_names = [k for k, v in props.items() if v.system_type == SystemType.SOURCE.value]
        source_unique_fields = [k for k, v in props.items() if v.unique and v.system_type == SystemType.SOURCE.value]
        source_required_fields = [k for k, v in props.items() if v.required and v.system_type == SystemType.SOURCE.value]
        source_field_properties = [v for k, v in props.items() if v.system_type == SystemType.SOURCE.value]
        source_custom_fields = [k for k, v in props.items() if v.system_type == SystemType.SOURCE.value and v.field_type == FieldType.CUSTOM.value]
        source_library_fields = [k for k, v in props.items() if v.system_type == SystemType.SOURCE.value and v.field_type == FieldType.LIBRARY.value]
        source_fields_with_logic = [k for k, v in props.items() if v.system_type == SystemType.SOURCE.value and v.logic is not None]

        target_field_names = [k for k, v in props.items() if v.system_type == SystemType.TARGET.value]
        target_unique_fields = [k for k, v in props.items() if v.unique and v.system_type == SystemType.TARGET.value]
        target_required_fields = [k for k, v in props.items() if v.required and v.system_type == SystemType.TARGET.value]
        target_field_properties = [v for k, v in props.items() if v.system_type == SystemType.TARGET.value]
        target_custom_fields = [k for k, v in props.items() if v.system_type == SystemType.TARGET.value and v.field_type == FieldType.CUSTOM.value]
        target_library_fields = [k for k, v in props.items() if v.system_type == SystemType.TARGET.value and v.field_type == FieldType.LIBRARY.value]
        target_fields_with_logic = [k for k, v in props.items() if v.system_type == SystemType.TARGET.value and v.logic is not None]

        # Build nested structures
        source = SourceTargetFields(
            type="source",
            field_names=source_field_names,
            unique_fields=source_unique_fields,
            required_fields=source_required_fields,
            field_properties=source_field_properties,
            custom_fields=source_custom_fields,
            library_fields=source_library_fields,
            fields_with_logic=source_fields_with_logic
        )
        target = SourceTargetFields(
            type="target",
            field_names=target_field_names,
            unique_fields=target_unique_fields,
            required_fields=target_required_fields,
            field_properties=target_field_properties,
            custom_fields=target_custom_fields,
            library_fields=target_library_fields,
            fields_with_logic=target_fields_with_logic
        )

        all_source_fields = set(source_to_target_map.keys())
        all_target_fields = set(target_to_source_map.keys())

        # Collect target fields from records where logic contains 'ignoreCompare'
        target_fields_to_ignore_in_compare = set()
        for record in records:
            if record.logic and 'ignoreCompare' in record.logic:
                target_fields_to_ignore_in_compare.update(record.target.field_names)

        return ParsedScenario(
            name=raw.get("name", "Unnamed"),
            id=raw.get("id", ""),
            records_count=len(raw.get("details", [])),
            description=raw.get("description", ""),
            records=records,
            source_to_target_map=s_to_t,
            target_to_source_map=t_to_s,
            field_properties=props,
            source=source,
            target=target,
            unique_fields=unique_fields,
            required_fields=required_fields,
            custom_fields=custom_fields,
            custom_fields_model=custom_model,
            all_source_fields=all_source_fields,
            all_target_fields=all_target_fields,
            source_to_value_mappings=dict(source_to_value_mappings),
            target_fields_to_ignore_in_compare=target_fields_to_ignore_in_compare
        )


class ParsedScenario(BaseModel):
    """The final, usable representation of a Scenario.

    This object is what users interact with. It contains all records,
    lookups, and property maps needed to perform data validation and transformation.

    Example:
        >>> scenario = ParsedScenario(...)
        >>> scenario.name
        'Personal Information'
        >>> scenario.all_source_fields
        {'first_name', 'last_name', 'email'}
        >>> scenario.has_field('email', field_type='source')
        True
        >>> scenario.get_mapped_field_names('first_name')
        ['firstname']
        >>> for record in scenario.records:
        ...     print(record.relation_type)
        one_to_one

    Attributes:
        name: Scenario display name
        id: Scenario identifier
        records_count: Number of records in this scenario
        description: Scenario business context (description of what the scenario does)
        records: List of Record objects representing field mappings
        source_to_target_map: Dictionary mapping source field names to target field names
        target_to_source_map: Dictionary mapping target field names to source field names
        field_properties: Dictionary mapping field names to FieldProperties objects
        all_source_fields: Set of all source field names
        all_target_fields: Set of all target field names
        source: SourceTargetFields object containing source unique_fields and required_fields
        target: SourceTargetFields object containing target unique_fields and required_fields
        unique_fields: List of field names that are part of unique constraints (deprecated: use source.unique_fields or target.unique_fields)
        required_fields: List of field names that are required (deprecated: use source.required_fields or target.required_fields)
        custom_fields: Dictionary of custom field properties (filtered from field_properties)
        custom_fields_model: Dynamically generated Pandera schema model for custom fields
        source_to_value_mappings: Dictionary mapping source fields to value mapping configurations
        target_fields_to_ignore_in_compare: Set of target field names that should be ignored in compare function
            (determined by records where logic contains 'ignoreCompare')
    """
    # Core
    name: str
    id: str
    records_count: int
    description: str

    # Mapping Data
    records: List[Record]
    source_to_target_map: SourceToTargetMap
    target_to_source_map: TargetToSourceMap

    # Field Metadata
    field_properties: FieldPropertiesMap
    all_source_fields: Set[str]
    all_target_fields: Set[str]
    source: SourceTargetFields
    target: SourceTargetFields
    unique_fields: List[str]
    required_fields: List[str]

    # Custom Field Data
    custom_fields: FieldPropertiesMap
    custom_fields_model: Optional[type] = None

    # Value Mappings
    source_to_value_mappings: Dict[str, List[ScenarioMappingConfiguration]]

    # Compare Configuration
    target_fields_to_ignore_in_compare: Set[str] = Field(default_factory=set)

    @classmethod
    def from_api_dict(cls, scenario: Dict[str, Any]) -> "ParsedScenario":
        """Factory method to create a ParsedScenario from raw API data.

        Args:
            scenario: Raw scenario dictionary from the BrynQ API

        Returns:
            ParsedScenario object with all parsed data
        """
        return ScenarioParser().parse(scenario)

    def __getattribute__(self, name: str):
        """Override attribute access to emit deprecation warnings for unique_fields and required_fields."""
        if name == 'unique_fields':
            warnings.warn(
                "unique_fields is deprecated. Use scenario.source.unique_fields or scenario.target.unique_fields instead.",
                DeprecationWarning,
                stacklevel=2
            )
        elif name == 'required_fields':
            warnings.warn(
                "required_fields is deprecated. Use scenario.source.required_fields or scenario.target.required_fields instead.",
                DeprecationWarning,
                stacklevel=2
            )
        return super().__getattribute__(name)

    def get_source_fields_with_value_mappings(self) -> List[str]:
        """Returns a list of source fields that have value mappings.

        Uses `source_to_value_mappings` attribute internally.

        Example:
            >>> scenario.get_source_fields_with_value_mappings()
            ['gender', 'status']
            >>> list(scenario.source_to_value_mappings.keys())
            ['gender', 'status']

        Returns:
            List of source field names that have value mappings
        """
        return list(self.source_to_value_mappings.keys())

    def get_target_fields_with_value_mappings(self) -> List[str]:
        """Returns a list of target fields that have value mappings (via their mapped source fields).

        Uses `source_to_value_mappings` and `source_to_target_map` attributes internally.

        Example:
            >>> scenario.get_target_fields_with_value_mappings()
            ['gender_code', 'status_code']
            >>> scenario.source_to_target_map['gender']
            ['gender_code']

        Returns:
            List of target field names that have value mappings
        """
        target_fields_with_mappings: Set[str] = set()
        for source_key in self.source_to_value_mappings.keys():
            # Handle keys that might be multiple source fields joined with '|'
            source_fields = source_key.split('|') if '|' in source_key else [source_key]
            for source_field in source_fields:
                # Find target fields mapped from this source field
                target_fields = self.source_to_target_map.get(source_field, [])
                target_fields_with_mappings.update(target_fields)
        return sorted(list(target_fields_with_mappings))

    def has_field(self, field_name: str, field_type: Optional[str] = None) -> bool:
        """Check field existence in scenario. Can denote source or target, else looks for both.

        Uses `all_source_fields` and `all_target_fields` attributes internally.

        Example:
            >>> scenario.has_field('email')
            True
            >>> scenario.has_field('email', field_type='source')
            True
            >>> scenario.has_field('email', field_type='target')
            False
            >>> 'email' in scenario.all_source_fields
            True

        Args:
            field_name: The field name to check
            field_type: Optional field type filter ("source" or "target")

        Returns:
            True if field exists, False otherwise
        """
        if field_type == "source":
            return field_name in self.all_source_fields
        if field_type == "target":
            return field_name in self.all_target_fields
        return field_name in self.all_source_fields or field_name in self.all_target_fields

    # Dunder(like) methods for pythonic field access
    def __iter__(self):
        """Enable iteration over records.

        Example:
            >>> for record in ParsedScenario:
            ...     print(f"Record {record.id}: {len(record.source.field_names)} source fields")
            Record rec_123: 2 source fields
            Record rec_456: 1 source fields
            >>> list(ParsedScenario)
            [Record(id='rec_123', ...), Record(id='rec_456', ...)]
        """
        return iter(self.records)

    def __len__(self) -> int:
        """Return the number of records in this scenario.

        Example:
            >>> len(scenario)
            15
            >>> scenario.records_count
            15

        Returns:
            int: The number of records in the scenario
        """
        return len(self.records)

    def __getitem__(self, field_id: str) -> FieldProperties:
        """Enable dict-style access to field properties.

        Example:
            >>> ParsedScenario['customer_id']
            FieldProperties(alias='customer_id', uuid='...', label='Customer ID', ...)
            >>> ParsedScenario['customer_id'].required
            True
            >>> ParsedScenario['nonexistent']
            KeyError: Field 'nonexistent' not found in scenario 'Personal Information'.

        Args:
            field_id: The field name to look up

        Returns:
            FieldProperties object for the field

        Raises:
            KeyError: If field is not found
        """
        try:
            return self.field_properties[field_id]
        except KeyError as exc:
            raise KeyError(f"Field '{field_id}' not found in scenario '{self.name}'.") from exc

    def __getattr__(self, name: str) -> FieldProperties:
        """Enable attribute-style access to field properties.

        Example:
            >>> ParsedScenario.customer_id
            FieldProperties(alias='customer_id', uuid='...', label='Customer ID', ...)
            >>> ParsedScenario.customer_id.unique
            True
            >>> ParsedScenario.nonexistent
            AttributeError: 'nonexistent' is not a valid field in scenario 'Personal Information'.

        Args:
            name: The field name to look up

        Returns:
            FieldProperties object for the field

        Raises:
            AttributeError: If field is not found
        """
        if name.startswith("_") or name in self.__dict__ or name in self.__class__.__dict__:
            return super().__getattribute__(name)
        try:
            return self.field_properties[name]
        except KeyError as exc:
            raise AttributeError(f"'{name}' is not a valid field in scenario '{self.name}'.") from exc

    def __repr__(self) -> str:
        """A human-friendly string representation.

        Example:
            >>> repr(ParsedScenario)
            "<ParsedScenario (field mapping of scenario) name='Personal Information' id='abc123' details=5 unique=2 required=3>"

        Returns:
            String representation of the ParsedScenario
        """
        return (
            f"<ParsedScenario (field mapping of scenario) "
            f"name='{self.name}' id='{self.id}' "
            f"records={self.records_count} unique={len(self.unique_fields)} "
            f"required={len(self.required_fields)}>"
        )

    def __str__(self) -> str:
        """String representation (used by print()). Delegates to __repr__."""
        return self.__repr__()

    @staticmethod
    def _build_custom_field_model(custom_fields: FieldPropertiesMap) -> Optional[type]:
        """Dynamically creates a Pandera Schema for custom fields validation.

        Uses the `custom_fields` dictionary to extract field metadata (technical_name, label, required)
        and create a Pandera schema model for validation.

        Args:
            custom_fields: Dictionary mapping field names to their FieldProperties objects (filtered to CUSTOM fields only)

        Returns:
            A dynamically generated BrynQ Pandera model class or None when no fields can be mapped
        """
        annotations = {}
        fields = {}
        for name, props in custom_fields.items():
            annotations[name] = Optional[Series[String]]
            # Use fallback, technical_name can be None by definition for CUSTOM fields if not found in data
            alias_value = props.technical_name or props.uuid or name
            fields[name] = pa.Field(
                coerce=True,
                nullable=not props.required,
                alias=alias_value,
                description=props.label
            )

        if not annotations:
            return None
        fields["__annotations__"] = annotations
        return type("CustomFieldModel", (BrynQPanderaDataFrameModel,), fields)


class DummyRecord:
    """Dummy record for logging unmapped sources that don't belong to any record.

    Used internally by Scenarios.rename_fields to track source columns present in
    the DataFrame but not mapped by the scenario.
    """
    def __init__(self):
        """Initialize a dummy record with empty attributes."""
        self.id = None
        self.logic = None
        self.relation_type = None
        self.source = SourceTargetFields(
            type="source",
            field_names=[],
            unique_fields=[],
            required_fields=[],
            field_properties=[],
            custom_fields=[],
            library_fields=[],
            fields_with_logic=[]
        )
        self.target = SourceTargetFields(
            type="target",
            field_names=[],
            unique_fields=[],
            required_fields=[],
            field_properties=[],
            custom_fields=[],
            library_fields=[],
            fields_with_logic=[]
        )


class Scenarios():
    """
    Provides convenient access to BrynQ scenarios, with lookups and a Pythonic interface.

    """
    # Missing value representations to detect in dataframes
    MISSING_VALUES: List[str] = [
        '<NA>', 'nan', 'None', 'NaN', 'null', 'NaT', '_NA_', '', r'\[\]', r'\{ \}'
    ]
    def __init__(self, brynq_instance: Any):
        """Initializes the scenarios manager.

        Fetches and parses scenarios from the BrynQ API. Scenarios are cached after first fetch.
        Dunder methods (__getitem__, __iter__, __len__) auto-fetch if not loaded.

        **Core Methods:**
            - get(): Fetches/returns ParsedScenario objects (cached after first call)

        **Convenience Methods:**
            - find_scenarios_with_field(): Find scenarios containing a field
            - scenario_names: Cached property with all scenario names

        **Dunder Methods:**
            - __getitem__: Dict access `scenarios['Name']`
            - __iter__: Iterate scenarios `for scenario in scenarios:`
            - __len__: Count scenarios `len(scenarios)`

        **ParsedScenario Iteration:**
            - Records: `for record in scenario:` (mapping records with logic/relation types)
            - Fields: `scenario.keys()`, `scenario.values()`, `scenario.items()`
            - Field access: `scenario['field']` or `scenario.field` (dict/attr style)
            - Source/Target: `scenario.source.field_names`, `scenario.target.field_names`, `scenario.source.unique_fields`, etc.
            - String repr: `print(scenario)` shows summary

        **Record Iteration:**
            - All fields: `for field in record:` (iterates over both source and target fields)
            - Source/Target: `for field in record.source:`, `for field in record.target:`
            - Field names: `record.source.field_names`, `record.target.field_names`
            - Field properties: `record.source.field_properties`, `record.target.field_properties`

        **Transformation Methods:**
            - rename_fields(): Rename/transform DataFrame columns per scenario.
            - apply_value_mappings(): Apply value mappings (e.g., 'F' → '1') per scenario.
            - add_fixed_values(): Add fixed literal values to DataFrames

        Args:
            brynq_instance: Authenticated BrynQ client instance.
        """
        self._brynq = brynq_instance

        # Attributes populated by get()
        self.raw_scenarios: Optional[List[Dict]] = None
        self.scenarios: Optional[List[ParsedScenario]] = None

    # ============================================================================
    # Public API Methods
    # ============================================================================

    def get(self, strict: bool = True) -> List[ParsedScenario]:
        """Fetches all scenarios from the API and returns them as ParsedScenario objects.

        Results are cached after the first call.

        Args:
            strict: If True, raises ValueError on validation errors. If False, skips invalid scenarios.

        Returns:
            List[ParsedScenario]: Validated scenario objects.
        """
        # only get once, else reuse initialized object
        if self.scenarios is None:
            self.raw_scenarios = self._fetch_from_api(strict=strict)
            self.scenarios = [
                ParsedScenario.from_api_dict(scenario=s)
                for s in self.raw_scenarios if "name" in s
            ]
            return self.scenarios
        else:
            return self.scenarios

    def find_scenarios_with_field(
        self,
        field_name: str,
        field_type: str = "source"
    ) -> List[ParsedScenario]:
        """Find all scenarios that contain a specific field.

        Example:
            >>> scenarios.find_scenarios_with_field('employee_id')
            []
            >>> scenarios.find_scenarios_with_field('employee_id', field_type='target')
            [<ParsedScenario name='Personal information' id='3c7f8e04-5b74-408f-a2d8-ad99b924a1af' details=15 unique=2 required=20>, <ParsedScenario name='Adres' ...>]

        Args:
            field_name (str): The field name to search for.
            field_type (str): The type of field to search in;
                must be either "source" or "target". Defaults to "source".

        Returns:
            List[ParsedScenario]: List of ParsedScenario objects containing the specified field.
        """
        return [
            scenario for scenario in self.get()
            if scenario.has_field(field_name, field_type=field_type)
        ]

    @cached_property
    def scenario_names(self) -> List[str]:
        """A list of all scenario names.

        Example:
            >>> scenarios.scenario_names
            ['Personal information', 'Adres', 'Bank Account', 'Contract Information', ...]

        Returns:
            List[str]: List of all scenario names.
        """
        return [s.name for s in self.get()] if self.scenarios is not None else []

    def __getitem__(self, scenario_name: str) -> ParsedScenario:
        """Returns scenario by name using dict-style access.

        Example:
            >>> scenario = scenarios['Personal information']
            >>> scenario.name
            'Personal information'
            >>> scenario['first_name'].required
            True
            >>> scenario.firstname.required  # Attribute-style access also works
            True

        Args:
            scenario_name: Name of the scenario to retrieve.

        Returns:
            ParsedScenario object with records, mappings, and field properties.

        Raises:
            KeyError: If scenario name not found.
        """
        scenarios = {s.name: s for s in self.get()}
        if scenario_name not in scenarios:
            raise KeyError(f"Scenario '{scenario_name}' not found.")
        return scenarios[scenario_name]

    def __iter__(self) -> Iterator[ParsedScenario]:
        """Iterates over all parsed scenarios.

        Example:
            >>> for scenario in scenarios:
            ...     print(f"{scenario.name}: {len(scenario.required_fields)} required fields")
            Personal information: 20 required fields

        Yields:
            ParsedScenario: Each scenario object.
        """
        return iter(self.get())

    def __len__(self) -> int:
        """Return the number of parsed scenarios.

        Example:
            >>> len(scenarios)
            13

        Returns:
            int: The number of available scenarios.
        """
        return len(self.get())

    # ============================================================================
    # Internal API Helpers
    # ============================================================================

    def _fetch_from_api(self, strict: bool = True) -> List[Dict[str, Any]]:
        """Fetches raw scenario data from BrynQ API and validates it.

        Makes HTTP GET request, validates JSON against Scenario model.
        Invalid scenarios are skipped (warning) or raise error, based on strict flag.

        Args:
            strict (bool): If True, raise ValueError on validation errors. If False, skip invalid scenarios with warning.

        Returns:
            List[Dict[str, Any]]: Validated scenario dictionaries (raw API format). Contains name, id, description, details.

        Raises:
            requests.HTTPError: API request failed (non-2xx status).
            TypeError: API response is not a list.
            ValueError: strict=True and validation failed.

        Note:
            Internal method called by get(). Returns raw dicts; get() converts to ParsedScenario objects.
        """
        response = self._brynq.brynq_session.get(
            url=(
                f"{self._brynq.url}interfaces/"
                f"{self._brynq.data_interface_id}/scenarios"
            ),
            timeout=self._brynq.timeout,
        )
        response.raise_for_status()
        scenario_list = response.json()
        if not isinstance(scenario_list, list):
            raise TypeError(f"Expected a list of scenarios, but got {type(scenario_list).__name__}.")

        valid_scenarios, invalid_scenarios = Functions.validate_pydantic_data(
            scenario_list,
            schema=Scenario,
            debug=True,
        )

        if invalid_scenarios:
            msg = (f"{len(invalid_scenarios)} scenario(s) failed validation and were skipped.")
            if strict:
                raise ValueError(f"Invalid scenario data found: {msg}")
            warnings.warn(msg, UserWarning, stacklevel=2)

        return valid_scenarios

    # ============================================================================
    # Public Transformation Methods
    # ============================================================================

    def add_fixed_values(
        self,
        df: pd.DataFrame,
        scenario_name: str
    ) -> pd.DataFrame:
        """Adds fixed literal values to DataFrame columns based on scenario mappings.

        Creates new columns with target field names, fills all rows with the fixed value.
        Only processes records with relation_type 'one_to_one' or 'one_to_many'.
        Supports both FIXED and CONFIGURATION source field types.

        Args:
            df (pd.DataFrame): Input DataFrame to add fixed value columns to.
            scenario_name (str): Name of scenario containing fixed value mappings.

        Returns:
            pd.DataFrame: Copy of input DataFrame with fixed value columns added.

        Raises:
            ValueError: Scenario name not found.

        Examples
        --------
        Adding a fixed value column from a scenario with FIXED source type.

        >>> df = pd.DataFrame({'id': [1, 2, 3], 'name': ['John', 'Jane', 'Bob']})
        >>> df.columns.tolist()
        ['id', 'name']
        >>> df
           id   name
        0   1   John
        1   2   Jane
        2   3    Bob

        Scenario has a record with FIXED source value 'NL' mapping to target 'country_code'.

        >>> df = scenarios.add_fixed_values(df, 'My Scenario')
        >>> df
           id   name   country_code
        0   1   John             NL
        1   2   Jane             NL
        2   3    Bob             NL

        The 'country_code' column is added and filled with the fixed value 'NL' for all rows.

        Also supports CONFIGURATION source types. Config values are parsed according to
        their type (TEXT, EMAIL, NUMBER, SELECTION, DATEPICKER, etc.) during record creation.

        Note:
            For many_to_one/many_to_many mappings, use rename_fields() instead.
        """
        df_fixed = df.copy()
        try:
            scenario = self[scenario_name]
        except KeyError as e:
            raise ValueError(f"Scenario with name '{scenario_name}' not found.") from e

        for record in scenario.records:
            if record.relation_type not in ("one_to_one", "one_to_many"):
                continue

            if not record.fixed_source_value:
                warnings.warn(f"Missing fixed/config value for record {record.id}", stacklevel=2)
                continue

            for target_field in record.target.field_names:
                df_fixed[target_field] = record.fixed_source_value

        return df_fixed

    def apply_value_mappings(
        self,
        df: pd.DataFrame,
        scenario_name: str,
        drop_unmapped: bool = False,
        how: Literal[ #Union list, geen valMap dan meer explicit
            'exactValMap',
            'ignoreCaseValMap',
            'ignoreSpecialValMap',
            'ignoreSpacesValMap',
            'flexValMap'
        ] = 'exactValMap'
    ) -> Tuple[pd.DataFrame, Set[str], pd.DataFrame]:
        """Transforms source values to target values based on scenario mappings.

        Processes records with value mapping configurations (e.g., "M" -> "1").
        Handles various relation types by preparing source values appropriately (direct vs concatenated).

        Mapping strategies (how parameter):
            - exactValMap: Precise matching (default)
            - ignoreCaseValMap: Case-insensitive matching
            - ignoreSpecialValMap: Ignores special characters including spaces
            - ignoreSpacesValMap: Ignores spaces only
            - flexValMap: Case-insensitive + ignores special characters including spaces

        Strategy selection priority:
            1. Check record.logic for 'matching strategy' (higher priority), evaluate if correspond to the strategy names above.
            2. Fall back to how kwarg if no match in logic

        Examples
        --------
        Example 1: Basic value mapping with exactValMap (default).

        >>> df = pd.DataFrame({'gender': ['F', 'M', 'F']})
        >>> # Scenario mapping configuration:
        >>> #   {'gender': 'F'} -> {'gender_code': '1'}
        >>> #   {'gender': 'M'} -> {'gender_code': '0'}
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario')
        >>> df
           gender  gender_code
        0       F            1
        1       M            0
        2       F            1

        Example 2: Case-insensitive matching with ignoreCaseValMap.

        >>> df = pd.DataFrame({'status': ['Active', 'ACTIVE', 'inactive']})
        >>> # Scenario mapping (source values normalized to lowercase for matching):
        >>> #   {'status': 'active'} -> {'status_code': '1'}  # Matches 'Active', 'ACTIVE'
        >>> #   {'status': 'inactive'} -> {'status_code': '0'}  # Matches 'inactive'
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario', how='ignoreCaseValMap')
        >>> df
            status  status_code
        0   Active            1
        1   ACTIVE            1
        2   inactive          0

        Example 3: Flexible matching with flexValMap (ignores case and special chars).

        >>> df = pd.DataFrame({
        ...     'product_code': ['ABC-123', 'xyz_456', 'MNO 789', 'PQR@#$%']
        ... })
        >>> # Scenario mapping (source values normalized: lowercase + remove special chars):
        >>> #   {'product_code': 'abc123'} -> {'product_id': 'P001'}  # Matches 'ABC-123'
        >>> #   {'product_code': 'xyz456'} -> {'product_id': 'P002'}  # Matches 'xyz_456'
        >>> #   {'product_code': 'mno789'} -> {'product_id': 'P003'}  # Matches 'MNO 789'
        >>> #   {'product_code': 'pqr'} -> {'product_id': 'P004'}     # Matches 'PQR@#$%'
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario', how='flexValMap')
        >>> df
          product_code product_id
        0      ABC-123       P001
        1      xyz_456       P002
        2      MNO 789       P003
        3      PQR@#$%       P004

        Example 4: Many-to-one mapping with concatenated fields and special chars.

        >>> df = pd.DataFrame({
        ...     'first_name': ['John', 'Jane', 'José'],
        ...     'last_name': ['Doe-Smith', 'O\'Brien', 'García-López']
        ... })
        >>> # Scenario mapping (concatenated with |, then normalized for matching):
        >>> #   {'first_name': 'John', 'last_name': 'Doe-Smith'} -> 'John|Doe-Smith' -> 'john|doesmith' -> {'full_id': 'JD001'}
        >>> #   {'first_name': 'Jane', 'last_name': 'O\'Brien'} -> 'Jane|O\'Brien' -> 'jane|obrien' -> {'full_id': 'JO002'}
        >>> #   {'first_name': 'José', 'last_name': 'García-López'} -> 'José|García-López' -> 'josé|garclpez' -> {'full_id': 'JG003'}
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario', how='flexValMap')
        >>> df
          first_name       last_name   full_id
        0       John       Doe-Smith     JD001
        1       Jane         O'Brien     JO002
        2       José    García-López     JG003

        Example 5: ignoreSpacesValMap - removes spaces but preserves other special chars.

        >>> df = pd.DataFrame({
        ...     'location': ['New York', 'New  York', 'New   York', 'New     York', 'New-York', 'New_York']
        ... })
        >>> # Scenario mapping (source values normalized: remove spaces only, preserves hyphens/underscores):
        >>> #   {'location': 'New   York'} -> {'location_code': 'NYC'}  # Mapping has spaces, normalizes to 'NewYork'
        >>> #   {'location': 'New-York'} -> {'location_code': 'NYD'}  # Matches 'New-York' (exact, spaces removed)
        >>> #   {'location': 'New_York'} -> {'location_code': 'NYU'}  # Matches 'New_York' (exact, spaces removed)
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario', how='ignoreSpacesValMap')
        >>> df
            location        location_code
        0   New York                 NYC
        1   New  York                NYC
        2   New   York               NYC
        3   New     York             NYC
        4   New-York                 NYD
        5   New_York                 NYU

        Example 6: Per-record strategy override via logic field.

        >>> df = pd.DataFrame({'code': ['A-B', 'C D', 'E|F']})
        >>> # Record 1: logic='flexValMap' -> uses flexValMap (normalizes to 'ab', 'cd', 'ef')
        >>> # Record 2: logic=None -> uses how='exactValMap' (exact match required)
        >>> df, _, stats = scenarios.apply_value_mappings(df, 'My Scenario', how='exactValMap')
        >>> # Records with flexValMap in logic will match 'A-B'->'ab', 'C D'->'cd', 'E|F'->'ef'
        >>> # Records without logic will only match exact values from how kwarg

        Args:
            df: Input DataFrame.
            scenario_name: Name of the scenario.
            drop_unmapped: If True (and no default value exists), drops rows that couldn't be mapped.
            how: Mapping strategy to use (default: 'exactValMap'). Can be overridden per record via logic.

        Returns:
            Tuple[pd.DataFrame, Set[str], pd.DataFrame]:
                1. Transformed DataFrame.
                2. Set of source fields processed.
                3. Statistics DataFrame detailing mapping success rates and value distributions.

        Statistics DataFrame columns:
            - record_id: Unique identifier for the mapping record
            - source_fields: Source field names, pipe-separated if multiple
            - target_fields: Target field names, pipe-separated if multiple
            - relation_type: Relation type ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many')
            - mapping_strategy: Mapping strategy used ('exactValMap', 'ignoreCaseValMap', etc.)
            - total_rows: Total number of rows in DataFrame
            - mapped_rows: Number of rows successfully mapped
            - unmapped_rows: Number of rows that couldn't be mapped
            - mapping_success_pct: Percentage of rows successfully mapped
            - successful_indices: List of DataFrame row indices that were successfully mapped
            - unsuccessful_indices: List of DataFrame row indices that couldn't be mapped
            - mapped_value_counts: Dictionary of mapped source values and their counts
            - unmapped_value_counts: Dictionary of unmapped source values and their counts
            - used_mapping_values: List of mapping rules that were used (with counts)
            - unused_mapping_values: List of mapping rules that were never encountered
        """
        try:
            scenario = self[scenario_name]
        except KeyError:
            # If scenario not found, return empty results
            stats_df = pd.DataFrame(
                columns=[
                    'record_id',
                    'source_fields',
                    'target_fields',
                    'relation_type',
                    'mapping_strategy',
                    'total_rows',
                    'mapped_rows',
                    'unmapped_rows',
                    'mapping_success_pct',
                    'successful_indices',
                    'unsuccessful_indices',
                    'mapped_value_counts',
                    'unmapped_value_counts',
                    'used_mapping_values',
                    'unused_mapping_values'
                ]
            )
            return df, set(), stats_df

        # Warn about missing values before processing to help users identify data quality issues early.
        # Missing values in source fields can cause mappings to fail silently or produce unexpected
        # results, so detecting them upfront prevents confusion about why certain rows didn't map correctly.
        all_source_fields_to_check = set()
        for record in scenario.records:
            if record.mapping:
                all_source_fields_to_check.update(record.source.field_names)

        if all_source_fields_to_check:
            missing_value_counts = self._detect_missing_values_in_fields(
                df=df,
                source_field_names=list(all_source_fields_to_check)
            )
            if missing_value_counts:
                missing_details = [
                    f"{field}: {count} occurrence(s)"
                    for field, count in missing_value_counts.items()
                ]
                warnings.warn(
                    f"DataFrame contains missing values (pd.NA or string representations) "
                    f"in source fields used for value mapping: {', '.join(missing_details)}. "
                    f"These may affect mapping accuracy.",
                    UserWarning,
                    stacklevel=2
                )

        handled_source_fields = set()
        statistics_rows = []

        # Process each record to apply value mappings (source values -> target values)
        for record in scenario.records:
            if not record.mapping:
                continue

            source_field_names = record.source.field_names
            target_field_names = record.target.field_names
            total_rows = len(df)
            default_val = record.mapping.default_value

            # Ensure source fields are present in the dataframe, else add default value to target column
            missing_fields = [field for field in source_field_names if field not in df.columns]
            if missing_fields:
                warnings.warn(f"Source fields {missing_fields} not found in dataframe for record {record.id}. Creating target columns with default values.", stacklevel=2)
                for target_field in target_field_names:
                    df[target_field] = default_val if default_val else None

                # Determine mapping strategy even when fields are missing (for statistics tracking)
                mapping_strategy = self._determine_mapping_strategy(record.logic, how)

                # Record statistics when missing: 0 mapped rows, all mappings unused (source fields missing)
                statistics_rows.append({
                    'record_id': record.id,
                    'source_fields': '|'.join(source_field_names),
                    'target_fields': '|'.join(target_field_names),
                    'relation_type': record.relation_type,
                    'mapping_strategy': mapping_strategy,
                    'total_rows': total_rows,
                    'mapped_rows': 0,
                    'unmapped_rows': total_rows,
                    'mapping_success_pct': 0.0,
                    'successful_indices': [],
                    'unsuccessful_indices': df.index.tolist(),
                    'mapped_value_counts': {},
                    'unmapped_value_counts': {},
                    'used_mapping_values': [],
                    'unused_mapping_values': []  # Source fields missing, so no mapping values could be evaluated
                })
                continue

            # Source fields are not missing:
            else:
                # Track processed fields
                handled_source_fields.update(source_field_names)

                # Determine mapping strategy: check record.logic first (higher priority), then use how kwarg
                mapping_strategy = self._determine_mapping_strategy(record.logic, how)

                # Step 1: Normalize dataframe according to mapping strategy.
                normalized_df = df[source_field_names].copy()
                for field_name in source_field_names:
                    if field_name in normalized_df.columns:
                        normalized_df[field_name] = normalized_df[field_name].apply(
                            lambda val: self._normalize_value_for_mapping(val, mapping_strategy)
                        )

                # Step 1b: Create Series with normalized source values (one Series, shared by all target fields)
                # Format: "f"/"m" (single) or "john|doe" (multiple, pipe-separated, pipes preserved)
                normalized_source_series = self._concatenate_source_fields(df=normalized_df, source_fields=source_field_names)

                # Step 1c: Create original (non-normalized) concatenated series for statistics and fillna
                concatenated_source_series = self._concatenate_source_fields(df=df, source_fields=source_field_names)

                # Step 2.A: Create empty mapping dicts (one dict per target field)
                # Structure: {target_field: {normalized_source_value: target_value}}
                # Each target gets its own dict; all use the same Series from Step 1
                # Example: {"gender_code": {"f": "1"}, "status": {"f": "Active"}} (if ignoreCaseValMap)
                replacements_by_target = {target_field: {} for target_field in target_field_names}

                # defined_mapping_values: tracks all mapping definitions for statistics (used vs unused)
                defined_mapping_values = []

                # 2.B Build lookup dictionaries for existing record.mapping.values
                # If values list is empty, skip building mappings but still collect statistics
                if record.mapping.values:
                    for mapping_value in record.mapping.values:
                        source_map_val = mapping_value.input
                        target_map_val = mapping_value.output
                        if not source_map_val or not target_map_val:
                            continue

                        # Concat/combine source values mapping to create the lookup key value.
                        # Normalize mapping values first, then join with pipe to preserve separator.
                        # (e.g., ["John", "Doe"] -> normalize each -> ["john", "doe"] -> concat -> "john|doe")
                        source_values = []
                        normalized_source_values = []
                        for field_name in source_field_names:
                            if field_name in source_map_val:
                                source_val = str(source_map_val[field_name]).strip()
                                source_values.append(source_val)
                                # Normalize individual field value before concatenation
                                normalized_source_values.append(
                                    self._normalize_value_for_mapping(source_val, mapping_strategy)
                                )
                            else:
                                source_values = None
                                normalized_source_values = None
                                break

                        # Validate that we have values for ALL source fields before using this mapping.
                        if source_values and len(source_values) == len(source_field_names):
                            combined_source_val = '|'.join(source_values)
                            normalized_combined_source_val = '|'.join(normalized_source_values)

                            # Store mapping definition for statistics tracking (not used for transformation).
                            mapping_def = {
                                'input': combined_source_val,
                                'output': {target_field: str(target_map_val.get(target_field, '')).strip()
                                        for target_field in target_field_names if target_field in target_map_val}
                            }
                            defined_mapping_values.append(mapping_def)

                            # Store mapping in lookup dict for actual transformation (used by apply_mapping_to_target in Step 4).
                            for target_field in target_field_names:
                                if target_field in target_map_val:
                                    target_val = str(target_map_val[target_field]).strip()
                                    replacements_by_target[target_field][normalized_combined_source_val] = target_val

                # Step 3: Apply mappings to target columns using normalized source series for lookup
                for target_field in target_field_names:
                    df = self._apply_mapping_to_target(
                        df=df,
                        concatenated_source_series=normalized_source_series,
                        target_field=target_field,
                        replacements=replacements_by_target[target_field],
                        default_val=default_val,
                        original_source_series=concatenated_source_series
                    )

                # Step 4: Collect statistics on mapping results
                all_mapped_source_values = set()
                for replacements in replacements_by_target.values():
                    all_mapped_source_values.update(replacements.keys())

                # Step 4b: Determine which rows were successfully mapped vs unmapped
                is_mapped = normalized_source_series.isin(all_mapped_source_values)
                mapped_rows = is_mapped.sum()
                unmapped_rows = (~is_mapped).sum()

                # Get indices of successful and unsuccessful mappings
                successful_indices = df.index[is_mapped].tolist()
                unsuccessful_indices = df.index[~is_mapped].tolist()

                # Step 4c: Count occurrences of each source VALUE in the data
                # Analyzes what values actually appeared in the data, regardless of mapping definitions.
                # (1) mapped_value_counts_dict: values that were successfully mapped (for Step 5d to use)
                # (2) unmapped_value_counts_dict: values that didn't map (to identify gaps in mapping rules)
                # (3) Convert Series to dict to avoid truncation and ensure ALL values are preserved in statistics.
                mapped_values = concatenated_source_series[is_mapped]
                unmapped_values = concatenated_source_series[~is_mapped]
                mapped_value_counts_dict = {}
                unmapped_value_counts_dict = {}
                if len(mapped_values) > 0:
                    mapped_value_counts_dict = dict(mapped_values.value_counts())
                if len(unmapped_values) > 0:
                    unmapped_value_counts_dict = dict(unmapped_values.value_counts())

                # Step 4d: Compare defined MAPPING RULES (from Step 3) against actual data.
                # Analyzes which mapping definitions were used vs unused, regardless of what values exist in data.
                # Different from Step 4c: 4c analyzes data values, 4d analyzes mapping rules.
                # (1) unused mappings: rules defined but never encountered (possibly typos or outdated rules)
                # (2) used mappings: rules that actually fired and how many times (validates mapping logic)
                # Need to compare normalized mapping inputs against normalized data values
                # Build a map of normalized values to their counts (sum counts for values that normalize to same key)
                normalized_mapped_inputs = {}
                for orig_val, count in mapped_value_counts_dict.items():
                    normalized_val = self._normalize_value_for_mapping(orig_val, mapping_strategy)
                    normalized_mapped_inputs[normalized_val] = normalized_mapped_inputs.get(normalized_val, 0) + count

                unused_mapping_values = []
                used_mapping_values_with_counts = []
                for mapping_def in defined_mapping_values:
                    mapping_input = mapping_def['input']
                    normalized_mapping_input = self._normalize_value_for_mapping(mapping_input, mapping_strategy)
                    # found in data: used rule (compare normalized values)
                    if normalized_mapping_input in normalized_mapped_inputs:
                        used_mapping_values_with_counts.append({
                            'input': mapping_input,
                            'output': mapping_def['output'],
                            'count': normalized_mapped_inputs.get(normalized_mapping_input, 0)
                        })
                    # never found in the data (unused rule)
                    else:
                        unused_mapping_values.append(mapping_def)

                # Optionally filter out unmapped rows if requested
                if drop_unmapped and not default_val:
                    df = df[is_mapped]

                # Step 4f: Calculate mapping success rate and store all statistics for this record.
                # At this point, we have all the information needed (counts from 5c, used/unused from 5d, row counts from 5b).
                # We store statistics per record because each record has different source/target fields and relation types, so users can analyze effectiveness per record and per mapping rule.
                mapping_success_pct = (mapped_rows / total_rows * 100) if total_rows > 0 else 0.0
                statistics_rows.append({
                    'record_id': record.id,
                    'source_fields': '|'.join(source_field_names),
                    'target_fields': '|'.join(target_field_names),
                    'relation_type': record.relation_type,
                    'mapping_strategy': mapping_strategy,
                    'total_rows': total_rows,
                    'mapped_rows': mapped_rows,
                    'unmapped_rows': unmapped_rows,
                    'mapping_success_pct': mapping_success_pct,
                    'successful_indices': successful_indices,
                    'unsuccessful_indices': unsuccessful_indices,
                    'mapped_value_counts': mapped_value_counts_dict,
                    'unmapped_value_counts': unmapped_value_counts_dict,
                    'used_mapping_values': used_mapping_values_with_counts,
                    'unused_mapping_values': unused_mapping_values
                })

        if statistics_rows:
            stats_df = pd.DataFrame(statistics_rows)
        else:
            stats_df = pd.DataFrame(columns=[
                'record_id', 'source_fields', 'target_fields', 'relation_type',
                'mapping_strategy', 'total_rows', 'mapped_rows', 'unmapped_rows', 'mapping_success_pct',
                'successful_indices', 'unsuccessful_indices',
                'mapped_value_counts', 'unmapped_value_counts',
                'used_mapping_values', 'unused_mapping_values'
            ])

        return df, handled_source_fields, stats_df

    def rename_fields(
        self,
        df: pd.DataFrame,
        scenario_name: str,
        columns_to_keep: List[str] = None,
        drop_unmapped: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Renames and transforms DataFrame columns based on scenario field mappings.

        Handles complex mappings like concatenation (many-to-one) and splitting (one-to-many).
        Records with value mappings are logged but skipped (use `apply_value_mappings` for those).

        Args:
            df: Input DataFrame.
            scenario_name: Name of the scenario.
            columns_to_keep: List of source column names to preserve even if mapped.
            drop_unmapped: If True, drops source columns that were successfully mapped (unless in columns_to_keep).

        Returns:
            Tuple containing:
                - Modified DataFrame with renamed/transformed columns based on scenario mappings.
                - Statistics DataFrame (stats_df) with detailed mapping information (see Notes).

        Raises:
            KeyError: If scenario_name is not found. Returns original DataFrame with empty statistics.

        Logic types:
            - "concat": Concatenate all sources with '|', fill all targets
            - "fill": Map source[i] → target[i] in order
            - "keep source": Keep source fields unchanged, no target columns
            - Default (no logic): Uses relation_type:
                * one_to_one: Direct mapping source[0] → target[0]
                * one_to_many: Duplicate single source value to all target fields
                * many_to_one: Concatenate all source fields with '|' into single target
                * many_to_many (n:m): Behavior depends on field counts:
                  - n == m: Direct 1:1 mapping source[i] → target[i]
                  - n < m: Map first n sources to first n targets, fill remaining with last source
                  - n > m: Concatenate all sources to each target field

        Notes:
            The statistics DataFrame (stats_df) provides comprehensive visibility into the transformation process:

            **What it reports:**
                - For each record processed: source/target column mappings, mapping status (mapped/source_missing/kept_source/value_mapped),
                  number of rows affected, mapping type (concat/fill/one_to_one/etc.), and default logic used (if applicable).
                - For unmapped sources: Columns that exist in the DataFrame but weren't processed by any record.

            **Statistics DataFrame columns:**
                - record_id: Unique identifier for the mapping record (None for unmapped sources)
                - source_column: Source column name(s), pipe-separated if multiple
                - target_column: Target column name (None if source was kept or unmapped)
                - mapping_status: Status of the mapping ('mapped', 'source_missing', 'kept_source', 'value_mapped', 'not_in_mapping')
                - source_existed: Whether source column(s) existed in the DataFrame
                - rows_affected: Number of rows in the DataFrame
                - mapping_type: Type of mapping applied ('concat', 'fill', 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many', etc.)
                - logic: Original logic string from the record
                - relation_type: Relation type from the record ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many')
                - source_count: Number of source fields in the record
                - target_count: Number of target fields in the record
                - default_logic: Description of default logic used if no explicit logic was specified (e.g., 'direct_mapping', 'concatenate_with_pipe')

        Examples
        --------
        Example 1: Renaming columns using one_to_one mapping (no logic, uses default).

        >>> df = pd.DataFrame({'id': [1, 2], 'first_name': ['John', 'Jane']})
        >>> df
           id  first_name
        0   1        John
        1   2        Jane

        Scenario maps 'first_name' → 'firstname' (one_to_one, no logic specified).
        Default behavior: direct mapping source[0] → target[0].

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id  firstname
        0   1       John
        1   2       Jane

        >>> stats_df[['source_column', 'target_column', 'logic', 'relation_type', 'default_logic']]
           source_column   target_column    logic    relation_type      default_logic
        0     first_name       firstname     None       one_to_one     direct_mapping


        Example 2: Using many_to_one mapping (no logic, uses default).

        >>> df = pd.DataFrame({'id': [1, 2], 'street': ['Main St', 'Oak Ave'], 'city': ['Amsterdam', 'Rotterdam']})
        >>> df
           id     street          city
        0   1    Main St     Amsterdam
        1   2    Oak Ave     Rotterdam

        Scenario maps 'street'|'city' → 'address' (many_to_one, no logic specified).
        Default behavior: concatenate all source fields with '|' separator into single target.

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id              address
        0   1    Main St|Amsterdam
        1   2    Oak Ave|Rotterdam

        >>> stats_df[['source_column', 'target_column', 'logic', 'relation_type', 'default_logic']]
          source_column    target_column    logic    relation_type             default_logic
        0   street|city          address     None      many_to_one     concatenate_with_pipe


        Example 3: Using many_to_many mapping with explicit 'concat' logic.

        >>> df = pd.DataFrame({
        ...     'id': [1, 2],
        ...     'first_name': ['John', 'Jane'],
        ...     'last_name': ['Doe', 'Smith']
        ... })
        >>> df
           id  first_name  last_name
        0   1        John        Doe
        1   2        Jane      Smith

        Scenario maps 'first_name'|'last_name' → 'full_name'|'display_name' (many_to_many with explicit 'concat' logic).

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id     full_name    display_name
        0   1      John|Doe        John|Doe
        1   2    Jane|Smith      Jane|Smith

        With 'concat' logic, all source fields are concatenated and filled into all target fields.

        >>> stats_df[['source_column', 'target_column', 'logic', 'relation_type']]
                  source_column     target_column     logic    relation_type
        0  first_name|last_name         full_name    concat     many_to_many
        1  first_name|last_name      display_name    concat     many_to_many


        Example 4: Using many_to_many mapping with explicit 'fill' logic.

        >>> df = pd.DataFrame({
        ...     'id': [1, 2],
        ...     'first_name': ['John', 'Jane'],
        ...     'last_name': ['Doe', 'Smith']
        ... })
        >>> df
           id  first_name   last_name
        0   1        John         Doe
        1   2        Jane       Smith

        Scenario maps 'first_name'|'last_name' → 'first'|'last' (many_to_many with explicit 'fill' logic).

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id       first        last
        0   1        John         Doe
        1   2        Jane       Smith

        With 'fill' logic, source[i] maps to target[i] in order (1:1 mapping by index).

        >>> stats_df[['source_column', 'target_column', 'logic', 'relation_type']]
           source_column   target_column   logic   relation_type
        0     first_name           first    fill    many_to_many
        1      last_name            last    fill    many_to_many


        Example 5: Using 'keep source' logic.

        >>> df = pd.DataFrame({'id': [1, 2], 'employee_id': ['E001', 'E002'], 'department': ['IT', 'HR']})
        >>> df
           id  employee_id  department
        0   1         E001          IT
        1   2         E002          HR

        Scenario has 'keep source' logic for 'employee_id' and 'department' fields.

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id  employee_id  department
        0   1         E001          IT
        1   2         E002          HR

        Source columns are kept unchanged; no target columns are created.

        >>> stats_df[['source_column', 'target_column', 'mapping_status', 'logic']]
          source_column  target_column   mapping_status         logic
        0   employee_id           None      kept_source   keep source
        1    department           None      kept_source   keep source


        Example 6: Using one_to_many mapping without logic (uses default).

        >>> df = pd.DataFrame({'id': [1, 2], 'postal_code': ['1234', '5678']})
        >>> df
           id  postal_code
        0   1         1234
        1   2         5678

        Scenario maps 'postal_code' → 'zip'|'postcode' (one_to_many, no logic specified).
        Default behavior: duplicate single source value to all target fields.

        >>> df, stats_df = scenarios.rename_fields(df, 'My Scenario')
        >>> df
           id    zip  postcode
        0   1   1234      1234
        1   2   5678      5678

        Both target columns are filled with the same source value (duplicated to all targets).

        >>> stats_df[['source_column', 'target_column', 'logic', 'relation_type', 'default_logic']]
          source_column  target_column   logic     relation_type                  default_logic
        0   postal_code            zip    None       one_to_many       duplicate_to_all_targets
        1   postal_code       postcode    None       one_to_many       duplicate_to_all_targets
        """
        if columns_to_keep is None:
            columns_to_keep = []

        try:
            scenario = self[scenario_name]
        except KeyError:
            warnings.warn(f"Scenario '{scenario_name}' not found. Returning original DataFrame with empty statistics.", stacklevel=2)
            empty_stats = pd.DataFrame(
                columns=[
                    'record_id', 'source_column', 'target_column', 'mapping_status',
                    'source_existed', 'rows_affected', 'mapping_type', 'logic',
                    'relation_type', 'source_count', 'target_count', 'default_logic'
                ]
            )
            return df, empty_stats

        # objects for tracking statistics
        newly_created_target_fields = set()
        source_fields_to_keep = set()
        stats_data = []

        # Handler dictionaries route records to transformation methods by logic (explicit) or relation_type (default).
        # Replaces long if/elif chains as adding handlers requires only a dictionary entry.
        logic_handlers = {
            'concat': self._apply_concat,
            'fill': self._apply_fill,
            'keepsource': self._apply_keep_source,
            'onlysource': self._apply_keep_source
        }

        default_handlers = {
            'one_to_one': self._apply_one_to_one,
            'one_to_many': self._apply_one_to_many,
            'many_to_one': self._apply_many_to_one,
            'many_to_many': self._apply_many_to_many
        }

        for record in scenario.records:
            source_field_names = record.source.field_names

            # Skip records with value mappings, they're handled by apply_value_mappings
            if record.mapping:
                self._apply_value_mapping_logging(df, record, stats_data, newly_created_target_fields)
                continue

            normalized_logic = self._normalize_logic(record.logic)
            existing_sources = [s for s in source_field_names if s in df.columns]

            # Check if normalized logic contains any handler key (substring match)
            # This handles cases like "keep source | parse to from date" -> "keepsourceparsetofromdate"
            matched_handler_key = None
            for handler_key in logic_handlers.keys():
                if handler_key in normalized_logic:
                    matched_handler_key = handler_key
                    break

            if matched_handler_key:
                logic_handler = logic_handlers[matched_handler_key]
                # 'keep source' handlers don't create columns, so they only need kept_sources to track preserved fields.
                # Other handlers need existing_sources and created_targets to filter and track new columns.
                if matched_handler_key in ('keepsource', 'onlysource'):
                    logic_handler(
                        df=df,
                        record=record,
                        stats_data=stats_data,
                        kept_sources=source_fields_to_keep
                    )
                else:
                    logic_handler(
                        df=df,
                        record=record,
                        existing_sources=existing_sources,
                        stats_data=stats_data,
                        created_targets=newly_created_target_fields
                    )
            else:
                default_handler = default_handlers.get(record.relation_type)
                if default_handler:
                    # Only many_to_many accepts kept_sources.
                    if record.relation_type == 'many_to_many':
                        default_handler(
                            df=df,
                            record=record,
                            existing_sources=existing_sources,
                            stats_data=stats_data,
                            created_targets=newly_created_target_fields,
                            kept_sources=source_fields_to_keep
                        )
                    else:
                        default_handler(
                            df=df,
                            record=record,
                            existing_sources=existing_sources,
                            stats_data=stats_data,
                            created_targets=newly_created_target_fields
                        )
                else:
                    raise ValueError(
                        f"Unknown relation_type '{record.relation_type}' for record {record.id}. "
                        f"Supported types: {', '.join(default_handlers.keys())}"
                    )

        #--- report
        stats_df = self._generate_statistics_dataframe(
            scenario=scenario,
            df=df,
            stats_data=stats_data,
            source_fields_to_keep=source_fields_to_keep
        )

        #--- Clean up
        df = self._finalize_dataframe_columns(
            df=df,
            scenario=scenario,
            drop_unmapped=drop_unmapped,
            newly_created_target_fields=newly_created_target_fields,
            source_fields_to_keep=source_fields_to_keep,
            columns_to_keep=columns_to_keep
        )

        return df, stats_df

    # ============================================================================
    # Rename Handlers
    # ============================================================================

    def _apply_keep_source(
        self,
        df: pd.DataFrame,
        record,
        stats_data: List[dict],
        kept_sources: Set[str]
    ) -> None:
        """Applies 'keep source' logic: preserves source columns without creating targets.

        Applied when the logic is "keepsource" or "onlysource". This indicates that the
        source fields should be retained in the DataFrame as-is, and no corresponding
        target columns should be generated. Allowing the developer to apply custom logic themselves.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record with "keepsource" logic.
            stats_data (List[dict]): List to append statistics to.
            kept_sources (Set[str]): Set to track source columns that must be preserved.
        """
        source_field_names = record.source.field_names
        for source_field in source_field_names:
            kept_sources.add(source_field)
            source_existed = source_field in df.columns
            self._log_transformation_stats(
                stats_data=stats_data,
                record=record,
                target_col=None,
                source_col=source_field,
                status='kept_source',
                mapping_type='keep_source',
                source_existed=source_existed,
                df_length=len(df) if source_existed else 0
            )

    def _apply_concat(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
    ) -> None:
        """Applies 'concat' logic: joins all sources and fills all targets.

        Applied when the logic is explicitly set to "concat". It concatenates values from
        all available source columns using a pipe ('|') separator and assigns this result
        to every target column defined in the record.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record with "concat" logic.
            existing_sources (List[str]): List of source fields present in the DataFrame.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
        """
        target_field_names = record.target.field_names
        if len(existing_sources) > 0:
            concatenated = self._concatenate_source_fields(df=df, source_fields=existing_sources)
            for target_field in target_field_names:
                created_targets.add(target_field)
                df[target_field] = concatenated
                self._log_transformation_stats(
                    stats_data=stats_data,
                    record=record,
                    target_col=target_field,
                    source_col=existing_sources,
                    status='mapped',
                    mapping_type='concat',
                    df_length=len(df)
                )
        else:
            for target_field in target_field_names:
                created_targets.add(target_field)
                df[target_field] = ''
                self._log_transformation_stats(
                    stats_data=stats_data,
                    record=record,
                    target_col=target_field,
                    source_col=record.source.field_names,
                    status='source_missing',
                    mapping_type='concat',
                    source_existed=False,
                    df_length=len(df)
                )

    def _apply_fill(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
    ) -> None:
        """Applies 'fill' logic: maps source[i] to target[i] sequentially.

        If the logic is explicitly set to "fill", it maps the first source field
        to the first target field, the second source to the second target, and so on.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record with "fill" logic.
            existing_sources (List[str]): List of source fields present in the DataFrame.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
        """
        target_field_names = record.target.field_names
        n = min(len(existing_sources), len(target_field_names))

        for i in range(n):
            source_field = existing_sources[i]
            target_field = target_field_names[i]
            created_targets.add(target_field)
            df[target_field] = df[source_field]
            self._log_transformation_stats(
                stats_data=stats_data,
                record=record,
                target_col=target_field,
                source_col=source_field,
                status='mapped',
                mapping_type='fill',
                df_length=len(df)
            )

        if len(target_field_names) > len(existing_sources):
            for i in range(len(existing_sources), len(target_field_names)):
                target_field = target_field_names[i]
                created_targets.add(target_field)
                df[target_field] = ''
                self._log_transformation_stats(
                    stats_data=stats_data,
                    record=record,
                    target_col=target_field,
                    source_col=None,
                    status='source_missing',
                    mapping_type='fill',
                    source_existed=False,
                    df_length=len(df)
                )

    def _apply_one_to_one(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
    ) -> None:
        """Applies default one-to-one logic: Direct value copy.

        Applied when no explicit logic is provided and the relation type is 'one_to_one'.
        Maps a single source field to a single target field.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record.
            existing_sources (List[str]): List containing the single source field.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
        """
        target_field_names = record.target.field_names
        n_sources = len(existing_sources)
        n_targets = len(target_field_names)

        if n_sources > 0 and n_targets > 0:
            source_field = existing_sources[0]
            target_field = target_field_names[0]
            created_targets.add(target_field)
            df[target_field] = df[source_field]
            self._log_transformation_stats(
                stats_data=stats_data, record=record, target_col=target_field, source_col=source_field,
                status='mapped', mapping_type='one_to_one', default_logic='direct_mapping', df_length=len(df)
            )
        elif n_targets > 0:
            target_field = target_field_names[0]
            created_targets.add(target_field)
            df[target_field] = ''
            self._log_transformation_stats(
                stats_data=stats_data, record=record, target_col=target_field,
                source_col=record.source.field_names[0] if record.source.field_names else None,
                status='source_missing', mapping_type='one_to_one', default_logic='direct_mapping',
                source_existed=False, df_length=len(df)
            )

    def _apply_one_to_many(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
    ) -> None:
        """Applies default one-to-many logic: Duplicate source value to all targets.

        Applied when no explicit logic is provided and the relation type is 'one_to_many'.
        A single source field is mapped to multiple target fields.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record.
            existing_sources (List[str]): List containing the single source field.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
        """
        target_field_names = record.target.field_names

        if len(existing_sources) > 0:
            source_field = existing_sources[0]
            for target_field in target_field_names:
                created_targets.add(target_field)
                df[target_field] = df[source_field]
                self._log_transformation_stats(
                    stats_data=stats_data, record=record, target_col=target_field, source_col=source_field,
                    status='mapped', mapping_type='one_to_many', default_logic='duplicate_to_all_targets', df_length=len(df)
                )
        else:
            for target_field in target_field_names:
                created_targets.add(target_field)
                df[target_field] = ''
                self._log_transformation_stats(
                    stats_data=stats_data, record=record, target_col=target_field,
                    source_col=record.source.field_names[0] if record.source.field_names else None,
                    status='source_missing', mapping_type='one_to_many', default_logic='duplicate_to_all_targets',
                    source_existed=False, df_length=len(df)
                )

    def _apply_many_to_one(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
    ) -> None:
        """Applies default many-to-one logic: Concatenate sources with pipe separator.

        Applied when no explicit logic is provided and the relation type is 'many_to_one'.
        Multiple source fields are mapped to a single target field via concanation of the source valuess.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record.
            existing_sources (List[str]): List of source fields present in the DataFrame.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
        """
        target_field_names = record.target.field_names

        if len(existing_sources) > 0:
            concatenated = self._concatenate_source_fields(df=df, source_fields=existing_sources)
            target_field = target_field_names[0]
            created_targets.add(target_field)
            df[target_field] = concatenated
            self._log_transformation_stats(
                stats_data=stats_data, record=record, target_col=target_field, source_col=existing_sources,
                status='mapped', mapping_type='many_to_one', default_logic='concatenate_with_pipe', df_length=len(df)
            )
        elif len(target_field_names) > 0:
            target_field = target_field_names[0]
            created_targets.add(target_field)
            df[target_field] = ''
            self._log_transformation_stats(
                stats_data=stats_data, record=record, target_col=target_field, source_col=record.source.field_names,
                status='source_missing', mapping_type='many_to_one', default_logic='concatenate_with_pipe',
                source_existed=False, df_length=len(df)
            )

    def _apply_many_to_many(
        self,
        df: pd.DataFrame,
        record,
        existing_sources: List[str],
        stats_data: List[dict],
        created_targets: Set[str],
        kept_sources: Optional[Set[str]] = None
    ) -> None:
        """Applies default many-to-many logic: Variable behavior based on field counts.

        Applied when no explicit logic is provided and the relation type is 'many_to_many'.
        The behavior adapts based on the number of source fields (N) vs target fields (M).

        defaults for (N:M) mappings with different cardinalities :
        - N == M: Direct 1:1 mapping
        - N < M:  Maps available sources 1:1, then fills remaining targets with the last source.
        - N > M:  Concatenates all sources into every target field.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record.
            existing_sources (List[str]): List of source fields present in the DataFrame.
            stats_data (List[dict]): List to append statistics to.
            created_targets (Set[str]): Set to track created target columns.
            kept_sources: Optional parameter for interface consistency (unused in this method).
        """
        target_field_names = record.target.field_names
        n_sources = len(existing_sources)
        n_targets = len(target_field_names)

        # Equal: 1:1 mapping
        if n_sources == n_targets:
            for i in range(n_sources):
                source_field = existing_sources[i]
                target_field = target_field_names[i]
                created_targets.add(target_field)
                df[target_field] = df[source_field]
                self._log_transformation_stats(
                    stats_data=stats_data, record=record, target_col=target_field, source_col=source_field,
                    status='mapped', mapping_type='many_to_many_equal', default_logic='direct_1_to_1_mapping', df_length=len(df)
                )

        # Less sources: Map 1:1 then fill remaining with last source
        elif n_sources < n_targets:
            # Map first n
            for i in range(n_sources):
                source_field = existing_sources[i]
                target_field = target_field_names[i]
                created_targets.add(target_field)
                df[target_field] = df[source_field]
                self._log_transformation_stats(
                    stats_data=stats_data, record=record, target_col=target_field, source_col=source_field,
                    status='mapped', mapping_type='many_to_many_n_lt_m', default_logic='map_n_then_fill_remaining', df_length=len(df)
                )

            # Fill remaining
            if n_sources > 0:
                last_source = existing_sources[-1]
                for i in range(n_sources, n_targets):
                    target_field = target_field_names[i]
                    created_targets.add(target_field)
                    df[target_field] = df[last_source]
                    self._log_transformation_stats(
                        stats_data=stats_data, record=record, target_col=target_field, source_col=last_source,
                        status='mapped', mapping_type='many_to_many_n_lt_m', default_logic='map_n_then_fill_remaining', df_length=len(df)
                    )
            else: # No sources at all
                for i in range(n_sources, n_targets):
                    target_field = target_field_names[i]
                    created_targets.add(target_field)
                    df[target_field] = ''
                    self._log_transformation_stats(
                        stats_data=stats_data, record=record, target_col=target_field, source_col=None,
                        status='source_missing', mapping_type='many_to_many_n_lt_m', default_logic='map_n_then_fill_remaining',
                        source_existed=False, df_length=len(df)
                    )

        # More sources: Concatenate all to each target
        else: # n_sources > n_targets
            if n_sources > 0:
                concatenated = self._concatenate_source_fields(df=df, source_fields=existing_sources)
                for target_field in target_field_names:
                    created_targets.add(target_field)
                    df[target_field] = concatenated
                    self._log_transformation_stats(
                        stats_data=stats_data, record=record, target_col=target_field, source_col=existing_sources,
                        status='mapped', mapping_type='many_to_many_n_gt_m', default_logic='concatenate_all_to_each_target', df_length=len(df)
                    )
            else:
                for target_field in target_field_names:
                    created_targets.add(target_field)
                    df[target_field] = ''
                    self._log_transformation_stats(
                        stats_data=stats_data, record=record, target_col=target_field, source_col=record.source.field_names,
                        status='source_missing', mapping_type='many_to_many_n_gt_m', default_logic='concatenate_all_to_each_target',
                        source_existed=False, df_length=len(df)
                    )

    # ============================================================================
    # Transformation Helpers
    # ============================================================================

    def _generate_statistics_dataframe(
        self,
        scenario: ParsedScenario,
        df: pd.DataFrame,
        stats_data: List[dict],
        source_fields_to_keep: Set[str]
    ) -> pd.DataFrame:
        """Generates the statistics DataFrame, including unmapped source columns.

        Args:
            scenario: The scenario object.
            df: The DataFrame being processed.
            stats_data: List of statistics dictionaries collected so far.
            source_fields_to_keep: Set of source fields that were explicitly kept.

        Returns:
            pd.DataFrame: The final statistics DataFrame.
        """
        # Track mapped/unmapped source columns for statistics
        # Only track unmapped sources that exist in DataFrame and aren't intentionally kept
        all_scenario_sources = scenario.all_source_fields
        mapped_sources_from_records = set()
        for record in scenario.records:
            mapped_sources_from_records.update(record.source.field_names)

        unmapped_sources_in_df = (all_scenario_sources & set(df.columns)) - mapped_sources_from_records - source_fields_to_keep

        # Log unmapped sources using a dummy record
        dummy_record = DummyRecord()
        for unmapped_source in unmapped_sources_in_df:
            self._log_transformation_stats(
                stats_data=stats_data,
                record=dummy_record,
                target_col=None,
                source_col=unmapped_source,
                status='not_in_mapping',
                mapping_type='unknown',
                source_existed=True,
                df_length=len(df)
            )

        # Build statistics DataFrame
        if stats_data:
            return pd.DataFrame(stats_data)

        return pd.DataFrame(columns=[
            'record_id', 'source_column', 'target_column', 'mapping_status',
            'source_existed', 'rows_affected', 'mapping_type', 'logic',
            'relation_type', 'source_count', 'target_count', 'default_logic'
        ])

    def _finalize_dataframe_columns(
        self,
        df: pd.DataFrame,
        scenario: ParsedScenario,
        drop_unmapped: bool,
        newly_created_target_fields: Set[str],
        source_fields_to_keep: Set[str],
        columns_to_keep: List[str]
    ) -> pd.DataFrame:
        """Finalizes the DataFrame by dropping unmapped columns and ensuring expected columns exist.

        Args:
            df: The DataFrame being processed.
            scenario: The scenario object.
            drop_unmapped: Whether to drop unmapped source columns.
            newly_created_target_fields: Set of target fields created during transformation.
            source_fields_to_keep: Set of source fields explicitly kept.
            columns_to_keep: List of additional columns to preserve.

        Returns:
            pd.DataFrame: The finalized DataFrame.
        """
        # 1. Define protected columns (must not be dropped)
        protected_columns = {'id'} | newly_created_target_fields | source_fields_to_keep | set(columns_to_keep)

        # 2. Drop mapped source columns if requested
        if drop_unmapped:
            mapped_source_columns = set()
            for record in scenario.records:
                # Skip value mappings (handled by apply_value_mappings)
                if record.mapping and hasattr(record.mapping, 'values'):
                    continue

                normalized_logic = self._normalize_logic(record.logic)
                is_keep_source = "keepsource" in normalized_logic or "onlysource" in normalized_logic

                if not is_keep_source:
                    mapped_source_columns.update(record.source.field_names)

            columns_to_drop = [col for col in mapped_source_columns if col not in protected_columns]
            df = df.drop(columns=columns_to_drop, errors='ignore')

        # 3. Ensure only expected columns remain and missing expected columns are created
        all_expected_columns = list(protected_columns) + columns_to_keep

        # Filter to keep only expected columns that exist
        final_df_columns = [col for col in df.columns if col in all_expected_columns]
        df = df[final_df_columns].copy()

        # Add missing expected columns with None
        columns_missing_in_df = [col for col in all_expected_columns if col not in df.columns]
        for col in columns_missing_in_df:
            df[col] = None

        return df

    def _log_transformation_stats(
        self,
        stats_data: List[dict],
        record,
        target_col: Optional[str],
        source_col: Optional[Union[str, List[str]]],
        status: str,
        mapping_type: str,
        default_logic: Optional[str] = None,
        source_existed: bool = True,
        df_length: int = 0
    ) -> List[dict]:
        """Logs statistics for one field mapping operation.

        Helper method that creates a statistics dictionary and appends it to stats_data.
        Called multiple times by rename_fields() to build the statistics DataFrame returned to users.

        Args:
            stats_data (List[dict]): List to append statistics dictionary to.
            record: Record object containing field metadata (id, logic, relation_type, etc.).
            target_col (Optional[str]): Target column name, or None if not applicable.
            source_col (Optional[Union[str, List[str]]]): Source column name(s). Can be single string,
                list of strings (pipe-separated in output), or None.
            status (str): Mapping status: 'mapped', 'source_missing', 'kept_source', 'value_mapped'.
            mapping_type (str): Type of mapping: 'concat', 'fill', 'one_to_one', etc.
            default_logic (Optional[str]): Description of default logic used if no explicit logic.
            source_existed (bool): Whether source column(s) existed in DataFrame. Defaults to True.
            df_length (int): Number of rows in DataFrame (rows affected). Defaults to 0.

        Returns:
            List[dict]: Updated stats_data list with new statistics dictionary appended.
        """
        # Standardize source_col to string if it's a list/None
        if isinstance(source_col, list):
            src_str = '|'.join(source_col) if source_col else None
        else:
            src_str = source_col

        stats_data.append({
            'record_id': record.id,
            'source_column': src_str,
            'target_column': target_col,
            'mapping_status': status,
            'source_existed': source_existed,
            'rows_affected': df_length,
            'mapping_type': mapping_type,
            'logic': record.logic,
            'relation_type': record.relation_type,
            'source_count': len(record.source.field_names),
            'target_count': len(record.target.field_names),
            'default_logic': default_logic
        })
        return stats_data

    def _apply_value_mapping_logging(
        self,
        df: pd.DataFrame,
        record,
        stats_data: List[dict],
        created_targets: Set[str]
    ) -> None:
        """Logs statistics for records with explicit value mappings (skipping renaming).

        This helper is applied when a record has defined value mappings (e.g., "M" -> "1").
        These transformations are complex and handled by `apply_value_mappings()`, not
        `rename_fields()`. However, `rename_fields()` still needs to log these records to provide
        a complete report of all scenario operations.

        **Why:**
        To ensure the statistics DataFrame returned by `rename_fields()` is exhaustive and
        includes records that were skipped for renaming but will be handled elsewhere. It also
        initializes the target columns with `None` to ensure structure consistency.

        Args:
            df (pd.DataFrame): The DataFrame being processed.
            record: The scenario record containing value mapping definitions.
            stats_data (List[dict]): List to append the statistics dictionary to.
            created_targets (Set[str]): Set to track newly created target columns.
        """
        source_field_names = record.source.field_names
        target_field_names = record.target.field_names
        for target_field in target_field_names:
            created_targets.add(target_field)
            if target_field not in df.columns:
                df[target_field] = None
            self._log_transformation_stats(
                stats_data=stats_data,
                record=record,
                target_col=target_field,
                source_col=source_field_names,
                status='value_mapped',
                mapping_type='value_mapping',
                source_existed=any(s in df.columns for s in source_field_names),
                df_length=len(df)
            )

    # ============================================================================
    # Utility Helpers
    # ============================================================================

    def _normalize_logic(self, logic: Optional[str]) -> str:
        """Normalizes logic string for flexible matching.

        Converts to lowercase and removes spaces/special characters so "Concat", "CONCAT", and "concat"
        all match the same logic type. Used by rename_fields() to match user-entered logic strings.

        Args:
            logic (Optional[str]): Original logic string (e.g., "Concat", "fill", "keep source").

        Returns:
            str: Normalized string (e.g., "concat", "fill", "keepsource"). Empty string if None.
        """
        if not logic:
            return ""
        # Lowercase, remove spaces, remove special characters
        return re.sub(r'[^a-z0-9]', '', logic.lower())

    def _normalize_value_for_mapping(self, value: str, strategy: str) -> str:
        """Normalizes a value according to the specified mapping strategy.

        Used by apply_value_mappings() to normalize both DataFrame source values and
        mapping source values before comparison, enabling flexible matching strategies.

        Args:
            value: The value to normalize (e.g., "John Doe", "F", "John|Doe").
            strategy: Mapping strategy name (exactValMap, ignoreCaseValMap, etc.).

        Returns:
            Normalized value ready for comparison.
        """
        if not value or pd.isna(value):
            return str(value) if value is not None else ""

        value_str = str(value).strip()

        if strategy == 'exactValMap':
            return value_str
        elif strategy == 'ignoreCaseValMap':
            return value_str.lower()
        elif strategy == 'ignoreSpecialValMap':
            # Remove special chars including spaces
            return re.sub(r'[^a-zA-Z0-9]', '', value_str)
        elif strategy == 'ignoreSpacesValMap':
            # Remove spaces only
            return value_str.replace(' ', '')
        elif strategy == 'flexValMap':
            # Lowercase + remove special chars including spaces
            return re.sub(r'[^a-z0-9]', '', value_str.lower())
        else:
            # Default to exact matching if unknown strategy
            return value_str

    def _determine_mapping_strategy(self, record_logic: Optional[str], default_how: str) -> str:
        """Determines which mapping strategy to use for a record.

        Checks record.logic first (higher priority), then falls back to default_how kwarg.
        Uses _normalize_logic to match strategy names flexibly. Checks if normalized logic
        contains any strategy name as a substring (to handle cases where logic contains other text).

        Args:
            record_logic: The logic string from the record (may contain strategy name).
            default_how: Default strategy from how kwarg (e.g., 'exactValMap').

        Returns:
            Strategy name to use (exactValMap, ignoreCaseValMap, etc.).
        """
        if not record_logic:
            return default_how

        normalized_logic = self._normalize_logic(record_logic)

        # Check if normalized logic contains any mapping strategy as substring
        # Order matters: check longer/more specific names first to avoid false matches
        strategies = [
            ('ignorecasevalmap', 'ignoreCaseValMap'),
            ('ignorespecialvalmap', 'ignoreSpecialValMap'),
            ('ignorespacesvalmap', 'ignoreSpacesValMap'),
            ('flexvalmap', 'flexValMap'),
            ('exactvalmap', 'exactValMap')
        ]

        for normalized_strategy, strategy_name in strategies:
            if normalized_strategy in normalized_logic:
                return strategy_name

        # No match found, use default
        return default_how

    def _concatenate_source_fields(
        self,
        df: pd.DataFrame,
        source_fields: List[str]
    ) -> pd.Series:
        """Concatenates values from multiple source columns into a single Series with '|' separator.

        Combines the values from multiple columns (not the column names).
        Example: values from 'first_name' and 'last_name' columns → 'John|Doe'.
        Returns a Series of values; caller assigns this Series to target column name(s).
        If only one field provided, returns its values converted to string and stripped (no concatenation).
        Called by rename_fields() for 'concat' logic and many_to_one/many_to_many default behaviors.

        Args:
            df (pd.DataFrame): DataFrame containing the source columns.
            source_fields (List[str]): List of column names whose VALUES will be concatenated (e.g., ['first_name', 'last_name']).

        Returns:
            pd.Series: Series of concatenated VALUES (no column name). Caller assigns to target column(s).
        """
        if len(source_fields) == 1:
            return df[source_fields[0]].astype(str).str.strip()
        else:
            return df[source_fields].astype(str).apply(
                lambda row: '|'.join(val.strip() for val in row), axis=1
            )

    def _apply_mapping_to_target(
        self,
        df: pd.DataFrame,
        concatenated_source_series: pd.Series,
        target_field: str,
        replacements: dict,
        default_val: Optional[str] = None,
        original_source_series: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """Applies value mappings to create/populate a target column.

        Transforms source values → target values using lookup dictionary via pandas .map().
        Unmapped values use default_val if provided, otherwise keep original source value.
        Always creates target column (uses default if no mappings exist).
        Called by apply_value_mappings() for each target field in records with value mappings.

        Args:
            df: DataFrame to modify. Target column added/updated in-place.
            concatenated_source_series: Source values formatted for lookup (may be normalized for flexible matching).
            target_field: Name of target column to create/populate.
            replacements: Mapping dict {normalized_source_value: target_value} (e.g., {"f": "1", "m": "0"}).
            default_val: Default for unmapped values. If None, keeps original source value.
            original_source_series: Original (non-normalized) source series for fillna when default_val is None.

        Returns:
            Modified DataFrame with target column added/updated.

        Example 1: Single source field mapping.
            >>> # Input DataFrame with source column
            >>> df = pd.DataFrame({'id': [1, 2, 3], 'gender': ['F', 'M', 'F']})
            >>> # Create Series from source column (single field)
            >>> concatenated_source_series = df['gender'].astype(str).str.strip()
            >>> # Define mapping rules and target column name
            >>> replacements = {'F': '1', 'M': '0'}
            >>> target_field = 'gender_code'
            >>> default_val = None
            >>> # Apply mapping: Series values lookup in dict keys → return dict values
            >>> df = _apply_mapping_to_target(df, concatenated_source_series, target_field, replacements, default_val)
            >>> df
               id  gender  gender_code
            0   1        F            1
            1   2        M            0
            2   3        F            1

        Example 2: Concatenated source fields (many_to_one mapping).
            Scenario mapping: 'first_name'|'last_name' → 'full_name_code'
            >>> # Input DataFrame with multiple source columns
            >>> df = pd.DataFrame({'id': [1, 2], 'first_name': ['John', 'Jane'], 'last_name': ['Doe', 'Smith']})
            >>> # Create Series from multiple source columns (concatenated with '|')
            >>> concatenated_source_series = df[['first_name', 'last_name']].astype(str).apply(
            ...     lambda row: '|'.join(val.strip() for val in row), axis=1)
            >>> # Define mapping rules (keys match concatenated format) and target column name
            >>> replacements = {'John|Doe': 'JD001', 'Jane|Smith': 'JS002'}
            >>> target_field = 'full_name_code'
            >>> default_val = None
            >>> # Apply mapping: "John|Doe" → "JD001", "Jane|Smith" → "JS002"
            >>> df = _apply_mapping_to_target(df, concatenated_source_series, target_field, replacements, default_val)
            >>> df
               id  first_name  last_name  full_name_code
            0   1        John        Doe            JD001
            1   2        Jane      Smith            JS002
        """
        if not replacements:
            df[target_field] = default_val if default_val else None
            return df

        mapped_series = concatenated_source_series.map(replacements)

        if default_val:
            mapped_series = mapped_series.fillna(default_val)
        else:
            # Use original source series for fillna to preserve original values (not normalized)
            fill_series = original_source_series if original_source_series is not None else concatenated_source_series
            mapped_series = mapped_series.fillna(fill_series)

        df[target_field] = mapped_series
        return df

    def _detect_missing_values_in_fields(
        self,
        df: pd.DataFrame,
        source_field_names: List[str]
    ) -> Dict[str, int]:
        """Detects missing values in source fields used for value mapping.

        Called by apply_value_mappings() before processing to warn users about missing values
        that may affect mapping accuracy. Missing values can cause mappings to fail silently
        or produce unexpected results, so early detection helps users identify data quality issues.

        Args:
            df: Input DataFrame to check.
            source_field_names: List of source field names to check for missing values.

        Returns:
            Dictionary mapping field names to counts of missing values found.
        """
        missing_counts = {}
        missing_value_patterns = self.MISSING_VALUES

        for field_name in source_field_names:
            if field_name not in df.columns:
                continue

            series = df[field_name]

            # Count pd.NA and numpy NaN (true missing values)
            missing_count = series.isna().sum()

            # Count string representations that indicate missing data (e.g., 'nan', 'None', 'null')
            # These are checked separately because they're not detected by isna() but still
            # represent missing/invalid data that should be handled before mapping
            for pattern in missing_value_patterns:
                missing_count += (series == pattern).sum()

            if missing_count > 0:
                missing_counts[field_name] = missing_count

        return missing_counts
