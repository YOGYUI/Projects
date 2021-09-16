# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : WebBrowserWindow.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of web browser window
# -------------------------------------------------------------------------------------------------------------------- #
import os
import pyautogui
from typing import Union, List
from functools import partial
from datetime import datetime
from multiprocessing.connection import Listener
from PyQt5.QtCore import Qt, QSize, QUrl, QPoint
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QTabBar, QPushButton, QApplication, QWidget, QAction, QSplitter
from PyQt5.QtWidgets import QMenuBar, QMenu, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from WebPageWidget import WebPageWidget, WebView
from CustomTabWidget import CustomTabWidget
from NavigationWidget import NavigationToolBar
from BookMarkWidget import BookMarkToolBar, BookMarkManager
from ConfigUtil import WebBrowserConfig
from DeveloperWidget import DeveloperWidget
from Common import makeQAction, ensurePathExist, writeLog
from Util import ThreadBlogAdClick, BlogAdClickParams, ThreadSocketListener, ThreadSocketClient


class WebBrowserWindow(QMainWindow):
    _mb_show_navbar: QAction
    _mb_show_bookmark: QAction
    _mb_show_devtool: QAction

    _sock_listener: Union[Listener, None] = None

    _threadBlogAdClick: Union[ThreadBlogAdClick, None] = None
    _threadSocketListener: Union[ThreadSocketListener, None] = None
    _threadSocketClient: Union[ThreadSocketClient, None] = None

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
        self._devWidget = DeveloperWidget(self._config)

        # self.initSocket()

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
        # self.releaseSocket()
        self.stopThreadBlogAdClick()
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
        self._bookmarkBar.sig_open_tab.connect(self.addWebPageTab)
        self._bookmarkBar.sig_open_window.connect(self.openNewWindowUrl)
        self._bookmarkBar.sig_toggle_show.connect(self.toggleBookMarkBar)
        self._bookmarkBar.sig_item_changed.connect(self.onBookMarkBarChanged)

        self._tabWidget.sig_add_tab.connect(self.addWebPageTab)
        self._tabWidget.sig_new_window.connect(self.onTabNewWindow)
        self._tabWidget.sig_close.connect(self.onTabCloseView)
        self._tabWidget.sig_close_others.connect(self.onTabCloseViewOthers)
        self._tabWidget.sig_close_right.connect(self.onTabCloseRight)
        self._tabWidget.currentChanged.connect(self.onTabWidgetCurrentChanged)

        self._devWidget.sig_run_js.connect(self.runJavaScript)
        self._devWidget.sig_start_blog_ad_click.connect(self.startThreadBlogAdClick)
        self._devWidget.sig_stop_blog_ad_click.connect(self.stopThreadBlogAdClick)

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
        else:
            if self._tabWidget.count() == 1:
                self.addWebPageTab(url)

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
                self._bookMarkManager.removeBookMark(url)
            else:
                url_icon = curwgt.view().iconUrl().toString()
                title = curwgt.view().title()
                self._bookMarkManager.addBookMark(url, title, url_icon)
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
        view.sig_dev_tool.connect(self.toggleDevTool)
        view.sig_edit_url_focus.connect(self._navBar.setEditUrlFocused)
        view.sig_load_started.connect(partial(self.onPageLoadStarted, view))
        view.sig_load_finished.connect(partial(self.onPageLoadFinished, view))
        view.sig_js_result.connect(self.onJavaScriptResult)
        view.sig_js_console_msg.connect(self.onPageJavaScriptConsoleMessage)
        view.sig_key_escape.connect(self.onPressKeyEscape)

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

    def setWebPageUrl(self, view: WebPageWidget, url: Union[str, QUrl]):
        if self._tabWidget.currentWidget() == view:
            if isinstance(url, QUrl):
                url = url.toString()
            self._navBar.editUrl.setText(url)

    def onPageLoadStarted(self, view: WebPageWidget, url: str):
        curwgt = self._tabWidget.currentWidget()
        if curwgt == view:
            self._navBar.setIsLoading(True)
            self._navBar.editUrl.setText(url)
            self.refreshNavBarState()

    def onPageLoadFinished(self, view: WebPageWidget, result: bool):
        curwgt = self._tabWidget.currentWidget()
        if curwgt == view:
            self.setWebPageUrl(view, view.url())
            if not result:
                self.setWebPageIcon(view, QIcon('./Resource/warning.png'))
            self._navBar.setIsLoading(False)
            self.refreshNavBarState()
        if self._threadBlogAdClick is not None:
            self._threadBlogAdClick.setVisitDone()

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

    def openNewWindowUrl(self, url: str):
        newwnd = WebBrowserWindow(self, init_url=url)
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
        elif a0.key() == Qt.Key_D:
            if modifier == Qt.ControlModifier:
                self.toggleDevTool()
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
        self.refreshNavBarState()

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
        if self._threadBlogAdClick is not None:
            self._threadBlogAdClick.setJavaScriptResult(obj)

    def onPageJavaScriptConsoleMessage(self, level, message: str, lineNumber: int, sourceID: str):
        print(level, message, lineNumber, sourceID)

    def onPressKeyEscape(self):
        self.stopThreadBlogAdClick()

    def onBookMarkBarChanged(self):
        self.sendToServer(self._bookMarkManager.bookmarks)

    def deleteAllCookies(self):
        QWebEngineProfile().defaultProfile().cookieStore().deleteAllCookies()
        writeLog('Delete All Cookies', self)

    ####################################################################################################################
    def startThreadBlogAdClick(self, params: BlogAdClickParams):
        self.setWindowState(Qt.WindowMaximized)
        self.closeWebPageAll()
        self.addWebPageTab()
        self._devWidget.hide()
        if self._threadBlogAdClick is None:
            self._threadBlogAdClick = ThreadBlogAdClick(params, self)
            self._threadBlogAdClick.sig_started.connect(self.onThreadBlogAdClickStarted)
            self._threadBlogAdClick.sig_terminated.connect(self.onThreadBlogAdClickTerminated)
            self._threadBlogAdClick.sig_visit.connect(self.onThreadBlogAdClickVisit)
            self._threadBlogAdClick.sig_run_js.connect(self.onThreadBlogAdClickRunJS)
            self._threadBlogAdClick.sig_exception.connect(self.onThreadBlogAdClickException)
            self._threadBlogAdClick.sig_close_tab.connect(self.onThreadBlogAdClickCloseTab)
            self._threadBlogAdClick.sig_mouse_move.connect(self.onThreadBlogAdClickMouseMove)
            self._threadBlogAdClick.sig_check_ad_open.connect(self.onThreadBlogAdClickCheckAdOpen)
            self._threadBlogAdClick.sig_delete_cookies.connect(self.deleteAllCookies)
            self._threadBlogAdClick.start()

    def stopThreadBlogAdClick(self):
        if self._threadBlogAdClick is not None:
            self._threadBlogAdClick.stop()

    def onThreadBlogAdClickStarted(self):
        self._devWidget.btnStartBlogAdClick.setEnabled(False)
        self._devWidget.btnStopBlogAdClick.setEnabled(True)

    def onThreadBlogAdClickTerminated(
            self,
            tm_start: datetime,
            tm_finish: datetime,
            visit_cnt: int,
            result: list,
            avg_visit_time: float
    ):
        del self._threadBlogAdClick
        self._threadBlogAdClick = None
        self._devWidget.btnStartBlogAdClick.setEnabled(True)
        self._devWidget.btnStopBlogAdClick.setEnabled(False)
        self.closeWebPageAll()

        if len(result) > 0:
            msg = ''
            for item in result:
                head = item.get('head')
                visit = item.get('visit')
                success = item.get('success')
                skip = item.get('skip')
                msg += f'[{head}] {success}/{visit} (Skip={skip})\n'
            QMessageBox.information(self, 'Blog Ad Click Result', msg)

        curpath = os.path.dirname(os.path.abspath(__file__))
        logpath = os.path.join(os.path.dirname(curpath), 'Log')
        ensurePathExist(logpath)
        logfilepath = os.path.join(logpath, 'BlogAdClick.log')
        with open(logfilepath, 'a') as fp:
            fp.write('<{}> ~ <{}>\n'.format(tm_start.strftime('%Y%m%d-%H:%M:%S'),
                                            tm_finish.strftime('%Y%m%d-%H:%M:%S')))
            fp.write(f'Total URL Visit: {visit_cnt}\n')
            fp.write(f'Average Visit Time per Site (sec): {avg_visit_time}\n')
            for item in result:
                head = item.get('head')
                visit = item.get('visit')
                success = item.get('success')
                skip = item.get('skip')
                fp.write('  [{:8s}] Try:{}, Success:{}, Skip:{}\n'.format(head, visit, success, skip))
            fp.write('\n')

    def onThreadBlogAdClickVisit(self, url: str):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            curwgt.load(url)

    def onThreadBlogAdClickRunJS(self, script: str):
        self.runJavaScript(script)

    def onThreadBlogAdClickException(self, message: str):
        QMessageBox.warning(self, 'Blog Ad Click Exception', message)

    def onThreadBlogAdClickCloseTab(self):
        self.onTabCloseViewOthers(0)

    def onThreadBlogAdClickMouseMove(self, left: float, top: float, width: float, height: float):
        curwgt = self._tabWidget.currentWidget()
        if isinstance(curwgt, WebPageWidget):
            pt = curwgt.mapToGlobal(QPoint(0, 0))
            x = pt.x() + left + (width * 0.4)
            y = pt.y() + top + (height / 2)
            pyautogui.moveTo(int(x), int(y))

    def onThreadBlogAdClickCheckAdOpen(self):
        if self._tabWidget.count() <= 2:
            pyautogui.click()
        else:
            if self._threadBlogAdClick is not None:
                self._threadBlogAdClick.setAdOpenDone()
    ####################################################################################################################
    # TODO: 최초로 열린 창이 닫기면 서버가 날아가기 때문에 적합한 방법이 아니다...ㅠㅠ

    def initSocket(self):
        # listener
        try:
            self._sock_listener = Listener(('localhost', 12345), authkey=b'YOGYUI')
            self.startThreadSocketListener()
        except OSError as e:
            print(e)
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))

        # client
        self.startThreadSocketClient()

    def releaseSocket(self):
        self.stopThreadSocketClient()
        self.stopThreadSocketListener()
        if self._sock_listener is not None:
            self._sock_listener.close()

    def startThreadSocketListener(self):
        if self._threadSocketListener is None:
            self._threadSocketListener = ThreadSocketListener(listner=self._sock_listener, parent=self)
            self._threadSocketListener.sig_terminated.connect(self.onThreadSocketListenerTerminated)
            self._threadSocketListener.start()

    def stopThreadSocketListener(self):
        if self._threadSocketListener is not None:
            self._threadSocketListener.stop()

    def onThreadSocketListenerTerminated(self):
        del self._threadSocketListener
        self._threadSocketListener = None

    def startThreadSocketClient(self):
        if self._threadSocketClient is None:
            self._threadSocketClient = ThreadSocketClient(port=12345, parent=self)
            self._threadSocketClient.sig_terminated.connect(self.onThreadSocketClientTerminated)
            self._threadSocketClient.start()

    def stopThreadSocketClient(self):
        if self._threadSocketClient is not None:
            self._threadSocketClient.stop()

    def onThreadSocketClientTerminated(self):
        del self._threadSocketClient
        self._threadSocketClient = None

    def sendToServer(self, obj: object):
        if self._threadSocketClient is not None:
            self._threadSocketClient.send(obj)

    ####################################################################################################################


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
