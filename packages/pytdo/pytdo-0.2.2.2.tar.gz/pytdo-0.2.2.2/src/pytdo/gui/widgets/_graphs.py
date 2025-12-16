"""The graphs area that holds all the plots."""

import pyqtgraph as pg
from PyQt6 import QtWidgets
from PyQt6.QtCore import QEvent, Qt, pyqtSignal, pyqtSlot


class GraphsWidget(QtWidgets.QWidget):
    """
    The graphs area with all the plots.

    Signals
    -------
    sig_roi1_changed : emits when the draggable field-window moved in tdo(B).
    sig_roi2_changed : emits when the draggable field-window moved in tdo_detrend(B).
    """

    sig_roi1_changed = pyqtSignal()
    sig_roi2_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Flags
        self._mouse_pan_mode = True
        self._sync_roi = True

        # Create grid
        grid = QtWidgets.QGridLayout()

        # Create empty canvases in tabs
        field_tab = self.create_field_plot()
        signal_tab = self.create_signal_plot()
        tdo_tab = self.create_tdo_plot()
        fft_tab = self.create_fft_plot()

        # Get pens
        self.init_plot_style()

        # Add Tabs to the grid
        grid.addWidget(field_tab, 0, 0, 1, 1)
        grid.addWidget(signal_tab, 0, 1, 1, 3)
        grid.addWidget(tdo_tab, 1, 0, 1, 2)
        grid.addWidget(fft_tab, 1, 2, 1, 2)

        # Force stretch factors
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        # Create widget
        self.setLayout(grid)

    @property
    def time2frame_scale(self) -> float:
        return self._time2frame_scale

    @time2frame_scale.setter
    def time2frame_scale(self, value: float):
        self._time2frame_scale = value
        self.field.getAxis("top").setScale(self.time2frame_scale)
        self.dfield.getAxis("top").setScale(self.time2frame_scale)

    def create_field_plot(self) -> QtWidgets.QTabWidget:
        tab = QtWidgets.QTabWidget(self)

        # magnetic field (integrated)
        self.field = pg.PlotWidget(title="Magnetic field")
        self.field.setLabel("bottom", "time (s)")
        self.field.setLabel("left", "field (T)")
        self.field.showGrid(y=True)

        # pickup coil voltage (measured)
        self.dfield = pg.PlotWidget(title="Pickup")
        self.dfield.setLabel("bottom", "time (s)")
        self.dfield.setLabel("left", "pickup (V)")
        self.dfield.showGrid(y=True)

        tab.addTab(self.field, "B(t)")
        tab.addTab(self.dfield, "Pickup")

        return tab

    def create_signal_plot(self) -> QtWidgets.QTabWidget:
        tab = QtWidgets.QTabWidget(self)

        # TDO signal versus field
        self.sig_field = pg.PlotWidget(title="Signal versus field")
        self.sig_field.setLabel("bottom", "field (T)")
        self.sig_field.setLabel("left", "TDO frequency (Hz)")
        self.sig_field.showGrid(y=True)
        self.roi = pg.LinearRegionItem()  # field-window selector
        self.sig_field.addItem(self.roi, ignoreBounds=True)
        self.roi.sigRegionChangeFinished.connect(self.roi1_changed)
        self.sig_field.getPlotItem().addLegend()

        # TDO signal versus time
        self.sig_time = pg.PlotWidget(title="Signal versus time")
        self.sig_time.setLabel("bottom", "time (s)")
        self.sig_time.setLabel("left", "TDO frequency (Hz)")
        self.sig_time.showGrid(y=True)

        tab.addTab(self.sig_field, "TDO(B)")
        tab.addTab(self.sig_time, "TDO(t)")

        return tab

    def create_tdo_plot(self) -> QtWidgets.QTabWidget:
        tab = QtWidgets.QTabWidget(self)

        # vs field
        self.tdo_field = pg.PlotWidget(title="Oscillatory part versus field")
        self.tdo_field.setLabel("bottom", "field (T)")
        self.tdo_field.setLabel("left", "TDO detrended")
        self.tdo_field.showGrid(y=True)
        self.tdo_field.getPlotItem().addLegend()
        self.roi2 = pg.LinearRegionItem()  # field-window selector
        self.tdo_field.addItem(self.roi2, ignoreBounds=True)
        self.roi2.sigRegionChangeFinished.connect(self.roi2_changed)

        # vs 1/B
        self.tdo_inverse_field = pg.PlotWidget(title="Oscillatory part versus 1/B")
        self.tdo_inverse_field.setLabel("bottom", "1/B (T^-1)")
        self.tdo_inverse_field.setLabel("left", "TDO detrended")
        self.tdo_inverse_field.showGrid(y=True)

        tab.addTab(self.tdo_field, "TDO detrended(B)")
        tab.addTab(self.tdo_inverse_field, "TDO detrended(1/B)")

        return tab

    def create_fft_plot(self) -> QtWidgets.QTabWidget:
        tab = QtWidgets.QTabWidget(self)

        # vs field
        self.fft = pg.PlotWidget(title="Fourier transform")
        self.fft.setLabel("bottom", "B-frequency (T)")
        self.fft.setLabel("left", "magnitude")
        self.fft.showGrid(y=True)
        self.fft.getPlotItem().addLegend()

        tab.addTab(self.fft, "FFT")

        return tab

    def init_plot_style(self):
        """Set up PyQtGraph line styles."""
        w0 = 1
        self.pen_field = pg.mkPen("#c7c7c7", width=w0)
        self.pen_bup = pg.mkPen("#2ca02cff", width=w0)
        self.pen_bdown = pg.mkPen("#d62728ff", width=w0)
        self.pen_fitbup = pg.mkPen("#2ca02cb1", width=w0)
        self.pen_fitdown = pg.mkPen("#d62728b1", width=w0)

    @pyqtSlot()
    def roi1_changed(self):
        """Update ROI in the TDO detrended panel when the ROI in the TDO panel moved."""
        self.sig_roi1_changed.emit()
        if not self._sync_roi:
            return

        roi1 = self.roi.getRegion()  # TDO panel
        roi2 = self.roi2.getRegion()  # TDO detrend panel

        if roi1 != roi2:
            self.roi2.setRegion(self.roi.getRegion())

    @pyqtSlot()
    def roi2_changed(self):
        """Update ROI in the TDO panel when the ROI in the TDO detrended panel moved."""
        self.sig_roi2_changed.emit()
        if not self._sync_roi:
            return

        roi1 = self.roi.getRegion()  # TDO panel
        roi2 = self.roi2.getRegion()  # TDO detrend panel

        if roi1 != roi2:
            self.roi.setRegion(self.roi2.getRegion())

    def enable_rois(self):
        """Enable moving ROIs."""
        self.roi.setMovable(True)
        self.roi2.setMovable(True)

    def disable_rois(self):
        """Disable moving ROIs."""
        self.roi.setMovable(False)
        self.roi2.setMovable(False)

    def clear_all_plots(self):
        """Clear plots."""
        self.field.clearPlots()
        self.dfield.clearPlots()
        self.sig_time.clearPlots()
        self.sig_field.clearPlots()
        self.tdo_field.clearPlots()
        self.tdo_inverse_field.clearPlots()
        self.fft.clearPlots()

    def event(self, ev: QEvent | None):
        """Handle mouse selection while holding CTRL to make a ROI zoom in plots."""
        if ev is None:
            return super().event(None)

        # Switch to rectangular zoom selection on the first Ctrl key press event
        if ev.type() == QEvent.Type.KeyPress and ev.key() == Qt.Key.Key_Control:
            if self._mouse_pan_mode:
                self.switch_mouse_pan_mode(False)

        # Switch back to pan mode on left click when releasing the Ctrl key
        if ev.type() == QEvent.Type.KeyRelease and ev.key() == Qt.Key.Key_Control:
            self.switch_mouse_pan_mode(True)

        return super().event(ev)

    def switch_mouse_pan_mode(self, state: bool):
        """
        Switch mouse behavior from panning to ROI-zooming when holding CTRL.

        Parameters
        ----------
        state : bool
            If True, all plots are set to pan mode, otherwise they are set in ROI-zoom
            mode.
        """
        # Get mode
        mode = pg.ViewBox.PanMode if state else pg.ViewBox.RectMode
        self._mouse_pan_mode = state

        # Set mode
        self.field.getPlotItem().getViewBox().setMouseMode(mode)
        self.dfield.getPlotItem().getViewBox().setMouseMode(mode)
        self.sig_time.getPlotItem().getViewBox().setMouseMode(mode)
        self.sig_field.getPlotItem().getViewBox().setMouseMode(mode)
        self.tdo_field.getPlotItem().getViewBox().setMouseMode(mode)
        self.tdo_inverse_field.getPlotItem().getViewBox().setMouseMode(mode)
        self.fft.getPlotItem().getViewBox().setMouseMode(mode)
