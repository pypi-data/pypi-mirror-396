from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dcbroker",
    version="1.0.0",
    author="aYukine",
    author_email="phayuk@gmail.com",
    description="A lightweight Python client for DC-broker message broker system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aYukine/DCBroker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
