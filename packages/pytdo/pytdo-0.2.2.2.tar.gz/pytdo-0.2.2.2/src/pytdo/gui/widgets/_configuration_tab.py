from PyQt6.QtCore import pyqtSignal
from pyqtgraph.parametertree import Parameter
from pyuson import gui


class ConfigurationWidget(gui.widgets.BaseConfigurationWidget):
    sig_syncroi_changed = pyqtSignal()

    def __init__(self, param_content: type):
        super().__init__(param_content)

        self.syncroi_parameter = Parameter.create(
            name="syncroi",
            type="bool",
            value=True,
            title="Sync. fit and FFT field-window",
        )

        self.syncroi_parameter.sigValueChanged.connect(self.sig_syncroi_changed.emit)
        self.host_parameters.addChild(self.syncroi_parameter)
