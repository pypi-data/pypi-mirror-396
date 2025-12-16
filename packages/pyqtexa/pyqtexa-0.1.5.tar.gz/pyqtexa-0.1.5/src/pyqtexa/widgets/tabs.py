from typing import NotRequired, Callable, Unpack

from PyQt6.QtWidgets import QTabWidget, QWidget, QTabBar

from .widget import WidgetKwargs, widget


class TabWidgetKwargs(WidgetKwargs):
    tabsClosable: NotRequired[bool]
    movable: NotRequired[bool]
    tabPosition: NotRequired[QTabWidget.TabPosition]
    tabShape: NotRequired[QTabWidget.TabShape]
    currentIndex: NotRequired[int]

    tabBar: NotRequired[QTabBar]
    tabs: NotRequired[list[tuple[str, QWidget]]]

    # Signals
    onCurrentChanged: NotRequired[Callable[[int], None]]
    onTabCloseRequested: NotRequired[Callable[[int], None]]
    onTabBarClicked: NotRequired[Callable[[int], None]]
    onTabBarDoubleClicked: NotRequired[Callable[[int], None]]
    onTabMoved: NotRequired[Callable[[int, int], None]]


def tabs(*, _tabs: QTabWidget | None = None, **kwargs: Unpack[TabWidgetKwargs]) -> QTabWidget:
    if _tabs is None:
        _tabs = QTabWidget()

    # QTabWidget parameters
    if (v := kwargs.get("tabsClosable")) is not None:
        _tabs.setTabsClosable(v)

    if (v := kwargs.get("movable")) is not None:
        _tabs.setMovable(v)

    if (v := kwargs.get("tabPosition")) is not None:
        _tabs.setTabPosition(v)

    if (v := kwargs.get("tabShape")) is not None:
        _tabs.setTabShape(v)

    if (v := kwargs.get("currentIndex")) is not None:
        _tabs.setCurrentIndex(v)

    if (v := kwargs.get("tabBar")) is not None:
        _tabs.setTabBar(v)

    if (v := kwargs.get("tabs")) is not None:
        for label, wdg in v:
            _tabs.addTab(wdg, label)

    # Signals
    if (fn := kwargs.get("onCurrentChanged")) is not None:
        _tabs.currentChanged.connect(fn)

    if (fn := kwargs.get("onTabCloseRequested")) is not None:
        _tabs.tabCloseRequested.connect(fn)

    if (fn := kwargs.get("onTabBarClicked")) is not None:
        _tabs.tabBar().tabBarClicked.connect(fn)

    if (fn := kwargs.get("onTabBarDoubleClicked")) is not None:
        _tabs.tabBar().tabBarDoubleClicked.connect(fn)

    if (fn := kwargs.get("onTabMoved")) is not None:
        _tabs.tabBar().tabMoved.connect(fn)

    # Base QWidget parameters
    widget(**kwargs, _widget=_tabs)

    return _tabs
