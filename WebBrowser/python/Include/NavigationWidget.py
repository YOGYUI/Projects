# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : NavigationWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of Navigation Toolbar
# -------------------------------------------------------------------------------------------------------------------- #
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar, QToolButton, QLineEdit


class NavigationToolBar(QToolBar):
    _is_loading: bool = False

    sig_navigate_url = pyqtSignal(str)
    sig_go_backward = pyqtSignal()
    sig_go_forward = pyqtSignal()
    sig_reload = pyqtSignal()
    sig_stop = pyqtSignal()
    sig_go_home = pyqtSignal()
    sig_toggle_bookmark = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__('Navigation', parent=parent)
        self.editUrl = QLineEdit()
        self.btnBackward = QToolButton()
        self.btnForward = QToolButton()
        self.btnReload = QToolButton()
        self.btnHome = QToolButton()
        self._iconRefresh = QIcon('./Resource/reload.png')
        self._iconStop = QIcon('./Resource/cancel.png')
        self.btnBookmark = QToolButton()
        self._iconBookmarkOff = QIcon('./Resource/bookmark_off.png')
        self._iconBookmarkOn = QIcon('./Resource/bookmark_on.png')
        self.initControl()
        self.initLayout()
        stylesheet = "QToolBar {border: 0px;}"
        self.setStyleSheet(stylesheet)

    def initLayout(self):
        self.setIconSize(QSize(22, 22))
        self.addWidget(self.btnBackward)
        self.addWidget(self.btnForward)
        self.addWidget(self.btnReload)
        self.addWidget(self.btnHome)
        self.addWidget(self.editUrl)
        self.addWidget(self.btnBookmark)
        self.editUrl.setFixedHeight(24)
        font = self.editUrl.font()
        font.setPointSize(11)
        self.editUrl.setFont(font)

    def initControl(self):
        self.editUrl.returnPressed.connect(self.onEditUrlReturnPressed)
        self.btnBackward.setEnabled(False)
        self.btnBackward.clicked.connect(self.sig_go_backward.emit)
        self.btnBackward.setIcon(QIcon('./Resource/previous.png'))
        self.btnBackward.setToolTip('Previous')
        self.btnForward.setEnabled(False)
        self.btnForward.clicked.connect(self.sig_go_forward.emit)
        self.btnForward.setIcon(QIcon('./Resource/forward.png'))
        self.btnForward.setToolTip('Forward')
        self.btnReload.clicked.connect(self.onClickBtnStopRefresh)
        self.btnReload.setIcon(self._iconRefresh)
        self.btnReload.setToolTip('Reload')
        self.btnHome.clicked.connect(self.sig_go_home.emit)
        self.btnHome.setIcon(QIcon('./Resource/home.png'))
        self.btnHome.setToolTip('Home')
        self.btnBookmark.clicked.connect(self.sig_toggle_bookmark.emit)
        self.btnBookmark.setIcon(self._iconBookmarkOff)
        self.btnBookmark.setToolTip('BookMark')

    def onEditUrlReturnPressed(self):
        self.sig_navigate_url.emit(self.editUrl.text())

    def onClickBtnStopRefresh(self):
        if self._is_loading:
            self.sig_stop.emit()
        else:
            self.sig_reload.emit()

    def setEditUrlFocused(self):
        self.editUrl.setFocus()
        self.editUrl.selectAll()

    def setIsLoading(self, loading: bool):
        self._is_loading = loading
        if loading:
            self.btnReload.setIcon(self._iconStop)
        else:
            self.btnReload.setIcon(self._iconRefresh)

    def setBookMarkStatus(self, exist: bool):
        if exist:
            self.btnBookmark.setIcon(self._iconBookmarkOn)
        else:
            self.btnBookmark.setIcon(self._iconBookmarkOff)
