from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QIntValidator


class Align:
    Default = Left = Qt.AlignmentFlag.AlignLeft
    Leading = Qt.AlignmentFlag.AlignLeading
    Right = Qt.AlignmentFlag.AlignRight
    Trailing = Qt.AlignmentFlag.AlignTrailing
    HCenter = Qt.AlignmentFlag.AlignHCenter
    Justify = Qt.AlignmentFlag.AlignJustify
    Absolute = Qt.AlignmentFlag.AlignAbsolute
    Horizontal_Mask = Qt.AlignmentFlag.AlignHorizontal_Mask
    Top = Qt.AlignmentFlag.AlignTop
    Bottom = Qt.AlignmentFlag.AlignBottom
    VCenter = Qt.AlignmentFlag.AlignVCenter
    Vertical_Mask = Qt.AlignmentFlag.AlignVertical_Mask
    Center = Qt.AlignmentFlag.AlignCenter
    Baseline = Qt.AlignmentFlag.AlignBaseline


def numericLimitRule(*, double: bool = False, start: float = 0, end: float = None):
    val = QDoubleValidator() if double else QIntValidator()
    if start is not None: val.setBottom(start)
    if end is not None: val.setTop(end)
    return val
