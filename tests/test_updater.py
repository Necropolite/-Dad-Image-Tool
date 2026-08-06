from __future__ import annotations

import unittest
import updater


class UpdaterTests(unittest.TestCase):
    def test_version_comparison_is_strict(self) -> None:
        self.assertLess(updater._version_tuple("v0.2.0"), updater._version_tuple("0.2.1"))
        with self.assertRaises(ValueError):
            updater._version_tuple("0.2.1-beta")

