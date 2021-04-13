#! /bin/env python
import os
import sys

from PySide2.QtCore import (
    Qt,
    QResource,
    # Signal,
    QTimer,
)

from PySide2.QtGui import (
    QPalette,
    QColor,
    QBrush,
    QPen,
    QPainter,
    QKeySequence,
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
    QStyleFactory,
    QStyleOptionComboBox,
    QStylePainter,
    QProgressBar,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QFileDialog,
    QAction,
    QCheckBox,
)


__version__ = "0.0.1"


class DefaultWidget(QWidget):
    """Default widget with no style mods"""

    button = None
    line = None
    combo = None
    timer = None
    progress = None

    ComboBoxType = QComboBox

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
    def setGlobalStyle(cls):
        """
        Set style applied globally in a running application
        """
        pass

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
        self.combo = combo = self.ComboBoxType(self)
        for i in '123':
            combo.addItem('Choice ' + i)
        self.progress = progress = self.createProgressBar()

        widgets = [
            button,
            line,
            combo,
            progress,
        ]
        innerLayout = QVBoxLayout(group)
        for widget in widgets:
            innerLayout.addWidget(widget)
        innerLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(group)

    def createProgressBar(self):
        progressBar = QProgressBar()
        progressBar.setRange(0, 1000)
        progressBar.setValue(0)

        self.timer = timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(100)

        return progressBar

    def advanceProgressBar(self):
        curVal = self.progress.value()
        maxVal = self.progress.maximum()
        self.progress.setValue((curVal + (maxVal - curVal) / 10) + 9)
        if self.progress.value() == 1000:
            self.timer.stop()


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


class StyleWidget(DefaultWidget):
    """
    A widget that customizes its appearance by changing style factories

    .. note::

        Doesn't work in Windows, windows disappear and app exits quietly.

        Tried setting style as early as possible, before app construction,
        and still application quits.
    """

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application

        .. note::

            A limited set of pre-defined styles are available

            If desired it is possible to create a completely custom style, see
            the links below...

            Best left for major application creation in C++,
            not recommended for Python

            https://doc.qt.io/qt-5/qstyle.html#creating-a-custom-style
            https://doc.qt.io/qt-5/qstyleplugin.html
            https://doc.qt.io/qt-5/qstylefactory.html

        """
        print("\n\nAvailable styles: " + ", ".join(
            sorted(QStyleFactory.keys())))
        style = "Fusion"
        for arg in args:
            if arg.lower() in [k.lower() for k in QStyleFactory.keys()]:
                style = arg
        style = QStyleFactory.create(style)
        QApplication.instance().setStyle(style)


def getStyleSheet():
    """
    Reads in the style sheet resource
    """
    dirname = os.path.dirname(__file__)
    rccPath = os.path.join(dirname, "resources.rcc")
    QResource.registerResource(rccPath)
    qssPath = os.path.join(dirname, "sample.css")
    with open(qssPath, "r") as fh:
        return fh.read()


class QssWidget(DefaultWidget):

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application
        """
        QApplication.instance().setStyleSheet(getStyleSheet())
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


class PaintedComboBox(QComboBox):
    """
    A combo box that allows for custom painting
    """

    def paintEvent(self, event):
        """
        A customized paint event

        .. note::

            Global styling such as style sheets can be combined with a custom
            paint event using the ``QStylePainter``. In this case we customize
            the text displayed for our combo box without losing the assigned style.
        """
        options = QStyleOptionComboBox()
        options.initFrom(self)

        # Customize the painting options to control the way the combo box is
        # painted by QStyle.
        options.currentText = 'MY CUSTOM TEXT'
        options.frame = False

        # Use the QStylePainter to ensure styling is still applied.
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.CC_ComboBox, options)
        painter.drawControl(QStyle.CE_ComboBoxLabel, options)


class PaintedWidget(DefaultWidget):
    """
    A widget that customizes its appearance by manually painting its contents
    """
    ComboBoxType = PaintedComboBox

    @classmethod
    def setGlobalStyle(cls):
        """
        Apply the style that will be used across the application
        """
        QApplication.instance().setStyleSheet(getStyleSheet())

    def paintEvent(self, event):
        """
        A customized paint event

        .. note::

            Manually painting a widget takes complete, manual control of its
            appearance. To do so, simply override the "paintEvent" method of any
            QWidget sub-class. Calling the inherited paintEvent method (e.g.
            QWidget.paintEvent(self)) will result in the original content of
            the widget to be painted. Painting additional custom content either
            before or after the inherited call of course paints that content
            under or over the original content.

        """
        geometry = self.geometry()

        # All painting coordinates are in a local coordinate space ranging from
        # 0, 0 to self.width(), self.height().
        geometry.moveTo(0, 0)

        # When drawing the rectangle below the pen will end up being drawn off
        # the bottom and right edges of the widget and will be automatically
        # clipped. We can adjust the bottom right corner back by a pixel so the
        # outline appears inside the widget.
        geometry.adjust(0, 0, -1, -1)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # The painter's assigned brush is used to fill any 2D vector shapes that
        # are drawn including polygons, rectangles and ellipses.
        painter.setBrush(QBrush(Qt.darkMagenta))

        # The painter's assigned pen is used to outline any vector shapes that
        # are drawn including lines, polygons, rectangles, ellipses and arcs.
        # The pen specifies the color and thickness of the line as well as other
        # rendering properties.
        painter.setPen(QPen(Qt.magenta))

        # Draw a rectangle over the entire background.
        painter.drawRect(geometry)

        # Draw lines corner to corner to create an X.
        painter.drawLine(geometry.topLeft(), geometry.bottomRight())
        painter.drawLine(geometry.bottomLeft(), geometry.topRight())


class ControllerWidget(QWidget):

    _WidgetType = DefaultWidget
    _demoWidget = None

    widget_type_map = dict(default=DefaultWidget,
                           palette=PaletteWidget,
                           painted=PaintedWidget,
                           qss=QssWidget,)

    def __init__(self):
        super(ControllerWidget, self).__init__()

        self.setWindowTitle(self.__class__.__name__)

        widget = ControllerWidget._demoWidget = \
            ControllerWidget._WidgetType.init()
        widget.show()

        self.styleCombo = styleCombo = QComboBox()
        applyButton = QPushButton("&Apply")
        errorButton = QPushButton("Error")
        addButton = QPushButton("Add")
        quitButton = QPushButton("&Quit")

        applyButton.setToolTip(
            "Apply the style selected in the drop-down")
        errorButton.setToolTip(
            "Apply styling to individual widgets indicating an error")
        addButton.setToolTip(
            "Add QSS styling to test mixing with custom paintEvent")
        quitButton.setToolTip(
            "Quit the application")

        styleCombo.addItems(sorted(self.widget_type_map.keys()))

        layout = QVBoxLayout(self)
        layout.addWidget(styleCombo)
        layout.addWidget(applyButton)
        layout.addWidget(addButton)
        layout.addWidget(errorButton)
        layout.addWidget(quitButton)
        layout.addStretch()

        applyButton.clicked.connect(self.onApplyClicked)
        addButton.clicked.connect(self.onAddClicked)
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

    def onAddClicked(self):
        widget = ControllerWidget._demoWidget
        widget.setGlobalStyle()


class MainWindow(QMainWindow):
    text = None
    fileMenu = None
    openAction = None
    saveAction = None
    saveAsAction = None
    closeAction = None
    prefsMenu = None
    themeMenu = None
    darkAction = None
    lightAction = None
    helpMenu = None
    aboutAction = None
    aboutQtAction = None

    @classmethod
    def init(cls, *args):
        cls.initGlobalStyle(*args)
        window = cls()
        window.initUi()
        window.initWindowStyle(*args)
        return window

    @classmethod
    def initGlobalStyle(cls, *args):
        """
        Initialize style that will be used across the application
        """
        QApplication.instance().setStyleSheet("")
        QApplication.instance().setPalette(
            QApplication.style().standardPalette())

    @classmethod
    def setDarkTheme(cls):
        """
        Switch UI to a dark theme
        """
        QApplication.instance().setStyleSheet(getStyleSheet())
        QApplication.instance().setPalette(
            QApplication.style().standardPalette())

    def __init__(self):
        super(MainWindow, self).__init__()
        self._filePath = None

    def initUi(self):
        self.setObjectName(self.__class__.__name__)
        self.text = text = QPlainTextEdit()
        self.setCentralWidget(text)
        self.addMenus()
        self.addActions()
        self.connectSignals()
        self.statusBar().showMessage("Ready")

    def initWindowStyle(self, *args):
        """
        Initialize style that will be applied to this instance
        """
        if "error" in args:
            self.text.setProperty('hasError', True)

    def setWindowStyle(self, *args):
        """
        Set style applied to this instance in a running application
        """
        widgets = [
            self.text,
        ]
        if "error" in args:
            self.text.setProperty('hasError', True)
            for widget in widgets:
                widget.style().unpolish(widget)
                widget.style().polish(widget)

    def addMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.prefsMenu = self.menuBar().addMenu("&Prefs")
        self.themeMenu = self.prefsMenu.addMenu("Theme")
        self.helpMenu = self.menuBar().addMenu("&Help")

    def addActions(self):
        self.openAction = openAction = QAction("&Open", self)
        openAction.setShortcut(QKeySequence.Open)
        self.saveAction = saveAction = QAction("&Save", self)
        saveAction.setShortcut(QKeySequence.Save)
        self.saveAsAction = saveAsAction = QAction("Save &As...", self)
        saveAsAction.setShortcut(QKeySequence.SaveAs)
        self.closeAction = closeAction = QAction("&Close", self)
        closeAction.setShortcut(QKeySequence.Close)
        self.fileMenu.addActions([
            openAction,
            saveAction,
            saveAsAction,
            closeAction,
        ])  
        
        self.darkAction = darkAction = QAction("Dark", self) 
        self.lightAction = lightAction = QAction("Light", self)
        self.themeMenu.addActions([
            darkAction, lightAction,
        ])

        self.aboutAction = aboutAction = QAction("&About", self)
        aboutAction.setShortcut(QKeySequence.WhatsThis)
        self.aboutQtAction = aboutQtAction = QAction("About &Qt", self)
        self.helpMenu.addActions([
            aboutAction,
            aboutQtAction,
        ])

    def connectSignals(self):
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.save)
        self.saveAsAction.triggered.connect(self.saveAs)
        self.closeAction.triggered.connect(self.close)
        self.darkAction.triggered.connect(self.setDarkTheme)
        self.lightAction.triggered.connect(self.initGlobalStyle)
        self.aboutAction.triggered.connect(self.about)
        self.aboutQtAction.triggered.connect(QApplication.instance().aboutQt)

    def closeEvent(self, event):
        if not self.text.document().isModified():
            return
        answer = QMessageBox.question(
            self, None,
            "You have unsaved changes. Save before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        if answer & QMessageBox.Save:
            self.save()
        elif answer & QMessageBox.Cancel:
            event.ignore()

    def save(self):
        if self._filePath is None:
            self.saveAs()
        else:
            with open(self._filePath, "w") as f:
                f.write(self.text.toPlainText())
            self.text.document().setModified(False)

    def saveAs(self):
        filePath = QFileDialog.getSaveFileName(self, "Save As")[0]
        if filePath:
            self._filePath = filePath
            self.save()

    def openFile(self):
        filePath = QFileDialog.getOpenFileName(self, "Open")[0]
        if filePath:
            self.text.setPlainText(open(filePath).read())

    def about(self):
        text = (
            "<center>"
            "<h1>Text Editor</h1>"
            "&#8291;"
            "<img src=icon.svg>"
            "</center>"
            "<p>Version {}<br/>"
            "Copyright &copy; Company Inc.</p>".format(__version__))
        QMessageBox.about(self, "About Text Editor", text)


if __name__ == "__main__":
    _app = QApplication(sys.argv)
    _app.setStyle("Fusion")

    # ui = ControllerWidget()
    ui = MainWindow.init()
    ui.show()
    _app.exec_()
