"""Application for TDO analysis."""

from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from pyuson import gui

from . import widgets
from ._workers import DataWorker

ICON_PATH = str(Path(__file__).parent / "assets" / "icon.png")
REGEXP_EXPID_SEPARATORS = r"[_-]"
PROGRAM_NAME = "pytdo"  # to get the relevant logger
OUT_FORMAT = (".txt", ".csv", ".tsv", ".out")
LOG_LEVEL = "INFO"


class MainWindow(gui.BaseMainWindow):
    sig_worker_extract = pyqtSignal()
    sig_worker_removebg = pyqtSignal()
    sig_worker_fft = pyqtSignal()
    sig_worker_tdocsv = pyqtSignal(str)
    sig_worker_rescsv = pyqtSignal(str)
    sig_worker_loadcsv = pyqtSignal(str)

    wbatch: gui.widgets.BatchProcessingWidget
    wbuttons: widgets.MainButtonsWidget
    wconfiguration: widgets.ConfigurationWidget
    wfiles: gui.widgets.FileBrowserWidget
    wplots: widgets.GraphsWidget
    worker: DataWorker

    def __init__(self):
        # Register the widgets
        self._type_wbatch = gui.widgets.BatchProcessingWidget
        self._type_wbuttons = widgets.MainButtonsWidget
        self._type_wconfiguration = widgets.ConfigurationWidget
        self._type_wfiles = gui.widgets.FileBrowserWidget
        self._type_wplots = widgets.GraphsWidget
        self._param_content = widgets.ParamContent
        self._type_worker = DataWorker

        super().__init__()

        # Initialize window
        self.setGeometry(300, 300, 900, 450)
        self.setWindowTitle("TDO Analyzer")

    def init_parameter_tree(self):
        super().init_parameter_tree()

        # Connect
        self.wconfiguration.sig_syncroi_changed.connect(self.syncroi_changed)

    def init_buttons(self):
        super().init_buttons()

        # Connect
        self.wbuttons.sig_extract.connect(self.extract_tdo)
        self.wbuttons.sig_removebg.connect(self.remove_background)
        self.wbuttons.sig_fft.connect(self.fft)
        self.wbuttons.sig_tdocsv.connect(self.save_tdo_csv)
        self.wbuttons.sig_rescsv.connect(self.save_results_csv)

    def init_plots(self):
        super().init_plots()

        # Connect ROIs
        self.wplots.sig_roi1_changed.connect(self.roi1_changed)
        self.wplots.sig_roi2_changed.connect(self.roi2_changed)
        self.wconfiguration.settings_parameters.child(
            "poly_window"
        ).sigValueChanged.connect(self.update_roi_from_poly)
        self.wconfiguration.settings_parameters.child(
            "fft_window"
        ).sigValueChanged.connect(self.update_roi_from_fft)

    def init_log(self):
        super().init_log(PROGRAM_NAME, log_level=LOG_LEVEL)

    def connect_worker(self):
        super().connect_worker()

        # Extract signal
        self.sig_worker_extract.connect(self.worker.extract_tdo)
        self.worker.sig_extract_finished.connect(self.extract_tdo_finished)

        # Remove background
        self.sig_worker_removebg.connect(self.worker.remove_background)
        self.worker.sig_removebg_finished.connect(self.remove_background_finished)

        # FFT
        self.sig_worker_fft.connect(self.worker.fft)
        self.worker.sig_fft_finished.connect(self.fft_finished)

        # Save TDO signal as CSV
        self.sig_worker_tdocsv.connect(self.worker.save_tdo_csv)
        self.worker.sig_tdocsv_finished.connect(self.save_tdo_csv_finished)

        # Save results as CSV
        self.sig_worker_rescsv.connect(self.worker.save_results_csv)
        self.worker.sig_rescsv_finished.connect(self.save_results_csv_finished)

        # Load from CSV
        self.sig_worker_loadcsv.connect(self.worker.load_csv_file)
        self.worker.sig_load_csv_finished.connect(self.load_csv_file_finished)

    @pyqtSlot()
    def extract_tdo(self):
        if not self.check_data_loaded():
            return
        self.disable_buttons()
        self.sig_worker_extract.emit()

    @pyqtSlot()
    def align_field_finished(self):
        self.ind_bup = self.worker.proc.inds_inc
        self.ind_bdown = self.worker.proc.inds_dec

    @pyqtSlot()
    def extract_tdo_finished(self):
        self.align_field_finished()
        self.plot_tdo()

        # Clear plots since source signal was changed
        self.wplots.tdo_field.clearPlots()
        self.wplots.tdo_inverse_field.clearPlots()
        self.wplots.fft.clearPlots()

        self.enable_buttons()

    @pyqtSlot()
    def remove_background(self):
        if not self.check_tdo_extracted():
            self.logger.error("TDO signal was not extracted.")
            return
        self.disable_buttons()
        self.sig_worker_removebg.emit()

    @pyqtSlot()
    def remove_background_finished(self):
        self.plot_tdo_detrended()
        self.enable_buttons()

    @pyqtSlot()
    def fft(self):
        if not self.check_data_loaded():
            return
        self.disable_buttons()
        self.sig_worker_fft.emit()

    @pyqtSlot()
    def fft_finished(self):
        self.plot_fft()
        self.enable_buttons()

    @pyqtSlot()
    def save_tdo_csv(self):
        """Save extracted TDO signal as CSV."""
        if not self.check_data_loaded():
            return

        self.disable_buttons()

        default_fname = self.worker.proc.get_csv_filename(suffix="-tdo")
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save TDO signals as...",
            default_fname,
            "Text files (*.txt, *.csv, *.tsv, *.out)",
        )

        if fname:
            self.sig_worker_tdocsv.emit(fname)
        else:
            self.logger.error("[GUI] Invalid output file name for CSV file.")
            self.save_tdo_csv_finished()

    @pyqtSlot()
    def save_tdo_csv_finished(self):
        self.enable_buttons()

    @pyqtSlot()
    def save_results_csv(self):
        """Save final results as CSV."""
        if not self.check_data_loaded():
            return

        self.disable_buttons()

        default_fname = self.worker.proc.get_csv_filename(suffix="-results")
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save TDO signals as...",
            default_fname,
            "Text files (*.txt, *.csv, *.tsv)",
        )

        if fname:
            self.sig_worker_rescsv.emit(fname)
        else:
            self.logger.error("[GUI] Invalid output file name for CSV file.")
            self.save_tdo_csv_finished()

    @pyqtSlot()
    def save_results_csv_finished(self):
        self.enable_buttons()

    def load_csv_file(self, file_path: str):
        if not self.check_config_loaded():
            self.logger.error(
                "Can't load a CSV file without loading a configuration file first."
            )
            return

        self.disable_buttons()
        self.sig_worker_loadcsv.emit(file_path)

    @pyqtSlot()
    def load_csv_file_finished(self):
        self.extract_tdo_finished()
        self.remove_background_finished()
        self.fft_finished()

    @pyqtSlot()
    def batch_process(self):
        self.logger.warning("Not implemented.")

    @pyqtSlot()
    def roi1_changed(self):
        # Get time range
        xmin, xmax = self.wplots.roi.getRegion()

        # Check the ROI was changed since it was created
        if (xmin, xmax) == (0, 1):
            return

        # Update parameter in the tree if the region was changed from the graph
        if self.flag_do_update_roi:
            self.flag_do_update_roi = False
            self.wconfiguration.settings_parameters["poly_window"] = (
                self.wconfiguration.get_numbers_from_text([xmin, xmax])
            )
            self.flag_do_update_roi = True

        self.remove_background()

    @pyqtSlot()
    def roi2_changed(self):
        # Get time range
        xmin, xmax = self.wplots.roi2.getRegion()

        # Check the ROI was changed since it was created
        if (xmin, xmax) == (0, 1):
            return

        # Update parameter in the tree if the region was changed from the graph
        if self.flag_do_update_roi:
            self.flag_do_update_roi = False
            self.wconfiguration.settings_parameters["fft_window"] = (
                self.wconfiguration.get_numbers_from_text([xmin, xmax])
            )
            self.flag_do_update_roi = True

    @pyqtSlot()
    def update_roi_from_poly(self):
        """
        Update the ROI in the graph from "Fit: field window" in the parameter tree.

        Use `flag_do_update_roi` to check if the change is done programatically or from
        the user.
        In the first case, this function is ignored.
        In the second case, the ROI in the graph is updated and computation is
        triggered.
        """
        if self.flag_do_update_roi:
            # ROI changed from the tree, update the ROI in the graph
            new_region = self.wconfiguration.get_numbers_from_text(
                self.wconfiguration.settings_parameters["poly_window"]
            )
            if len(new_region) != 2:
                self.logger.error(f"[GUI] Invalid analysis window : {new_region}")
                return
            elif new_region[0] >= new_region[1]:
                self.logger.error(f"[GUI] Invalid analysis window : {new_region}")
                return

            # Update ROI, without recomputing
            self.flag_do_update_roi = False
            self.wplots.roi.setRegion(new_region)
            self.flag_do_update_roi = True
        else:
            return

    @pyqtSlot()
    def update_roi_from_fft(self):
        """
        Update the ROI in the graph from "FFT: field window" in the parameter tree.

        Use `flag_do_update_roi` to check if the change is done programatically or from
        the user.
        In the first case, this function is ignored.
        In the second case, the ROI in the graph is updated and computation is
        triggered.
        """
        if self.flag_do_update_roi:
            # ROI changed from the tree, update the ROI in the graph
            new_region = self.wconfiguration.get_numbers_from_text(
                self.wconfiguration.settings_parameters["fft_window"]
            )
            if len(new_region) != 2:
                self.logger.error(f"[GUI] Invalid analysis window : {new_region}")
                return
            elif new_region[0] >= new_region[1]:
                self.logger.error(f"[GUI] Invalid analysis window : {new_region}")
                return

            # Update ROI, without recomputing
            self.flag_do_update_roi = False
            self.wplots.roi.setRegion(new_region)
            self.flag_do_update_roi = True
        else:
            return

    def plot_tdo(self):
        """Plot TDO signal versus field and time."""
        if not self.check_field_aligned():
            self.worker.align_field()

        ## TDO signal versus field
        self.wplots.sig_field.clearPlots()
        self.wplots.sig_field.setAutoVisible(y=True)

        # Decreasing magnetic field
        self.wplots.sig_field.plot(
            self.worker.proc.get_data_processed("magfield")[self.ind_bdown],
            self.worker.proc.get_data_processed(self.worker.proc._tdo_name)[
                self.ind_bdown
            ],
            pen=self.wplots.pen_bdown,
            name="B down",
        )
        # Increasing magnetic field
        self.wplots.sig_field.plot(
            self.worker.proc.get_data_processed("magfield")[self.ind_bup],
            self.worker.proc.get_data_processed(self.worker.proc._tdo_name)[
                self.ind_bup
            ],
            pen=self.wplots.pen_bup,
            name="B up",
        )

        ## TDO signal versus time
        self.wplots.sig_time.clearPlots()
        self.wplots.sig_time.setAutoVisible(y=True)

        # Decreasing magnetic field
        self.wplots.sig_time.plot(
            self.worker.proc.get_data_processed("time_exp")[self.ind_bdown],
            self.worker.proc.get_data_processed(self.worker.proc._tdo_name)[
                self.ind_bdown
            ],
            pen=self.wplots.pen_bdown,
            name="B down",
        )
        # Increasing magnetic field
        self.wplots.sig_time.plot(
            self.worker.proc.get_data_processed("time_exp")[self.ind_bup],
            self.worker.proc.get_data_processed(self.worker.proc._tdo_name)[
                self.ind_bup
            ],
            pen=self.wplots.pen_bup,
            name="B up",
        )

    def plot_tdo_detrended(self):
        """Plot TDO signal with background removed."""
        # Get parameters
        offset = self.worker.proc.cfg.settings.offset
        lower_b, upper_b = self.worker.proc.cfg.settings.fft_window

        # Sync fit and FFT windows
        if lower_b == -1:
            lower_b = self.worker.proc.cfg.settings.poly_window[0]
        if upper_b == -1:
            upper_b = self.worker.proc.cfg.settings.poly_window[1]

        ## TDO detrended versus field
        self.wplots.tdo_field.clearPlots()
        self.wplots.tdo_field.setAutoVisible(y=True)
        self.wplots.sig_field.clearPlots()
        self.plot_tdo()

        # Decreasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_det_dec_name, checkonly=True
        ):
            self.wplots.tdo_field.plot(
                self.worker.proc.get_data_processed("magfield")[self.ind_bdown],
                self.worker.proc.get_data_processed(self.worker.proc._tdo_det_dec_name)
                - offset / 2,
                pen=self.wplots.pen_bdown,
                name="B down",
            )
        # Increasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_det_inc_name, checkonly=True
        ):
            self.wplots.tdo_field.plot(
                self.worker.proc.get_data_processed("magfield")[self.ind_bup],
                self.worker.proc.get_data_processed(self.worker.proc._tdo_det_inc_name)
                + offset / 2,
                pen=self.wplots.pen_bup,
                name="B up",
            )
        self.wplots.tdo_field.setXRange(lower_b, upper_b, padding=0.05)

        # Fit decreasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_name + "_fit_dec", checkonly=True
        ):
            self.wplots.sig_field.plot(
                self.worker.proc.get_data_processed("magfield")[self.ind_bdown],
                self.worker.proc.get_data_processed(
                    self.worker.proc._tdo_name + "_fit_dec"
                ),
                pen=self.wplots.pen_fitdown,
                name="Fit B down",
            )
        # Fit increasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_name + "_fit_inc", checkonly=True
        ):
            self.wplots.sig_field.plot(
                self.worker.proc.get_data_processed("magfield")[self.ind_bup],
                self.worker.proc.get_data_processed(
                    self.worker.proc._tdo_name + "_fit_inc"
                ),
                pen=self.wplots.pen_fitbup,
                name="Fit B up",
            )

        ## TDO detrended versus 1/B
        self.wplots.tdo_inverse_field.clearPlots()
        self.wplots.tdo_inverse_field.setAutoVisible(y=True)

        # Decreasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_inv_dec_name, checkonly=True
        ):
            self.wplots.tdo_inverse_field.plot(
                self.worker.proc.get_data_processed("magfield_inverse_dec"),
                self.worker.proc.get_data_processed(self.worker.proc._tdo_inv_dec_name)
                - offset / 2,
                pen=self.wplots.pen_bdown,
                name="B down",
            )
        # Increasing magnetic field
        if self.worker.proc.get_data_processed(
            self.worker.proc._tdo_inv_inc_name, checkonly=True
        ):
            self.wplots.tdo_inverse_field.plot(
                self.worker.proc.get_data_processed("magfield_inverse_inc"),
                self.worker.proc.get_data_processed(self.worker.proc._tdo_inv_inc_name)
                + offset / 2,
                pen=self.wplots.pen_bup,
                name="B up",
            )
        self.wplots.tdo_inverse_field.setXRange(1 / upper_b, 1 / lower_b, padding=0.05)

    def plot_fft(self):
        """Plot FFT in 1/B."""
        self.wplots.fft.clearPlots()

        # Decreasing magnetic field
        if self.worker.proc.get_data_processed("fft_dec", checkonly=True):
            self.wplots.fft.plot(
                self.worker.proc.get_data_processed("bfreq_dec"),
                self.worker.proc.get_data_processed("fft_dec"),
                pen=self.wplots.pen_bdown,
                name="B down",
            )
        # Increasing magnetic field
        if self.worker.proc.get_data_processed("fft_inc", checkonly=True):
            self.wplots.fft.plot(
                self.worker.proc.get_data_processed("bfreq_inc"),
                self.worker.proc.get_data_processed("fft_inc"),
                pen=self.wplots.pen_bup,
                name="B up",
            )

    def syncroi_changed(self):
        """Update fit and FFT windows sync. status."""
        self.wplots._sync_roi = self.wconfiguration.syncroi_parameter.value()

    def check_tdo_extracted(self) -> bool:
        if not self.check_data_loaded():
            return False
        return self.worker.proc._check_barycenters_computed()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(OUT_FORMAT):
                self.load_csv_file(file_path)
                return

        super().dropEvent(e)
