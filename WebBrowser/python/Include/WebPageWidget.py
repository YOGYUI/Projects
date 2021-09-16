# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : WebPageWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of basic web page (viewer) widget
# -------------------------------------------------------------------------------------------------------------------- #
import os
from enum import IntEnum
from typing import Union
from PyQt5.QtCore import Qt, QUrl, QObject, QEvent, pyqtSignal, QVariant
from PyQt5.QtGui import QIcon, QKeyEvent, QMouseEvent, QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtWidgets import QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class WebPage(QWebEnginePage):
    sig_js_console_msg = pyqtSignal(int, str, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, message: str, lineNumber: int, sourceID: str):
        # level: 0 = Info, 1 = Warning, 2 = Error
        self.sig_js_console_msg.emit(int(level), message, lineNumber, sourceID)


class WebView(QWebEngineView):
    sig_new_tab = pyqtSignal(QWebEngineView)
    sig_new_window = pyqtSignal(QWebEngineView)
    sig_js_console_msg = pyqtSignal(int, str, int, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        page = WebPage(self)
        page.sig_js_console_msg.connect(self.sig_js_console_msg.emit)
        self.setPage(page)
        QApplication.instance().installEventFilter(self)

    def load(self, *args):
        if isinstance(args[0], QUrl):
            qurl: QUrl = args[0]
            if qurl.isRelative():
                qurl.setScheme('http')
            return super().load(qurl)
        return super().load(*args)

    def release(self):
        self.deleteLater()
        self.close()

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a0.parent() == self:
            if a1.type() == QEvent.MouseButtonPress:
                if a1.button() == Qt.ForwardButton:
                    self.forward()
                elif a1.button() == Qt.BackButton:
                    self.back()
            elif a1.type() == QEvent.Wheel:
                modifier = QApplication.keyboardModifiers()
                if modifier == Qt.ControlModifier:
                    y_angle = a1.angleDelta().y()
                    factor = self.zoomFactor()
                    if y_angle > 0:
                        self.setZoomFactor(factor + 0.1)
                        return True
                    elif y_angle < 0:
                        self.setZoomFactor(factor - 0.1)
                        return True
        return False

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            view = WebView()
            self.sig_new_tab.emit(view)
            return view
        elif windowType == QWebEnginePage.WebBrowserWindow:
            view = WebView()
            self.sig_new_window.emit(view)
            return view
        # open tab when ctrl key is pressed
        modifier = QApplication.keyboardModifiers()
        if modifier == Qt.ControlModifier:
            view = WebView()
            self.sig_new_tab.emit(view)
            return view
        return QWebEngineView.createWindow(self, windowType)


class WebPageWidget(QWidget):
    sig_page_icon = pyqtSignal(QIcon)
    sig_page_title = pyqtSignal(str)
    sig_load_started = pyqtSignal(str)
    sig_load_finished = pyqtSignal(bool)
    sig_new_tab = pyqtSignal(object)
    sig_new_window = pyqtSignal(object)
    sig_close = pyqtSignal(object)
    sig_home = pyqtSignal()
    sig_dev_tool = pyqtSignal()
    sig_edit_url_focus = pyqtSignal()
    sig_js_result = pyqtSignal(object)
    sig_key_escape = pyqtSignal()
    sig_js_console_msg = pyqtSignal(int, str, int, str)

    def __init__(self, parent=None, url: Union[str, QUrl] = 'about:blank', view: WebView = None):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)
        self._webview = WebView() if view is None else view
        self.initControl()
        self.initLayout()
        self.load(url)

    def release(self):
        self._webview.release()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.addWidget(self._webview)

    def initControl(self):
        QShortcut(QKeySequence.Cancel, self, self.onShortCutEscape)
        self.setWebViewSignals()
        self._webview.titleChanged.connect(self.onWebViewTitleChanged)
        self._webview.iconChanged.connect(self.onWebViewIconChanged)

    def setWebViewSignals(self):
        self._webview.loadStarted.connect(self.onWebViewLoadStarted)
        self._webview.loadProgress.connect(self.onWebViewLoadProgress)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)
        self._webview.sig_new_tab.connect(self.sig_new_tab.emit)
        self._webview.sig_new_window.connect(self.sig_new_window.emit)
        self._webview.sig_js_console_msg.connect(self.sig_js_console_msg.emit)

    def load(self, url: Union[str, QUrl]):
        if isinstance(url, QUrl):
            self._webview.load(url)
        else:
            self._webview.load(QUrl(url))

    def onWebViewLoadStarted(self):
        url = self._webview.page().requestedUrl().toString()
        self.sig_load_started.emit(url)
        # self.sig_page_icon.emit(QIcon('./Resource/processing.png'))

    def onWebViewLoadProgress(self, progress: int):
        """
        if 0 < progress < 100:
            self.sig_page_title.emit(f'Loading...({progress})')
        """

    def onWebViewLoadFinished(self, result: bool):
        self.sig_load_finished.emit(result)

    def onWebViewTitleChanged(self, title: str):
        # print('onWebViewTitleChanged')
        self.sig_page_title.emit(title)

    def onWebViewIconChanged(self, icon: QIcon):
        # print('onWebViewIconChanged')
        self.sig_page_icon.emit(icon)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        modifier = QApplication.keyboardModifiers()
        if a0.key() == Qt.Key_N:
            if modifier == Qt.ControlModifier:
                self.sig_new_window.emit(None)
        elif a0.key() == Qt.Key_T:
            if modifier == Qt.ControlModifier:
                self.sig_new_tab.emit(None)
        elif a0.key() == Qt.Key_W:
            if modifier == Qt.ControlModifier:
                self.sig_close.emit(self)
        elif a0.key() == Qt.Key_H:
            if modifier == Qt.ControlModifier:
                self.sig_home.emit()
        elif a0.key() == Qt.Key_D:
            if modifier == Qt.ControlModifier:
                self.sig_dev_tool.emit()
        elif a0.key() == Qt.Key_F5:
            self._webview.reload()
        elif a0.key() == Qt.Key_F6:
            self.sig_edit_url_focus.emit()
        elif a0.key() == Qt.Key_Backspace:
            self._webview.back()

    def onShortCutEscape(self):
        self._webview.stop()
        self.sig_key_escape.emit()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        pass

    def url(self) -> QUrl:
        return self._webview.url()

    def view(self) -> WebView:
        return self._webview

    def title(self) -> str:
        return self._webview.title()

    def icon(self) -> QIcon:
        return self._webview.icon()

    def runJavaScript(self, script: str):
        self.view().page().runJavaScript(script, self.jsCallback)

    def jsCallback(self, v: QVariant):
        # print(v, type(v))
        self.sig_js_result.emit(v)


if __name__ == '__main__':
    import sys
    from PyQt5.QtCore import QCoreApplication

    QApplication.setStyle('fusion')
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    wgt_ = WebPageWidget()
    wgt_.show()
    wgt_.resize(600, 600)

    app.exec_()
    wgt_.release()
