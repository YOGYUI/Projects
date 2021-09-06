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
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QTabBar, QPushButton, QApplication, QWidget, QAction, QSplitter
from PyQt5.QtWidgets import QMenuBar, QMenu, QMessageBox
from WebPageWidget import WebPageWidget, WebView
from CustomTabWidget import CustomTabWidget
from NavigationWidget import NavigationToolBar
from BookMarkWidget import BookMarkToolBar, BookMarkManager
from ConfigUtil import WebBrowserConfig
from DeveloperWidget import DeveloperWidget
from Common import makeQAction


class WebBrowserWindow(QMainWindow):
    _mb_show_navbar: QAction
    _mb_show_bookmark: QAction
    _mb_show_devtool: QAction

    def __init__(self, parent=None, init_url: Union[str, QUrl, None] = 'about:blank'):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)

        self._bookMarkManager = BookMarkManager()
        self._config = WebBrowserConfig(self._bookMarkManager)

        self._navBar = NavigationToolBar(self)
        self._bookmarkBar = BookMarkToolBar(self._bookMarkManager, self)

        self._splitter = QSplitter(Qt.Horizontal, self)
        self._tabWidget = CustomTabWidget()
        self._devWidget = DeveloperWidget()

        self.initControl()
        self.initLayout()
        self._menuBar = QMenuBar(self)
        self.initMenuBar()
        self.setWindowTitle('YOGYUI Browser')
        self.setWindowIcon(QIcon('./Resource/application.ico'))
        if init_url is not None:
            if init_url == 'home':
                self.addWebPageTab(self._config.url_home)
            else:
                self.addWebPageTab(init_url)

    def release(self):
        self.closeWebPageAll()
        self._config.save_to_xml()

    def initLayout(self):
        self.setCentralWidget(self._splitter)
        self._splitter.addWidget(self._tabWidget)
        self._splitter.addWidget(self._devWidget)
        self._devWidget.hide()

    def initControl(self):
        self._splitter.setStyleSheet("QSplitter:handle:horizontal {background:rgb(204,206,219); margin:1px 1px}")

        self.addToolBar(Qt.TopToolBarArea, self._navBar)
        self._navBar.sig_navigate_url.connect(self.onNavBarNavitageUrl)
        self._navBar.sig_go_backward.connect(self.onNavBarGoBackward)
        self._navBar.sig_go_forward.connect(self.onNavBarGoForward)
        self._navBar.sig_reload.connect(self.onNavBarReload)
        self._navBar.sig_stop.connect(self.onNavBarStop)
        self._navBar.sig_go_home.connect(self.onNavBarGoHome)
        self._navBar.sig_toggle_bookmark.connect(self.onNavBarToggleBookmark)

        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, self._bookmarkBar)
        self._bookmarkBar.sig_navitage.connect(self.onNavBarNavitageUrl)

        self._tabWidget.sig_add_tab.connect(self.addWebPageTab)
        self._tabWidget.sig_new_window.connect(self.onTabNewWindow)
        self._tabWidget.sig_close.connect(self.onTabCloseView)
        self._tabWidget.sig_close_others.connect(self.onTabCloseViewOthers)
        self._tabWidget.sig_close_right.connect(self.onTabCloseRight)
        self._tabWidget.currentChanged.connect(self.onTabWidgetCurrentChanged)

        self._devWidget.sig_run_js.connect(self.runJavaScript)

    def initMenuBar(self):
        self.setMenuBar(self._menuBar)
        menuFile = QMenu('File', self._menuBar)
        self._menuBar.addAction(menuFile.menuAction())
        mb_close = makeQAction(parent=self, text='Close', triggered=self.close)
        menuFile.addAction(mb_close)

        menuView = QMenu('View', self._menuBar)
        self._menuBar.addAction(menuView.menuAction())
        self._mb_show_navbar = makeQAction(parent=self, text='Navigation Bar', checkable=True,
                                           triggered=self.toggleNavigationBar)
        self._mb_show_bookmark = makeQAction(parent=self, text='Bookmark Bar', checkable=True,
                                             triggered=self.toggleBookMarkBar)
        self._mb_show_devtool = makeQAction(parent=self, text='Dev Tool', checkable=True,
                                            triggered=self.toggleDevTool)
        menuView.addAction(self._mb_show_navbar)
        menuView.addAction(self._mb_show_bookmark)
        menuView.addSeparator()
        menuView.addAction(self._mb_show_devtool)
        menuView.aboutToShow.connect(self.onMenuViewAboutToShow)

        menuAbout = QMenu('About', self._menuBar)
        self._menuBar.addAction(menuAbout.menuAction())
        mb_about_page = makeQAction(parent=self, text='Page Info', triggered=self.showAboutPage)
        menuAbout.addAction(mb_about_page)

    def onMenuViewAboutToShow(self):
        self._mb_show_navbar.setChecked(self._navBar.isVisible())
        self._mb_show_bookmark.setChecked(self._bookmarkBar.isVisible())
        self._mb_show_devtool.setChecked(self._devWidget.isVisible())

    def onNavBarNavitageUrl(self, url: str):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.load(url)

    def onNavBarGoBackward(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.view().back()

    def onNavBarGoForward(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.view().forward()

    def onNavBarReload(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.view().reload()

    def onNavBarStop(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.view().stop()

    def onNavBarGoHome(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.load(self._config.url_home)

    def onNavBarToggleBookmark(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            url = curwgt.view().url().toString()
            if self._bookMarkManager.isExist(url):
                self._bookMarkManager.remove(url)
            else:
                url_icon = curwgt.view().iconUrl().toString()
                title = curwgt.view().title()
                self._bookMarkManager.add(url, title, url_icon)
            self.refreshNavBarState()

    def refreshNavBarState(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            history = curwgt.view().history()
            self._navBar.btnBackward.setEnabled(history.canGoBack())
            self._navBar.btnForward.setEnabled(history.canGoForward())

            bookmark_url_list = self._bookMarkManager.urlList()
            self._navBar.setBookMarkStatus(curwgt.view().url().toString() in bookmark_url_list)

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
        view.sig_home.connect(partial(self.goHome, view))
        view.sig_page_url.connect(partial(self.setWebPageUrl, view))
        view.sig_edit_url_focus.connect(self._navBar.setEditUrlFocused)
        view.sig_load_started.connect(partial(self.onPageLoadStarted, view))
        view.sig_load_finished.connect(partial(self.onPageLoadFinished, view))
        view.sig_js_result.connect(self.onJavaScriptResult)

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
        if title == 'about:blank':
            self._navBar.setEditUrlFocused()
        self._tabWidget.setTabText(index, title)
        self._tabWidget.setTabToolTip(index, title)

    def setWebPageIcon(self, view: WebPageWidget, icon: QIcon):
        index = self._tabWidget.indexOf(view)
        self._tabWidget.setTabIcon(index, icon)

    def setWebPageUrl(self, view: WebPageWidget, url: str):
        if self._tabWidget.currentWidget() == view:
            self._navBar.editUrl.setText(url)

    def onPageLoadStarted(self, view: WebPageWidget):
        curwgt = self._tabWidget.currentWidget()
        if curwgt == view:
            self._navBar.setIsLoading(True)
            self.refreshNavBarState()

    def onPageLoadFinished(self, view: WebPageWidget):
        curwgt = self._tabWidget.currentWidget()
        if curwgt == view:
            self._navBar.setIsLoading(False)
            self.refreshNavBarState()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.release()

    def openNewWindow(self, view: Union[WebView, None]):
        if view is None:
            newwnd = WebBrowserWindow(self)
        else:
            newwnd = WebBrowserWindow(self, init_url=None)
            newwnd.addWebPageView(view)
        newwnd.show()
        newwnd.resize(self.size())

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
        elif a0.key() == Qt.Key_H:
            if modifier == Qt.ControlModifier:
                curwgt = self._tabWidget.currentWidget()
                if isinstance(curwgt, WebPageWidget):
                    self.goHome(curwgt)
                else:
                    pass
        elif a0.key() == Qt.Key_F6:
            self._navBar.setEditUrlFocused()

    def onTabWidgetCurrentChanged(self):
        if self._tabWidget.currentIndex() == self._tabWidget.count() - 1:
            if self._tabWidget.count() > 1:
                self._tabWidget.setCurrentIndex(self._tabWidget.count() - 2)
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            self._navBar.editUrl.setText(curwgt.url().toString())
        else:
            self._navBar.editUrl.clear()

    def onTabNewWindow(self, index: int):
        widget = self._tabWidget.widget(index)
        self._tabWidget.removeTab(index)
        newwnd = WebBrowserWindow(self, init_url=None)
        if isinstance(widget, WebPageWidget):
            newwnd.addWebPageWidget(widget)
        newwnd.show()
        newwnd.resize(self.size())

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

    def goHome(self, view: WebPageWidget):
        view.load(self._config.url_home)

    def toggleNavigationBar(self):
        if self._navBar.isVisible():
            self._navBar.hide()
        else:
            self._navBar.show()

    def toggleBookMarkBar(self):
        if self._bookmarkBar.isVisible():
            self._bookmarkBar.hide()
        else:
            self._bookmarkBar.show()

    def toggleDevTool(self):
        if self._devWidget.isVisible():
            self._devWidget.hide()
        else:
            self._devWidget.show()

    def showAboutPage(self):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            page = curwgt.view().page()
            msg = f'URL: {page.url().toString()}'
            msg += f'\nTitle: {page.title()}'
            msg += f'\nIcon URL: {page.iconUrl().toString()}'
            print(msg)
            QMessageBox.information(self, 'Page Info', msg)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        w, h = self.size().width(), self.size().height()
        self._splitter.resize(w, h)

    def runJavaScript(self, script: str):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.runJavaScript(script)

    def onJavaScriptResult(self, obj: object):
        self._devWidget.setJsResult(obj)


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
