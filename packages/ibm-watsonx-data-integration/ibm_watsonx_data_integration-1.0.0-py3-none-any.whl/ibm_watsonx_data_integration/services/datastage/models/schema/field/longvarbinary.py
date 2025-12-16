"""Module for longvarbinary schema field."""

from ibm_watsonx_data_integration.services.datastage.models import flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import TypeVar

T = TypeVar("T", bound="LongVarBinary")


class LongVarBinary(BaseField):
    """Class for longvarbinary schema field."""

    def __init__(self, name: str) -> None:
        """Initializes a schema field."""
        super().__init__(name)
        self._set_model_type("binary")
        self._set_app_type_code("BINARY")
        self._set_app_odbc_type("LONGVARBINARY")
        self.configuration.metadata.min_length = 0
        self.configuration.metadata.max_length = 100

    def _create_from_model(self, model: models.FieldModelComplex) -> T:
        field = LongVarBinary(model.name)
        field.configuration = model
        return field

    def length(self, length: int) -> "BaseField":
        """Set the length of this field.

        Args:
            length: The length to set for this field.

        Returns:
            A new instance of the field with the updated length.

        """
        return self._length(length)._max_length(length)

    def byte_to_skip(self, num_bytes: int) -> "BaseField":
        """Sets bytes to skip."""
        return self._byte_to_skip(num_bytes)

    def delimiter(self, delim: FIELD.Delim) -> "BaseField":
        """Sets delimiter."""
        return self._delim(delim)

    def delimiter_string(self, delimiter_string: str) -> "BaseField":
        """Sets delimiter string."""
        return self._delim_string(delimiter_string)

    def generate_on_output(self) -> "BaseField":
        """Sets generate on output."""
        return self._generate_on_output()

    def prefix_bytes(self, prefix_bytes: FIELD.Prefix) -> "BaseField":
        """Sets prefix bytes."""
        return self._prefix_bytes(prefix_bytes)

    def quote(self, quote_type: FIELD.Quote) -> "BaseField":
        """Sets quote type."""
        return self._quote(quote_type)

    def start_position(self, position: int) -> "BaseField":
        """Sets start position."""
        return self._start_position(position)

    def tag_case_value(self, tag_case_value: int) -> "BaseField":
        """Sets tag case value."""
        return self._tagcase(tag_case_value)

    def link_field_reference(self, link_field_reference: str) -> "BaseField":
        """Sets link field reference."""
        return self._link_field_reference(link_field_reference)
