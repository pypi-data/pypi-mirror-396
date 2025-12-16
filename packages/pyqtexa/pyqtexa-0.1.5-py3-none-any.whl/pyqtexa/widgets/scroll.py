from typing import NotRequired, Unpack

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea, QFrame, QWidget

from .widget import WidgetKwargs, widget


class ScrollAreaKwargs(WidgetKwargs):
    widget: NotRequired[QWidget]
    widgetResizable: NotRequired[bool]
    horizontalScrollBar: NotRequired[bool | Qt.ScrollBarPolicy]
    verticalScrollBar: NotRequired[bool | Qt.ScrollBarPolicy]
    frameShape: NotRequired[QFrame.Shape]
    frameShadow: NotRequired[QFrame.Shadow]


def scroll(*, _scroll: QScrollArea | None = None, **kwargs: Unpack[ScrollAreaKwargs]) -> QScrollArea:
    if _scroll is None:
        _scroll = QScrollArea()

    if (v := kwargs.get("widget")) is not None:
        _scroll.setWidget(v)
    if (v := kwargs.get("widgetResizable")) is not None:
        _scroll.setWidgetResizable(v)
    if (v := kwargs.get("horizontalScrollBar")) is not None:
        _scroll.setHorizontalScrollBarPolicy(
            (Qt.ScrollBarPolicy.ScrollBarAsNeeded if v else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            if isinstance(v, bool) else v
        )
    if (v := kwargs.get("verticalScrollBar")) is not None:
        _scroll.setVerticalScrollBarPolicy(
            (Qt.ScrollBarPolicy.ScrollBarAsNeeded if v else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            if isinstance(v, bool) else v
        )
    if (v := kwargs.get("frameShape")) is not None:
        _scroll.setFrameShape(v)
    if (v := kwargs.get("frameShadow")) is not None:
        _scroll.setFrameShadow(v)

    widget(**kwargs, _widget=_scroll)
    return _scroll
