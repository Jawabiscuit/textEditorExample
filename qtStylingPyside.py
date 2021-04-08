#! /bin/env python
import os
import sys

from PySide2.QtCore import (
    QResource,
    Signal,
)

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
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


class PreviewWidget(QWidget):

    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)

        closeButton = QPushButton("&Close")
        closeButton.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(closeButton)
        self.setLayout(layout)

        self.setWindowTitle("Preview")


class ControllerWidget(QWidget):

    _WidgetType = DefaultWidget
    _previewWidget = None

    def __init__(self):
        super(ControllerWidget, self).__init__()

        widget = ControllerWidget._previewWidget = \
            ControllerWidget._WidgetType.init()
        widget.show()

        previewButton = QPushButton("&Preview")
        quitButton = QPushButton("&Quit")

        layout = QVBoxLayout(self)
        layout.addWidget(previewButton)
        layout.addWidget(quitButton)
        layout.addStretch()

        previewButton.clicked.connect(self.onPreviewClicked)
        quitButton.clicked.connect(self.close)

    def onPreviewClicked(self):
        widget = ControllerWidget._previewWidget
        new = ControllerWidget._previewWidget = \
            ControllerWidget._WidgetType.init()
        new.show()

        widget.close()

    def closeEvent(self, event):
        ControllerWidget._previewWidget.deleteLater()
        event.accept()


if __name__ == "__main__":
    _app = QApplication(sys.argv)

    ui = ControllerWidget()
    ui.show()
    _app.exec_()
