from __future__ import annotations

from unittest import mock

import ui_layout
from tests.common import DadImageToolTestCase


class UiHelperTests(DadImageToolTestCase):
    def test_open_folder_recreates_missing_folder(self) -> None:
        folder = self.root / "missing"
        with mock.patch.object(ui_layout.app, "open_path") as open_path:
            ui_layout.open_folder(folder)
        self.assertTrue(folder.is_dir())
        open_path.assert_called_once_with(folder)
