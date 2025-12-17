from setuptools import setup, find_packages

setup(
    name="genesis-framework-sdk",
    version="0.1.1",
    description="The OS for Recursive Agentic Intelligence",
    author="Genesis Inc.",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)