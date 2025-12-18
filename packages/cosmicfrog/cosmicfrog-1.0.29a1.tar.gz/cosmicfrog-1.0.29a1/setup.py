"""
    Library setup file
"""

import subprocess
from setuptools import setup, find_packages


try:
    subprocess.check_output(["pip", "show", "psycopg2"])
    PSYCOPG2_INSTALLED = True
except subprocess.CalledProcessError:
    PSYCOPG2_INSTALLED = False


install_requires = [
    "charset-normalizer>=3.4.4",
    "numpy>=1.26.4",
    "pandas>=2.3.3",
    "sqlalchemy>=2.0.44",
    "optilogic>=2.14.0",
    "PyJWT>=2.10.1",
    "httpx>=0.28.1",
    "splitio_client>=9.7.0",
    "opentelemetry-api>=1.27.0",
    "opentelemetry-sdk>=1.27.0",
    "azure-monitor-opentelemetry-exporter>=1.0.0b40",
]

# If psycopg2 is not installed let's check if we should use the binary version instead
if not PSYCOPG2_INSTALLED:
    import os

    # Look for USE_PSYCOPG2_BINARY, if not set, default to True, otherwise, use the value
    USE_BINARY = os.getenv("USE_PSYCOPG2_BINARY", "True").lower() == "true"

    if USE_BINARY:
        install_requires.append("psycopg2-binary>=2.9.9")
    else:
        install_requires.append("psycopg2>=2.9.9")


setup(
    name="cosmicfrog",
    include_package_data=True,
    version="1.0.29a1",
    description="Helpful utilities for working with Cosmic Frog models",
    url="https://cosmicfrog.com",
    author="Optilogic",
    packages=find_packages(include=["cosmicfrog", "cosmicfrog.*"]),
    package_data={
        "cosmicfrog": [
            "anura28/*.json",
            "anura28/table_definitions/*.json",
        ],
    },
    license="MIT",
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
