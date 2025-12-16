"""Worker class."""

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ..processors import TDOProcessor


class DataWorker(QObject):
    sig_load_finished = pyqtSignal()
    sig_extract_finished = pyqtSignal()
    sig_align_finished = pyqtSignal()
    sig_removebg_finished = pyqtSignal()
    sig_fft_finished = pyqtSignal()
    sig_batch_progress = pyqtSignal(int)
    sig_batch_finished = pyqtSignal()
    sig_tdocsv_finished = pyqtSignal()
    sig_rescsv_finished = pyqtSignal()
    sig_save_nexus_finished = pyqtSignal()
    sig_load_csv_finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.proc = TDOProcessor(*args, **kwargs)
        if self.proc.is_nexus_file:
            self.is_dataloaded = True
        else:
            self.is_dataloaded = False

    @pyqtSlot()
    def load_data(self):
        """Load data."""
        self.proc.load_oscillo()
        self.is_dataloaded = True
        self.sig_load_finished.emit()

    @pyqtSlot()
    def extract_tdo(self):
        """Extract TDO signal."""
        self.proc.extract_tdo()
        self.sig_extract_finished.emit()

    def align_field(self):
        self.proc.align_field()
        self.sig_align_finished.emit()

    @pyqtSlot()
    def remove_background(self):
        """Remove background and oversample in 1/B."""
        self.proc.remove_background()
        self.sig_removebg_finished.emit()

    @pyqtSlot()
    def fft(self):
        """FFT in 1/B."""
        self.proc.fft_inverse_field()
        self.sig_fft_finished.emit()

    @pyqtSlot()
    def batch_process(self):
        return

    @pyqtSlot(str)
    def save_tdo_csv(self, fname: str | Path):
        """Save TDO signal as CSV."""
        self.proc.save_tdo_csv(filename=fname)
        self.sig_tdocsv_finished.emit()

    @pyqtSlot(str)
    def save_results_csv(self, fname: str | Path):
        """Save results as CSV."""
        self.proc.save_results_csv(filename_prefix=fname)
        self.sig_rescsv_finished.emit()

    @pyqtSlot(str)
    def save_as_nexus(self, fname: str | Path):
        """Save data as NeXus."""
        self.proc.save(filename=fname)
        self.sig_save_nexus_finished.emit()

    @pyqtSlot(str)
    def load_csv_file(self, fname: str):
        self.proc.load_csv(fname)
        self.sig_load_csv_finished.emit()
