from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="canonical_json",
    version="0.1",
    rust_extensions=[RustExtension("canonical_json", binding=Binding.PyO3)],
    zip_safe=False,
)
