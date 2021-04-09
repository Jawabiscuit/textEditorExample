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
    QComboBox,
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
        QApplication.instance().setStyleSheet("")

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

    def initInstanceStyle(self, *args):
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


class ControllerWidget(QWidget):

    _WidgetType = DefaultWidget
    _demoWidget = None

    widget_type_map = dict(default=DefaultWidget,
                           qss=QssWidget,)

    def __init__(self):
        super(ControllerWidget, self).__init__()

        widget = ControllerWidget._demoWidget = \
            ControllerWidget._WidgetType.init()
        widget.show()

        self.styleCombo = styleCombo = QComboBox()
        setButton = QPushButton("&Set")
        quitButton = QPushButton("&Quit")

        styleCombo.addItems(["default", "qss"])

        layout = QVBoxLayout(self)
        layout.addWidget(styleCombo)
        layout.addWidget(setButton)
        layout.addWidget(quitButton)
        layout.addStretch()

        setButton.clicked.connect(self.onSetClicked)
        quitButton.clicked.connect(self.close)

    def onSetClicked(self):
        widget = ControllerWidget._demoWidget
        uiSelection = self.styleCombo.currentText()
        uiType = self.widget_type_map.get(uiSelection)
        ControllerWidget._WidgetType = uiType
        new = ControllerWidget._demoWidget = uiType.init()
        new.show()

        widget.close()

    def closeEvent(self, event):
        ControllerWidget._demoWidget.deleteLater()
        event.accept()


if __name__ == "__main__":
    _app = QApplication(sys.argv)

    ui = ControllerWidget()
    ui.show()
    _app.exec_()
