import os
from setuptools import setup, find_packages

# Read the version from the package
with open("tubox_client/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tubox-client",
    version=version,
    description="Official Python client for Tubox Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tubox",
    author_email="aegis.invincible@gmail.com",
    url="https://tubox.cloud",
    project_urls={
        "Documentation": "https://tubox.cloud/",
        "Source": "https://github.com/axiomchronicles/tubox-client",
        "Tracker": "https://github.com/axiomchronicles/tubox-client/issues",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
    license="MIT",  # SPDX identifier
    install_requires=[
        "crous>=1.0.0",  # Required for binary protocol serialization
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    keywords="tubox database async client driver",
    include_package_data=True,
    zip_safe=False,
)
