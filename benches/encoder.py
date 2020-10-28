import canonical_json
import pytest
from hypothesis_jsonschema._encode import encode_canonical_json

serializers = pytest.mark.parametrize("func", (canonical_json.dumps, encode_canonical_json), ids=["rust", "python"])


@pytest.mark.parametrize(
    "value",
    (None, 0, "A", 0.0, True, [], {}),
    ids=["null", "integer", "string", "number", "boolean", "array", "object"],
)
@serializers
@pytest.mark.benchmark(group="Simple values")
def test_primitives(benchmark, func, value):
    benchmark(func, value)


SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "multipleOf": {"type": "number", "minimum": 0, "exclusiveMinimum": True},
        "maximum": {"type": "number"},
        "exclusiveMaximum": {"type": "boolean", "default": False},
        "minimum": {"type": "number"},
        "exclusiveMinimum": {"type": "boolean", "default": False},
        "maxLength": {"type": "integer", "minimum": 0},
        "minLength": {"type": "integer", "minimum": 0, "default": 0},
        "pattern": {"type": "string", "format": "regex"},
        "maxItems": {"type": "integer", "minimum": 0},
        "minItems": {"type": "integer", "minimum": 0, "default": 0},
        "uniqueItems": {"type": "boolean", "default": False},
        "maxProperties": {"type": "integer", "minimum": 0},
        "minProperties": {"type": "integer", "minimum": 0, "default": 0},
        "required": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "uniqueItems": True,
        },
        "enum": {"type": "array", "items": {}, "minItems": 1, "uniqueItems": False},
        "type": {
            "type": "string",
            "enum": ["array", "boolean", "integer", "number", "object", "string"],
        },
        "not": {
            "oneOf": [
                {"$ref": "#/definitions/Schema"},
                {"$ref": "#/definitions/Reference"},
            ]
        },
        "allOf": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Schema"},
                    {"$ref": "#/definitions/Reference"},
                ]
            },
        },
        "oneOf": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Schema"},
                    {"$ref": "#/definitions/Reference"},
                ]
            },
        },
        "anyOf": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Schema"},
                    {"$ref": "#/definitions/Reference"},
                ]
            },
        },
        "items": {
            "oneOf": [
                {"$ref": "#/definitions/Schema"},
                {"$ref": "#/definitions/Reference"},
            ]
        },
        "properties": {
            "type": "object",
            "additionalProperties": {
                "oneOf": [
                    {"$ref": "#/definitions/Schema"},
                    {"$ref": "#/definitions/Reference"},
                ]
            },
        },
        "additionalProperties": {
            "oneOf": [
                {"$ref": "#/definitions/Schema"},
                {"$ref": "#/definitions/Reference"},
                {"type": "boolean"},
            ],
            "default": True,
        },
        "description": {"type": "string"},
        "format": {"type": "string"},
        "default": {},
        "nullable": {"type": "boolean", "default": False},
        "discriminator": {"$ref": "#/definitions/Discriminator"},
        "readOnly": {"type": "boolean", "default": False},
        "writeOnly": {"type": "boolean", "default": False},
        "example": {},
        "externalDocs": {"$ref": "#/definitions/ExternalDocumentation"},
        "deprecated": {"type": "boolean", "default": False},
        "xml": {"$ref": "#/definitions/XML"},
    },
    "patternProperties": {"^x-": {}},
    "additionalProperties": False,
}


@serializers
@pytest.mark.benchmark(group="Complex schema")
def test_complex(benchmark, func):
    benchmark(func, SCHEMA)


@pytest.mark.parametrize(
    "value",
    ({"foo": 1}, list(range(10)), float(2 ** 64)),
    ids=["single-item-object", "list-of-integers", "big-float"],
)
@serializers
@pytest.mark.benchmark(group="Specific cases")
def test_specific(benchmark, func, value):
    benchmark(func, value)
