from setuptools import setup, Extension

module = Extension("c", sources=["core.c"])

setup(
    name="PyKimixC",
    version="0.1",
    description="C extension for PyKimix",
    ext_modules=[module]
)