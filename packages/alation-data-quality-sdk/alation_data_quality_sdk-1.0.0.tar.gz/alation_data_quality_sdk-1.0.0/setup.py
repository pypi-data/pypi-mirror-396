"""Setup script for the Alation Data Quality SDK."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="alation-data-quality-sdk",
    version="1.0.0",
    author="Alation",
    author_email="support@alation.com",
    description="Production-ready SDK for running Alation data quality checks using Soda Core",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alation/data-quality-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "alation-dq=data_quality_sdk.main:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "data_quality_sdk": ["templates/**/*.yaml"],
    },
)
