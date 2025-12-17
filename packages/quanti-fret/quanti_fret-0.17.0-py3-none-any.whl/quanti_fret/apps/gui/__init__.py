from quanti_fret.apps.gui.phases import CalibrationWidget, FretWidget
from quanti_fret.apps.gui.popup import PopUpManager  # noqa: F401
from quanti_fret.apps.gui.utils import VersionLabel  # noqa: F401

from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices
from qtpy.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class QtfMainWidget(QWidget):
    """ Top level widget for QuanTI-FRET Gui application.

    Can be called inside a window, or passed to Napari.
    """
    def __init__(self, *args, **kwargs) -> None:
        """Constructor
        """
        super().__init__(*args, **kwargs)

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._buildStagesTab()
        self._buildFooter()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def _buildStagesTab(self) -> None:
        """Create the tab widget that will host the different stages of the
        QuanTI-FRET process.
        """
        # Create Tab Widget
        operations = QTabWidget(self)
        operations.setDocumentMode(True)
        tabBar = operations.tabBar()
        assert tabBar is not None
        tabBar.setExpanding(True)
        self._layout.addWidget(operations)  # type: ignore

        # Add Calibration Operation tab
        calibrationWidget = CalibrationWidget(parent=tabBar)
        operations.addTab(calibrationWidget, 'Calibration')

        # Add Fret Operation tab
        fretWidget = FretWidget(parent=tabBar)
        operations.addTab(fretWidget, 'Fret')

    def _buildFooter(self) -> None:
        """ Build the footer with the doc button and the version
        """
        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(5, 0, 10, 5)
        footerLayout.setSpacing(0)
        self._layout.addLayout(footerLayout)

        doc = QPushButton('Documentation')
        # doc.setEnabled(False)
        doc.adjustSize()
        doc.setToolTip('Open the online documentation in your browser.')
        doc.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        doc.clicked.connect(self._openDoc)
        footerLayout.addWidget(doc)

        version = VersionLabel()
        footerLayout.addWidget(version)

    def _openDoc(self):
        """ Open the documentation in a browser.
        """
        QDesktopServices.openUrl(QUrl(
            'https://liphy.gricad-pages.univ-grenoble-alpes.fr/quanti-fret/'
        ))


__ALL__ = [
    'PopUpManager',
    'QtfMainWidget',
]
