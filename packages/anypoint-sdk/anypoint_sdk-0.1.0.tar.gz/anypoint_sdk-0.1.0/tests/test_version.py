# tests/test_version.py
import importlib
import sys
import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

MODULE_PATH = "anypoint_sdk._version"
DIST_NAME = "anypoint-sdk"


def reload_version_module():
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    return importlib.import_module(MODULE_PATH)


class TestVersionModule(unittest.TestCase):
    def test_sets_real_version_when_distribution_available(self):
        with patch("importlib.metadata.version", return_value="1.2.3") as mock_version:
            mod = reload_version_module()

        self.assertEqual(mod.__version__, "1.2.3")
        mock_version.assert_called_once_with(DIST_NAME)

    def test_falls_back_to_000_when_distribution_missing(self):
        with patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError,
        ) as mock_version:
            mod = reload_version_module()

        self.assertEqual(mod.__version__, "0.0.0")
        mock_version.assert_called_once_with(DIST_NAME)
