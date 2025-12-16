"""The grid with main action buttons."""

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal


class MainButtonsWidget(QtWidgets.QWidget):
    sig_load = pyqtSignal()
    sig_extract = pyqtSignal()
    sig_removebg = pyqtSignal()
    sig_fft = pyqtSignal()
    sig_tdocsv = pyqtSignal()
    sig_rescsv = pyqtSignal()
    sig_save_nexus = pyqtSignal()

    def __init__(self):
        super().__init__()

        grid = QtWidgets.QGridLayout()

        self.button_load = QtWidgets.QPushButton("Load data", self)
        self.button_extract = QtWidgets.QPushButton("Extract TDO", self)
        self.button_removebg = QtWidgets.QPushButton("Remove background", self)
        self.button_fft = QtWidgets.QPushButton("FFT in 1/B", self)
        self.button_tdocsv = QtWidgets.QPushButton("Export TDO as CSV", self)
        self.button_rescsv = QtWidgets.QPushButton("Export results as CSV", self)
        self.button_save_nexus = QtWidgets.QPushButton("Save as NeXus", self)

        self.disable_buttons()

        self.connect_buttons()

        grid.addWidget(self.button_load, 0, 0)
        grid.addWidget(self.button_extract, 0, 1)
        grid.addWidget(self.button_removebg, 1, 0)
        grid.addWidget(self.button_fft, 1, 1)

        grid_save = QtWidgets.QHBoxLayout()
        grid_save.addWidget(self.button_tdocsv)
        grid_save.addWidget(self.button_rescsv)
        grid_save.addWidget(self.button_save_nexus)

        grid.addLayout(grid_save, 2, 0, 1, 2)

        self.setLayout(grid)

    def connect_buttons(self):
        self.button_load.clicked.connect(self.sig_load.emit)
        self.button_extract.clicked.connect(self.sig_extract.emit)
        self.button_removebg.clicked.connect(self.sig_removebg.emit)
        self.button_fft.clicked.connect(self.sig_fft.emit)
        self.button_tdocsv.clicked.connect(self.sig_tdocsv.emit)
        self.button_rescsv.clicked.connect(self.sig_rescsv.emit)
        self.button_save_nexus.clicked.connect(self.sig_save_nexus.emit)

    def disable_buttons(self):
        self.button_load.setEnabled(False)
        self.button_extract.setEnabled(False)
        self.button_removebg.setEnabled(False)
        self.button_fft.setEnabled(False)
        self.button_tdocsv.setEnabled(False)
        self.button_rescsv.setEnabled(False)
        self.button_save_nexus.setEnabled(False)

    def enable_buttons(self):
        self.button_load.setEnabled(False)
        self.button_extract.setEnabled(True)
        self.button_removebg.setEnabled(True)
        self.button_fft.setEnabled(True)
        self.button_tdocsv.setEnabled(True)
        self.button_rescsv.setEnabled(True)
        self.button_save_nexus.setEnabled(True)
