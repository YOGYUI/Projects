# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : WebBrowserWindow.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of web browser window
# -------------------------------------------------------------------------------------------------------------------- #
import os
from typing import Union, List
from functools import partial
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QTabBar, QPushButton, QApplication, QWidget
from .WebPageWidget import WebPageWidget, WebView
from .CustomTabWidget import CustomTabWidget


class WebBrowserWindow(QMainWindow):
    def __init__(self, parent=None, init_url: Union[str, QUrl, None] = 'about:blank'):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)
        self._tabWidget = CustomTabWidget()
        self.initControl()
        self.initLayout()
        self.setWindowTitle('YOGYUI Browser')
        self.setWindowIcon(QIcon('./Resource/application.ico'))
        if init_url is not None:
            self.addWebPageTab(init_url)

    def release(self):
        self.closeWebPageAll()

    def initLayout(self):
        self.setCentralWidget(self._tabWidget)

    def initControl(self):
        self._tabWidget.sig_add_tab.connect(self.addWebPageTab)
        self._tabWidget.sig_new_window.connect(self.onTabNewWindow)
        self._tabWidget.sig_close.connect(self.onTabCloseView)
        self._tabWidget.sig_close_others.connect(self.onTabCloseViewOthers)
        self._tabWidget.sig_close_right.connect(self.onTabCloseRight)
        self._tabWidget.currentChanged.connect(self.onTabWidgetCurrentChanged)
        """
        # add "add tab view" button
        btn = QPushButton()
        btn.setIcon(QIcon('./Resource/add.png'))
        btn.setFlat(True)
        btn.clicked.connect(lambda: self.addWebPageTab())
        self._tabWidget.setCornerWidget(btn)
        """

    def addWebPageTab(self, url: Union[str, QUrl] = 'about:blank'):
        view = WebPageWidget(parent=self, url=url)
        self.setWebPageViewSignals(view)
        self.addTabCommon(view)

    def addWebPageView(self, view: Union[WebView, None]):
        if view is None:
            widget = WebPageWidget(parent=self)
        else:
            widget = WebPageWidget(parent=self, view=view)
        self.setWebPageViewSignals(widget)
        self.addTabCommon(widget)

    def addWebPageWidget(self, widget: WebPageWidget):
        self.setWebPageViewSignals(widget)
        self.addTabCommon(widget)

    def setWebPageViewSignals(self, view: WebPageWidget):
        view.sig_page_title.connect(partial(self.setWebPageTitle, view))
        view.sig_page_icon.connect(partial(self.setWebPageIcon, view))
        view.sig_new_tab.connect(self.addWebPageView)
        view.sig_new_window.connect(self.openNewWindow)
        view.sig_close.connect(partial(self.closeWebPageTab, view))

    def addTabCommon(self, widget: WebPageWidget):
        index = self._tabWidget.count() - 1
        title = widget.view().title()
        if len(title) == 0:
            title = 'Empty'
        self._tabWidget.insertTab(index, widget, title)
        # add close button in tab
        index = self._tabWidget.indexOf(widget)
        btn = QPushButton()
        btn.setIcon(QIcon('./Resource/close.png'))
        btn.setFlat(True)
        btn.setFixedSize(16, 16)
        btn.setIconSize(QSize(14, 14))
        btn.clicked.connect(partial(self.closeWebPageTab, widget))
        self._tabWidget.tabBar().setTabButton(index, QTabBar.RightSide, btn)
        self._tabWidget.setCurrentIndex(index)

    def closeWebPageTab(self, view: QWidget):
        if isinstance(view, WebPageWidget):
            index = self._tabWidget.indexOf(view)
            self._tabWidget.removeTab(index)
            view.release()

    def closeWebPageTabs(self, views: List[QWidget]):
        for view in views:
            self.closeWebPageTab(view)

    def closeWebPageAll(self):
        views = [self._tabWidget.widget(i) for i in range(self._tabWidget.count())]
        for view in views:
            idx = self._tabWidget.indexOf(view)
            if isinstance(view, WebPageWidget):
                self._tabWidget.removeTab(idx)
                view.release()

    def setWebPageTitle(self, view: WebPageWidget, title: str):
        index = self._tabWidget.indexOf(view)
        self._tabWidget.setTabText(index, title)
        self._tabWidget.setTabToolTip(index, title)

    def setWebPageIcon(self, view: WebPageWidget, icon: QIcon):
        index = self._tabWidget.indexOf(view)
        self._tabWidget.setTabIcon(index, icon)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.release()

    def openNewWindow(self, view: Union[WebView, None]):
        if view is None:
            newwnd = WebBrowserWindow(self)
        else:
            newwnd = WebBrowserWindow(self, init_url=None)
            newwnd.addWebPageView(view)
        newwnd.show()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        modifier = QApplication.keyboardModifiers()
        if a0.key() == Qt.Key_N:
            if modifier == Qt.ControlModifier:
                self.openNewWindow(None)
        elif a0.key() == Qt.Key_T:
            if modifier == Qt.ControlModifier:
                self.addWebPageTab()
        elif a0.key() == Qt.Key_W:
            if modifier == Qt.ControlModifier:
                curwgt = self._tabWidget.currentWidget()
                self.closeWebPageTab(curwgt)

    def onTabWidgetCurrentChanged(self):
        if self._tabWidget.currentIndex() == self._tabWidget.count() - 1:
            if self._tabWidget.count() > 1:
                self._tabWidget.setCurrentIndex(self._tabWidget.count() - 2)

    def onTabNewWindow(self, index: int):
        widget = self._tabWidget.widget(index)
        self._tabWidget.removeTab(index)
        newwnd = WebBrowserWindow(self, init_url=None)
        if isinstance(widget, WebPageWidget):
            newwnd.addWebPageWidget(widget)
        newwnd.show()

    def onTabCloseView(self, index: int):
        view = self._tabWidget.widget(index)
        self.closeWebPageTab(view)

    def onTabCloseViewOthers(self, index: int):
        view = self._tabWidget.widget(index)
        lst = []
        for i in range(self._tabWidget.count()):
            wgt = self._tabWidget.widget(i)
            if wgt != view:
                lst.append(wgt)
        self.closeWebPageTabs(lst)

    def onTabCloseRight(self, index: int):
        lst = []
        for i in range(index + 1, self._tabWidget.count()):
            wgt = self._tabWidget.widget(i)
            lst.append(wgt)
        self.closeWebPageTabs(lst)


if __name__ == '__main__':
    import sys
    from PyQt5.QtCore import QCoreApplication

    QApplication.setStyle('fusion')
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    wnd_ = WebBrowserWindow()
    wnd_.show()
    wnd_.resize(600, 600)

    app.exec_()
