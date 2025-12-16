from typing import NotRequired, Unpack, Callable

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from .widget import WidgetKwargs, widget


class ButtonKwargs(WidgetKwargs):
    text: NotRequired[str]
    checkable: NotRequired[bool]
    checked: NotRequired[bool]
    autoDefault: NotRequired[bool]
    default: NotRequired[bool]
    flat: NotRequired[bool]
    icon: NotRequired[str]
    shortcut: NotRequired[str]

    onClicked: NotRequired[Callable[[bool], None]]
    onPressed: NotRequired[Callable[[], None]]
    onReleased: NotRequired[Callable[[], None]]
    onToggled: NotRequired[Callable[[bool], None]]


def button(*, _button: QPushButton | None = None, **kwargs: Unpack[ButtonKwargs]):
    if _button is None:
        _button = QPushButton()

    if (v := kwargs.get("text")) is not None:
        _button.setText(v)

    if (v := kwargs.get("checkable")) is not None:
        _button.setCheckable(v)

    if (v := kwargs.get("checked")) is not None:
        _button.setChecked(v)

    if (v := kwargs.get("autoDefault")) is not None:
        _button.setAutoDefault(v)

    if (v := kwargs.get("default")) is not None:
        _button.setDefault(v)

    if (v := kwargs.get("flat")) is not None:
        _button.setFlat(v)

    if (v := kwargs.get("icon")) is not None:
        _button.setIcon(QIcon(v))

    if (v := kwargs.get("shortcut")) is not None:
        _button.setShortcut(v)

    # -------- Handlers (explicit) ---------

    if (fn := kwargs.get("onClicked")) is not None:
        _button.clicked.connect(fn)

    if (fn := kwargs.get("onPressed")) is not None:
        _button.pressed.connect(fn)

    if (fn := kwargs.get("onReleased")) is not None:
        _button.released.connect(fn)

    if (fn := kwargs.get("onToggled")) is not None:
        _button.toggled.connect(fn)

    # ---- apply base QWidget params ----
    widget(**kwargs, _widget=_button)

    return _button
