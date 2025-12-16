# generated from codegen/templates/_pydantic.py

from typing import Any

import pydantic
import pydantic_core

import emath


def BVector1_deserialize(value: Any) -> emath.BVector1:
    return emath.BVector1.from_buffer(value)


def BVector1_serialize(value: emath.BVector1) -> Any:
    return bytes(value)


def BVector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector1_serialize, when_used="always"
        ),
    )


def BVector1Array_deserialize(value: Any) -> emath.BVector1Array:
    return emath.BVector1Array.from_buffer(value)


def BVector1Array_serialize(value: emath.BVector1Array) -> Any:
    return bytes(value)


def BVector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector1Array_serialize, when_used="always"
        ),
    )


def DVector1_deserialize(value: Any) -> emath.DVector1:
    return emath.DVector1.from_buffer(value)


def DVector1_serialize(value: emath.DVector1) -> Any:
    return bytes(value)


def DVector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector1_serialize, when_used="always"
        ),
    )


def DVector1Array_deserialize(value: Any) -> emath.DVector1Array:
    return emath.DVector1Array.from_buffer(value)


def DVector1Array_serialize(value: emath.DVector1Array) -> Any:
    return bytes(value)


def DVector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector1Array_serialize, when_used="always"
        ),
    )


def FVector1_deserialize(value: Any) -> emath.FVector1:
    return emath.FVector1.from_buffer(value)


def FVector1_serialize(value: emath.FVector1) -> Any:
    return bytes(value)


def FVector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector1_serialize, when_used="always"
        ),
    )


def FVector1Array_deserialize(value: Any) -> emath.FVector1Array:
    return emath.FVector1Array.from_buffer(value)


def FVector1Array_serialize(value: emath.FVector1Array) -> Any:
    return bytes(value)


def FVector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector1Array_serialize, when_used="always"
        ),
    )


def I8Vector1_deserialize(value: Any) -> emath.I8Vector1:
    return emath.I8Vector1.from_buffer(value)


def I8Vector1_serialize(value: emath.I8Vector1) -> Any:
    return bytes(value)


def I8Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector1_serialize, when_used="always"
        ),
    )


def I8Vector1Array_deserialize(value: Any) -> emath.I8Vector1Array:
    return emath.I8Vector1Array.from_buffer(value)


def I8Vector1Array_serialize(value: emath.I8Vector1Array) -> Any:
    return bytes(value)


def I8Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector1Array_serialize, when_used="always"
        ),
    )


def U8Vector1_deserialize(value: Any) -> emath.U8Vector1:
    return emath.U8Vector1.from_buffer(value)


def U8Vector1_serialize(value: emath.U8Vector1) -> Any:
    return bytes(value)


def U8Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector1_serialize, when_used="always"
        ),
    )


def U8Vector1Array_deserialize(value: Any) -> emath.U8Vector1Array:
    return emath.U8Vector1Array.from_buffer(value)


def U8Vector1Array_serialize(value: emath.U8Vector1Array) -> Any:
    return bytes(value)


def U8Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector1Array_serialize, when_used="always"
        ),
    )


def I16Vector1_deserialize(value: Any) -> emath.I16Vector1:
    return emath.I16Vector1.from_buffer(value)


def I16Vector1_serialize(value: emath.I16Vector1) -> Any:
    return bytes(value)


def I16Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector1_serialize, when_used="always"
        ),
    )


def I16Vector1Array_deserialize(value: Any) -> emath.I16Vector1Array:
    return emath.I16Vector1Array.from_buffer(value)


def I16Vector1Array_serialize(value: emath.I16Vector1Array) -> Any:
    return bytes(value)


def I16Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector1Array_serialize, when_used="always"
        ),
    )


def U16Vector1_deserialize(value: Any) -> emath.U16Vector1:
    return emath.U16Vector1.from_buffer(value)


def U16Vector1_serialize(value: emath.U16Vector1) -> Any:
    return bytes(value)


def U16Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector1_serialize, when_used="always"
        ),
    )


def U16Vector1Array_deserialize(value: Any) -> emath.U16Vector1Array:
    return emath.U16Vector1Array.from_buffer(value)


def U16Vector1Array_serialize(value: emath.U16Vector1Array) -> Any:
    return bytes(value)


def U16Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector1Array_serialize, when_used="always"
        ),
    )


def I32Vector1_deserialize(value: Any) -> emath.I32Vector1:
    return emath.I32Vector1.from_buffer(value)


def I32Vector1_serialize(value: emath.I32Vector1) -> Any:
    return bytes(value)


def I32Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector1_serialize, when_used="always"
        ),
    )


def I32Vector1Array_deserialize(value: Any) -> emath.I32Vector1Array:
    return emath.I32Vector1Array.from_buffer(value)


def I32Vector1Array_serialize(value: emath.I32Vector1Array) -> Any:
    return bytes(value)


def I32Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector1Array_serialize, when_used="always"
        ),
    )


def U32Vector1_deserialize(value: Any) -> emath.U32Vector1:
    return emath.U32Vector1.from_buffer(value)


def U32Vector1_serialize(value: emath.U32Vector1) -> Any:
    return bytes(value)


def U32Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector1_serialize, when_used="always"
        ),
    )


def U32Vector1Array_deserialize(value: Any) -> emath.U32Vector1Array:
    return emath.U32Vector1Array.from_buffer(value)


def U32Vector1Array_serialize(value: emath.U32Vector1Array) -> Any:
    return bytes(value)


def U32Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector1Array_serialize, when_used="always"
        ),
    )


def IVector1_deserialize(value: Any) -> emath.IVector1:
    return emath.IVector1.from_buffer(value)


def IVector1_serialize(value: emath.IVector1) -> Any:
    return bytes(value)


def IVector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector1_serialize, when_used="always"
        ),
    )


def IVector1Array_deserialize(value: Any) -> emath.IVector1Array:
    return emath.IVector1Array.from_buffer(value)


def IVector1Array_serialize(value: emath.IVector1Array) -> Any:
    return bytes(value)


def IVector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector1Array_serialize, when_used="always"
        ),
    )


def UVector1_deserialize(value: Any) -> emath.UVector1:
    return emath.UVector1.from_buffer(value)


def UVector1_serialize(value: emath.UVector1) -> Any:
    return bytes(value)


def UVector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector1_serialize, when_used="always"
        ),
    )


def UVector1Array_deserialize(value: Any) -> emath.UVector1Array:
    return emath.UVector1Array.from_buffer(value)


def UVector1Array_serialize(value: emath.UVector1Array) -> Any:
    return bytes(value)


def UVector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector1Array_serialize, when_used="always"
        ),
    )


def I64Vector1_deserialize(value: Any) -> emath.I64Vector1:
    return emath.I64Vector1.from_buffer(value)


def I64Vector1_serialize(value: emath.I64Vector1) -> Any:
    return bytes(value)


def I64Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector1_serialize, when_used="always"
        ),
    )


def I64Vector1Array_deserialize(value: Any) -> emath.I64Vector1Array:
    return emath.I64Vector1Array.from_buffer(value)


def I64Vector1Array_serialize(value: emath.I64Vector1Array) -> Any:
    return bytes(value)


def I64Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector1Array_serialize, when_used="always"
        ),
    )


def U64Vector1_deserialize(value: Any) -> emath.U64Vector1:
    return emath.U64Vector1.from_buffer(value)


def U64Vector1_serialize(value: emath.U64Vector1) -> Any:
    return bytes(value)


def U64Vector1__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector1_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector1_serialize, when_used="always"
        ),
    )


def U64Vector1Array_deserialize(value: Any) -> emath.U64Vector1Array:
    return emath.U64Vector1Array.from_buffer(value)


def U64Vector1Array_serialize(value: emath.U64Vector1Array) -> Any:
    return bytes(value)


def U64Vector1Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector1Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector1Array_serialize, when_used="always"
        ),
    )


def BVector2_deserialize(value: Any) -> emath.BVector2:
    return emath.BVector2.from_buffer(value)


def BVector2_serialize(value: emath.BVector2) -> Any:
    return bytes(value)


def BVector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector2_serialize, when_used="always"
        ),
    )


def BVector2Array_deserialize(value: Any) -> emath.BVector2Array:
    return emath.BVector2Array.from_buffer(value)


def BVector2Array_serialize(value: emath.BVector2Array) -> Any:
    return bytes(value)


def BVector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector2Array_serialize, when_used="always"
        ),
    )


def DVector2_deserialize(value: Any) -> emath.DVector2:
    return emath.DVector2.from_buffer(value)


def DVector2_serialize(value: emath.DVector2) -> Any:
    return bytes(value)


def DVector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector2_serialize, when_used="always"
        ),
    )


def DVector2Array_deserialize(value: Any) -> emath.DVector2Array:
    return emath.DVector2Array.from_buffer(value)


def DVector2Array_serialize(value: emath.DVector2Array) -> Any:
    return bytes(value)


def DVector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector2Array_serialize, when_used="always"
        ),
    )


def FVector2_deserialize(value: Any) -> emath.FVector2:
    return emath.FVector2.from_buffer(value)


def FVector2_serialize(value: emath.FVector2) -> Any:
    return bytes(value)


def FVector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector2_serialize, when_used="always"
        ),
    )


def FVector2Array_deserialize(value: Any) -> emath.FVector2Array:
    return emath.FVector2Array.from_buffer(value)


def FVector2Array_serialize(value: emath.FVector2Array) -> Any:
    return bytes(value)


def FVector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector2Array_serialize, when_used="always"
        ),
    )


def I8Vector2_deserialize(value: Any) -> emath.I8Vector2:
    return emath.I8Vector2.from_buffer(value)


def I8Vector2_serialize(value: emath.I8Vector2) -> Any:
    return bytes(value)


def I8Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector2_serialize, when_used="always"
        ),
    )


def I8Vector2Array_deserialize(value: Any) -> emath.I8Vector2Array:
    return emath.I8Vector2Array.from_buffer(value)


def I8Vector2Array_serialize(value: emath.I8Vector2Array) -> Any:
    return bytes(value)


def I8Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector2Array_serialize, when_used="always"
        ),
    )


def U8Vector2_deserialize(value: Any) -> emath.U8Vector2:
    return emath.U8Vector2.from_buffer(value)


def U8Vector2_serialize(value: emath.U8Vector2) -> Any:
    return bytes(value)


def U8Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector2_serialize, when_used="always"
        ),
    )


def U8Vector2Array_deserialize(value: Any) -> emath.U8Vector2Array:
    return emath.U8Vector2Array.from_buffer(value)


def U8Vector2Array_serialize(value: emath.U8Vector2Array) -> Any:
    return bytes(value)


def U8Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector2Array_serialize, when_used="always"
        ),
    )


def I16Vector2_deserialize(value: Any) -> emath.I16Vector2:
    return emath.I16Vector2.from_buffer(value)


def I16Vector2_serialize(value: emath.I16Vector2) -> Any:
    return bytes(value)


def I16Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector2_serialize, when_used="always"
        ),
    )


def I16Vector2Array_deserialize(value: Any) -> emath.I16Vector2Array:
    return emath.I16Vector2Array.from_buffer(value)


def I16Vector2Array_serialize(value: emath.I16Vector2Array) -> Any:
    return bytes(value)


def I16Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector2Array_serialize, when_used="always"
        ),
    )


def U16Vector2_deserialize(value: Any) -> emath.U16Vector2:
    return emath.U16Vector2.from_buffer(value)


def U16Vector2_serialize(value: emath.U16Vector2) -> Any:
    return bytes(value)


def U16Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector2_serialize, when_used="always"
        ),
    )


def U16Vector2Array_deserialize(value: Any) -> emath.U16Vector2Array:
    return emath.U16Vector2Array.from_buffer(value)


def U16Vector2Array_serialize(value: emath.U16Vector2Array) -> Any:
    return bytes(value)


def U16Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector2Array_serialize, when_used="always"
        ),
    )


def I32Vector2_deserialize(value: Any) -> emath.I32Vector2:
    return emath.I32Vector2.from_buffer(value)


def I32Vector2_serialize(value: emath.I32Vector2) -> Any:
    return bytes(value)


def I32Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector2_serialize, when_used="always"
        ),
    )


def I32Vector2Array_deserialize(value: Any) -> emath.I32Vector2Array:
    return emath.I32Vector2Array.from_buffer(value)


def I32Vector2Array_serialize(value: emath.I32Vector2Array) -> Any:
    return bytes(value)


def I32Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector2Array_serialize, when_used="always"
        ),
    )


def U32Vector2_deserialize(value: Any) -> emath.U32Vector2:
    return emath.U32Vector2.from_buffer(value)


def U32Vector2_serialize(value: emath.U32Vector2) -> Any:
    return bytes(value)


def U32Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector2_serialize, when_used="always"
        ),
    )


def U32Vector2Array_deserialize(value: Any) -> emath.U32Vector2Array:
    return emath.U32Vector2Array.from_buffer(value)


def U32Vector2Array_serialize(value: emath.U32Vector2Array) -> Any:
    return bytes(value)


def U32Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector2Array_serialize, when_used="always"
        ),
    )


def IVector2_deserialize(value: Any) -> emath.IVector2:
    return emath.IVector2.from_buffer(value)


def IVector2_serialize(value: emath.IVector2) -> Any:
    return bytes(value)


def IVector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector2_serialize, when_used="always"
        ),
    )


def IVector2Array_deserialize(value: Any) -> emath.IVector2Array:
    return emath.IVector2Array.from_buffer(value)


def IVector2Array_serialize(value: emath.IVector2Array) -> Any:
    return bytes(value)


def IVector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector2Array_serialize, when_used="always"
        ),
    )


def UVector2_deserialize(value: Any) -> emath.UVector2:
    return emath.UVector2.from_buffer(value)


def UVector2_serialize(value: emath.UVector2) -> Any:
    return bytes(value)


def UVector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector2_serialize, when_used="always"
        ),
    )


def UVector2Array_deserialize(value: Any) -> emath.UVector2Array:
    return emath.UVector2Array.from_buffer(value)


def UVector2Array_serialize(value: emath.UVector2Array) -> Any:
    return bytes(value)


def UVector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector2Array_serialize, when_used="always"
        ),
    )


def I64Vector2_deserialize(value: Any) -> emath.I64Vector2:
    return emath.I64Vector2.from_buffer(value)


def I64Vector2_serialize(value: emath.I64Vector2) -> Any:
    return bytes(value)


def I64Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector2_serialize, when_used="always"
        ),
    )


def I64Vector2Array_deserialize(value: Any) -> emath.I64Vector2Array:
    return emath.I64Vector2Array.from_buffer(value)


def I64Vector2Array_serialize(value: emath.I64Vector2Array) -> Any:
    return bytes(value)


def I64Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector2Array_serialize, when_used="always"
        ),
    )


def U64Vector2_deserialize(value: Any) -> emath.U64Vector2:
    return emath.U64Vector2.from_buffer(value)


def U64Vector2_serialize(value: emath.U64Vector2) -> Any:
    return bytes(value)


def U64Vector2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector2_serialize, when_used="always"
        ),
    )


def U64Vector2Array_deserialize(value: Any) -> emath.U64Vector2Array:
    return emath.U64Vector2Array.from_buffer(value)


def U64Vector2Array_serialize(value: emath.U64Vector2Array) -> Any:
    return bytes(value)


def U64Vector2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector2Array_serialize, when_used="always"
        ),
    )


def BVector3_deserialize(value: Any) -> emath.BVector3:
    return emath.BVector3.from_buffer(value)


def BVector3_serialize(value: emath.BVector3) -> Any:
    return bytes(value)


def BVector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector3_serialize, when_used="always"
        ),
    )


def BVector3Array_deserialize(value: Any) -> emath.BVector3Array:
    return emath.BVector3Array.from_buffer(value)


def BVector3Array_serialize(value: emath.BVector3Array) -> Any:
    return bytes(value)


def BVector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector3Array_serialize, when_used="always"
        ),
    )


def DVector3_deserialize(value: Any) -> emath.DVector3:
    return emath.DVector3.from_buffer(value)


def DVector3_serialize(value: emath.DVector3) -> Any:
    return bytes(value)


def DVector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector3_serialize, when_used="always"
        ),
    )


def DVector3Array_deserialize(value: Any) -> emath.DVector3Array:
    return emath.DVector3Array.from_buffer(value)


def DVector3Array_serialize(value: emath.DVector3Array) -> Any:
    return bytes(value)


def DVector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector3Array_serialize, when_used="always"
        ),
    )


def FVector3_deserialize(value: Any) -> emath.FVector3:
    return emath.FVector3.from_buffer(value)


def FVector3_serialize(value: emath.FVector3) -> Any:
    return bytes(value)


def FVector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector3_serialize, when_used="always"
        ),
    )


def FVector3Array_deserialize(value: Any) -> emath.FVector3Array:
    return emath.FVector3Array.from_buffer(value)


def FVector3Array_serialize(value: emath.FVector3Array) -> Any:
    return bytes(value)


def FVector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector3Array_serialize, when_used="always"
        ),
    )


def I8Vector3_deserialize(value: Any) -> emath.I8Vector3:
    return emath.I8Vector3.from_buffer(value)


def I8Vector3_serialize(value: emath.I8Vector3) -> Any:
    return bytes(value)


def I8Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector3_serialize, when_used="always"
        ),
    )


def I8Vector3Array_deserialize(value: Any) -> emath.I8Vector3Array:
    return emath.I8Vector3Array.from_buffer(value)


def I8Vector3Array_serialize(value: emath.I8Vector3Array) -> Any:
    return bytes(value)


def I8Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector3Array_serialize, when_used="always"
        ),
    )


def U8Vector3_deserialize(value: Any) -> emath.U8Vector3:
    return emath.U8Vector3.from_buffer(value)


def U8Vector3_serialize(value: emath.U8Vector3) -> Any:
    return bytes(value)


def U8Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector3_serialize, when_used="always"
        ),
    )


def U8Vector3Array_deserialize(value: Any) -> emath.U8Vector3Array:
    return emath.U8Vector3Array.from_buffer(value)


def U8Vector3Array_serialize(value: emath.U8Vector3Array) -> Any:
    return bytes(value)


def U8Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector3Array_serialize, when_used="always"
        ),
    )


def I16Vector3_deserialize(value: Any) -> emath.I16Vector3:
    return emath.I16Vector3.from_buffer(value)


def I16Vector3_serialize(value: emath.I16Vector3) -> Any:
    return bytes(value)


def I16Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector3_serialize, when_used="always"
        ),
    )


def I16Vector3Array_deserialize(value: Any) -> emath.I16Vector3Array:
    return emath.I16Vector3Array.from_buffer(value)


def I16Vector3Array_serialize(value: emath.I16Vector3Array) -> Any:
    return bytes(value)


def I16Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector3Array_serialize, when_used="always"
        ),
    )


def U16Vector3_deserialize(value: Any) -> emath.U16Vector3:
    return emath.U16Vector3.from_buffer(value)


def U16Vector3_serialize(value: emath.U16Vector3) -> Any:
    return bytes(value)


def U16Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector3_serialize, when_used="always"
        ),
    )


def U16Vector3Array_deserialize(value: Any) -> emath.U16Vector3Array:
    return emath.U16Vector3Array.from_buffer(value)


def U16Vector3Array_serialize(value: emath.U16Vector3Array) -> Any:
    return bytes(value)


def U16Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector3Array_serialize, when_used="always"
        ),
    )


def I32Vector3_deserialize(value: Any) -> emath.I32Vector3:
    return emath.I32Vector3.from_buffer(value)


def I32Vector3_serialize(value: emath.I32Vector3) -> Any:
    return bytes(value)


def I32Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector3_serialize, when_used="always"
        ),
    )


def I32Vector3Array_deserialize(value: Any) -> emath.I32Vector3Array:
    return emath.I32Vector3Array.from_buffer(value)


def I32Vector3Array_serialize(value: emath.I32Vector3Array) -> Any:
    return bytes(value)


def I32Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector3Array_serialize, when_used="always"
        ),
    )


def U32Vector3_deserialize(value: Any) -> emath.U32Vector3:
    return emath.U32Vector3.from_buffer(value)


def U32Vector3_serialize(value: emath.U32Vector3) -> Any:
    return bytes(value)


def U32Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector3_serialize, when_used="always"
        ),
    )


def U32Vector3Array_deserialize(value: Any) -> emath.U32Vector3Array:
    return emath.U32Vector3Array.from_buffer(value)


def U32Vector3Array_serialize(value: emath.U32Vector3Array) -> Any:
    return bytes(value)


def U32Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector3Array_serialize, when_used="always"
        ),
    )


def IVector3_deserialize(value: Any) -> emath.IVector3:
    return emath.IVector3.from_buffer(value)


def IVector3_serialize(value: emath.IVector3) -> Any:
    return bytes(value)


def IVector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector3_serialize, when_used="always"
        ),
    )


def IVector3Array_deserialize(value: Any) -> emath.IVector3Array:
    return emath.IVector3Array.from_buffer(value)


def IVector3Array_serialize(value: emath.IVector3Array) -> Any:
    return bytes(value)


def IVector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector3Array_serialize, when_used="always"
        ),
    )


def UVector3_deserialize(value: Any) -> emath.UVector3:
    return emath.UVector3.from_buffer(value)


def UVector3_serialize(value: emath.UVector3) -> Any:
    return bytes(value)


def UVector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector3_serialize, when_used="always"
        ),
    )


def UVector3Array_deserialize(value: Any) -> emath.UVector3Array:
    return emath.UVector3Array.from_buffer(value)


def UVector3Array_serialize(value: emath.UVector3Array) -> Any:
    return bytes(value)


def UVector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector3Array_serialize, when_used="always"
        ),
    )


def I64Vector3_deserialize(value: Any) -> emath.I64Vector3:
    return emath.I64Vector3.from_buffer(value)


def I64Vector3_serialize(value: emath.I64Vector3) -> Any:
    return bytes(value)


def I64Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector3_serialize, when_used="always"
        ),
    )


def I64Vector3Array_deserialize(value: Any) -> emath.I64Vector3Array:
    return emath.I64Vector3Array.from_buffer(value)


def I64Vector3Array_serialize(value: emath.I64Vector3Array) -> Any:
    return bytes(value)


def I64Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector3Array_serialize, when_used="always"
        ),
    )


def U64Vector3_deserialize(value: Any) -> emath.U64Vector3:
    return emath.U64Vector3.from_buffer(value)


def U64Vector3_serialize(value: emath.U64Vector3) -> Any:
    return bytes(value)


def U64Vector3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector3_serialize, when_used="always"
        ),
    )


def U64Vector3Array_deserialize(value: Any) -> emath.U64Vector3Array:
    return emath.U64Vector3Array.from_buffer(value)


def U64Vector3Array_serialize(value: emath.U64Vector3Array) -> Any:
    return bytes(value)


def U64Vector3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector3Array_serialize, when_used="always"
        ),
    )


def BVector4_deserialize(value: Any) -> emath.BVector4:
    return emath.BVector4.from_buffer(value)


def BVector4_serialize(value: emath.BVector4) -> Any:
    return bytes(value)


def BVector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector4_serialize, when_used="always"
        ),
    )


def BVector4Array_deserialize(value: Any) -> emath.BVector4Array:
    return emath.BVector4Array.from_buffer(value)


def BVector4Array_serialize(value: emath.BVector4Array) -> Any:
    return bytes(value)


def BVector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BVector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BVector4Array_serialize, when_used="always"
        ),
    )


def DVector4_deserialize(value: Any) -> emath.DVector4:
    return emath.DVector4.from_buffer(value)


def DVector4_serialize(value: emath.DVector4) -> Any:
    return bytes(value)


def DVector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector4_serialize, when_used="always"
        ),
    )


def DVector4Array_deserialize(value: Any) -> emath.DVector4Array:
    return emath.DVector4Array.from_buffer(value)


def DVector4Array_serialize(value: emath.DVector4Array) -> Any:
    return bytes(value)


def DVector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DVector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DVector4Array_serialize, when_used="always"
        ),
    )


def FVector4_deserialize(value: Any) -> emath.FVector4:
    return emath.FVector4.from_buffer(value)


def FVector4_serialize(value: emath.FVector4) -> Any:
    return bytes(value)


def FVector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector4_serialize, when_used="always"
        ),
    )


def FVector4Array_deserialize(value: Any) -> emath.FVector4Array:
    return emath.FVector4Array.from_buffer(value)


def FVector4Array_serialize(value: emath.FVector4Array) -> Any:
    return bytes(value)


def FVector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FVector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FVector4Array_serialize, when_used="always"
        ),
    )


def I8Vector4_deserialize(value: Any) -> emath.I8Vector4:
    return emath.I8Vector4.from_buffer(value)


def I8Vector4_serialize(value: emath.I8Vector4) -> Any:
    return bytes(value)


def I8Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector4_serialize, when_used="always"
        ),
    )


def I8Vector4Array_deserialize(value: Any) -> emath.I8Vector4Array:
    return emath.I8Vector4Array.from_buffer(value)


def I8Vector4Array_serialize(value: emath.I8Vector4Array) -> Any:
    return bytes(value)


def I8Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Vector4Array_serialize, when_used="always"
        ),
    )


def U8Vector4_deserialize(value: Any) -> emath.U8Vector4:
    return emath.U8Vector4.from_buffer(value)


def U8Vector4_serialize(value: emath.U8Vector4) -> Any:
    return bytes(value)


def U8Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector4_serialize, when_used="always"
        ),
    )


def U8Vector4Array_deserialize(value: Any) -> emath.U8Vector4Array:
    return emath.U8Vector4Array.from_buffer(value)


def U8Vector4Array_serialize(value: emath.U8Vector4Array) -> Any:
    return bytes(value)


def U8Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Vector4Array_serialize, when_used="always"
        ),
    )


def I16Vector4_deserialize(value: Any) -> emath.I16Vector4:
    return emath.I16Vector4.from_buffer(value)


def I16Vector4_serialize(value: emath.I16Vector4) -> Any:
    return bytes(value)


def I16Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector4_serialize, when_used="always"
        ),
    )


def I16Vector4Array_deserialize(value: Any) -> emath.I16Vector4Array:
    return emath.I16Vector4Array.from_buffer(value)


def I16Vector4Array_serialize(value: emath.I16Vector4Array) -> Any:
    return bytes(value)


def I16Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Vector4Array_serialize, when_used="always"
        ),
    )


def U16Vector4_deserialize(value: Any) -> emath.U16Vector4:
    return emath.U16Vector4.from_buffer(value)


def U16Vector4_serialize(value: emath.U16Vector4) -> Any:
    return bytes(value)


def U16Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector4_serialize, when_used="always"
        ),
    )


def U16Vector4Array_deserialize(value: Any) -> emath.U16Vector4Array:
    return emath.U16Vector4Array.from_buffer(value)


def U16Vector4Array_serialize(value: emath.U16Vector4Array) -> Any:
    return bytes(value)


def U16Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Vector4Array_serialize, when_used="always"
        ),
    )


def I32Vector4_deserialize(value: Any) -> emath.I32Vector4:
    return emath.I32Vector4.from_buffer(value)


def I32Vector4_serialize(value: emath.I32Vector4) -> Any:
    return bytes(value)


def I32Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector4_serialize, when_used="always"
        ),
    )


def I32Vector4Array_deserialize(value: Any) -> emath.I32Vector4Array:
    return emath.I32Vector4Array.from_buffer(value)


def I32Vector4Array_serialize(value: emath.I32Vector4Array) -> Any:
    return bytes(value)


def I32Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Vector4Array_serialize, when_used="always"
        ),
    )


def U32Vector4_deserialize(value: Any) -> emath.U32Vector4:
    return emath.U32Vector4.from_buffer(value)


def U32Vector4_serialize(value: emath.U32Vector4) -> Any:
    return bytes(value)


def U32Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector4_serialize, when_used="always"
        ),
    )


def U32Vector4Array_deserialize(value: Any) -> emath.U32Vector4Array:
    return emath.U32Vector4Array.from_buffer(value)


def U32Vector4Array_serialize(value: emath.U32Vector4Array) -> Any:
    return bytes(value)


def U32Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Vector4Array_serialize, when_used="always"
        ),
    )


def IVector4_deserialize(value: Any) -> emath.IVector4:
    return emath.IVector4.from_buffer(value)


def IVector4_serialize(value: emath.IVector4) -> Any:
    return bytes(value)


def IVector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector4_serialize, when_used="always"
        ),
    )


def IVector4Array_deserialize(value: Any) -> emath.IVector4Array:
    return emath.IVector4Array.from_buffer(value)


def IVector4Array_serialize(value: emath.IVector4Array) -> Any:
    return bytes(value)


def IVector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IVector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IVector4Array_serialize, when_used="always"
        ),
    )


def UVector4_deserialize(value: Any) -> emath.UVector4:
    return emath.UVector4.from_buffer(value)


def UVector4_serialize(value: emath.UVector4) -> Any:
    return bytes(value)


def UVector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector4_serialize, when_used="always"
        ),
    )


def UVector4Array_deserialize(value: Any) -> emath.UVector4Array:
    return emath.UVector4Array.from_buffer(value)


def UVector4Array_serialize(value: emath.UVector4Array) -> Any:
    return bytes(value)


def UVector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UVector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UVector4Array_serialize, when_used="always"
        ),
    )


def I64Vector4_deserialize(value: Any) -> emath.I64Vector4:
    return emath.I64Vector4.from_buffer(value)


def I64Vector4_serialize(value: emath.I64Vector4) -> Any:
    return bytes(value)


def I64Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector4_serialize, when_used="always"
        ),
    )


def I64Vector4Array_deserialize(value: Any) -> emath.I64Vector4Array:
    return emath.I64Vector4Array.from_buffer(value)


def I64Vector4Array_serialize(value: emath.I64Vector4Array) -> Any:
    return bytes(value)


def I64Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Vector4Array_serialize, when_used="always"
        ),
    )


def U64Vector4_deserialize(value: Any) -> emath.U64Vector4:
    return emath.U64Vector4.from_buffer(value)


def U64Vector4_serialize(value: emath.U64Vector4) -> Any:
    return bytes(value)


def U64Vector4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector4_serialize, when_used="always"
        ),
    )


def U64Vector4Array_deserialize(value: Any) -> emath.U64Vector4Array:
    return emath.U64Vector4Array.from_buffer(value)


def U64Vector4Array_serialize(value: emath.U64Vector4Array) -> Any:
    return bytes(value)


def U64Vector4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Vector4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Vector4Array_serialize, when_used="always"
        ),
    )


def DMatrix2x2_deserialize(value: Any) -> emath.DMatrix2x2:
    return emath.DMatrix2x2.from_buffer(value)


def DMatrix2x2_serialize(value: emath.DMatrix2x2) -> Any:
    return bytes(value)


def DMatrix2x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x2_serialize, when_used="always"
        ),
    )


def DMatrix2x2Array_deserialize(value: Any) -> emath.DMatrix2x2Array:
    return emath.DMatrix2x2Array.from_buffer(value)


def DMatrix2x2Array_serialize(value: emath.DMatrix2x2Array) -> Any:
    return bytes(value)


def DMatrix2x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x2Array_serialize, when_used="always"
        ),
    )


def FMatrix2x2_deserialize(value: Any) -> emath.FMatrix2x2:
    return emath.FMatrix2x2.from_buffer(value)


def FMatrix2x2_serialize(value: emath.FMatrix2x2) -> Any:
    return bytes(value)


def FMatrix2x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x2_serialize, when_used="always"
        ),
    )


def FMatrix2x2Array_deserialize(value: Any) -> emath.FMatrix2x2Array:
    return emath.FMatrix2x2Array.from_buffer(value)


def FMatrix2x2Array_serialize(value: emath.FMatrix2x2Array) -> Any:
    return bytes(value)


def FMatrix2x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x2Array_serialize, when_used="always"
        ),
    )


def DMatrix2x3_deserialize(value: Any) -> emath.DMatrix2x3:
    return emath.DMatrix2x3.from_buffer(value)


def DMatrix2x3_serialize(value: emath.DMatrix2x3) -> Any:
    return bytes(value)


def DMatrix2x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x3_serialize, when_used="always"
        ),
    )


def DMatrix2x3Array_deserialize(value: Any) -> emath.DMatrix2x3Array:
    return emath.DMatrix2x3Array.from_buffer(value)


def DMatrix2x3Array_serialize(value: emath.DMatrix2x3Array) -> Any:
    return bytes(value)


def DMatrix2x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x3Array_serialize, when_used="always"
        ),
    )


def FMatrix2x3_deserialize(value: Any) -> emath.FMatrix2x3:
    return emath.FMatrix2x3.from_buffer(value)


def FMatrix2x3_serialize(value: emath.FMatrix2x3) -> Any:
    return bytes(value)


def FMatrix2x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x3_serialize, when_used="always"
        ),
    )


def FMatrix2x3Array_deserialize(value: Any) -> emath.FMatrix2x3Array:
    return emath.FMatrix2x3Array.from_buffer(value)


def FMatrix2x3Array_serialize(value: emath.FMatrix2x3Array) -> Any:
    return bytes(value)


def FMatrix2x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x3Array_serialize, when_used="always"
        ),
    )


def DMatrix2x4_deserialize(value: Any) -> emath.DMatrix2x4:
    return emath.DMatrix2x4.from_buffer(value)


def DMatrix2x4_serialize(value: emath.DMatrix2x4) -> Any:
    return bytes(value)


def DMatrix2x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x4_serialize, when_used="always"
        ),
    )


def DMatrix2x4Array_deserialize(value: Any) -> emath.DMatrix2x4Array:
    return emath.DMatrix2x4Array.from_buffer(value)


def DMatrix2x4Array_serialize(value: emath.DMatrix2x4Array) -> Any:
    return bytes(value)


def DMatrix2x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix2x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix2x4Array_serialize, when_used="always"
        ),
    )


def FMatrix2x4_deserialize(value: Any) -> emath.FMatrix2x4:
    return emath.FMatrix2x4.from_buffer(value)


def FMatrix2x4_serialize(value: emath.FMatrix2x4) -> Any:
    return bytes(value)


def FMatrix2x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x4_serialize, when_used="always"
        ),
    )


def FMatrix2x4Array_deserialize(value: Any) -> emath.FMatrix2x4Array:
    return emath.FMatrix2x4Array.from_buffer(value)


def FMatrix2x4Array_serialize(value: emath.FMatrix2x4Array) -> Any:
    return bytes(value)


def FMatrix2x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix2x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix2x4Array_serialize, when_used="always"
        ),
    )


def DMatrix3x2_deserialize(value: Any) -> emath.DMatrix3x2:
    return emath.DMatrix3x2.from_buffer(value)


def DMatrix3x2_serialize(value: emath.DMatrix3x2) -> Any:
    return bytes(value)


def DMatrix3x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x2_serialize, when_used="always"
        ),
    )


def DMatrix3x2Array_deserialize(value: Any) -> emath.DMatrix3x2Array:
    return emath.DMatrix3x2Array.from_buffer(value)


def DMatrix3x2Array_serialize(value: emath.DMatrix3x2Array) -> Any:
    return bytes(value)


def DMatrix3x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x2Array_serialize, when_used="always"
        ),
    )


def FMatrix3x2_deserialize(value: Any) -> emath.FMatrix3x2:
    return emath.FMatrix3x2.from_buffer(value)


def FMatrix3x2_serialize(value: emath.FMatrix3x2) -> Any:
    return bytes(value)


def FMatrix3x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x2_serialize, when_used="always"
        ),
    )


def FMatrix3x2Array_deserialize(value: Any) -> emath.FMatrix3x2Array:
    return emath.FMatrix3x2Array.from_buffer(value)


def FMatrix3x2Array_serialize(value: emath.FMatrix3x2Array) -> Any:
    return bytes(value)


def FMatrix3x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x2Array_serialize, when_used="always"
        ),
    )


def DMatrix3x3_deserialize(value: Any) -> emath.DMatrix3x3:
    return emath.DMatrix3x3.from_buffer(value)


def DMatrix3x3_serialize(value: emath.DMatrix3x3) -> Any:
    return bytes(value)


def DMatrix3x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x3_serialize, when_used="always"
        ),
    )


def DMatrix3x3Array_deserialize(value: Any) -> emath.DMatrix3x3Array:
    return emath.DMatrix3x3Array.from_buffer(value)


def DMatrix3x3Array_serialize(value: emath.DMatrix3x3Array) -> Any:
    return bytes(value)


def DMatrix3x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x3Array_serialize, when_used="always"
        ),
    )


def FMatrix3x3_deserialize(value: Any) -> emath.FMatrix3x3:
    return emath.FMatrix3x3.from_buffer(value)


def FMatrix3x3_serialize(value: emath.FMatrix3x3) -> Any:
    return bytes(value)


def FMatrix3x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x3_serialize, when_used="always"
        ),
    )


def FMatrix3x3Array_deserialize(value: Any) -> emath.FMatrix3x3Array:
    return emath.FMatrix3x3Array.from_buffer(value)


def FMatrix3x3Array_serialize(value: emath.FMatrix3x3Array) -> Any:
    return bytes(value)


def FMatrix3x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x3Array_serialize, when_used="always"
        ),
    )


def DMatrix3x4_deserialize(value: Any) -> emath.DMatrix3x4:
    return emath.DMatrix3x4.from_buffer(value)


def DMatrix3x4_serialize(value: emath.DMatrix3x4) -> Any:
    return bytes(value)


def DMatrix3x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x4_serialize, when_used="always"
        ),
    )


def DMatrix3x4Array_deserialize(value: Any) -> emath.DMatrix3x4Array:
    return emath.DMatrix3x4Array.from_buffer(value)


def DMatrix3x4Array_serialize(value: emath.DMatrix3x4Array) -> Any:
    return bytes(value)


def DMatrix3x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix3x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix3x4Array_serialize, when_used="always"
        ),
    )


def FMatrix3x4_deserialize(value: Any) -> emath.FMatrix3x4:
    return emath.FMatrix3x4.from_buffer(value)


def FMatrix3x4_serialize(value: emath.FMatrix3x4) -> Any:
    return bytes(value)


def FMatrix3x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x4_serialize, when_used="always"
        ),
    )


def FMatrix3x4Array_deserialize(value: Any) -> emath.FMatrix3x4Array:
    return emath.FMatrix3x4Array.from_buffer(value)


def FMatrix3x4Array_serialize(value: emath.FMatrix3x4Array) -> Any:
    return bytes(value)


def FMatrix3x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix3x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix3x4Array_serialize, when_used="always"
        ),
    )


def DMatrix4x2_deserialize(value: Any) -> emath.DMatrix4x2:
    return emath.DMatrix4x2.from_buffer(value)


def DMatrix4x2_serialize(value: emath.DMatrix4x2) -> Any:
    return bytes(value)


def DMatrix4x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x2_serialize, when_used="always"
        ),
    )


def DMatrix4x2Array_deserialize(value: Any) -> emath.DMatrix4x2Array:
    return emath.DMatrix4x2Array.from_buffer(value)


def DMatrix4x2Array_serialize(value: emath.DMatrix4x2Array) -> Any:
    return bytes(value)


def DMatrix4x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x2Array_serialize, when_used="always"
        ),
    )


def FMatrix4x2_deserialize(value: Any) -> emath.FMatrix4x2:
    return emath.FMatrix4x2.from_buffer(value)


def FMatrix4x2_serialize(value: emath.FMatrix4x2) -> Any:
    return bytes(value)


def FMatrix4x2__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x2_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x2_serialize, when_used="always"
        ),
    )


def FMatrix4x2Array_deserialize(value: Any) -> emath.FMatrix4x2Array:
    return emath.FMatrix4x2Array.from_buffer(value)


def FMatrix4x2Array_serialize(value: emath.FMatrix4x2Array) -> Any:
    return bytes(value)


def FMatrix4x2Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x2Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x2Array_serialize, when_used="always"
        ),
    )


def DMatrix4x3_deserialize(value: Any) -> emath.DMatrix4x3:
    return emath.DMatrix4x3.from_buffer(value)


def DMatrix4x3_serialize(value: emath.DMatrix4x3) -> Any:
    return bytes(value)


def DMatrix4x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x3_serialize, when_used="always"
        ),
    )


def DMatrix4x3Array_deserialize(value: Any) -> emath.DMatrix4x3Array:
    return emath.DMatrix4x3Array.from_buffer(value)


def DMatrix4x3Array_serialize(value: emath.DMatrix4x3Array) -> Any:
    return bytes(value)


def DMatrix4x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x3Array_serialize, when_used="always"
        ),
    )


def FMatrix4x3_deserialize(value: Any) -> emath.FMatrix4x3:
    return emath.FMatrix4x3.from_buffer(value)


def FMatrix4x3_serialize(value: emath.FMatrix4x3) -> Any:
    return bytes(value)


def FMatrix4x3__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x3_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x3_serialize, when_used="always"
        ),
    )


def FMatrix4x3Array_deserialize(value: Any) -> emath.FMatrix4x3Array:
    return emath.FMatrix4x3Array.from_buffer(value)


def FMatrix4x3Array_serialize(value: emath.FMatrix4x3Array) -> Any:
    return bytes(value)


def FMatrix4x3Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x3Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x3Array_serialize, when_used="always"
        ),
    )


def DMatrix4x4_deserialize(value: Any) -> emath.DMatrix4x4:
    return emath.DMatrix4x4.from_buffer(value)


def DMatrix4x4_serialize(value: emath.DMatrix4x4) -> Any:
    return bytes(value)


def DMatrix4x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x4_serialize, when_used="always"
        ),
    )


def DMatrix4x4Array_deserialize(value: Any) -> emath.DMatrix4x4Array:
    return emath.DMatrix4x4Array.from_buffer(value)


def DMatrix4x4Array_serialize(value: emath.DMatrix4x4Array) -> Any:
    return bytes(value)


def DMatrix4x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DMatrix4x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DMatrix4x4Array_serialize, when_used="always"
        ),
    )


def FMatrix4x4_deserialize(value: Any) -> emath.FMatrix4x4:
    return emath.FMatrix4x4.from_buffer(value)


def FMatrix4x4_serialize(value: emath.FMatrix4x4) -> Any:
    return bytes(value)


def FMatrix4x4__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x4_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x4_serialize, when_used="always"
        ),
    )


def FMatrix4x4Array_deserialize(value: Any) -> emath.FMatrix4x4Array:
    return emath.FMatrix4x4Array.from_buffer(value)


def FMatrix4x4Array_serialize(value: emath.FMatrix4x4Array) -> Any:
    return bytes(value)


def FMatrix4x4Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FMatrix4x4Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FMatrix4x4Array_serialize, when_used="always"
        ),
    )


def DQuaternion_deserialize(value: Any) -> emath.DQuaternion:
    return emath.DQuaternion.from_buffer(value)


def DQuaternion_serialize(value: emath.DQuaternion) -> Any:
    return bytes(value)


def DQuaternion__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DQuaternion_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DQuaternion_serialize, when_used="always"
        ),
    )


def DQuaternionArray_deserialize(value: Any) -> emath.DQuaternionArray:
    return emath.DQuaternionArray.from_buffer(value)


def DQuaternionArray_serialize(value: emath.DQuaternionArray) -> Any:
    return bytes(value)


def DQuaternionArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DQuaternionArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DQuaternionArray_serialize, when_used="always"
        ),
    )


def FQuaternion_deserialize(value: Any) -> emath.FQuaternion:
    return emath.FQuaternion.from_buffer(value)


def FQuaternion_serialize(value: emath.FQuaternion) -> Any:
    return bytes(value)


def FQuaternion__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FQuaternion_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FQuaternion_serialize, when_used="always"
        ),
    )


def FQuaternionArray_deserialize(value: Any) -> emath.FQuaternionArray:
    return emath.FQuaternionArray.from_buffer(value)


def FQuaternionArray_serialize(value: emath.FQuaternionArray) -> Any:
    return bytes(value)


def FQuaternionArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FQuaternionArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FQuaternionArray_serialize, when_used="always"
        ),
    )


def BArray_deserialize(value: Any) -> emath.BArray:
    return emath.BArray.from_buffer(value)


def BArray_serialize(value: emath.BArray) -> Any:
    return bytes(value)


def BArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        BArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            BArray_serialize, when_used="always"
        ),
    )


def DArray_deserialize(value: Any) -> emath.DArray:
    return emath.DArray.from_buffer(value)


def DArray_serialize(value: emath.DArray) -> Any:
    return bytes(value)


def DArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        DArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            DArray_serialize, when_used="always"
        ),
    )


def FArray_deserialize(value: Any) -> emath.FArray:
    return emath.FArray.from_buffer(value)


def FArray_serialize(value: emath.FArray) -> Any:
    return bytes(value)


def FArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        FArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            FArray_serialize, when_used="always"
        ),
    )


def I8Array_deserialize(value: Any) -> emath.I8Array:
    return emath.I8Array.from_buffer(value)


def I8Array_serialize(value: emath.I8Array) -> Any:
    return bytes(value)


def I8Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I8Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I8Array_serialize, when_used="always"
        ),
    )


def U8Array_deserialize(value: Any) -> emath.U8Array:
    return emath.U8Array.from_buffer(value)


def U8Array_serialize(value: emath.U8Array) -> Any:
    return bytes(value)


def U8Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U8Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U8Array_serialize, when_used="always"
        ),
    )


def I16Array_deserialize(value: Any) -> emath.I16Array:
    return emath.I16Array.from_buffer(value)


def I16Array_serialize(value: emath.I16Array) -> Any:
    return bytes(value)


def I16Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I16Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I16Array_serialize, when_used="always"
        ),
    )


def U16Array_deserialize(value: Any) -> emath.U16Array:
    return emath.U16Array.from_buffer(value)


def U16Array_serialize(value: emath.U16Array) -> Any:
    return bytes(value)


def U16Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U16Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U16Array_serialize, when_used="always"
        ),
    )


def I32Array_deserialize(value: Any) -> emath.I32Array:
    return emath.I32Array.from_buffer(value)


def I32Array_serialize(value: emath.I32Array) -> Any:
    return bytes(value)


def I32Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I32Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I32Array_serialize, when_used="always"
        ),
    )


def U32Array_deserialize(value: Any) -> emath.U32Array:
    return emath.U32Array.from_buffer(value)


def U32Array_serialize(value: emath.U32Array) -> Any:
    return bytes(value)


def U32Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U32Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U32Array_serialize, when_used="always"
        ),
    )


def IArray_deserialize(value: Any) -> emath.IArray:
    return emath.IArray.from_buffer(value)


def IArray_serialize(value: emath.IArray) -> Any:
    return bytes(value)


def IArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        IArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            IArray_serialize, when_used="always"
        ),
    )


def UArray_deserialize(value: Any) -> emath.UArray:
    return emath.UArray.from_buffer(value)


def UArray_serialize(value: emath.UArray) -> Any:
    return bytes(value)


def UArray__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        UArray_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            UArray_serialize, when_used="always"
        ),
    )


def I64Array_deserialize(value: Any) -> emath.I64Array:
    return emath.I64Array.from_buffer(value)


def I64Array_serialize(value: emath.I64Array) -> Any:
    return bytes(value)


def I64Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        I64Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            I64Array_serialize, when_used="always"
        ),
    )


def U64Array_deserialize(value: Any) -> emath.U64Array:
    return emath.U64Array.from_buffer(value)


def U64Array_serialize(value: emath.U64Array) -> Any:
    return bytes(value)


def U64Array__get_pydantic_core_schema__(
    source_type: Any, handler: pydantic.GetCoreSchemaHandler
) -> pydantic_core.CoreSchema:
    return pydantic_core.core_schema.no_info_after_validator_function(
        U64Array_deserialize,
        pydantic_core.core_schema.any_schema(),
        serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
            U64Array_serialize, when_used="always"
        ),
    )
