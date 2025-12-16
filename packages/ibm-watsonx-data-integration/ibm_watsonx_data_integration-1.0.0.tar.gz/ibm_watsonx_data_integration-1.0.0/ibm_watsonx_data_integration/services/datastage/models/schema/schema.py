"""Module for schema."""

import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
import ibm_watsonx_data_integration.services.datastage.models.schema.field as field
import json
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from inspect import signature
from typing import Literal, overload

_ODBC_TYPE_TO_FIELD_CLASS = {
    "BIGINT": field.BigInt,
    "BINARY": field.Binary,
    "BIT": field.Bit,
    "CHAR": field.Char,
    "DATE": field.Date,
    "DECIMAL": field.Decimal,
    "DOUBLE": field.Double,
    "FLOAT": field.Float,
    "INTEGER": field.Integer,
    "LONGNVARCHAR": field.LongNVarChar,
    "LONGVARBINARY": field.LongVarBinary,
    "LONGVARCHAR": field.LongVarChar,
    "NCHAR": field.NChar,
    "NUMERIC": field.Numeric,
    "NVARCHAR": field.NVarChar,
    "REAL": field.Real,
    "SMALLINT": field.SmallInt,
    "TIME": field.Time,
    "TIMESTAMP": field.Timestamp,
    "TINYINT": field.TinyInt,
    "UNKNOWN": field.Unknown,
    "VARBINARY": field.VarBinary,
    "VARCHAR": field.VarChar,
}


class Schema:
    """Column schema for batch stage."""

    def __init__(self, fields: list[BaseField] = None) -> None:
        """Initializes an empty schema or a schema based on inputted fields."""
        self.fields = fields or []

    @property
    def configuration(self) -> models.RecordSchema:
        """Computed configuration."""
        return models.RecordSchema(id="", fields=[f.configuration.get_field_model() for f in self.fields])

    @overload
    def add_field(self, odbc_type: Literal["BIGINT"], name: str) -> field.BigInt: ...

    @overload
    def add_field(self, odbc_type: Literal["BINARY"], name: str) -> field.Binary: ...

    @overload
    def add_field(self, odbc_type: Literal["BIT"], name: str) -> field.Bit: ...

    @overload
    def add_field(self, odbc_type: Literal["CHAR"], name: str) -> field.Char: ...

    @overload
    def add_field(self, odbc_type: Literal["DATE"], name: str) -> field.Date: ...

    @overload
    def add_field(self, odbc_type: Literal["DECIMAL"], name: str) -> field.Decimal: ...

    @overload
    def add_field(self, odbc_type: Literal["DOUBLE"], name: str) -> field.Double: ...

    @overload
    def add_field(self, odbc_type: Literal["FLOAT"], name: str) -> field.Float: ...

    @overload
    def add_field(self, odbc_type: Literal["INTEGER"], name: str) -> field.Integer: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGVARBINARY"], name: str) -> field.LongVarBinary: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGVARCHAR"], name: str) -> field.LongVarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NUMERIC"], name: str) -> field.Numeric: ...

    @overload
    def add_field(self, odbc_type: Literal["REAL"], name: str) -> field.Real: ...

    @overload
    def add_field(self, odbc_type: Literal["SMALLINT"], name: str) -> field.SmallInt: ...

    @overload
    def add_field(self, odbc_type: Literal["TIME"], name: str) -> field.Time: ...

    @overload
    def add_field(self, odbc_type: Literal["TIMESTAMP"], name: str) -> field.Timestamp: ...

    @overload
    def add_field(self, odbc_type: Literal["TINYINT"], name: str) -> field.TinyInt: ...

    @overload
    def add_field(self, odbc_type: Literal["UNKNOWN"], name: str) -> field.Unknown: ...

    @overload
    def add_field(self, odbc_type: Literal["VARBINARY"], name: str) -> field.VarBinary: ...

    @overload
    def add_field(self, odbc_type: Literal["VARCHAR"], name: str) -> field.VarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NCHAR"], name: str) -> field.NChar: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGNVARCHAR"], name: str) -> field.LongNVarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NVARCHAR"], name: str) -> field.NVarChar: ...

    def add_field(
        self,
        odbc_type: str,
        name: str,
        description: str = "",
        nullable: bool = None,
        key: bool = None,
        source: str = None,
        pivot: str = None,
        length: int = None,
        scale: int = None,
        unicode: bool = None,
        unsigned: bool = None,
        extended_type: str = None,
        cluster_key_change: bool = None,
        key_change: bool = None,
        difference: bool = None,
        c_format: str = None,
        default: str | int = None,
        format_string: str = None,
        decimal_separator: FIELD.DecimalSeparator = None,
        out_format: str = None,
        link_field_reference: str = None,
        padchar: FIELD.PadChar = None,
        prefix_bytes: FIELD.Prefix = None,
        vector_prefix: FIELD.VectorPrefix = None,
        epoch: int = None,
        field_max_width: int = None,
        precision: int = None,
        scale_factor: int = None,
        start_position: int = None,
        percent_invalid: int = None,
        percent_zeros: int = None,
        tag_case_value: int = None,
        days_since: int = None,
        field_width: int = None,
        generate_on_output: bool = None,
        julian: bool = None,
        is_link_field: bool = None,
        check_packed: bool = None,
        export_ebcdic_as_ascii: bool = None,
        packed_signed: bool = None,
        is_midnight_seconds: bool = None,
        packed: FIELD.DecimalPacked = None,
        byte_order: FIELD.ByteOrder = None,
        charset: FIELD.CharSet = None,
        allow_all_zeros: bool = None,
        sign_position: FIELD.SignPosition = None,
        data_format: FIELD.DataFormat = None,
        level_number: int = None,
        vector: FIELD.VectorType = None,
        vector_occurs: int = None,
        byte_to_skip: int = None,
        delimeter: FIELD.Delim = None,
        delimeter_string: str = None,
        quote: FIELD.Quote = None,
        cycle_increment: FIELD.CycleIncrement | int = None,
        cycle_initial_value: FIELD.CycleInitialValue | int = None,
        cycle_limit: FIELD.CycleLimit | int = None,
        cycle_values: list[int | str] = None,
        alphabet: str = None,
        generate_algorithm: FIELD.GenerateAlgorithm = None,
        generate_type: FIELD.GenerateType = None,
        random_limit: FIELD.RandomLimit = None,
        random_seed: FIELD.RandomSeed = None,
        random_signed: bool = None,
        use_current_date: bool = None,
        rounding: FIELD.Round = None,
        actual_field_length: int = None,
        null_field_length: int = None,
        null_field_value: int = None,
        decimal_type_scale: int = None,
        null_seed: int = None,
        percent_null: int = None,
        change_code: bool = None,
        derivation: str = None,
        timezone: bool = None,
        microseconds: bool = None,
    ):
        """Add a field to the schema."""
        changed_args = {k: v for k, v in locals().items() if v is not None and k not in ["self", "odbc_type", "name"]}

        if odbc_type.upper() in _ODBC_TYPE_TO_FIELD_CLASS:
            field_class = _ODBC_TYPE_TO_FIELD_CLASS[odbc_type.upper()]
            new_field = field_class(name=name)
            new_field = new_field.description(description)
            for key, value in changed_args.items():
                method = getattr(new_field, key)
                if not len(signature(method).parameters):
                    if value:
                        method()
                else:
                    method(value)

            self.fields.append(new_field)
            return new_field
        else:
            raise ValueError(
                f"Unsupported field type: {odbc_type}. Supported types are: {list(_ODBC_TYPE_TO_FIELD_CLASS.keys())}"
            )

    def remove_field(self, name: str) -> "Schema":
        """Remove a field by name from the schema."""
        new_fields = []
        for cur_field in self.fields:
            if cur_field.configuration.name != name:
                new_fields.append(cur_field)
        self.fields = new_fields
        return self

    def select_fields(self, *args: str) -> "Schema":
        """Create a new schema with selected fields."""
        new_fields = []
        for cur_field in self.fields:
            if cur_field.configuration.name in args:
                new_fields.append(cur_field)
        return Schema(new_fields)

    def clone(self) -> "Schema":
        """Clone a schema."""
        new_fields = [f.clone() for f in self.fields]
        return Schema(new_fields)

    def __str__(self) -> str:
        """Formats schema as a string."""
        new_fields = [str(f) for f in self.fields]
        new_fields = "[" + ",\n".join(map(str, new_fields)) + "]"
        return json.dumps(json.loads(new_fields), indent=4)

    # def add_data_definition(self, data_definition: DataDefinition) -> "Schema":
    #     """Add a data definition to the schema fields."""
    #     self.fields.extend(data_definition._get_fields())
    #     return self
