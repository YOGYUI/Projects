# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : BookMarkWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Browser Bookmark Widget
# -------------------------------------------------------------------------------------------------------------------- #
import urllib.request
from typing import List
from functools import partial
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolBar, QToolButton


class BookMarkItem:
    def __init__(self, url: str, title: str, icon_url: str):
        self.url = url
        self.title = title
        self.icon_url = icon_url


class BookMarkManager(QObject):
    sig_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.bookmarks: List[BookMarkItem] = list()

    def urlList(self) -> List[str]:
        return [x.url for x in self.bookmarks]

    def isExist(self, url: str):
        return url in self.urlList()

    def add(self, url: str, title: str, icon_url: str):
        self.bookmarks.append(BookMarkItem(url, title, icon_url))
        self.sig_changed.emit()

    def remove(self, url: str):
        find = list(filter(lambda x: x.url == url, self.bookmarks))
        if len(find) >= 1:
            self.bookmarks.remove(find[0])
        self.sig_changed.emit()


class BookMarkToolBar(QToolBar):
    sig_navitage = pyqtSignal(str)

    def __init__(self, manager: BookMarkManager, parent=None):
        super().__init__('Bookmark', parent=parent)
        stylesheet = "QToolBar {border: 0px; spacing: 0px;}"
        self.setStyleSheet(stylesheet)
        self._manager = manager
        self._manager.sig_changed.connect(self.drawItems)

        self.setIconSize(QSize(18, 18))
        self.drawItems()

    def drawItems(self):
        self.clear()
        for item in self._manager.bookmarks:
            try:
                data = urllib.request.urlopen(item.icon_url).read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                icon = QIcon(pixmap)

                btn = QToolButton()
                btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                btn.setIcon(icon)
                btn.setText(item.title)
                btn.setToolTip(item.title)
                btn.clicked.connect(partial(self.sig_navitage.emit, item.url))

                self.addWidget(btn)
            except Exception:
                pass
