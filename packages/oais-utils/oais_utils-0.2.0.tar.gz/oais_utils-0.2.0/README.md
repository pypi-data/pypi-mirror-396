# oais-utilities

[![PyPI version](https://badge.fury.io/py/oais-utils.svg)](https://pypi.org/project/oais-utils/)

 Utilities to work with the CERN OAIS artifacts, such as Submission Information Packages.

## Features

### Validate CERN SIP

Validates the folder in the given path according to the [CERN SIP specification](https://gitlab.cern.ch/digitalmemory/sip-spec), following these steps:

1. Verify directory structure
2. Validate the manifest file against the desired sip JSON schema. By default uses [sip-schema-v1.json](https://gitlab.cern.ch/digitalmemory/sip-spec/-/blob/main/versions/sip-schema-v1.json), also shipped in this package
3. Validate the folder as a BagIt package
	- file are allowed to be missing if the manifest specifies it's a "lightweight" SIP.
4. Checks if every content file mentioned in the manifest is actually present in the payload

Usage:

```python
from oais_utils import validate
validate("name_of_the_sip_folder")
```

### sip.json schemas

SIP manifest JSON schemas are also shipped and exposed with this package.

To get a python dictionary with the schema short name as keys and the parsed (as python object) schema as value for the corresponding schema name, run:

```python
import oais_utils
schemas = oais_utils.schemas

schemas.keys()
# ['v1']

schemas['v1']
# [...]
# (Returns the sip JSON schema "v1" as parsed python object)

schemas['v1']['$id']
# https://gitlab.cern.ch/digitalmemory/sip-spec/-/raw/main/versions/sip-schema-v1.json
```

## Install

Install from PyPi

```bash
pip install oais-utils
```

For development, you can clone this repository and then install it with the `-e` flag:

```bash
# Clone the repository
git clone https://gitlab.cern.ch/digitalmemory/oais-utils
cd oais-utils
pip install -e .
```

## Use

```python
from oais_utils import validate
validate("../bagit-create/bagitexport::cds::2751237")
```
