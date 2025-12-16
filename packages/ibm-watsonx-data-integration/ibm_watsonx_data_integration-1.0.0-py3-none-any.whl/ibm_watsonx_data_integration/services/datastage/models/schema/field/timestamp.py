"""Module for timestamp schema field."""

from ibm_watsonx_data_integration.services.datastage.models import flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import TypeVar

T = TypeVar("T", bound="Timestamp")


class Timestamp(BaseField):
    """Class for timestamp schema field."""

    def __init__(self, name: str) -> None:
        """Initializes a schema field."""
        super().__init__(name)
        self._set_model_type("timestamp")
        self._set_app_type_code("DATETIME")
        self._set_app_odbc_type("TIMESTAMP")
        self.configuration.metadata.decimal_scale = 0
        self.configuration.metadata.decimal_precision = 19
        self.configuration.metadata.min_length = 0
        self.configuration.metadata.max_length = 19

    def _create_from_model(self, model: models.FieldModelComplex) -> T:
        field = Timestamp(model.name)
        field.configuration = model
        return field

    def length(self, length: int) -> "BaseField":
        """Set the length of this field.

        Args:
            length: The length to set for this field.

        Returns:
            A new instance of the field with the updated length.

        """
        return self._length(length)._max_length(length)._decimal_precision(length)

    def scale(self, scale: int) -> "BaseField":
        """Sets scale."""
        return self._time_scale(scale)

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

    def byte_order(self, byte_order: FIELD.ByteOrder) -> "BaseField":
        """Sets byte order."""
        return self._byte_order(byte_order)

    def charset(self, charset: FIELD.CharSet) -> "BaseField":
        """Sets charset."""
        return self._charset(charset)

    def data_format(self, data_format: FIELD.DataFormat) -> "BaseField":
        """Sets date format."""
        return self._data_format(data_format)

    def default(self, default: str) -> "BaseField":
        """Sets default."""
        return self._default(default)

    def format_string(self, format_string: str) -> "BaseField":
        """Sets format string."""
        return self._timestamp_format(format_string)

    def epoch(self, epoch: int) -> "BaseField":
        """Sets epoch."""
        return self._epoch(epoch)

    def percent_invalid(self, generated_percent_invalid: int) -> "BaseField":
        """Sets percent invalid."""
        return self._generated_percent_invalid(generated_percent_invalid)

    def scale_factor(self, time_scale_factor: int) -> "BaseField":
        """Sets scale factor."""
        return self._time_scale_factor(time_scale_factor)

    def generate_type(self, generate_type: FIELD.GenerateType) -> "BaseField":
        """Sets generate type."""
        return self._generate_type(generate_type)

    def cycle_increment(self, cycle_increment: FIELD.CycleIncrement | int) -> "BaseField":
        """Sets cycle increment."""
        return self._cycle_increment(cycle_increment)

    def cycle_initial_value(self, cycle_initial_value: FIELD.CycleInitialValue | int) -> "BaseField":
        """Sets cycle initial value."""
        return self._cycle_initial_value(cycle_initial_value)

    def cycle_limit(self, cycle_limit: FIELD.CycleLimit | int) -> "BaseField":
        """Sets cycle limit."""
        return self._cycle_limit(cycle_limit)

    def random_limit(self, random_limit: FIELD.RandomLimit) -> "BaseField":
        """Sets random limit."""
        return self._random_limit(random_limit)

    def random_seed(self, random_seed: FIELD.RandomSeed) -> "BaseField":
        """Sets random seed."""
        return self._random_seed(random_seed)

    def random_signed(self) -> "BaseField":
        """Sets random signed."""
        return self._random_signed()

    def timezone(self) -> "BaseField":
        """Sets timezone."""
        if self.configuration.extended_type == FIELD.TimeExtendedType.microseconds:
            return self.extended_type(FIELD.TimeExtendedType.microseconds_and_timezone)
        else:
            return self.extended_type(self.extended_type(FIELD.TimeExtendedType.timezone))

    def microseconds(self) -> "BaseField":
        """Sets microseconds."""
        if self.configuration.extended_type == FIELD.TimeExtendedType.timezone:
            return self.extended_type(FIELD.TimeExtendedType.microseconds_and_timezone)
        else:
            return self.extended_type(FIELD.TimeExtendedType.microseconds)

    def extended_type(self, typ: FIELD.TimeExtendedType) -> "BaseField":
        """Sets extended type."""
        return self._extended_type(typ)

    def link_field_reference(self, link_field_reference: str) -> "BaseField":
        """Sets link field reference."""
        return self._link_field_reference(link_field_reference)

    def null_seed(self, seed: int) -> "BaseField":
        """Sets null seed."""
        return self._null_seed(seed)

    def percent_null(self, percent_null: int) -> "BaseField":
        """Sets percent null."""
        return self._percent_null(percent_null)
