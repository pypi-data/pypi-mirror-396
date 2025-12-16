from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QMainWindow, QLayout, QWidget

from pyqtexa import widgets
from pyqtexa.widgets.scroll import scroll, ScrollAreaKwargs


class OverlayFeature:
    def __init__(self, window: QMainWindow) -> None:
        self.__window = window
        self.__modalsQueue: list[QWidget] = []

    @property
    def shown(self):
        return len(self.__modalsQueue) > 0

    def hide(self, *, every: bool = False):
        assert self.shown, "Modal not shown"
        if every:
            for widget in self.__modalsQueue:
                widget.setParent(None)
                widget.deleteLater()
        else:
            widget: QWidget = self.__modalsQueue.pop()
            widget.setParent(None)
            widget.deleteLater()

    def show(
        self, layout: QLayout, *,
        closeManually: bool = True,
        closeEvery: bool = False,
        scrollKwargs: ScrollAreaKwargs | None = None,
    ):
        root: QWidget = self.__window.centralWidget()

        overflow = scroll(
            **scrollKwargs,
            id="overlay-scrollarea",
            parent=root,
            widgetResizable=True,
            styleSheet="QScrollArea#overlay-scrollarea{ background: transparent; }",
            widget=widgets.widget(
                id="overflow",
                styleSheet="#overflow{ background-color:rgba(0,0,0,0." +
                           ("1" if len(self.__modalsQueue) >= 1 else "3") + "); }",
                layout=widgets.boxLayout(
                    alignment=widgets.Align.Center,
                    contentsMargins=(50, 50, 50, 50),
                    widgets=[
                        widgets.widget(
                            id="overflow-modal",
                            layout=layout,
                            styleSheet="#overflow-modal{ background-color: white; border-radius: 10px; }"
                        )
                    ]
                )
            ),
        )

        if closeManually:
            overflow.mousePressEvent = lambda ev: self.hide(every=closeEvery)

        overflow.move(0, 0)
        overflow.resize(root.size())

        self.__modalsQueue.append(overflow)

    def onResizeWindow(self, ev: QResizeEvent):
        if not self.shown: return
        for widget in self.__modalsQueue:
            widget.resize(ev.size())
