#! /bin/env python
import os
import sys

from PySide2.QtCore import QResource

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
)


class DefaultWidget(QWidget):
    """Default widget with no style mods"""

    @classmethod
    def init(cls, *args):
        cls.initGlobalStyle(args)
        widget = cls()
        widget.setWindowTitle(cls.__name__)
        widget.initUi()
        widget.initInstanceStyle(*args)
        return widget

    @classmethod
    def initGlobalStyle(cls, args):
        """
        Initialize style that will be used across the application
        """
        pass

    @classmethod
    def getStyleSheet(cls):
        """
        Reads in the style sheet resource
        """
        raise NotImplementedError()

    def initInstanceStyle(self, *args):
        """
        Initialize style that will be applied to this instance
        """
        pass

    def initUi(self):
        self.setObjectName(self.__class__.__name__)
        button = QPushButton("Button", self)
        group = QGroupBox('Group', self)

        widgets = [
            button,
        ]
        innerLayout = QVBoxLayout(group)
        for widget in widgets:
            innerLayout.addWidget(widget)
        innerLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(group)


class QssWidget(DefaultWidget):

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application
        """
        QApplication.instance().setStyleSheet(cls.getStyleSheet())

    @classmethod
    def initInstanceStyle(cls, *args):
        """
        Initialize style that will be applied to this instance
        """
        pass

    @classmethod
    def getStyleSheet(cls):
        """
        Reads in the style sheet resource
        """
        dirname = os.path.dirname(__file__)
        rccPath = os.path.join(dirname, "resources.rcc")
        QResource.registerResource(rccPath)
        qssPath = os.path.join(dirname, "sample.css")
        with open(qssPath, "r") as fh:
            return fh.read()


if __name__ == "__main__":
    from collections import deque

    # Style to window type map
    styleMap = dict(
        default=DefaultWidget,
        qss=QssWidget,
    )
    _app = QApplication(sys.argv)

    # Process the arguments
    mode = "qss"
    args = deque(sys.argv[1:])
    error = "Provide a styling mode from the list: [{}]".format(
        ", ".join(sorted(styleMap.keys())))

    if args:
        mode = args.popleft()
    else:
        print(error)
    uiType = styleMap.get(mode, False)
    if not uiType:
        raise RuntimeError(error)

    ui = uiType.init(args)
    ui.show()
    _app.exec_()
