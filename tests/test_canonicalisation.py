"""
The code in this file is a modified version from
https://github.com/Zac-HD/hypothesis-jsonschema/blob/b50af13a837db0f2243822f233512d8ebdff0694/src/hypothesis_jsonschema/_from_schema.py#L32
The original author is Zac Hatfield-Dodds
"""

import json

import canonical_json
import pytest
from hypothesis import given
from hypothesis_jsonschema._from_schema import JSON_STRATEGY


@given(JSON_STRATEGY)
def test_canonical_json_encoding(v):
    encoded = canonical_json.dumps(v)
    v2 = json.loads(encoded)
    assert v == v2
    assert canonical_json.dumps(v2) == encoded


@pytest.mark.parametrize(
    "value, expected",
    (
        (float(2 ** 64), 2 ** 64),
        # The following is the default serde behavior
        # Such values are not likely to appear in schemas, but it there will be a case for this,
        # Then it could be changed to match the Python behavior with such input
        (float("nan"), "null"),
        (float("-inf"), "null"),
        (float("inf"), "null"),
    ),
)
def test_floats(value, expected):
    assert canonical_json.dumps(value) == str(expected)
