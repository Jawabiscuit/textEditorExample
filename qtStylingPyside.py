#! /bin/env python
import os
import sys

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
    def init(cls, args):
        cls.initGlobalStyle(args)
        widget = cls()
        widget.setWindowTitle(cls.__name__)
        widget.initUi()
        widget.initInstanceStyle(args)
        return widget

    @classmethod
    def initGlobalStyle(cls, args):
        """
        Initialize style that will be used across the application
        """
        pass

    def initInstanceStyle(self, args):
        """
        Initialize style that will be applied to this instance
        """
        pass

    def initUi(self):
        self.setObjectName(self.__class__.__name__)
        self.button = button = QPushButton("Button", self)
        self.group = group = QGroupBox('Group', self)

        self.widgets = widgets = [
            button,
        ]
        innerLayout = QVBoxLayout(group)
        for widget in widgets:
            innerLayout.addWidget(widget)
        innerLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(group)


if __name__ == "__main__":
    from collections import deque

    # Style to window type map
    styleMap = dict(
        default=DefaultWidget,
    )
    _app = QApplication(sys.argv)

    # Process the arguments
    mode = "default"
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
        sys.exit(1)

    ui = uiType.init(args)
    ui.show()
    _app.exec_()
