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
    "optilogic>=2.13.0",
    "PyJWT>=2.8.0",
    "requests>=2.31.0",
    "pandas>=2.0.0",
    "SQLAlchemy>=2.0.0",
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


def read_version() -> str:
    import os

    version_ns = {}
    here = os.path.abspath(os.path.dirname(__file__))
    version_path = os.path.join(here, "datastar", "_version.py")
    with open(version_path, "r", encoding="utf-8") as f:
        exec(f.read(), version_ns)
    return version_ns["__version__"]


def read_long_description() -> str:
    import os

    here = os.path.abspath(os.path.dirname(__file__))
    md_path = os.path.join(here, "docs", "datastar.md")
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="ol_datastar",
    include_package_data=True,
    package_data={
        # PEP 561: indicate inline typing information is included
        "ol_datastar.datastar": ["py.typed"],
    },
    version=read_version(),
    description="Helpful utilities for working with Datastar projects",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://cosmicfrog.com",
    author="Optilogic",
    packages=find_packages(),
    license="MIT",
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
