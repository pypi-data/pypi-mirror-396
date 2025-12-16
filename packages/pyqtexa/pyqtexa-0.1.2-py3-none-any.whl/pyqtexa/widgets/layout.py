from typing import TypedDict, NotRequired, Unpack

from PyQt6.QtWidgets import QWidget, QBoxLayout, QLayout

from .options import Align

LayoutDirection = QBoxLayout.Direction


class BoxLayoutKwargs(TypedDict):
    spacing: NotRequired[int]
    contentsMargins: NotRequired[tuple[int, int, int, int]]  # left, top, right, bottom
    alignment: NotRequired[Align]
    direction: NotRequired[LayoutDirection]
    sizeConstraint: NotRequired[QLayout.SizeConstraint]
    stretchFactors: NotRequired[dict[int, int]]  # (index, stretch)
    widgets: NotRequired[list[QWidget]]


def boxLayout(*, _layout: QBoxLayout | None = None, **kwargs: Unpack[BoxLayoutKwargs]):
    if _layout is None:
        _layout = QBoxLayout(kwargs.get("direction") or LayoutDirection.TopToBottom)
    elif (v := kwargs.get("direction")) is not None:
        _layout.setDirection(v)

    if (v := kwargs.get("spacing")) is not None:
        _layout.setSpacing(v)

    if (v := kwargs.get("contentsMargins")) is not None:
        _layout.setContentsMargins(*v)

    if (v := kwargs.get("sizeConstraint")) is not None:
        _layout.setSizeConstraint(v)

    alignment = kwargs.get("alignment")

    if (widgets := kwargs.get("widgets")) is not None:
        for w, align in widgets:
            _layout.addWidget(w, alignment=alignment)

    if (v := kwargs.get("stretchFactors")) is not None:
        for index, stretch in v.items():
            _layout.setStretch(index, stretch)

    return _layout
