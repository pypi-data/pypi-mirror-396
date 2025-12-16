from typing import NotRequired, Callable, Unpack

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget

from .widget import WidgetKwargs, widget


class TableWidgetKwargs(WidgetKwargs):
    rowCount: NotRequired[int]
    columnCount: NotRequired[int]
    sortingEnabled: NotRequired[bool]
    showGrid: NotRequired[bool]
    cornerButtonEnabled: NotRequired[bool]

    horizontalHeaderLabels: NotRequired[list[str]]
    verticalHeaderLabels: NotRequired[list[str]]
    columnWidths: NotRequired[dict[int, int]]
    rowHeights: NotRequired[dict[int, int]]
    hiddenColumns: NotRequired[list[int]]
    hiddenRows: NotRequired[list[int]]
    rows: NotRequired[list[list[str | QWidget]]]

    onCellClicked: NotRequired[Callable[[int, int], None]]
    onCellDoubleClicked: NotRequired[Callable[[int, int], None]]
    onCellChanged: NotRequired[Callable[[int, int], None]]
    onCurrentCellChanged: NotRequired[Callable[[int, int, int, int], None]]
    onItemClicked: NotRequired[Callable[[object], None]]
    onItemDoubleClicked: NotRequired[Callable[[object], None]]
    onItemChanged: NotRequired[Callable[[object], None]]


def table(*, _table: QTableWidget | None = None, **kwargs: Unpack[TableWidgetKwargs]):
    if _table is None:
        _table = QTableWidget()

    if (v := kwargs.get("rowCount")) is not None:
        _table.setRowCount(v)
    if (v := kwargs.get("columnCount")) is not None:
        _table.setColumnCount(v)
    if (v := kwargs.get("sortingEnabled")) is not None:
        _table.setSortingEnabled(v)
    if (v := kwargs.get("showGrid")) is not None:
        _table.setShowGrid(v)
    if (v := kwargs.get("cornerButtonEnabled")) is not None:
        _table.setCornerButtonEnabled(v)

    # Headers
    if (v := kwargs.get("horizontalHeaderLabels")) is not None:
        _table.setHorizontalHeaderLabels(v)
    if (v := kwargs.get("verticalHeaderLabels")) is not None:
        _table.setVerticalHeaderLabels(v)

    # Column widths
    if (v := kwargs.get("columnWidths")) is not None:
        for col, width in v.items():
            _table.setColumnWidth(col, width)

    # Row heights
    if (v := kwargs.get("rowHeights")) is not None:
        for row, height in v.items():
            _table.setRowHeight(row, height)

    # Hide/show rows/columns
    if (v := kwargs.get("hiddenColumns")) is not None:
        for col in v:
            _table.hideColumn(col)

    if (v := kwargs.get("hiddenRows")) is not None:
        for row in v:
            _table.hideRow(row)

    if (rows := kwargs.get("rows")) is not None:
        for r in rows:
            tableRow(_table, *r)

    # Signals
    if (fn := kwargs.get("onCellClicked")) is not None:
        _table.cellClicked.connect(fn)
    if (fn := kwargs.get("onCellDoubleClicked")) is not None:
        _table.cellDoubleClicked.connect(fn)
    if (fn := kwargs.get("onCellChanged")) is not None:
        _table.cellChanged.connect(fn)
    if (fn := kwargs.get("onCurrentCellChanged")) is not None:
        _table.currentCellChanged.connect(fn)
    if (fn := kwargs.get("onItemClicked")) is not None:
        _table.itemClicked.connect(fn)
    if (fn := kwargs.get("onItemDoubleClicked")) is not None:
        _table.itemDoubleClicked.connect(fn)
    if (fn := kwargs.get("onItemChanged")) is not None:
        _table.itemChanged.connect(fn)

    widget(**kwargs, _widget=_table)
    return _table


def tableRow(table: QTableWidget, *cells: str | QWidget, index: int | None = None):
    if index is None:
        index = table.rowCount()
    table.insertRow(index)

    for i, el in enumerate(cells):
        if isinstance(el, str):
            table.setItem(index, i, QTableWidgetItem(el))
        elif isinstance(el, QWidget):
            table.setCellWidget(index, i, el)

    return index
