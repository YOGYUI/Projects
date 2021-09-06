if __name__ == '__main__':
    import sys
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    from Include import WebBrowserWindow

    maximized = False
    # url_ = 'home'
    url_ = 'about:blank'
    for argv in sys.argv:
        if '--window_maximized' in argv:
            splt = argv.split('=')
            maximized = bool(int(splt[-1]))
        if '--start_page' in argv:
            splt = argv.split('=')
            url_ = splt[-1]

    app = QApplication([])
    QApplication.setStyle('fusion')
    mainwnd = WebBrowserWindow(init_url=url_)
    if maximized:
        mainwnd.setWindowState(Qt.WindowMaximized)
    else:
        mainwnd.resize(1024, 1024)
    mainwnd.show()
    app.exec_()
    QApplication.quit()
    sys.exit()
