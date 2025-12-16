"""Tests for data_assets module"""
import unittest

from aind_metadata_utils.data_assets import (
    name_to_qc_view_link,
    name_to_metadata_view_link,
    co_id_to_co_link,
)


class TestNameToQcViewLink(unittest.TestCase):
    """Tests for name_to_qc_view_link function"""

    def test_basic_asset_name(self):
        """Test converting a basic asset name to QC view link"""
        result = name_to_qc_view_link("test-asset")
        expected = '<a href="https://qc.allenneuraldynamics-test.org/view?name=test-asset" target="_blank">QC view</a>'
        self.assertEqual(result, expected)

    def test_asset_name_with_special_characters(self):
        """Test asset name with underscores and numbers"""
        result = name_to_qc_view_link("asset_123_test")
        expected = '<a href="https://qc.allenneuraldynamics-test.org/view?name=asset_123_test" target="_blank">QC view</a>'
        self.assertEqual(result, expected)

    def test_empty_string(self):
        """Test with empty string"""
        result = name_to_qc_view_link("")
        expected = '<a href="https://qc.allenneuraldynamics-test.org/view?name=" target="_blank">QC view</a>'
        self.assertEqual(result, expected)


class TestNameToMetadataViewLink(unittest.TestCase):
    """Tests for name_to_metadata_view_link function"""

    def test_basic_asset_name(self):
        """Test converting a basic asset name to Metadata view link"""
        result = name_to_metadata_view_link("test-asset")
        expected = '<a href="https://metadata.allenneuraldynamics-test.org/view?name=test-asset" target="_blank">Metadata view</a>'
        self.assertEqual(result, expected)

    def test_asset_name_with_special_characters(self):
        """Test asset name with underscores and numbers"""
        result = name_to_metadata_view_link("asset_456_metadata")
        expected = '<a href="https://metadata.allenneuraldynamics-test.org/view?name=asset_456_metadata" target="_blank">Metadata view</a>'
        self.assertEqual(result, expected)

    def test_empty_string(self):
        """Test with empty string"""
        result = name_to_metadata_view_link("")
        expected = '<a href="https://metadata.allenneuraldynamics-test.org/view?name=" target="_blank">Metadata view</a>'
        self.assertEqual(result, expected)


class TestCoIdToCoLink(unittest.TestCase):
    """Tests for co_id_to_co_link function"""

    def test_basic_co_id(self):
        """Test converting a basic Code Ocean ID to link"""
        result = co_id_to_co_link("abc123")
        expected = '<a href="https://codeocean.allenneuraldynamics.org/data-assets/abc123" target="_blank">CO link</a>'
        self.assertEqual(result, expected)

    def test_uuid_format_id(self):
        """Test with UUID-like Code Ocean ID"""
        result = co_id_to_co_link("12345678-1234-1234-1234-123456789abc")
        expected = '<a href="https://codeocean.allenneuraldynamics.org/data-assets/12345678-1234-1234-1234-123456789abc" target="_blank">CO link</a>'
        self.assertEqual(result, expected)

    def test_empty_string(self):
        """Test with empty string"""
        result = co_id_to_co_link("")
        expected = '<a href="https://codeocean.allenneuraldynamics.org/data-assets/" target="_blank">CO link</a>'
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
