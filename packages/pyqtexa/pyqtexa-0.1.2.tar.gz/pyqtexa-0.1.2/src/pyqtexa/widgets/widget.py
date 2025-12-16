from typing import NotRequired, TypedDict, Unpack, Callable
from PyQt6.QtCore import QRect, QSize, Qt, QObject, QPoint
from PyQt6.QtGui import QCursor, QFont, QPalette, QIcon
from PyQt6.QtWidgets import QWidget, QLayout, QSizePolicy


class WidgetKwargs(TypedDict):
    id: NotRequired[str]
    parent: NotRequired[QWidget]

    # SIZE
    fixedSize: NotRequired[QSize | tuple[int, int] | int]
    minimumSize: NotRequired[QSize | tuple[int, int]]
    maximumSize: NotRequired[QSize | tuple[int, int]]
    baseSize: NotRequired[QSize | tuple[int, int]]
    sizeIncrement: NotRequired[QSize | tuple[int, int]]
    sizePolicy: NotRequired[QSizePolicy]

    minimumWidth: NotRequired[int]
    minimumHeight: NotRequired[int]
    maximumWidth: NotRequired[int]
    maximumHeight: NotRequired[int]

    # GEOMETRY
    geometry: NotRequired[QRect | tuple[int, int, int, int]]
    pos: NotRequired[tuple[int, int]]
    x: NotRequired[int]
    y: NotRequired[int]
    width: NotRequired[int]
    height: NotRequired[int]

    # BEHAVIOR
    enabled: NotRequired[bool]
    disabled: NotRequired[bool]
    visible: NotRequired[bool]
    hidden: NotRequired[bool]
    updatesEnabled: NotRequired[bool]
    acceptDrops: NotRequired[bool]
    mouseTracking: NotRequired[bool]
    tabletTracking: NotRequired[bool]
    focus: NotRequired[bool]

    # LOOK
    styleSheet: NotRequired[str]
    cursor: NotRequired[QCursor]
    font: NotRequired[QFont]
    palette: NotRequired[QPalette]
    autoFillBackground: NotRequired[bool]

    # WINDOW PROPS
    windowTitle: NotRequired[str]
    windowOpacity: NotRequired[float]
    windowIconText: NotRequired[str]
    windowRole: NotRequired[str]
    windowFilePath: NotRequired[str]
    windowFlag: NotRequired[Qt.WindowType]
    windowFlags: NotRequired[Qt.WindowType]

    # LAYOUT
    layout: NotRequired[QLayout]
    contentsMargins: NotRequired[tuple[int, int, int, int]]
    layoutDirection: NotRequired[Qt.LayoutDirection]

    # INFO TEXT
    toolTip: NotRequired[str]
    statusTip: NotRequired[str]
    whatsThis: NotRequired[str]
    accessibleName: NotRequired[str]
    accessibleDescription: NotRequired[str]
    contextMenuPolicy: NotRequired[Qt.ContextMenuPolicy]

    # QWidget event handlers
    onDestroyed: NotRequired[Callable[[QObject], None]]
    onWindowTitleChanged: NotRequired[Callable[[str], None]]
    onWindowIconChanged: NotRequired[Callable[[QIcon], None]]
    onCustomContextMenuRequested: NotRequired[Callable[[QPoint], None]]


def widget(*, _widget: QWidget | None = None, **kwargs: Unpack[WidgetKwargs]):
    if _widget is None:
        _widget = QWidget()

    # OBJECT NAME
    if "id" in kwargs:
        _widget.setObjectName(kwargs["id"])

    if "parent" in kwargs:
        _widget.setParent(kwargs["parent"])

    # SIZE
    if "fixedSize" in kwargs:
        v = kwargs["fixedSize"]
        if isinstance(v, int):
            _widget.setFixedSize(v, v)
        elif isinstance(v, tuple):
            _widget.setFixedSize(*v)
        else:
            _widget.setFixedSize(v)

    if "minimumSize" in kwargs:
        v = kwargs["minimumSize"]
        _widget.setMinimumSize(*v) if isinstance(v, tuple) else _widget.setMinimumSize(v)
    if "maximumSize" in kwargs:
        v = kwargs["maximumSize"]
        _widget.setMaximumSize(*v) if isinstance(v, tuple) else _widget.setMaximumSize(v)
    if "baseSize" in kwargs:
        v = kwargs["baseSize"]
        _widget.setBaseSize(*v) if isinstance(v, tuple) else _widget.setBaseSize(v)
    if "sizeIncrement" in kwargs:
        v = kwargs["sizeIncrement"]
        _widget.setSizeIncrement(*v) if isinstance(v, tuple) else _widget.setSizeIncrement(v)
    if "sizePolicy" in kwargs:
        _widget.setSizePolicy(kwargs["sizePolicy"])

    if "minimumWidth" in kwargs:
        _widget.setMinimumWidth(kwargs["minimumWidth"])
    if "minimumHeight" in kwargs:
        _widget.setMinimumHeight(kwargs["minimumHeight"])
    if "maximumWidth" in kwargs:
        _widget.setMaximumWidth(kwargs["maximumWidth"])
    if "maximumHeight" in kwargs:
        _widget.setMaximumHeight(kwargs["maximumHeight"])

    # GEOMETRY
    if "geometry" in kwargs:
        v = kwargs["geometry"]
        _widget.setGeometry(QRect(*v)) if isinstance(v, tuple) else _widget.setGeometry(v)

    if "pos" in kwargs:
        _widget.move(*kwargs["pos"])
    if "x" in kwargs:
        _widget.move(kwargs["x"], _widget.y())
    if "y" in kwargs:
        _widget.move(_widget.x(), kwargs["y"])
    if "width" in kwargs:
        _widget.resize(kwargs["width"], _widget.height())
    if "height" in kwargs:
        _widget.resize(_widget.width(), kwargs["height"])

    # BEHAVIOR
    if "enabled" in kwargs:
        _widget.setEnabled(kwargs["enabled"])
    if "disabled" in kwargs:
        _widget.setDisabled(kwargs["disabled"])
    if "visible" in kwargs:
        _widget.setVisible(kwargs["visible"])
    if "hidden" in kwargs:
        _widget.setHidden(kwargs["hidden"])
    if "updatesEnabled" in kwargs:
        _widget.setUpdatesEnabled(kwargs["updatesEnabled"])
    if "acceptDrops" in kwargs:
        _widget.setAcceptDrops(kwargs["acceptDrops"])
    if "mouseTracking" in kwargs:
        _widget.setMouseTracking(kwargs["mouseTracking"])
    if "tabletTracking" in kwargs:
        _widget.setTabletTracking(kwargs["tabletTracking"])
    if "focus" in kwargs and kwargs["focus"]:
        _widget.setFocus()

    # LOOK
    if "styleSheet" in kwargs:
        _widget.setStyleSheet(kwargs["styleSheet"])
    if "cursor" in kwargs:
        _widget.setCursor(kwargs["cursor"])
    if "font" in kwargs:
        _widget.setFont(kwargs["font"])
    if "palette" in kwargs:
        _widget.setPalette(kwargs["palette"])
    if "autoFillBackground" in kwargs:
        _widget.setAutoFillBackground(kwargs["autoFillBackground"])

    # WINDOW PROPS
    if "windowTitle" in kwargs:
        _widget.setWindowTitle(kwargs["windowTitle"])
    if "windowOpacity" in kwargs:
        _widget.setWindowOpacity(kwargs["windowOpacity"])
    if "windowIconText" in kwargs:
        _widget.setWindowIconText(kwargs["windowIconText"])
    if "windowRole" in kwargs:
        _widget.setWindowRole(kwargs["windowRole"])
    if "windowFilePath" in kwargs:
        _widget.setWindowFilePath(kwargs["windowFilePath"])
    if "windowFlag" in kwargs:
        _widget.setWindowFlag(kwargs["windowFlag"])
    if "windowFlags" in kwargs:
        _widget.setWindowFlags(kwargs["windowFlags"])

    # LAYOUT
    if "layout" in kwargs:
        _widget.setLayout(kwargs["layout"])
    if "contentsMargins" in kwargs:
        _widget.setContentsMargins(*kwargs["contentsMargins"])
    if "layoutDirection" in kwargs:
        _widget.setLayoutDirection(kwargs["layoutDirection"])

    # TEXT INFO
    if "toolTip" in kwargs:
        _widget.setToolTip(kwargs["toolTip"])
    if "statusTip" in kwargs:
        _widget.setStatusTip(kwargs["statusTip"])
    if "whatsThis" in kwargs:
        _widget.setWhatsThis(kwargs["whatsThis"])
    if "accessibleName" in kwargs:
        _widget.setAccessibleName(kwargs["accessibleName"])
    if "accessibleDescription" in kwargs:
        _widget.setAccessibleDescription(kwargs["accessibleDescription"])
    if "contextMenuPolicy" in kwargs:
        _widget.setContextMenuPolicy(kwargs["contextMenuPolicy"])

    # ---------- EVENT HANDLERS ----------
    if (fn := kwargs.get("onDestroyed")) is not None:
        _widget.destroyed.connect(fn)
    if (fn := kwargs.get("onWindowTitleChanged")) is not None:
        _widget.windowTitleChanged.connect(fn)
    if (fn := kwargs.get("onWindowIconChanged")) is not None:
        _widget.windowIconChanged.connect(fn)
    if (fn := kwargs.get("onCustomContextMenuRequested")) is not None:
        _widget.customContextMenuRequested.connect(fn)

    return _widget
