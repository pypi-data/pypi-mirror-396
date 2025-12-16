from typing import Unpack

from PyQt6.QtWidgets import QFrame

from .widget import WidgetKwargs, widget


def divider(vertical: bool, **kwargs: Unpack[WidgetKwargs]):
    line = QFrame()
    if vertical:
        line.setGeometry(0, 0, 3, 50)
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
    else:
        line.setGeometry(0, 0, 50, 3)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

    # ---- apply base QWidget params ----
    widget(**kwargs, _widget=line)
    return line
