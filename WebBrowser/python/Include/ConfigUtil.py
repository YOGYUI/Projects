# -------------------------------------------------------------------------------------------------------------------- #
# File Name    : ConfigUtil.py
# Project Name : WebBrowser
# Author       : Yogyui
# Description  : Configuration Web Browser
# -------------------------------------------------------------------------------------------------------------------- #
import os
import xml.etree.ElementTree as ET
from BookMarkWidget import BookMarkManager
from Common import writeXmlFile


class WebBrowserConfig:
    def __init__(self, bookmarkManager: BookMarkManager):
        curpath = os.path.dirname(os.path.abspath(__file__))
        configpath = os.path.join(os.path.dirname(curpath), 'Config')
        self.xml_path = os.path.join(configpath, 'config.xml')

        self.url_home = 'about:blank'
        self.url_blog_sitemap = ''
        self.bookmarkManager = bookmarkManager
        self.load_from_xml()

    def load_from_xml(self):
        if not os.path.isfile(self.xml_path):
            self.save_to_xml()
        xmldata = ET.parse(self.xml_path)
        root = xmldata.getroot()

        node = root.find('home')
        if node is not None:
            self.url_home = node.text

        node = root.find('blog_sitemap')
        if node is not None:
            self.url_blog_sitemap = node.text

        node = root.find('bookmarks')
        if node is not None:
            for child in list(node):
                if child.tag == 'item':
                    title = child.get('title')
                    url = child.attrib.get('url')
                    icon_url = child.attrib.get('icon_url')
                    self.bookmarkManager.addBookMark(url, title, icon_url)

    def save_to_xml(self):
        if os.path.isfile(self.xml_path):
            xmldata = ET.parse(self.xml_path)
        else:
            xmldata = ET.ElementTree(ET.Element('BrowserConfig'))
        root = xmldata.getroot()

        node = root.find('home')
        if node is None:
            node = ET.Element('home')
            root.append(node)
        node.text = self.url_home

        node = root.find('blog_sitemap')
        if node is None:
            node = ET.Element('blog_sitemap')
            root.append(node)
        node.text = self.url_blog_sitemap

        node = root.find('bookmarks')
        if node is None:
            node = ET.Element('bookmarks')
            root.append(node)

        for item in self.bookmarkManager.bookmarks:
            find = list(filter(lambda x: x.tag == 'item' and x.attrib['url'] == item.url, list(node)))
            if len(find) == 1:
                child = find[0]
            else:
                child = ET.Element('item')
                node.append(child)
            child.attrib['title'] = item.title
            child.attrib['url'] = item.url
            child.attrib['icon_url'] = item.icon_url

        writeXmlFile(root, self.xml_path, backup=False)
