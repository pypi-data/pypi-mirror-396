import numpy as np
from pyuson.gui.widgets import BaseParamContent


class ParamContent(BaseParamContent):
    PARAMS_TO_PARSE = ["poly_window", "fft_window"]
    children_parameters = [
        dict(
            name="pickup_surface",
            type="float",
            limits=[0, np.inf],
            value=None,
            suffix="m²",
            siPrefix=False,
            readonly=True,
            title="Pickup surface",
        )
    ]

    children_settings = [
        dict(
            name="max_time",
            type="float",
            limits=[0, np.inf],
            step=0.1,
            value=1,
            suffix="s",
            siPrefix=True,
            title="Max. time",
        ),
        dict(
            name="barycenters_fwindow",
            type="float",
            limits=[0, np.inf],
            step=1e3,
            value=1,
            suffix="Hz",
            siPrefix=True,
            title="Barycenters: frequency window",
        ),
        dict(
            name="barycenters_fast",
            type="bool",
            limits=[True, False],
            value=True,
            title="Barycenters: fast algo.",
        ),
        dict(
            name="spectro_nperseg",
            type="int",
            limits=[2, np.inf],
            value=1024,
            step=1024,
            title="Spectro: n/segment",
        ),
        dict(
            name="spectro_win_size",
            type="int",
            limits=[2, np.inf],
            value=2048,
            step=1024,
            title="Spectro: FFT win. size",
        ),
        dict(
            name="spectro_noverlap",
            type="int",
            limits=[-1, np.inf],
            value=-1,
            step=512,
            title="Spectro: n overlap",
        ),
        dict(name="poly_window", type="str", value="", title="Fit: field window"),
        dict(
            name="poly_deg",
            type="int",
            value=3,
            step=1,
            limits=[1, 10],
            title="Fit: degree",
        ),
        dict(
            name="npoints_interp_inverse",
            type="int",
            value=100000,
            step=5e4,
            limits=[1000, np.inf],
            title="n points interp. 1/B",
        ),
        dict(
            name="fft_window",
            type="str",
            value="-1, 1",
            title="FFT: field window",
        ),
        dict(
            name="fft_pad_mult",
            type="int",
            value=100,
            step=100,
            title="FFT: padding size mult.",
        ),
        dict(
            name="max_bfreq",
            type="float",
            value=70000,
            step=1e4,
            limits=[1, np.inf],
            suffix="T",
            siPrefix=True,
            title="Max. B-frequency",
        ),
        dict(
            name="offset",
            type="float",
            value=1000,
            step=500,
            limits=[0, np.inf],
            title="Display: curve offset",
        ),
    ]
