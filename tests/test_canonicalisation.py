"""
The code in this file is a modified version from
https://github.com/Zac-HD/hypothesis-jsonschema/blob/b50af13a837db0f2243822f233512d8ebdff0694/src/hypothesis_jsonschema/_from_schema.py#L32
The original author is Zac Hatfield-Dodds
"""

import json

import canonical_json
from hypothesis import given
from hypothesis_jsonschema._from_schema import JSON_STRATEGY


@given(JSON_STRATEGY)
def test_canonical_json_encoding(v):
    encoded = canonical_json.dumps(v)
    v2 = json.loads(encoded)
    assert v == v2
    assert canonical_json.dumps(v2) == encoded
