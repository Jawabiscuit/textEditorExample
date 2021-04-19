#!/usr/bin/env python
import os
import sys
import pickle

from PySide2.QtCore import (
    Qt,
    QResource,
    QSettings,
    QSize,
    QPoint,
    QByteArray,
)

from PySide2.QtGui import (
    QKeySequence,
    QTextCharFormat,
    QTextCursor,
)

from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QFileDialog,
    QAction,
    QToolBar,
    QFontComboBox,
)


__version__ = "0.0.1"


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


class WindowSettings(object):
    """
    Persistent user settings

    Window class must implement specific methods for settings to work.

    Override::

        def saveState(self):
            '''Re-implement to collect internal data to save'''
            return {}

        def restoreState(self, data):
            '''Re-implement to load saved internal data'''
            pass
    """

    def __init__(self,
                 widget,
                 companyName,
                 toolName,
                 toolVersion):
        self.widget = widget
        self.companyName = companyName
        self.toolName = toolName
        self.toolVersion = toolVersion

    def readSettings(self):
        """Read settings from disk, restore window geometry."""
        settings = QSettings(self.companyName, self.toolName)

        settings.beginGroup(str(self.toolVersion))
        self.widget.resize(settings.value("size", QSize(400, 200)))
        self.widget.move(settings.value("pos", QPoint(200, 200)))

        errors = []

        if hasattr(self.widget, "restoreState"):
            settings.beginGroup("widgetState")
            string = settings.value("state", QByteArray('(dp0\n.)'))
            if string:
                try:
                    state = pickle.loads(string)
                    self.widget.restoreState(state)
                except:
                    import traceback
                    errors.append(traceback.format_exc())
            # end widgetState
            settings.endGroup()
        # end toolVersion
        settings.endGroup()

        if errors:
            print(errors[-1])
            return False

        return True

    def writeSettings(self):
        """Write settings to disk, save window geometry"""
        settings = QSettings(self.companyName, self.toolName)

        settings.beginGroup('{}'.format(self.toolVersion))
        settings.setValue("size", self.widget.size())
        settings.setValue("pos", self.widget.pos())

        errors = []
        if hasattr(self.widget, "saveState"):
            settings.beginGroup("widgetState")

            try:
                state = pickle.dumps(self.widget.saveState())
            except:
                import traceback
                errors.append(traceback.format_exc())
            else:
                settings.setValue("state", QByteArray(state))

            # end widgetState
            settings.endGroup()

        # end toolVersion
        settings.endGroup()

        if errors:
            print(errors[-1])
            return False

        return True

    def clearSettings(self):
        """Remove all settings"""
        settings = QSettings(self.companyName, self.toolName)
        settings.clear()

    def save(self):
        """Save settings and close the widget"""
        result = self.writeSettings()
        self.widget.close()
        return result

    def restore(self):
        """Restore the previously saved settings"""
        self.widget.restoreState({})
        self.widget.close()
        self.clearSettings()
        # print("Settings cleared")

    def cancel(self):
        self.widget.close()
        self.readSettings()


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
    fontCombo = None

    @classmethod
    def init(cls, *args):
        cls.initGlobalStyle(*args)
        window = cls()
        window.setToolName("TextEditExample")
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

    @classmethod
    def setToolName(cls, value):
        """Set tool name for config and settings"""
        cls.ToolName = value or cls.__name__

    @classmethod
    def toolName(cls):
        """Tool name for config and settings"""
        return getattr(cls, "ToolName", cls.__name__)

    def __init__(self):
        super(MainWindow, self).__init__()
        self._filePath = None
        self._recentFiles = []
        self._maxNumRecentFiles = 4

    def initUi(self):
        """Construct a new UI instance"""
        self.setObjectName(self.__class__.__name__)
        self.setWindowTitle(self.toolName())
        self.text = text = QPlainTextEdit()
        self.setCentralWidget(text)
        self.addMenus()
        self.addActions()
        self.addFileToolBar()
        self.addTextToolBar()
        self.settings = WindowSettings(
            self, "XYZ-Company", self.toolName(), __version__)
        self.settings.readSettings()
        self.connectSignals()
        self.statusBar().showMessage("Ready")

    def saveState(self):
        """Collect internal data to save"""
        return {}

    def restoreState(self, data):
        """Load saved internal data"""
        pass

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
        """Create all menus"""
        self.fileMenu = self.menuBar().addMenu("&File")
        self.recentFilesMenu = self.fileMenu.addMenu("Open Recent")
        self.prefsMenu = self.menuBar().addMenu("&Prefs")
        self.themeMenu = self.prefsMenu.addMenu("Theme")
        self.helpMenu = self.menuBar().addMenu("&Help")

    def addActions(self):
        """Generate all actions"""
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

        self.recentFileActions = []
        for _ in range(self._maxNumRecentFiles):
            recentFileAction = QAction(self)
            recentFileAction.setVisible(False)
            self.recentFileActions.append(recentFileAction)
        self.recentFilesMenu.addActions(self.recentFileActions)

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

    def addFileToolBar(self):
        """Create toolbar to house file actions"""
        tb = QToolBar()
        tb.setWindowTitle("File Actions")
        tb.addActions([
            self.openAction,
            self.saveAction,
            self.closeAction,
        ])
        self.addToolBar(tb)

    def addTextToolBar(self):
        """Create toolbar to house text actions"""
        tb = QToolBar()
        tb.setWindowTitle("Text Actions")
        self.fontCombo = fontCombo = QFontComboBox(tb)
        tb.addWidget(self.fontCombo)
        self.addToolBar(tb)

        font = self.font()
        fontCombo.setFont(font)
        fontCombo.setCurrentFont(font)

    def connectSignals(self):
        """Connect all signals to slots"""
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.save)
        self.saveAsAction.triggered.connect(self.saveAs)
        self.closeAction.triggered.connect(self.close)
        for recentfAction in self.recentFileActions:
            recentfAction.triggered.connect(self.openRecent)
        self.darkAction.triggered.connect(self.setDarkTheme)
        self.lightAction.triggered.connect(self.initGlobalStyle)
        self.aboutAction.triggered.connect(self.about)
        self.aboutQtAction.triggered.connect(QApplication.instance().aboutQt)
        self.fontCombo.currentFontChanged.connect(self.currentFontChanged)
        QApplication.instance().aboutToQuit.connect(self.settings.save)

    def closeEvent(self, event):
        """Perform all actions that must happen upon closing the window"""
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
        """Save the text to disk"""
        if self._filePath is None:
            self.saveAs()
        else:
            with open(self._filePath, "w") as f:
                f.write(self.text.toPlainText())
            self.text.document().setModified(False)

    def saveAs(self):
        """Save the text to disk, file name not previously stored"""
        filePath = QFileDialog.getSaveFileName(self, "Save As")[0]
        if filePath:
            self._filePath = filePath
            self.save()

    def openFile(self):
        """Insert text into text edit from contents of a file on disk"""
        filePath = QFileDialog.getOpenFileName(self, "Open")[0]
        self._loadFile(filePath)

    def openRecent(self):
        """Open the most recently edited file"""
        action = self.sender()
        if action:
            self._loadFile(action.data())

    def _loadFile(self, filePath):
        if not os.path.isfile(filePath):
            QMessageBox.warning(
                self,
                "Could not open file.\n"
                "File path does not exist: {}".format(filePath),
            )
            return
        if filePath:
            self.text.setPlainText(open(filePath).read())
        self._updateCurrentFile(filePath)

    def _updateCurrentFile(self, filePath):
        """Update UI with new file information"""
        self._filePath = filePath

        while filePath in self._recentFiles:
            self._recentFiles.remove(filePath)
        self._recentFiles.insert(0, self._filePath)

        if len(self._recentFiles) > self._maxNumRecentFiles:
            self._recentFiles = self._recentFiles[:self._maxNumRecentFiles]

        self._updateRecentFileActions()

    def _updateRecentFileActions(self):
        """Update the recent files list"""
        recentFiles = self._recentFiles
        if len(recentFiles) <= self._maxNumRecentFiles:
            itEnd = len(recentFiles)
        else:
            itEnd = self._maxNumRecentFiles

        for i, recentFile in enumerate(recentFiles):
            action = self.recentFileActions[i]
            action.setText(os.path.basename(recentFile))
            action.setData(recentFile)
            action.setVisible(True)

        for ii, action in enumerate(self.recentFileActions):
            if ii > itEnd:
                action.setVisible(False)

    def currentFontChanged(self, font):
        """Do when font is changed using the font combo"""
        fmt = QTextCharFormat()
        family = font.family()
        fmt.setFontFamily(family)
        self.mergeFormatOnWordOrSelection(fmt)

    def mergeFormatOnWordOrSelection(self, fmt):
        """
        Change format of text that is selected, or change text under cursor
        """
        cursor = self.text.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.text.mergeCurrentCharFormat(fmt)

    def about(self):
        """Show the 'about' dialog for tool"""
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

    ui = MainWindow.init()
    ui.show()
    _app.exec_()
