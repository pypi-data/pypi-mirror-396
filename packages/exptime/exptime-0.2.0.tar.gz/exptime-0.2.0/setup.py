from setuptools import setup

setup(
    name="exptime",
    version="0.2.0",
    author="wirnty",
    author_email="skedovichusjdj@gmail.com",
    description="Simple timeout-based exception helpers.",
    py_modules=["exptime"],   # 🔥 THIS IS THE KEY LINE 🔥
    python_requires=">=3.6",
)