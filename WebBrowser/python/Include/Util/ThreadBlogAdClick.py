import os
import sys
import time
import random
import requests
import dateutil.parser
from typing import List
from urllib import parse
from bs4 import BeautifulSoup
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, QTime
CURPATH = os.path.dirname(os.path.abspath(__file__))
INCPATH = os.path.dirname(CURPATH)
sys.path.extend([CURPATH, INCPATH])
sys.path = list(set(sys.path))
del CURPATH, INCPATH
from Common import writeLog


class SiteInfo:
    url: str = ''
    last_modification: datetime

    def __init__(self, url: str, last_modification: datetime):
        self.url = url
        self.last_modification = last_modification


def getBlogSitemaps(sitemap) -> List[SiteInfo]:
    response = requests.get(sitemap)
    url_lst_ = []
    try:
        result_ = BeautifulSoup(response.text, "lxml")
        urls_ = result_.find_all('url')
        for url_ in urls_:
            if len(url_.find_all('lastmod')) > 0 and len(url_.find_all('priority')) == 0:
                loc = url_.find('loc').text
                lastmod = url_.find('lastmod').text
                url_lst_.append(SiteInfo(parse.unquote(loc), dateutil.parser.isoparse(lastmod)))
    except Exception:
        pass
    return url_lst_


class BlogAdClickParams:
    sitemap_url: str = ''
    enable_ad_sense: bool = True
    enable_ad_fit: bool = True
    visit_count: int = 0  # 0 = infinite
    delay_after_visit: int = 10  # unit: sec
    delay_between_ad: int = 10  # unit: sec
    timeout: int = 10  # unit: sec
    random_skip: bool = False
    enable_time_range: bool = False
    time_range_start: QTime = QTime(1, 0, 0)
    time_range_end: QTime = QTime(23, 0, 0)

    def __repr__(self):
        msg = f'sitemap_url: {self.sitemap_url}, '
        msg += f'enable_ad_sense: {self.enable_ad_sense}, '
        msg += f'enable_ad_fit: {self.enable_ad_fit}, '
        msg += f'visit_count: {self.visit_count}, '
        msg += f'delay_after_visit: {self.delay_after_visit}, '
        msg += f'delay_between_ad: {self.delay_between_ad}, '
        msg += f'timeout: {self.timeout}, '
        msg += f'random_skip: {self.random_skip}'
        return msg


class ThreadBlogAdClick(QThread):
    _keepAlive: bool = True
    _wait_visit_done: bool = False
    _wait_js_result: bool = False
    _wait_ad_open: bool = False

    _js_result: object = None

    sig_started = pyqtSignal()
    sig_terminated = pyqtSignal(datetime, datetime, int, list, float)
    sig_exception = pyqtSignal(str)
    sig_visit = pyqtSignal(str)
    sig_run_js = pyqtSignal(str)
    sig_close_tab = pyqtSignal()
    sig_mouse_move = pyqtSignal(float, float, float, float)
    sig_check_ad_open = pyqtSignal()
    sig_delete_cookies = pyqtSignal()

    def __init__(self, params: BlogAdClickParams, parent=None):
        super().__init__(parent=parent)
        self.params = params

    def run(self):
        self.sig_started.emit()
        tm_start = datetime.now()

        self.sig_delete_cookies.emit()

        sites = getBlogSitemaps(self.params.sitemap_url)
        visit_count: int = 0

        # sidebar: apply to tistory blog
        js_open_sidebar = 'document.getElementById("dkWrap").setAttribute("class", "wrap_skin navi_on");'
        js_close_sidebar = 'document.getElementById("dkWrap").setAttribute("class", "wrap_skin");'
        js_count = 'document.getElementsByClassName("{}").length;'
        js_rect = 'document.getElementsByClassName("{}")[{}].getBoundingClientRect().toJSON();'
        js_scroll = 'document.getElementsByClassName("{}")[{}].scrollIntoView();'

        writeLog('Started', self)
        writeLog(str(self.params), self)

        ad_items = []
        if self.params.enable_ad_sense:
            ad_items.append({
                'head': 'AdSense',
                'classname': 'adsbygoogle',
                'visit': 0,
                'success': 0,
                'skip': 0,
                'click': False  # 클릭하면 계정 정지당한다 ㅋㅋ
            })
        if self.params.enable_ad_fit:
            ad_items.append({
                'head': 'AdFit',
                'classname': 'revenue_unit_item adfit',
                'visit': 0,
                'success': 0,
                'skip': 0,
                'click': False
            })

        avg_visit_time: float = 0.

        while self._keepAlive:
            try:
                if self.params.enable_time_range:
                    t1 = self.params.time_range_start
                    t2 = self.params.time_range_end
                    if not t1 <= QTime().currentTime() <= t2:
                        writeLog(f'Out of Time Range', self)
                        self.delay(1)
                        continue

                idx = random.sample(range(len(sites)), 1)[0]
                site = sites[idx]

                tm_visit_start = time.perf_counter()
                # Visit Site
                url = site.url
                self._wait_visit_done = True
                writeLog(f'[Visit] to {url}', self)
                self.sig_visit.emit(url)
                if not self.waitVisitDone():
                    continue
                writeLog('[Visit] Done', self)
                if self.params.delay_after_visit > 0:
                    self.delay(self.params.delay_after_visit)

                for item in ad_items:
                    head = item.get('head')
                    classname = item.get('classname')
                    click = item.get('click')
                    if self._keepAlive:
                        writeLog(f'[{head}] Start', self)
                        # get element count
                        elem_count = 0
                        self.runJavaScript(js_count.format(classname))
                        if isinstance(self._js_result, int):
                            elem_count = self._js_result
                            writeLog(f'[{head}] Element Count: {elem_count}', self)

                        for i in range(elem_count):
                            if not self._keepAlive:
                                break
                            writeLog(f'[{head}] Element Index - {i}', self)

                            hidden: bool = False
                            # get element bound rect and move mouse
                            self.runJavaScript(js_rect.format(classname, i))
                            writeLog(f'[{head}] Get Element Bounding Rect', self)
                            top, left, width, height = 0, 0, 0, 0
                            if isinstance(self._js_result, dict):
                                top = self._js_result.get('top')
                                left = self._js_result.get('left')
                                width = self._js_result.get('width')
                                height = self._js_result.get('height')
                            else:
                                writeLog(f'[{head}] Failed to Get Element Rect', self)
                            if top == 0 and left == 0 and width == 0 and height == 0:
                                hidden = True

                            if hidden:
                                self.runJavaScript(js_open_sidebar)
                                writeLog('Open Side-Bar', self)
                                self.msleep(1000)

                            # element scroll into view
                            self.runJavaScript(js_scroll.format(classname, i))
                            writeLog(f'[{head}] Ad Element Scroll Into View', self)

                            # get element bound rect and move mouse
                            self.runJavaScript(js_rect.format(classname, i))
                            writeLog(f'[{head}] Get Element Bounding Rect', self)
                            top, left, width, height = 0, 0, 0, 0
                            if isinstance(self._js_result, dict):
                                top = self._js_result.get('top')
                                left = self._js_result.get('left')
                                width = self._js_result.get('width')
                                height = self._js_result.get('height')
                            else:
                                writeLog(f'[{head}] Failed to Get Element Rect', self)
                            self.sig_mouse_move.emit(left, top, width, height)

                            # open ad tab
                            visit = False
                            if click:
                                if self.params.random_skip:
                                    visit = bool(int(random.random() * 1000) % 2)
                                else:
                                    visit = True

                            if visit:
                                item['visit'] += 1
                                self._wait_ad_open = True
                                if self.waitAdOpen():
                                    writeLog(f'[{head}] Open Ad Success', self)
                                    item['success'] += 1
                                else:
                                    writeLog(f'[{head}] Failed to Open Ad', self)
                            else:
                                writeLog(f'[{head}] Ad Click Skipped', self)
                                item['skip'] += 1

                            self.delay(self.params.delay_between_ad)

                            # close other tabs
                            self.sig_close_tab.emit()

                            if hidden:
                                self.runJavaScript(js_close_sidebar)
                                writeLog('Close Side-Bar', self)
                                self.msleep(1000)

                visit_count += 1
                tm_visit_time = time.perf_counter() - tm_visit_start
                writeLog(f'[Visit] Elapsed (s): {tm_visit_time}', self)
                avg_visit_time = avg_visit_time * (visit_count - 1) / visit_count + tm_visit_time / visit_count

                if visit_count >= self.params.visit_count > 0:
                    break
                if visit_count >= len(sites):
                    # refresh site map list
                    self.sig_delete_cookies.emit()
                    sites = getBlogSitemaps(self.params.sitemap_url)
            except Exception as e:
                self.sig_exception.emit(str(e))
        writeLog('Finished', self)
        self.sig_terminated.emit(tm_start, datetime.now(), visit_count, ad_items, avg_visit_time)

    def stop(self):
        self._keepAlive = False

    def delay(self, sec: int):
        if sec > 0:
            tm_start = time.perf_counter()
            while time.perf_counter() - tm_start < sec:
                if not self._keepAlive:
                    break
                self.msleep(10)

    def waitVisitDone(self) -> bool:
        result = True
        tm_start = time.perf_counter()
        while self._wait_visit_done:
            if time.perf_counter() - tm_start > self.params.timeout:
                result = False
                break
            if not self._keepAlive:
                result = False
                break
            self.msleep(100)
        return result

    def setVisitDone(self):
        self._wait_visit_done = False

    def runJavaScript(self, script: str) -> bool:
        self._wait_js_result = True
        self._js_result = None
        self.sig_run_js.emit(script)
        return self.waitJavaScriptResult()

    def waitJavaScriptResult(self) -> bool:
        result = True
        tm_start = time.perf_counter()
        while self._wait_js_result:
            if time.perf_counter() - tm_start > self.params.timeout:
                result = False
                break
            if not self._keepAlive:
                result = False
                break
            self.msleep(10)
        return result

    def setJavaScriptResult(self, obj: object):
        self._js_result = obj
        self._wait_js_result = False

    def waitAdOpen(self):
        result = True
        tm_start = time.perf_counter()
        while self._wait_ad_open:
            if time.perf_counter() - tm_start > self.params.timeout:
                result = False
                break
            if not self._keepAlive:
                result = False
                break
            # self.sig_mouse_move.emit(left, top, width, height)
            # self.msleep(100)
            self.sig_check_ad_open.emit()
            self.msleep(1000)
        return result

    def setAdOpenDone(self):
        self._wait_ad_open = False
