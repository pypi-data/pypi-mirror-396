import os
import pathlib
import re

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Get the version string. Cannot be done with import!
with open(os.path.join("oais_utils", "version.py"), "rt") as f:
    version = re.search(r'__version__\s*=\s*"(?P<version>.*)"\n', f.read()).group(
        "version"
    )

# This call to setup() does all the work
setup(
    name="oais_utils",
    version=version,
    description="OAIS utilities",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/digitalmemory/utils",
    author="CERN Digital Memory",
    author_email="digitalmemory-support@cern.ch",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(include=["oais_utils", "oais_utils.*"]),
    include_package_data=True,
    install_requires=["jsonschema==3.0.2", "bagit==1.9.0"],
)
