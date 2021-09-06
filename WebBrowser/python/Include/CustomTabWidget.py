# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : CustomTabWidget.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Customize tab widget and tab bar
# -------------------------------------------------------------------------------------------------------------------- #
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect
from PyQt5.QtGui import QIcon, QPaintEvent
from PyQt5.QtWidgets import QTabBar, QTabWidget, QPushButton, QWidget, QStylePainter, QStyleOptionTab, QStyle
from PyQt5.QtWidgets import QMenu
from Common import makeQAction


class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
    """
    def paintEvent(self, a0: QPaintEvent) -> None:
        # https://stackoverflow.com/questions/3607709/how-to-change-text-alignment-in-qtabwidget
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        ico_rect_size = 32
        ico_size = 28

        print(option, str(option))
        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)

            icon = self.tabIcon(index)
            iconrect = QRect(tabRect.left(), tabRect.top(), ico_rect_size, ico_rect_size)
            pixmap = icon.pixmap(icon.actualSize(QSize(ico_size, ico_size)))
            painter.drawPixmap(iconrect, pixmap)

            tabRect.setLeft(tabRect.left() + ico_rect_size)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, Qt.AlignVCenter | Qt.TextDontClip, self.tabText(index))
    """
    def tabSizeHint(self, index: int) -> QSize:
        size = super().tabSizeHint(index)
        add_btn_width = 36
        parent_width = self.parent().width()
        if index == self.count() - 1:
            if self.count() == 1:
                width = add_btn_width + 14
            else:
                width = add_btn_width
        else:
            width_max = 240
            if (self.count() - 1) * width_max < parent_width:
                width = width_max
            else:
                width = int((parent_width - add_btn_width) / (self.count() - 1))
        return QSize(width, size.height())


class CustomTabWidget(QTabWidget):
    sig_add_tab = pyqtSignal()
    sig_new_window = pyqtSignal(int)
    sig_close = pyqtSignal(int)
    sig_close_others = pyqtSignal(int)
    sig_close_right = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._tabbar = CustomTabBar(self)
        self.setTabBar(self._tabbar)
        self.setMovable(True)

        btn = QPushButton()
        btn.setIcon(QIcon('./Resource/add.png'))
        btn.setFlat(True)
        btn.setIconSize(QSize(18, 16))
        btn.setToolTip('Add New Tab')
        btn.clicked.connect(lambda: self.sig_add_tab.emit())

        self._defaultWidget = QWidget()
        self.addTab(self._defaultWidget, '')
        self.tabBar().setTabButton(0, QTabBar.LeftSide, btn)
        self.setTabEnabled(0, False)
        self.tabBar().tabMoved.connect(self.onTabMoved)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        stylesheet = "QTabBar::tab {height: 32px; font: 12px;}\n"
        stylesheet += "QTabBar::tab:!selected {border: 0px; margin-left: 8px;}\n"
        self.setStyleSheet(stylesheet)

    def onTabMoved(self):
        # add tab should be always on right side
        index = self.indexOf(self._defaultWidget)
        self.tabBar().moveTab(index, self.count() - 1)

    def showContextMenu(self, point: QPoint):
        if point.isNull():
            return
        index = self.tabBar().tabAt(point)
        menu = QMenu(self)
        menuAddtab = makeQAction(parent=self, text='Add New Tab',
                                 triggered=self.sig_add_tab.emit)
        menu.addAction(menuAddtab)
        menuNewWnd = makeQAction(parent=self, text='Move to New Window',
                                 triggered=lambda: self.sig_new_window.emit(index),
                                 enabled=index >= 0 and self.count() > 2)
        menu.addAction(menuNewWnd)
        menu.addSeparator()
        menuCloseTab = makeQAction(parent=self, text='Close',
                                   triggered=lambda: self.sig_close.emit(index),
                                   enabled=index >= 0)
        menu.addAction(menuCloseTab)
        menuCloseOthers = makeQAction(parent=self, text='Close Others',
                                      triggered=lambda: self.sig_close_others.emit(index),
                                      enabled=index >= 0 and self.count() > 2)
        menu.addAction(menuCloseOthers)
        menuCloseRight = makeQAction(parent=self, text='Close Right-side',
                                     triggered=lambda: self.sig_close_right.emit(index),
                                     enabled=0 <= index < self.count() - 2)
        menu.addAction(menuCloseRight)
        menu.exec(self.tabBar().mapToGlobal(point))
