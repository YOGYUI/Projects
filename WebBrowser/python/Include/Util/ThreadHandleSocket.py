import os
import io
import sys
import pickle
from functools import partial
from multiprocessing.connection import Listener, Client, Connection
from PyQt5.QtCore import QThread, pyqtSignal
CURPATH = os.path.dirname(os.path.abspath(__file__))
INCPATH = os.path.dirname(CURPATH)
sys.path.extend([CURPATH, INCPATH])
sys.path = list(set(sys.path))
del CURPATH, INCPATH
from Common import writeLog


class ThreadHandleClient(QThread):
    _keepAlive: bool = True

    sig_terminated = pyqtSignal()
    sig_recv = pyqtSignal(object)

    def __init__(self, conn: Connection, parent=None):
        super().__init__(parent=parent)
        self._conn = conn

    def run(self):
        writeLog('Started', self)
        while self._keepAlive:
            try:
                buffer = self._conn.recv_bytes()
                obj = pickle.loads(buffer)
                self.sig_recv.emit(obj)
            except Exception:
                writeLog('Connection Lost', self)
                break
        self.sig_terminated.emit()
        writeLog('Terminated', self)

    def stop(self):
        self._keepAlive = False


class ThreadSocketListener(QThread):
    _keepAlive: bool = True

    sig_terminated = pyqtSignal()

    def __init__(self, listner: Listener, parent=None):
        super().__init__(parent=parent)
        self._listener = listner
        self._client_list = []

    def run(self):
        writeLog('Started', self)
        while self._keepAlive:
            try:
                conn = self._listener.accept()
                writeLog(f'Client({id(conn)}) Accepted', self)
                thread = ThreadHandleClient(conn, self)
                thread.sig_terminated.connect(partial(self.onClientThreadTerminated, conn))
                thread.sig_recv.connect(partial(self.onClientThreadRecv, conn))
                self._client_list.append(conn)
                thread.start()
            except Exception:
                break
        writeLog('Terminated', self)
        self.sig_terminated.emit()

    def stop(self):
        self._keepAlive = False

    def onClientThreadTerminated(self, conn: Connection):
        writeLog(f'Client({id(conn)}) Disconnected', self)
        self._client_list.remove(conn)

    def onClientThreadRecv(self, conn: Connection, obj: object):
        writeLog(f'Recieved from Client({id(conn)}) - {obj}', self)


class ThreadSocketClient(QThread):
    _keepAlive: bool = True
    _client: Client = None

    sig_terminated = pyqtSignal()

    def __init__(self, port: int, parent=None):
        super().__init__(parent=parent)
        self.port = port

    def run(self):
        writeLog('Started', self)
        try:
            self._client = Client(('localhost', self.port), authkey=b'YOGYUI')
        except Exception as e:
            writeLog(f'Exception::{e}', self)

        while self._keepAlive:
            self.msleep(1)

        if self._client is not None:
            self._client.close()
        writeLog('Terminated', self)
        self.sig_terminated.emit()

    def stop(self):
        self._keepAlive = False

    def send(self, obj: object):
        buffer = io.BytesIO()
        pickle.dump(obj, buffer)
        self._client.send_bytes(buffer.getvalue())
