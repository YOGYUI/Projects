# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : DeveloperWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Widget for Developer (Javascript, Page Source)
# -------------------------------------------------------------------------------------------------------------------- #
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QSizePolicy


class DeveloperWidget(QWidget):
    sig_run_js = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._editJavaScript = QTextEdit()
        self._btnRunJavaScript = QPushButton('RUN')
        self._editJsResult = QLineEdit()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)

        grbox = QGroupBox('JavaScript')
        grbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        vbox_gr = QVBoxLayout(grbox)
        vbox_gr.setContentsMargins(4, 4, 4, 4)
        vbox_gr.setSpacing(4)
        vbox_gr.addWidget(self._editJavaScript)
        vbox_gr.addWidget(self._btnRunJavaScript)
        vbox_gr.addWidget(self._editJsResult)
        vbox.addWidget(grbox)

        vbox.addWidget(QWidget())

    def initControl(self):
        self._editJavaScript.setLineWrapColumnOrWidth(-1)
        self._editJavaScript.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self._btnRunJavaScript.clicked.connect(self.onClickBtnRunJavaScript)
        self._editJsResult.setReadOnly(True)

    def onClickBtnRunJavaScript(self):
        script = self._editJavaScript.toPlainText()
        self.sig_run_js.emit(script)

    def setJsResult(self, obj: object):
        self._editJsResult.setText(str(obj))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication

    QApplication.setStyle('fusion')
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    wgt_ = DeveloperWidget()
    wgt_.show()

    app.exec_()
