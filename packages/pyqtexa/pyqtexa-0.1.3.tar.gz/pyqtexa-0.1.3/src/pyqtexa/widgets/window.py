from typing import Callable, Unpack

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar, QMenuBar, QToolBar, QLayout

from .widget import WidgetKwargs, widget


class MainWindow(QMainWindow):
    def __init__(
        self,
        *,
        parent: QMainWindow | None = None,
        root: QWidget | QLayout = None,
        statusBar: QStatusBar = None,
        menuBar: QMenuBar = None,
        toolBars: list[QToolBar] = None,
        # Signals
        onWindowTitleChanged: Callable[[str], None] = None,
        onWindowIconChanged: Callable[[QIcon], None] = None,
        onIconSizeChanged: Callable[[QSize], None] = None,
        onStatusBarChanged: Callable[[QStatusBar], None] = None,
        onMenuBarChanged: Callable[[QMenuBar], None] = None,
        onToolBarAdded: Callable[[QToolBar], None] = None,
        onToolBarRemoved: Callable[[QToolBar], None] = None,
        **kwargs: Unpack[WidgetKwargs]
    ):
        super().__init__(parent=parent)

        if root is not None:
            if isinstance(root, QLayout):
                self.setLayout(root)
            if isinstance(root, QWidget):
                self.setCentralWidget(root)

        if statusBar is not None:
            self.setStatusBar(statusBar)

        if menuBar is not None:
            self.setMenuBar(menuBar)

        if toolBars:
            for tb in toolBars:
                self.addToolBar(tb)

        # ---------- Signals ----------
        if onWindowTitleChanged is not None:
            self.windowTitleChanged.connect(onWindowTitleChanged)

        if onWindowIconChanged is not None:
            self.windowIconChanged.connect(onWindowIconChanged)

        if onIconSizeChanged is not None:
            self.iconSizeChanged.connect(onIconSizeChanged)

        if onStatusBarChanged is not None:
            self.statusBarChanged.connect(onStatusBarChanged)

        if onMenuBarChanged is not None:
            self.menuBarChanged.connect(onMenuBarChanged)

        if onToolBarAdded is not None:
            self.toolBarAdded.connect(onToolBarAdded)

        if onToolBarRemoved is not None:
            self.toolBarRemoved.connect(onToolBarRemoved)

        # ---- apply base QWidget params ----
        widget(**kwargs, _widget=self)

    @classmethod
    def execute(cls):
        app = QApplication([])
        window = cls()
        window.show()
        return app.exec_()
