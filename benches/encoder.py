import pytest

import canonical_json

from hypothesis_jsonschema._encode import encode_canonical_json


serializers = pytest.mark.parametrize("func", (canonical_json.dumps, encode_canonical_json), ids=["rust", "python"])


@serializers
@pytest.mark.parametrize("primitive", (None, 0, "A", 0.0, True, [], {}))
@pytest.mark.benchmark(group="Simple values")
def test_primitives(benchmark, func, primitive):
    benchmark(func, primitive)
