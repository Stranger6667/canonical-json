# Canonical JSON

It is a specialized JSON encoder for Python, written in Rust. Its use-case is to produce values that honor the JSON Schema semantics:

- Integer-valued floats are serialized as integers. For example: `1.0` becomes `1`;
- Mappings are sorted during serialization.

With this rule applied, it is possible to de-duplicate a list of JSON schemas, which plays a crucial role in the [hypothesis-jsonschema](https://github.com/Zac-HD/hypothesis-jsonschema) project.

Currently, this project is in the early development stage but passes canonical encoding tests from `hypothesis-jsonschema`.

On average it performs **3-4.5x** faster than the Python version.

Note, there is a lot of **unsafe** code.

Install from sources via `pip`:

```bash
git clone https://github.com/Stranger6667/canonical-json.git
cd canonical-json
pip install -U .
```

Tests:

```bash
tox -e py38
```

Benchmark:

```bash
tox -e bench
```
