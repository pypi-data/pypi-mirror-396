from typing import Unpack, NotRequired

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from .options import Align
from .widget import WidgetKwargs, widget


class LabelKwargs(WidgetKwargs):
    text: NotRequired[str]
    alignment: NotRequired[Align]
    wordWrap: NotRequired[bool]
    indent: NotRequired[int]
    margin: NotRequired[int]
    scaledContents: NotRequired[bool]
    openExternalLinks: NotRequired[bool]
    textFormat: NotRequired[Qt.TextFormat]
    pixmap: NotRequired[QPixmap]


def label(*, _label: QLabel | None = None, **kwargs: Unpack[LabelKwargs]):
    if _label is None:
        _label = QLabel()

    # ---- QLabel-specific ----
    if (v := kwargs.get("text")) is not None:
        _label.setText(v)

    if (v := kwargs.get("alignment")) is not None:
        _label.setAlignment(v)

    if (v := kwargs.get("wordWrap")) is not None:
        _label.setWordWrap(v)

    if (v := kwargs.get("indent")) is not None:
        _label.setIndent(v)

    if (v := kwargs.get("margin")) is not None:
        _label.setMargin(v)

    if (v := kwargs.get("scaledContents")) is not None:
        _label.setScaledContents(v)

    if (v := kwargs.get("openExternalLinks")) is not None:
        _label.setOpenExternalLinks(v)

    if (v := kwargs.get("textFormat")) is not None:
        _label.setTextFormat(v)

    if (v := kwargs.get("pixmap")) is not None:
        _label.setPixmap(v)

    # ---- apply base QWidget params ----
    widget(**kwargs, _widget=_label)

    return _label