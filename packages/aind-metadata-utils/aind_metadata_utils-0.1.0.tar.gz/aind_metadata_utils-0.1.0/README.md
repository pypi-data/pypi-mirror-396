# aind-metadata-utils

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/python->=3.10-blue?logo=python)

## Usage

```{bash}
pip install aind-metadata-utils
```

### Examples

```python
from aind_metadata_utils.data_assets import name_to_qc_view_link, name_to_metadata_view_link, co_id_to_co_link

# Convert a data asset name to a QC view HTML link
qc_link = name_to_qc_view_link("my-asset-name")
# Returns: '<a href="https://qc.allenneuraldynamics-test.org/view?name=my-asset-name" target="_blank">QC view</a>'

# Convert a data asset name to a Metadata view HTML link
metadata_link = name_to_metadata_view_link("my-asset-name")
# Returns: '<a href="https://metadata.allenneuraldynamics-test.org/view?name=my-asset-name" target="_blank">Metadata view</a>'

# Convert a Code Ocean ID to a Code Ocean HTML link
co_link = co_id_to_co_link("abc123-def456")
# Returns: '<a href="https://codeocean.allenneuraldynamics.org/data-assets/abc123-def456" target="_blank">CO link</a>'
```

## Level of Support
Please indicate a level of support:
 - [X] Supported: We are releasing this code to the public as a tool we expect others to use. Issues are welcomed, and we expect to address them promptly; pull requests will be vetted by our staff before inclusion.
