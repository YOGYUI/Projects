import os
import _io
import shutil
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
import xml.etree.ElementTree as ElementTree


def makeQAction(**kwargs):
    parent = None
    text = None
    iconPath = None
    triggered = None
    checkable = False
    checked = False
    enabled = True

    if 'parent' in kwargs.keys():
        parent = kwargs['parent']
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if 'iconPath' in kwargs.keys():
        iconPath = kwargs['iconPath']
    if 'triggered' in kwargs.keys():
        triggered = kwargs['triggered']
    if 'checkable' in kwargs.keys():
        checkable = kwargs['checkable']
    if 'checked' in kwargs.keys():
        checked = kwargs['checked']
    if 'enabled' in kwargs.keys():
        enabled = kwargs['enabled']

    action = QAction(parent)
    action.setText(text)
    action.setIcon(QIcon(iconPath))
    if triggered is not None:
        action.triggered.connect(triggered)
    action.setCheckable(checkable)
    action.setChecked(checked)
    action.setEnabled(enabled)

    return action


def ensurePathExist(path: str):
    targetpath = os.path.abspath(path)
    if not os.path.isdir(targetpath):
        if os.name == 'nt':
            pathsplit = targetpath.split('\\')
            ptemp = str(pathsplit[0]) + '\\'
        else:
            pathsplit = targetpath.split('/')
            ptemp = str(pathsplit[0]) + '/'
        for i in range(len(pathsplit) - 1):
            p = pathsplit[i + 1]
            ptemp = os.path.join(ptemp, p)
            ptemp = os.path.abspath(ptemp)
            if not os.path.isdir(ptemp):
                os.mkdir(ptemp)


def writeXmlFile(
        elem: ElementTree.Element,
        path: str = '',
        fp: _io.TextIOWrapper = None,
        level: int = 0,
        backup: bool = True
):
    if fp is None:
        dir_name = os.path.dirname(os.path.abspath(path))
        ensurePathExist(dir_name)
        if backup and os.path.isfile(path):
            try:
                origin_data = ElementTree.parse(path)
                origin_root = origin_data.getroot()
                if ElementTree.tostring(origin_root) != ElementTree.tostring(elem):
                    backup_path = os.path.join(dir_name, 'Backup')
                    if not os.path.isdir(backup_path):
                        os.mkdir(backup_path)
                    origin_file_name = os.path.basename(path)
                    origin_name, origin_ext = os.path.splitext(origin_file_name)
                    backup_file_name = origin_name + '_backup' + origin_ext
                    backup_file_path = os.path.join(backup_path, backup_file_name)
                    shutil.copyfile(path, backup_file_path)
            except Exception:
                pass
        _fp = open(path, 'w', encoding='utf-8')
        _fp.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + '\n')
    else:
        _fp = fp
    _fp.write('\t' * level)
    _fp.write('<' + elem.tag)
    for key in elem.keys():
        fp.write(' ' + key + '="' + elem.attrib[key] + '"')
    if len(list(elem)) > 0:
        _fp.write('>\n')
        for child in list(elem):
            writeXmlFile(child, fp=_fp, level=level+1)
        _fp.write('\t' * level)
        _fp.write('</' + elem.tag + '>\n')
    else:
        if elem.text is not None:
            txt = elem.text
            txt = txt.replace('\r', '')
            txt = txt.replace('\n', '')
            txt = txt.replace('\t', '')
            if len(txt) > 0:
                _fp.write('>' + txt + '</' + elem.tag + '>\n')
            else:
                _fp.write('/>\n')
        else:
            _fp.write('/>\n')
    if level == 0:
        _fp.close()
