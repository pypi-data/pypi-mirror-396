from typing import Unpack
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie, QImage, QPixmap

from .label import label, LabelKwargs, Align


def gifView(
    path: str,
    **extra: Unpack[LabelKwargs]
):
    container: QLabel = label(
        **extra,
        scaledContents=True,
    )
    
    movie = QMovie(path)
    container.setMovie(movie)
    movie.start()
    return container


def pictureView(
    src: str | bytes,
    **extra: Unpack[LabelKwargs]
):
    container: QLabel = label(
        **extra,
        scaledContents=True,
    )

    image = QImage()
    if isinstance(src, str):
        image.load(src)
    else:
        image.loadFromData(src)

    pixmap = QPixmap.fromImage(image)
    del image
    container.setPixmap(pixmap)

    return container
