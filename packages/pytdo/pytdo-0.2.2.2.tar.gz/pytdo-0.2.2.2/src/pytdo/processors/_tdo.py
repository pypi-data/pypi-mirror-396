"""TDO Processor class to analyse TDO experiments."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Literal, Self

import numpy as np
from pyuson import BaseProcessor
from scipy import signal

from .. import sp
from ..config import Config
from ._types import MetadataProcessor, tTDOProcessor

logger = logging.getLogger(__name__)

MEAS_TO_CROP = (
    "pickup_time",
    "pickup",
    "magfield_time",
    "magfield",
    "signal_time",
)

TDO_SIGNAL_NAME = "tdo_signal"  # name of the TDO signal (the frequencies barycenters)
PROGRAM_NAME = "pytdo"
OUT_FORMAT = (".csv", ".tsv", ".txt", ".out")
CSV_TDO_NCOLS = 3
CSV_RES_NCOLS = 11


class TDOProcessor(tTDOProcessor, BaseProcessor):
    """A Processor class for TDO experiments."""

    def __init__(self, *args, **kwargs):
        self._program_name = PROGRAM_NAME
        self._config_cls = Config
        super().__init__(*args, **kwargs)

        self.metadata = MetadataProcessor()

        self._meas_name = [*self.cfg.measurements.keys()][0]
        self._tdo_name = TDO_SIGNAL_NAME
        self._tdo_det_inc_name = self._tdo_name + "_detrend_inc"
        self._tdo_det_dec_name = self._tdo_name + "_detrend_dec"
        self._tdo_inv_inc_name = self._tdo_det_inc_name.replace("detrend", "inverse")
        self._tdo_inv_dec_name = self._tdo_det_dec_name.replace("detrend", "inverse")

        self.npoints_raw = 0

        self.is_cropped = {meas_name: False for meas_name in MEAS_TO_CROP}
        self.is_cropped[self._meas_name] = False

    @property
    def expid(self) -> str:
        """Experiment ID, linked to the Config object."""
        return self.cfg.expid

    @expid.setter
    def expid(self, value: str):
        """Setter for expid."""
        self.cfg.expid = value
        self.cfg.build_filenames()

    @property
    def data_directory(self) -> Path:
        """Data directory, linked to the Config object."""
        return self.cfg.data_directory

    @data_directory.setter
    def data_directory(self, value: str | Path):
        """Setter for `data_directory`."""
        self.cfg.data_directory = Path(value)
        self.cfg.build_filenames()

    def load_pickup(self) -> Self:
        """
        Load the pickup binary file with the settings from the configuration.

        The experiment temperature and the sampling rate is also read from the file and
        added to the metadata.
        """
        # Get reader settings
        filename = Path(self.cfg.filenames["pickup"])
        precision = self.cfg.files["pickup"].precision
        endian = self.cfg.files["pickup"].endian
        order = self.cfg.files["pickup"].order
        npickups = self.cfg.parameters.pickup_number
        pickup_index = self.cfg.parameters.pickup_index

        logger.info(f"Loading pickup data from from {filename.name}...")
        if filename.is_file():
            # Load file
            pu = self._load_pickup(
                filename,
                precision=precision,
                endian=endian,
                order=order,
                nseries=npickups,
                index=pickup_index,
            )
            # Store metadata
            self.metadata["fs_pickup"] = float(pu[0])
            self.metadata["temperature"] = float(pu[1])

            # Store in the Data object
            nsamples = pu.shape[0] - 2
            self.set_data_raw(
                "pickup_time",
                np.linspace(
                    0, nsamples / self.metadata["fs_pickup"], nsamples, endpoint=False
                ),
            )
            self.set_data_raw("pickup", pu[2:])

            logger.info(
                f"Pickup loaded. Temperature : {self.metadata['temperature']:2.4f}K, "
                f"{nsamples} points sampled at {self.metadata['fs_pickup'] / 1e3}kHz."
            )
        else:
            # We'll simulate a fake pickup when we'll know the signal size
            logger.info(f"{filename.name} not found, skipping.")
            self.set_data_raw("pickup_time", np.array([]))
            self.set_data_raw("pickup", np.array([]))
            self.metadata["fs_pickup"] = 1.0

        self.is_cropped["pickup_time"] = False
        self.is_cropped["pickup"] = False

        return self

    def load_oscillo(self) -> Self:
        """
        Load TDO signal.

        Corresponding data is stored in `data_raw`.
        """
        # Get reader settings
        filename = Path(self.cfg.filenames["oscillo"])
        precision = self.cfg.files["oscillo"].precision
        endian = self.cfg.files["oscillo"].endian

        if not filename.is_file():
            logger.error(f"{filename.name} not found.")
            return self

        # Load data
        logger.info(f"Loading data from {filename.name}...")
        data = self.load_bin(filename, precision=precision, endian=endian)

        # Store metadata
        self.metadata["fs_signal"] = float(data[0])
        temperature = float(data[1])
        self.npoints_raw = data.shape[0] - 2

        if "temperature" in self.metadata:
            # Already the temperature found in the pickup binary file
            other_temperature = self.metadata.pop("temperature")
            if temperature != other_temperature:
                logger.error(
                    "Temperatures found in the files do not match "
                    f"(got {temperature} and {other_temperature})."
                )

        # Keep the one from the TDO binary file
        self.metadata["temperature"] = temperature

        # Store data
        self.set_data_raw(self._meas_name, data[2:])
        self.get_signal_time()

        self.is_cropped[self._meas_name] = False

        logger.info(
            f"{self._meas_name} loaded. "
            f"Temperature : {temperature:2.4f}K, {self.npoints_raw} points sampled"
            f" at {self.metadata['fs_signal'] / 1e6}MHz."
        )

        return self

    def get_signal_time(self, fs: float | None = None) -> Self:
        """Get the experiment time vector corresponding to the raw data."""
        if fs is None:
            fs = self.metadata["fs_signal"]
        elif "fs_signal" not in self.metadata:
            self.load_oscillo()

        self.set_data_raw(
            "signal_time",
            np.linspace(
                0,
                self.npoints_raw / fs,
                self.npoints_raw,
                endpoint=False,
            ),
        )
        self.is_cropped["signal_time"] = False

        return self

    def compute_field(self, method: str = "trapz") -> Self:
        """Compute magnetic field."""
        # Checks
        if "pickup" not in self.data_raw:
            self.load_pickup()

        # Get parameters
        surface = self.cfg.parameters.pickup_surface

        # Integrate and store
        self._compute_field(surface=surface, method=method)

        self.is_cropped["magfield"] = False
        self.is_cropped["magfield_time"] = False

        return self

    def _crop_signal(
        self,
        meas_name: str,
        start: int,
        stop: int,
        where: Literal["raw", "processed"] = "raw",
        force: bool = False,
        append: str = "_full",
    ):
        """
        Crop a 1D vector from `start` to `stop`.

        The dataset named `meas_name` must be a 1D vector.

        Parameters
        ----------
        meas_name : str
            Dataset name. Must be allowed to be re-cropped, e.g. exists in the
            `is_cropped` dict.
        start, stop : int
            Start and stop index.
        where : {"raw", "processed"}, optional
            Where to get and set the data (`data_raw` or `data_processed`). Default is
            "raw".
        force : bool, optional
            Whether to crop even if a dataset named `meas_name + append` already exists.
            Default is False.
        append : str, optional
            Bit of text that is appended to the base measurement name to store the
            original data. Default is "_full".
        """
        match where:
            case "raw":
                getter = getattr(self, "get_data_raw")
                setter = getattr(self, "set_data_raw")
            case "processed":
                getter = getattr(self, "get_data_processed")
                setter = getattr(self, "set_data_processed")

        if getter(meas_name + append, checkonly=True) and not force:
            self.is_cropped[meas_name] = True
            logger.info(f"{meas_name} not cropped because already cropped.")
        elif getter(meas_name, checkonly=True):
            sig = getter(meas_name)
            setter(meas_name + append, sig.copy())
            setter(meas_name, sig[start:stop])
            self.is_cropped[meas_name] = True
            logger.info(f"{meas_name} cropped.")
        else:
            self.is_cropped[meas_name] = False
            logger.warning(f"{meas_name} not cropped because not loaded or created.")

    def crop_signal(self, force: bool = False) -> Self:
        """
        Crop signal up until `max_time` defined in the settings.

        The resulting signal is put in `data_raw`, the original data is kept with a
        trailing `_full`.
        """
        logger.info("Cropping data...")

        # Signal
        if "fs_signal" in self.metadata:
            idx_crop = int(self.metadata["fs_signal"] * self.cfg.settings.max_time)
            self._crop_signal(self._meas_name, 0, idx_crop, where="raw", force=force)
            self._crop_signal("signal_time", 0, idx_crop, where="raw", force=force)
        else:
            logger.warning("Data not loaded.")

        # Pickup and magnetic field
        if "fs_pickup" in self.metadata:
            idx_crop = int(self.metadata["fs_pickup"] * self.cfg.settings.max_time)
            self._crop_signal("pickup_time", 0, idx_crop, where="raw", force=force)
            self._crop_signal("pickup", 0, idx_crop, where="raw", force=force)
            self._crop_signal(
                "magfield_time", 0, idx_crop, where="processed", force=force
            )
            self._crop_signal("magfield", 0, idx_crop, where="processed", force=force)
        else:
            logger.warning("Pickup not loaded.")

        return self

    def compute_spectrogram(self) -> Self:
        """
        Perform a spectrogram on the raw signal.

        This a FFT performed on overlapping time windows of the signal. This results in
        a power spectral density (PSD) as a function of time and frequency.
        Parameters for the spectrogram are defined in the settings section of the
        configuration.

        The time and frequency vector and the 2D PSD are stored in `data_processed`.
        """
        # Check if data was loaded
        if not self._check_data_loaded():
            self.load_oscillo()
        # Check if data was time-cropped
        if not self.is_cropped[self._meas_name]:
            self.crop_signal()

        # Get parameters
        window = "hann"
        nperseg = self.cfg.settings.spectro_nperseg
        detrend = "linear"
        noverlap = self.cfg.settings.spectro_noverlap
        nfft = self.cfg.settings.spectro_win_size

        if noverlap == -1:
            noverlap = nperseg // 2

        # Perform spectrogram
        logger.info(
            "Computing spectrogram (time-window size : "
            f"{nperseg / self.metadata['fs_signal'] * 1e6:2.2f}µs)..."
        )
        fxx, txx, sxx = signal.spectrogram(
            self.get_data_raw(self._meas_name),
            self.metadata["fs_signal"],
            window=window,
            nperseg=nperseg,
            noverlap=noverlap,
            nfft=nfft,
            detrend=detrend,
        )
        logger.info("Spectrogram computed.")

        # Store data
        self.set_data_processed("spectro_f", fxx)
        self.set_data_processed("spectro_t", txx)
        self.set_data_processed("spectro_s", sxx)

        return self

    def find_barycenters(self) -> Self:
        """
        Find barycenters in the spectrogram.

        The maxima are found in the 2D PSD. The barycenter of the corresponding
        frequencies is computed in a time window around the maxima, defined by the
        settings in the configuration.

        This results in a time vector (the time windows) and the TDO signal (the
        barycenters, e.g. frequencies). Those two quantities are stored in
        `data_processed`.
        """
        # Checks
        if not self._check_spectro_computed():
            logger.error("Spectrogram not computed. Run `compute_spectrogram()` first")
            return self

        logger.info(
            "Finding spectrogram barycenters (frequency-window size : "
            f"{2 * self.cfg.settings.barycenters_fwindow:2.3f}Hz)..."
        )
        self.set_data_processed(
            self._tdo_name,
            sp.find_barycenters(
                self.get_data_processed("spectro_f"),
                self.get_data_processed("spectro_s"),
                self.cfg.settings.barycenters_fwindow,
                fast=self.cfg.settings.barycenters_fast,
            ),
        )
        # Corresponding time vector (start at 0)
        time_tdo = self.get_data_processed("spectro_t")
        self.set_data_processed("time_exp", time_tdo - time_tdo[0])

        # Remove previously-computed values based on this TDO signal
        self.remove_data_processed(self._tdo_name + "_fit_inc")
        self.remove_data_processed(self._tdo_name + "_fit_dec")
        self.remove_data_processed(self._tdo_det_inc_name)
        self.remove_data_processed(self._tdo_det_dec_name)
        logger.info("TDO signal extracted.")

        return self

    def align_field(self) -> Self:
        """Align magnetic field on the `time_exp` vector."""
        if not self._check_field_computed():
            self.compute_field()
            self.crop_signal()

        if not self._check_barycenters_computed():
            self.find_barycenters()
            if not self._check_barycenters_computed():
                logger.error("TDO signal could not be extracted, check messages above.")
                return self

        exptime = self.get_data_processed("time_exp")
        magtime = self.get_data_processed("magfield_time")
        magfield = self.get_data_processed("magfield")
        self.set_data_processed(
            "magfield", np.interp(exptime, magtime, magfield, left=0)
        )
        self.set_data_processed("magfield_time", exptime)

        # Get the up / down indices
        self.get_up_down_indices()

        return self

    def get_up_down_indices(self) -> Self:
        """Get increasing and decreasing field indices."""
        self.inds_inc, self.inds_dec = sp.get_up_down_indices(
            self.get_data_processed("magfield")
        )

        return self

    def detrend_polyfit(self) -> Self:
        """Fit the signal to detrend it."""
        # Checks
        if not self._check_field_aligned():
            self.align_field()
            if not self._check_field_aligned():
                logger.error(
                    "Magnetic field could not be aligned, check messages above"
                )
                return self

        if not hasattr(self, "inds_inc") or not hasattr(self, "inds_dec"):
            self.get_up_down_indices()

        # Get parameters
        b1, b2 = self.cfg.settings.poly_window
        deg = self.cfg.settings.poly_deg

        # Fit and detrend
        logger.info(
            f"Fitting (degree : {deg}) and detrending TDO signal in {b1, b2}T..."
        )
        fp_inc, res_inc = sp.fit_poly(
            self.get_data_processed("magfield")[self.inds_inc],
            self.get_data_processed(self._tdo_name)[self.inds_inc],
            b1,
            b2,
            deg,
        )

        fp_dec, res_dec = sp.fit_poly(
            self.get_data_processed("magfield")[self.inds_dec],
            self.get_data_processed(self._tdo_name)[self.inds_dec],
            b1,
            b2,
            deg,
        )

        # Store
        self.set_data_processed(self._tdo_name + "_fit_inc", fp_inc)
        self.set_data_processed(self._tdo_name + "_fit_dec", fp_dec)
        self.set_data_processed(self._tdo_det_inc_name, res_inc)
        self.set_data_processed(self._tdo_det_dec_name, res_dec)

        logger.info("TDO signal detrended.")

        return self

    def oversample_inverse_field(self) -> Self:
        """Express data in 1/B and oversample."""
        # Checks
        if not self._check_tdo_detrended():
            self.detrend_polyfit()

        # Get parameters
        b1, b2 = self.cfg.settings.fft_window
        npoints = self.cfg.settings.npoints_interp_inverse

        if b1 == -1:
            b1 = self.cfg.settings.poly_window[0]
        if b2 == -1:
            b2 = self.cfg.settings.poly_window[1]

        # Interpolate inverse field
        logger.info(
            f"Oversampling TDO signal in 1/B ({npoints} points in {b1, b2}T)..."
        )
        field_inverse_inc, tdo_inverse_inc = sp.interpolate_inverse(
            self.get_data_processed("magfield")[self.inds_inc],
            self.get_data_processed(self._tdo_det_inc_name),
            b1,
            b2,
            npoints,
        )

        field_inverse_dec, tdo_inverse_dec = sp.interpolate_inverse(
            self.get_data_processed("magfield")[self.inds_dec],
            self.get_data_processed(self._tdo_det_dec_name),
            b1,
            b2,
            npoints,
        )

        # Store
        self.set_data_processed("magfield_inverse_inc", field_inverse_inc)
        self.set_data_processed(self._tdo_inv_inc_name, tdo_inverse_inc)
        self.set_data_processed("magfield_inverse_dec", field_inverse_dec)
        self.set_data_processed(self._tdo_inv_dec_name, tdo_inverse_dec)

        logger.info("TDO signal interpolated in 1/B.")

        return self

    def fft_inverse_field(self) -> Self:
        """
        FFT on the signal in 1/B.

        The resulting "frequencies" are therefore in units of B (teslas).
        """
        # Checks
        if not self._check_tdo_inverse():
            self.oversample_inverse_field()

        # FFT
        logger.info("FFT on TDO signal in 1/B...")
        f_inc, fft_inc = sp.fourier_transform(
            self.get_data_processed(self._tdo_inv_inc_name),
            np.mean(np.diff(self.get_data_processed("magfield_inverse_inc"))),
            pad_mult=self.cfg.settings.fft_pad_mult,
        )

        f_dec, fft_dec = sp.fourier_transform(
            self.get_data_processed(self._tdo_inv_dec_name),
            np.mean(np.diff(self.get_data_processed("magfield_inverse_dec"))),
            pad_mult=self.cfg.settings.fft_pad_mult,
        )

        # Clip
        idx_max_bfreq = sp.find_nearest_index(f_dec, self.cfg.settings.max_bfreq)
        f_inc = f_inc[:idx_max_bfreq]
        fft_inc = fft_inc[:idx_max_bfreq]
        f_dec = f_dec[:idx_max_bfreq]
        fft_dec = fft_dec[:idx_max_bfreq]

        # Store
        self.set_data_processed("bfreq_inc", f_inc)
        self.set_data_processed("fft_inc", fft_inc)
        self.set_data_processed("bfreq_dec", f_dec)
        self.set_data_processed("fft_dec", fft_dec)

        logger.info(
            f"FFT computed and cropped up until {self.cfg.settings.max_bfreq}T."
        )

        return self

    def extract_tdo(self) -> Self:
        """Helper function that does everything required to extract the TDO signal."""
        self.compute_spectrogram().find_barycenters().align_field()

        return self

    def remove_background(self) -> Self:
        """Helper function to detrend the signal and sort signal in 1/B."""
        self.detrend_polyfit().oversample_inverse_field()

        return self

    def collect_arrays(self, array_names_list: list[str]) -> list[np.ndarray]:
        """Collect and data in `data_processed`."""
        return [self.get_data_processed(name) for name in array_names_list]

    def get_csv_filename(self, suffix: str = "", ext: str = ".csv") -> str:
        """Build the output file name."""
        return str(self.data_directory / (self.expid + suffix + ext))

    def save_tdo_csv(self, filename: str | Path | None = None, sep: str = "\t") -> Self:
        """
        Save intermediate results as a CSV file.

        The intermediate results correspond to the extracted TDO signal, before any
        post-processing (detrending, ...).
        If the file already exists, it is overwritten.
        """
        if filename is None:
            filename = self.get_csv_filename(suffix="-tdo")

        logger.info("Saving extracted TDO signal...")

        if not self._check_field_aligned():
            logger.warning(
                "The TDO signal and the magnetic fields are not aligned, aligning now"
            )
            self.align_field()

        to_save = ["time_exp", "magfield", self._tdo_name]
        a = sp.collate_arrays(self.collect_arrays(to_save))

        header = sep.join(["time", "field", "tdo"])

        np.savetxt(
            filename,
            a,
            delimiter=sep,
            header=header,
            comments="",
        )

        logger.info(f"Saved at {Path(filename).name}.")

        return self

    def _get_result_names_list(self, ud: Literal["inc", "dec"]):
        """
        Generate the list of things to save.

        Either in increasing or decreasing magnetic field.
        """
        return [
            "time_exp",
            "magfield",
            self._tdo_name,
            self._tdo_name + "_fit_" + ud,
            self._tdo_det_dec_name if ud == "dec" else self._tdo_det_inc_name,
            "magfield_inverse_" + ud,
            self._tdo_inv_dec_name if ud == "dec" else self._tdo_inv_inc_name,
            "bfreq_" + ud,
            "fft_" + ud,
        ]

    def _get_results_up_down(
        self, ud: Literal["inc", "dec"]
    ) -> tuple[np.ndarray, list[str]]:
        """Save increasing or decreasing magnetic field results in a CSV file."""
        names_list = self._get_result_names_list(ud)
        to_save = self.collect_arrays(names_list)
        names_list.insert(3, "magfield_" + ud)
        to_save.insert(
            3,
            self.get_data_processed("magfield")[
                self.inds_dec if ud == "dec" else self.inds_inc
            ],
        )
        names_list.insert(4, self._tdo_name + "_" + ud)
        to_save.insert(
            4,
            self.get_data_processed(self._tdo_name)[
                self.inds_dec if ud == "dec" else self.inds_inc
            ],
        )
        return sp.collate_arrays(to_save), names_list

    def save_results_csv(
        self,
        filename_prefix: str | Path | None = None,
        sep: str = "\t",
    ) -> Self:
        """
        Save analysed results as CSV.

        It includes : time, aligned magnetic field, TDO signal, detrended TDO signal,
        1/B, TDO signal oversampled in 1/B, Fourier transform.
        """
        if filename_prefix is None:
            filename_prefix = Path(self.get_csv_filename(suffix="-results"))
        else:
            filename_prefix = Path(filename_prefix)

        logger.info("Saving analysed results...")

        # Increasing magnetic field
        filename_inc = filename_prefix.with_stem(filename_prefix.stem + "-up")
        to_save, header = self._get_results_up_down("inc")
        header_inc = sep.join(header)
        np.savetxt(
            filename_inc,
            to_save,
            delimiter=sep,
            header=header_inc,
            comments="",
        )

        # Decreasing magnetic field
        filename_dec = filename_prefix.with_stem(filename_prefix.stem + "-down")
        to_save, header = self._get_results_up_down("dec")
        header_dec = sep.join(header)
        np.savetxt(
            filename_dec,
            to_save,
            delimiter=sep,
            header=header_dec,
            comments="",
        )

        logger.info(f"Saved at {filename_inc.name} and {filename_dec.name}.")

        return self

    def load_csv(self, filepath: Path, sep: str | None = None):
        """Load data from a CSV file."""
        filepath = Path(filepath)
        if not filepath.is_file():
            logger.error("File does not exist")
            return

        reader, delimiter = self._determine_file_format(filepath, sep=sep)

        if isinstance(reader, str) and reader == "unknown":
            logger.error(f"Could not load input file ({filepath})")
            return

        logger.info(f"Reading data from {filepath.name}...")
        status = reader(filepath, sep=delimiter)
        if not status:
            logger.error(f"Failed to read {filepath.name}, check messages above")
            return

        # Get the up / down indices
        self.get_up_down_indices()

        logger.info(f"Read data from {filepath.name}.")

    def _determine_file_format(
        self, filepath: Path, sep: str | None = None
    ) -> tuple[Callable[[Path, str], bool] | str, str]:
        """Determine what type of file we got."""
        match filepath.suffix:
            case ".out":
                return self._load_csv_legacy_tdo, " " if sep is None else sep
            case ".txt":
                return self._load_csv_legacy_results, "," if sep is None else sep
            case ".csv" | ".tsv":
                return self._determine_csv_format(filepath, sep=sep)
            case _:
                logger.error(f"Unknown file extension : {filepath.suffix}")
                return "unknown", ""

    def _determine_csv_format(
        self, filepath: Path, sep: str | None = None
    ) -> tuple[Callable[[Path, str], bool] | str, str]:
        """Determine what type of CSV file we got."""
        # Read first line
        with open(filepath) as f:
            header = f.readline()

        # Count how much delimiters there are to find the number of columns
        if sep is None:
            sep = "\t"
        ncols = header.count(sep) + 1

        if ncols == CSV_TDO_NCOLS:
            return self._load_csv_tdo, sep
        elif ncols == CSV_RES_NCOLS:
            return self._load_csv_results, sep
        else:
            logger.error(
                f"Could not determine what type of file this is : {filepath.name}"
            )
            return "unknown", ""

    def _load_csv_legacy_tdo(self, filepath: Path, sep: str = " ") -> bool:
        """Load already extracted TDO signal from a legacy .out file."""
        logger.info("Loading TDO signal from a (legacy) .out file...")
        data = np.loadtxt(filepath, delimiter=sep, skiprows=1, usecols=(0, 1))

        # data is ["magfield", self._tdo_name]
        self.set_data_processed("magfield", data[:, 0])
        self.set_data_processed(self._tdo_name, data[:, 1])

        # Create the time vector to pass the field-aligned checks
        self.set_data_processed(
            "time_exp", np.linspace(0, self.cfg.settings.max_time, data.shape[0])
        )
        self.set_data_processed("magfield_time", self.get_data_processed("time_exp"))

        # Get the up / down indices
        self.get_up_down_indices()

        return True

    def _load_csv_legacy_results(self, filepath: Path, sep: str = ",") -> bool:
        """Load already computed results from a legacy .txt file."""
        logger.info("Loading results from a (legacy) .txt file...")

        # Load data
        data = np.loadtxt(filepath, delimiter=sep, skiprows=1)

        # Guess if it's increasing or decreasing magnetic field
        inc_or_dec = self._determine_inc_or_dec(filepath)
        if inc_or_dec == "unknown":
            logger.error(
                "Couldn't determine if the file is for increasing or decreasing "
                "magnetic field"
            )
            return False
        self._set_map_in_data_processed(self._map_cols_legacy_results(data, inc_or_dec))

        # Set extra data (to pass field-aligned check)
        self.set_data_processed("magfield_time", self.get_data_processed("time_exp"))

        return True

    def _load_csv_tdo(self, filepath: Path, sep: str = "\t") -> bool:
        """Load already extracted TDO signal from a CSV file."""
        logger.info("Loading TDO signal from CSV file...")
        data = np.loadtxt(filepath, delimiter=sep, skiprows=1, usecols=(0, 1, 2))

        # data is ["time_exp", "magfield", self._tdo_name]
        self.set_data_processed("time_exp", data[:, 0])
        self.set_data_processed("magfield_time", data[:, 0])
        self.set_data_processed("magfield", data[:, 1])
        self.set_data_processed(self._tdo_name, data[:, 2])

        return True

    def _load_csv_results(self, filepath: Path, sep: str = "\t") -> bool:
        """Load already computed results from a CSV file."""
        logger.info("Loading results from a CSV file...")

        # Load data
        data = np.loadtxt(filepath, delimiter=sep, skiprows=1)

        # Guess if it's increasing or decreasing magnetic field
        inc_or_dec = self._determine_inc_or_dec(filepath)
        if inc_or_dec == "unknown":
            logger.error(
                "Couldn't determine if the file is for increasing or decreasing "
                "magnetic field"
            )
            return False
        self._set_map_in_data_processed(self._map_cols_results(data, inc_or_dec))

        # Set extra data (to pass field-aligned check)
        self.set_data_processed("magfield_time", self.get_data_processed("time_exp"))

        return True

    def _determine_inc_or_dec(
        self, filepath: Path, keywords: tuple[str] = ("inc", "dec")
    ) -> Literal["inc", "dec", "unknown"]:
        """
        Determine if CSV file is for increasing or decreasing magnetic field.

        Parameters
        ----------
        filepath : Path
            Path to the CSV file.
        keywords : tuple[str]
            Two-elements tuple with the strings that allow to determine if it is
            increasing or decreasing, respectively. Default is ("inc", "dec").

        Returns
        -------
        inc_or_dec : {"inc", "dec", "unknown"}
        """
        with open(filepath) as f:
            header = f.readline()

        ninc = header.count(keywords[0])
        ndec = header.count(keywords[1])

        if ninc > ndec:
            return "inc"
        elif ninc < ndec:
            return "dec"
        else:
            return "unknown"

    def _map_cols_legacy_results(
        self, data: np.ndarray, kw: Literal["inc", "dec"]
    ) -> dict[str, np.ndarray]:
        """
        Map a field name with a column in the legacy results CSV file.

        Parameters
        ----------
        data : np.ndarray
            Tabular data read from the legacy results CSV file.
        kw : {"inc", "dec"}
            Increasing or decreasing magnetic field identifier (usually "inc" or "dec").
        """
        where_nan = np.isnan(data)

        def extract_col(idx):
            return data[~where_nan[:, idx], idx]

        return {
            "time_exp": extract_col(0),
            "magfield": extract_col(1),
            self._tdo_name: extract_col(2),
            self._tdo_name + "_fit_" + kw: extract_col(7),
            self._tdo_det_dec_name
            if kw == "dec"
            else self._tdo_det_inc_name: extract_col(8),
            "magfield_inverse_" + kw: extract_col(9),
            self._tdo_inv_dec_name
            if kw == "dec"
            else self._tdo_inv_inc_name: extract_col(10),
            "bfreq_" + kw: extract_col(11),
            "fft_" + kw: extract_col(12),
        }

    def _map_cols_results(
        self, data: np.ndarray, kw: Literal["inc", "dec"]
    ) -> dict[str, np.ndarray]:
        """
        Map a field name with a column in the results CSV file.

        Parameters
        ----------
        data : np.ndarray
            Tabular data read from the results CSV file.
        kw : {"inc", "dec"}
            Increasing or decreasing magnetic field identifier (usually "inc" or "dec").
        """
        where_nan = np.isnan(data)

        def extract_col(idx):
            return data[~where_nan[:, idx], idx]

        return {
            "time_exp": extract_col(0),
            "magfield": extract_col(1),
            self._tdo_name: extract_col(2),
            self._tdo_name + "_fit_" + kw: extract_col(5),
            self._tdo_det_dec_name
            if kw == "dec"
            else self._tdo_det_inc_name: extract_col(6),
            "magfield_inverse_" + kw: extract_col(7),
            self._tdo_inv_dec_name
            if kw == "dec"
            else self._tdo_inv_inc_name: extract_col(8),
            "bfreq_" + kw: extract_col(9),
            "fft_" + kw: extract_col(10),
        }

    def _set_map_in_data_processed(self, data: dict[str, np.ndarray]):
        """Set data in `data_processed`."""
        for key, value in data.items():
            self.set_data_processed(key, value)

    def _check_pickup_loaded(self) -> bool:
        """Check if the pickup data was loaded."""
        if ("pickup" not in self.data_raw) or ("fs_pickup" not in self.metadata):
            return False
        else:
            return True

    def _check_data_loaded(self) -> bool:
        """Check if oscilloscope data was loaded."""
        return (self._meas_name in self.data_raw) and ("fs_signal" in self.metadata)

    def _check_field_computed(self) -> bool:
        """Check if magnetic field was computed."""
        return self.get_data_processed(
            "magfield_time", checkonly=True
        ) and self.get_data_processed("magfield", checkonly=True)

    def _check_spectro_computed(self) -> bool:
        """Check if the spectrogram was computed."""
        return self.get_data_processed("spectro_s", checkonly=True)

    def _check_barycenters_computed(self) -> bool:
        """Check if the frequencies barycenters were computed."""
        return self.get_data_processed(
            self._tdo_name, checkonly=True
        ) and self.get_data_processed("time_exp", checkonly=True)

    def _check_field_aligned(self) -> bool:
        """Check if the magnetic field was aligned on the TDO signal."""
        if not (self._check_field_computed() and self._check_barycenters_computed()):
            return False
        return (
            self.get_data_processed("time_exp").size
            == self.get_data_processed("magfield_time").size
        )

    def _check_tdo_detrended(self) -> bool:
        """Check if the TDO signal has been detrended."""
        return self.get_data_processed(
            self._tdo_det_inc_name, checkonly=True
        ) and self.get_data_processed(self._tdo_det_dec_name, checkonly=True)

    def _check_tdo_inverse(self) -> bool:
        """Check if the TDO signal was oversampled in 1/B."""
        return self.get_data_processed(
            self._tdo_inv_inc_name, checkonly=True
        ) and self.get_data_processed(self._tdo_inv_dec_name, checkonly=True)
