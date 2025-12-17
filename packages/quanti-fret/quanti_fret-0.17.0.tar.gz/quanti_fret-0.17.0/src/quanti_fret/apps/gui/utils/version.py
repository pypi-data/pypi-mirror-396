from quanti_fret import __version__ as qtf_version

import time

from PyQt6.QtGui import QMouseEvent
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QLabel, QMessageBox


class VersionLabel(QLabel):
    """ Label displaying the app version
    """
    clicked = Signal()

    def __init__(self, *args, **kwargs) -> None:
        """ Constructor
        """
        super().__init__(f'Version: {qtf_version}', *args, **kwargs)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet('VersionLabel {color: gray;}')
        self._last_click = 0.
        self._click_count = 0

    def mousePressEvent(self, ev: QMouseEvent | None) -> None:
        """ Handle a press event

        Args:
            ev (QMouseEvent | None): Event
        """
        t = time.time()
        if t - self._last_click <= 0.5:
            self._click_count += 1
            if self._click_count >= 2:
                self._click_count = 0
                QMessageBox.information(
                    self,
                    ":)",
                    "Thank you for using QuanTI-FRET!!!"
                )
        else:
            self._click_count = 0

        self._last_click = t
        super().mousePressEvent(ev)
