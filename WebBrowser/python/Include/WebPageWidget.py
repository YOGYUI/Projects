# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : WebPageWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Implementation of basic web page (viewer) widget
# -------------------------------------------------------------------------------------------------------------------- #
import os
from typing import Union
from PyQt5.QtCore import Qt, QUrl, QSize, QObject, QEvent, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineHistory, QWebEnginePage


class WebView(QWebEngineView):
    sig_new_tab = pyqtSignal(QWebEngineView)
    sig_new_window = pyqtSignal(QWebEngineView)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    _is_loading: bool = False

    sig_page_icon = pyqtSignal(QIcon)
    sig_page_title = pyqtSignal(str)
    sig_new_tab = pyqtSignal(object)
    sig_new_window = pyqtSignal(object)
    sig_close = pyqtSignal(object)

    def __init__(self, parent=None, url: Union[str, QUrl] = 'about:blank', view: WebView = None):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)
        self._editUrl = QLineEdit()
        self._btnGoBackward = QPushButton()
        self._btnGoForward = QPushButton()
        self._btnStopRefresh = QPushButton()
        self._iconRefresh = QIcon('./Resource/reload.png')
        self._iconStop = QIcon('./Resource/cancel.png')
        self._btnZoomIn = QPushButton()
        self._btnZoomOut = QPushButton()
        self._webview = WebView() if view is None else view
        self.initControl()
        self.initLayout()
        self.load(url)

    def release(self):
        self._webview.release()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 4, 0, 0)
        vbox.setSpacing(4)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(4, 0, 4, 0)
        hbox.setSpacing(4)
        hbox.addWidget(self._btnGoBackward)
        hbox.addWidget(self._btnGoForward)
        hbox.addWidget(self._btnStopRefresh)
        hbox.addWidget(self._editUrl)
        hbox.addWidget(self._btnZoomIn)
        hbox.addWidget(self._btnZoomOut)
        vbox.addWidget(subwgt)
        vbox.addWidget(self._webview)

    def initControl(self):
        self._editUrl.returnPressed.connect(self.onEditUrlReturnPressed)
        self.setWebViewSignals()
        self._webview.titleChanged.connect(lambda x: self.sig_page_title.emit(x))
        self._webview.iconChanged.connect(lambda x: self.sig_page_icon.emit(x))
        self._btnGoBackward.setEnabled(False)
        self._btnGoBackward.clicked.connect(lambda: self._webview.back())
        self._btnGoBackward.setIcon(QIcon('./Resource/previous.png'))
        self._btnGoBackward.setFlat(True)
        self._btnGoBackward.setIconSize(QSize(20, 20))
        self._btnGoBackward.setFixedSize(QSize(24, 20))
        self._btnGoForward.setEnabled(False)
        self._btnGoForward.clicked.connect(lambda: self._webview.forward())
        self._btnGoForward.setIcon(QIcon('./Resource/forward.png'))
        self._btnGoForward.setFlat(True)
        self._btnGoForward.setIconSize(QSize(20, 20))
        self._btnGoForward.setFixedSize(QSize(24, 20))
        self._btnStopRefresh.setEnabled(False)
        self._btnStopRefresh.clicked.connect(self.onClickBtnStopRefresh)
        self._btnStopRefresh.setIcon(self._iconRefresh)
        self._btnStopRefresh.setFlat(True)
        self._btnStopRefresh.setIconSize(QSize(20, 20))
        self._btnStopRefresh.setFixedSize(QSize(24, 20))
        self._btnZoomIn.clicked.connect(self.onClickBtnZoomIn)
        self._btnZoomIn.setIcon(QIcon('./Resource/zoomin.png'))
        self._btnZoomIn.setFlat(True)
        self._btnZoomIn.setIconSize(QSize(20, 20))
        self._btnZoomIn.setFixedSize(QSize(24, 20))
        self._btnZoomOut.clicked.connect(self.onClickBtnZoomOut)
        self._btnZoomOut.setIcon(QIcon('./Resource/zoomout.png'))
        self._btnZoomOut.setFlat(True)
        self._btnZoomOut.setIconSize(QSize(20, 20))
        self._btnZoomOut.setFixedSize(QSize(24, 20))

    def setWebViewSignals(self):
        self._webview.loadStarted.connect(self.onWebViewLoadStarted)
        self._webview.loadProgress.connect(self.onWebViewLoadProgress)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)
        self._webview.sig_new_tab.connect(self.sig_new_tab.emit)
        self._webview.sig_new_window.connect(self.sig_new_window.emit)

    def load(self, url: Union[str, QUrl]):
        if isinstance(url, QUrl):
            self._webview.load(url)
        else:
            self._webview.load(QUrl(url))

    def onEditUrlReturnPressed(self):
        url = self._editUrl.text()
        self.load(url)

    def onWebViewLoadStarted(self):
        self._is_loading = True
        self._btnStopRefresh.setEnabled(True)
        self._btnStopRefresh.setIcon(self._iconStop)
        # self.sig_page_icon.emit(QIcon('./Resource/processing.png'))

    def onWebViewLoadProgress(self, progress: int):
        """
        if 0 < progress < 100:
            self.sig_page_title.emit(f'Loading...({progress})')
        """

    def onWebViewLoadFinished(self, result: bool):
        self._is_loading = False
        url: QUrl = self._webview.url()
        self._editUrl.setText(url.toString())
        history: QWebEngineHistory = self._webview.history()
        self._btnGoBackward.setEnabled(history.canGoBack())
        self._btnGoForward.setEnabled(history.canGoForward())
        self._btnStopRefresh.setIcon(self._iconRefresh)
        self.sig_page_title.emit(self._webview.title())
        if result:
            self.sig_page_icon.emit(self._webview.icon())
        else:
            self.sig_page_icon.emit(QIcon('./Resource/warning.png'))

    def onClickBtnStopRefresh(self):
        if self._is_loading:
            self._webview.stop()
        else:
            self._webview.reload()

    def onClickBtnZoomIn(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor + 0.1)

    def onClickBtnZoomOut(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor - 0.1)

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
        elif a0.key() == Qt.Key_F5:
            self._webview.reload()
        elif a0.key() == Qt.Key_F6:
            self._editUrl.setFocus()
            self._editUrl.selectAll()
        elif a0.key() == Qt.Key_Escape:
            self._webview.stop()
        elif a0.key() == Qt.Key_Backspace:
            self._webview.back()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        pass

    def url(self) -> QUrl:
        return self._webview.url()

    def view(self) -> WebView:
        return self._webview


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
