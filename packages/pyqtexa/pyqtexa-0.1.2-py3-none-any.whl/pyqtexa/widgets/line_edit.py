from typing import Unpack, NotRequired, Callable

from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QLineEdit

from .options import Align
from .widget import WidgetKwargs, widget


class LineEditKwargs(WidgetKwargs):
    text: NotRequired[str]
    placeholderText: NotRequired[str]
    readOnly: NotRequired[bool]
    maxLength: NotRequired[int]
    echoMode: NotRequired[QLineEdit.EchoMode]
    alignment: NotRequired[Align]
    clearButtonEnabled: NotRequired[bool]
    cursorPosition: NotRequired[int]
    inputMask: NotRequired[str]
    validator: NotRequired[QValidator]
    dragEnabled: NotRequired[bool]

    onTextChanged: NotRequired[Callable[[str], None]]
    onTextEdited: NotRequired[Callable[[str], None]]
    onEditingFinished: NotRequired[Callable[[], None]]
    onReturnPressed: NotRequired[Callable[[], None]]


def lineEdit(*, _edit: QLineEdit | None = None, **kwargs: Unpack[LineEditKwargs]):
    if _edit is None:
        _edit = QLineEdit()

    # ---- QLineEdit parameters ----

    if (v := kwargs.get("text")) is not None:
        _edit.setText(v)

    if (v := kwargs.get("placeholderText")) is not None:
        _edit.setPlaceholderText(v)

    if (v := kwargs.get("readOnly")) is not None:
        _edit.setReadOnly(v)

    if (v := kwargs.get("maxLength")) is not None:
        _edit.setMaxLength(v)

    if (v := kwargs.get("echoMode")) is not None:
        _edit.setEchoMode(v)

    if (v := kwargs.get("alignment")) is not None:
        _edit.setAlignment(v)

    if (v := kwargs.get("clearButtonEnabled")) is not None:
        _edit.setClearButtonEnabled(v)

    if (v := kwargs.get("cursorPosition")) is not None:
        _edit.setCursorPosition(v)

    if (v := kwargs.get("inputMask")) is not None:
        _edit.setInputMask(v)

    if (v := kwargs.get("validator")) is not None:
        _edit.setValidator(v)

    if (v := kwargs.get("dragEnabled")) is not None:
        _edit.setDragEnabled(v)

    # -------- Handlers (explicit) ---------

    if (fn := kwargs.get("onTextChanged")) is not None:
        _edit.textChanged.connect(fn)

    if (fn := kwargs.get("onTextEdited")) is not None:
        _edit.textEdited.connect(fn)

    if (fn := kwargs.get("onEditingFinished")) is not None:
        _edit.editingFinished.connect(fn)

    if (fn := kwargs.get("onReturnPressed")) is not None:
        _edit.returnPressed.connect(fn)

    # ---- apply base QWidget params ----
    widget(**kwargs, _widget=_edit)

    return _edit
