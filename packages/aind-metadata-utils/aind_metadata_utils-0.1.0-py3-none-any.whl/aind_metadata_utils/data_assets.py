"""Utility functions for data asset IDs/names"""


def name_to_qc_view_link(asset_name: str) -> str:
    """Convert a data asset name to a QC view HTML link."""
    return f'<a href="https://qc.allenneuraldynamics-test.org/view?name={asset_name}" target="_blank">QC view</a>'


def name_to_metadata_view_link(asset_name: str) -> str:
    """Convert a data asset name to a Metadata view HTML link."""
    return f'<a href="https://metadata.allenneuraldynamics-test.org/view?name={asset_name}" target="_blank">Metadata view</a>'


def co_id_to_co_link(co_id: str) -> str:
    """Convert a Code Ocean ID to a Code Ocean HTML link."""
    return f'<a href="https://codeocean.allenneuraldynamics.org/data-assets/{co_id}" target="_blank">CO link</a>'
