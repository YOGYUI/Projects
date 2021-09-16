# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : BookMarkWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Browser Bookmark Widget
# TODO: 모든 열린 window 동기화
# -------------------------------------------------------------------------------------------------------------------- #
import urllib.request
from typing import List
from functools import partial
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QObject
from PyQt5.QtGui import QIcon, QPixmap, QContextMenuEvent
from PyQt5.QtWidgets import QToolBar, QToolButton, QMenu, QDialog, QLineEdit, QPushButton, QVBoxLayout, QApplication
from Common import makeQAction


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

    def addBookMark(self, url: str, title: str, icon_url: str):
        self.bookmarks.append(BookMarkItem(url, title, icon_url))
        self.sig_changed.emit()

    def removeBookMark(self, url: str):
        find = list(filter(lambda x: x.url == url, self.bookmarks))
        if len(find) >= 1:
            self.bookmarks.remove(find[0])
        self.sig_changed.emit()

    def renameBookMark(self, index: int, title: str):
        self.bookmarks[index].title = title
        self.sig_changed.emit()


class RenameDialog(QDialog):
    sig_rename = pyqtSignal(str)

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.editTitle = QLineEdit(title)
        self.editTitle.selectAll()
        btn = QPushButton('Modify')
        btn.clicked.connect(self.onClickBtn)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)
        vbox.addWidget(self.editTitle)
        vbox.addWidget(btn)

        self.setWindowTitle('Rename')

    def onClickBtn(self):
        self.close()
        self.sig_rename.emit(self.editTitle.text())


class BookMarkToolBar(QToolBar):
    sig_navitage = pyqtSignal(str)
    sig_toggle_show = pyqtSignal()
    sig_open_tab = pyqtSignal(str)
    sig_open_window = pyqtSignal(str)
    sig_item_changed = pyqtSignal()

    def __init__(self, manager: BookMarkManager, parent=None):
        super().__init__('Bookmark', parent=parent)
        stylesheet = "QToolBar {border: 0px; spacing: 0px;}"
        self.setStyleSheet(stylesheet)
        self._manager = manager
        self._manager.sig_changed.connect(lambda: self.drawItems(True))
        self._action_list = list()

        self.setIconSize(QSize(18, 18))
        self.drawItems()

    def drawItems(self, notify: bool = False):
        if notify:
            self.sig_item_changed.emit()
        self.clear()
        self._action_list.clear()
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
                btn.clicked.connect(partial(self.onClickBookMarkButton, item.url))

                action = self.addWidget(btn)
                self._action_list.append(action)
            except Exception:
                pass

    def contextMenuEvent(self, a0: QContextMenuEvent) -> None:
        menu = QMenu(self)
        action = self.actionAt(a0.pos())
        # self.action

        if action is not None:
            find = list(filter(lambda x: x == action, self._action_list))
            if len(find) == 1:
                idx = self._action_list.index(find[0])
                url = self._manager.bookmarks[idx].url
                menuOpenTab = makeQAction(parent=self, text='Open in New Tab',
                                          triggered=lambda: self.sig_open_tab.emit(url))
                menu.addAction(menuOpenTab)
                menuOpenWindow = makeQAction(parent=self, text='Open in New Window',
                                             triggered=lambda: self.sig_open_window.emit(url))
                menu.addAction(menuOpenWindow)
                menu.addSeparator()
                menuRename = makeQAction(parent=self, text='Rename',
                                         triggered=lambda: self.renameTitle(idx))
                menu.addAction(menuRename)
                menu.addSeparator()
                menuRemove = makeQAction(parent=self, text='Remove',
                                         triggered=lambda: self._manager.removeBookMark(url))
                menu.addAction(menuRemove)
        else:
            menuOpenAll = makeQAction(parent=self, text='Open All',
                                      triggered=self.openAllBookmarks)
            menu.addAction(menuOpenAll)
        menu.addSeparator()
        menuShowBookmark = makeQAction(parent=self, text='Show BookMark Bar', triggered=self.sig_toggle_show.emit,
                                       checkable=True, checked=self.isVisible())
        menu.addAction(menuShowBookmark)
        menu.exec(a0.globalPos())

    def renameTitle(self, index: int):
        curtitle = self._manager.bookmarks[index].title
        dlg = RenameDialog(curtitle, self)
        dlg.sig_rename.connect(lambda x: self._manager.renameBookMark(index, x))
        dlg.exec()

    def openAllBookmarks(self):
        for item in self._manager.bookmarks:
            self.sig_open_tab.emit(item.url)

    def onClickBookMarkButton(self, url: str):
        modifier = QApplication.keyboardModifiers()
        if modifier == Qt.ControlModifier:
            self.sig_open_tab.emit(url)
        else:
            self.sig_navitage.emit(url)
