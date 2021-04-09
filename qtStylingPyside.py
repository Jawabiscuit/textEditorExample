#! /bin/env python
import os
import sys

from PySide2.QtCore import (
    Qt,
    QResource,
    Signal,
)

from PySide2.QtGui import (
    QPalette,
    QColor,
    QBrush,
)

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QStyle,
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
        QApplication.instance().setPalette(
            QApplication.style().standardPalette())

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


class PaletteWidget(DefaultWidget):
    """
    A widget that customizes its appearance by assigning a palette

    .. note::

        Palettes are NOT recommended. They are inconsistent, confusing and can
        only customize color. See `Qt docs QPalette`_

    .. _Qt docs QPalette: https://doc.qt.io/qt-5/qpalette.html
    """

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application
        """
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(150, 150, 255))
        palette.setBrush(QPalette.Window, QBrush(Qt.darkMagenta, Qt.Dense7Pattern))
        palette.setColor(QPalette.Base, Qt.darkGreen)
        palette.setColor(QPalette.AlternateBase, Qt.darkMagenta)
        QApplication.instance().setPalette(palette)

    def initInstanceStyle(self, *args):
        """
        Initialize style that will be applied to this instance
        """
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Button, Qt.darkRed)
        palette.setColor(QPalette.ButtonText, Qt.red)
        palette.setColor(QPalette.Base, Qt.darkRed)
        palette.setColor(QPalette.AlternateBase, Qt.red)
        self.button.setPalette(palette)
        self.line.setPalette(palette)


class QssWidget(DefaultWidget):

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application
        """
        QApplication.instance().setStyleSheet(cls.getStyleSheet())
        # For the purposes of demo'ing If a palette has been applied previously
        # as well as reset back to standard, simply running setStyleSheet() will
        # unexpectedly re-apply palette settings!
        QApplication.instance().setPalette(
            QApplication.style().standardPalette())

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
                           palette=PaletteWidget,
                           qss=QssWidget,)

    def __init__(self):
        super(ControllerWidget, self).__init__()

        widget = ControllerWidget._demoWidget = \
            ControllerWidget._WidgetType.init()
        widget.show()

        self.styleCombo = styleCombo = QComboBox()
        applyButton = QPushButton("&Apply")
        errorButton = QPushButton("Error")
        quitButton = QPushButton("&Quit")

        applyButton.setToolTip(
            "Apply the style selected in the drop-down")
        errorButton.setToolTip(
            "Apply styling to individual widgets indicating an error")
        quitButton.setToolTip(
            "Quit the application")

        styleCombo.addItems(sorted(self.widget_type_map.keys()))

        layout = QVBoxLayout(self)
        layout.addWidget(styleCombo)
        layout.addWidget(applyButton)
        layout.addWidget(errorButton)
        layout.addWidget(quitButton)
        layout.addStretch()

        applyButton.clicked.connect(self.onApplyClicked)
        errorButton.clicked.connect(self.onErrorClicked)
        quitButton.clicked.connect(self.close)

    def closeEvent(self, event):
        ControllerWidget._demoWidget.deleteLater()
        event.accept()

    def onApplyClicked(self):
        widget = ControllerWidget._demoWidget
        uiSelection = self.styleCombo.currentText()
        uiType = self.widget_type_map.get(uiSelection)
        ControllerWidget._WidgetType = uiType
        new = ControllerWidget._demoWidget = uiType.init()
        new.show()
        widget.close()

    def onErrorClicked(self):
        widget = ControllerWidget._demoWidget
        widget.setInstanceStyle("error")


if __name__ == "__main__":
    _app = QApplication(sys.argv)

    ui = ControllerWidget()
    ui.show()
    _app.exec_()
