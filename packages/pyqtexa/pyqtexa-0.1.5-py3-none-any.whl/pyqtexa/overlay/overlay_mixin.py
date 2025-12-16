from abc import ABC, abstractmethod

from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QMainWindow, QLayout

from .overlay_feature import OverlayFeature
from pyqtexa import widgets
from pyqtexa.widgets.scroll import ScrollAreaKwargs


class OverlayModal(ABC):

    def __init__(self) -> None:
        assert isinstance(self, QLayout), "Mixin must be extends from QLayout"

    @abstractmethod
    def overlaySignal(self, **kwargs):
        pass

    def hide(self, *, every: bool = False):
        mixin: 'OverlayMixin' = self.window
        mixin.hideModal(every=every)


class OverlayMixin:
    def __init__(self) -> None:
        assert isinstance(self, QMainWindow), "Mixin must be extends from QMainWindow"
        self.overlayFeature = OverlayFeature(self)

    def showModal(
        self,
        content: QLayout | type[OverlayModal] | OverlayModal, *,
        closeManually: bool = True,
        closeEvery: bool = False,
        scrollKwargs: ScrollAreaKwargs | None = None,
        signal: dict = None
    ):
        if isinstance(content, type(OverlayModal)):
            content = content(self)
        if isinstance(content, OverlayModal) and signal:
            content.overlaySignal(**signal)

        self.overlayFeature.show(
            content,
            closeManually=closeManually,
            closeEvery=closeEvery,
            scrollKwargs=scrollKwargs,
        )

    def hideModal(self, *, every: bool = False):
        self.overlayFeature.hide(every=every)

    def showTextPopup(self, text: str, *, okayText: str = "OK"):
        self.showModal(
            widgets.boxLayout(
                widgets=[
                    widgets.label(text=text),
                    widgets.button(text=okayText, onClicked= lambda _: self.hideModal())
                ]
            )
        )

    @property
    def overlayShown(self):
        return self.overlayFeature.shown

    def resizeEvent(self, event: QResizeEvent):
        super(QMainWindow, self).resizeEvent(event)
        if self.overlayFeature.shown:
            self.overlayFeature.onResizeWindow(event)
