# Canonical JSON

It is a specialized JSON encoder for Python, written in Rust. Its use-case is to produce values that honor the JSON Schema semantics:

- Integer-valued floats are serialized as integers. For example: `1.0` becomes `1`;
- Mappings are sorted during serialization.

With this rule applied, it is possible to de-duplicate a list of JSON schemas, which plays a crucial role in the [hypothesis-jsonschema](https://github.com/Zac-HD/hypothesis-jsonschema) project.

Currently, this project is in the early development stage and doesn't have all corner-cases adequately implemented. However, it is working for common schemas.

Note, there is a lot of **unsafe** code.
