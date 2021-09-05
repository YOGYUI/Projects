from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction


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
