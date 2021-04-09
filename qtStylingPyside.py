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
    QLineEdit,
    QComboBox,
)


class DefaultWidget(QWidget):
    """Default widget with no style mods"""

    button = None
    line = None
    combo = None

    @classmethod
    def init(cls, *args):
        cls.initGlobalStyle(*args)
        widget = cls()
        widget.setWindowTitle(cls.__name__)
        widget.initUi()
        widget.initInstanceStyle(*args)
        return widget

    @classmethod
    def initGlobalStyle(cls, *args):
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

    def setInstanceStyle(self, *args):
        """
        Set style applied to this instance in a running application
        """
        pass

    def initUi(self):
        self.setObjectName(self.__class__.__name__)

        self.button = button = QPushButton("Button", self)
        group = QGroupBox("Group", self)
        self.line = line = QLineEdit("Demo text.", self)
        self.combo = combo = QComboBox(self)
        for i in '123':
            combo.addItem('Choice ' + i)

        widgets = [
            button,
            line,
            combo,
        ]
        innerLayout = QVBoxLayout(group)
        for widget in widgets:
            innerLayout.addWidget(widget)
            innerLayout.addWidget(combo)
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
        if "error" in args:
            self.line.setProperty('hasError', True)
            self.combo.setObjectName('ErrorWidget')
            self.button.setObjectName('ErrorWidget')

    def setInstanceStyle(self, *args):
        """
        Set style applied to this instance in a running application
        """
        widgets = [
            self.line, self.combo, self.button,
        ]
        if "error" in args:
            self.line.setProperty('hasError', True)
            self.combo.setObjectName('ErrorWidget')
            self.button.setObjectName('ErrorWidget')

            for widget in widgets:
                widget.style().unpolish(widget)
                widget.style().polish(widget)

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
        errorButton = QPushButton("Error")
        quitButton = QPushButton("&Quit")

        setButton.setToolTip(
            "Apply the style selected in the drop-down")
        errorButton.setToolTip(
            "Apply styling to individual widgets indicating an error")
        quitButton.setToolTip(
            "Quit the application")

        styleCombo.addItems(["default", "qss"])

        layout = QVBoxLayout(self)
        layout.addWidget(styleCombo)
        layout.addWidget(setButton)
        layout.addWidget(errorButton)
        layout.addWidget(quitButton)
        layout.addStretch()

        setButton.clicked.connect(self.onSetClicked)
        errorButton.clicked.connect(self.onErrorClicked)
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

    def onErrorClicked(self):
        widget = ControllerWidget._demoWidget
        widget.setInstanceStyle("error")


if __name__ == "__main__":
    _app = QApplication(sys.argv)

    ui = ControllerWidget()
    ui.show()
    _app.exec_()
