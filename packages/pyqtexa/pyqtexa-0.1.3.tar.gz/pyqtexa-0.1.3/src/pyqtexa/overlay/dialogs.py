from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog


def getMainWindow() -> QMainWindow | None:
    # Global function to find the (open) QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


def openFileDialog(*,
    title: str | None = None,
    initial: str | None = None,
    filter: str | None = None,
    multiple: bool = False
) -> str | list[str] | None:
    parent = getMainWindow()
    if not parent: return

    if multiple:
        return QFileDialog.getOpenFileNames(
            parent=parent,
            caption=title,
            directory=initial,
            filter=filter
        )[0]

    return QFileDialog.getOpenFileName(
        parent=parent,
        caption=title,
        directory=initial,
        filter=filter
    )[0]


def openDirDialog(*,
    title: str | None = None,
    initial: str | None = None,
):
    parent = getMainWindow()
    if not parent: return

    return QFileDialog.getExistingDirectory(
        parent=parent,
        caption=title,
        directory=initial,
    )
