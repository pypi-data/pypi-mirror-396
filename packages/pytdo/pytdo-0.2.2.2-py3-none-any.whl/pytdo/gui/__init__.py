"""Graphical user interface module."""

from PyQt6 import QtWidgets

from ._core import MainWindow


def run(exec: bool = True):
    """
    Build and run the GUI.

    Set `exec=False` in an interactive prompt to interact with the GUI from the shell.
    """
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    if exec:
        app.exec()
    else:
        return win
