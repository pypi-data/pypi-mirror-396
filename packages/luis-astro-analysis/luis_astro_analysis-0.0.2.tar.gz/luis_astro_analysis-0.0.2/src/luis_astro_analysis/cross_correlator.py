from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from astropy.io import fits


@dataclass
class CygX2Analysis:

    ### Static fields (fixed after initialization)

    ninja_path: str
    tess_path: str
    gti_path: str
    rmf_path: str

    ninja_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    tess_data: pd.DataFrame = field(default_factory=pd.DataFrame)

    gti: np.ndarray | None = None
    rmf: pd.DataFrame | None = None

    ### dynamic fields

    time_bins: np.ndarray | None = None
    lightcurve_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    colorbands: dict = field(default_factory=dict)
    binsize_sec: int = field(default_factory=int)

    ### tracking
    context: dict = field(default_factory=dict)
    log: list[str] = field(default_factory=list)

    # automatically load raw data and process the required stuff

    def __post_init__(self):  # (fold)
        self.log.append("[LOADING DATA]")
        self._load_ninja_data()
        self._load_ninja_gti()
        self._load_ninja_rmf()
        self._load_tess_data()

        self.log.append("[PRE-PROCESSING]")
        self._select_good_time("ninja_data")
        self._select_good_time("tess_data")
        self._assign_ninja_channel_energy()
        self._mask_non_overlaping_gtis()

        self.log.append("[DONE!]\n")
        # (end)

    # utilities

    def print_context(self):  # (fold)
        if self.context == {}:
            print("Context is empty.")
        else:
            print("Analyis Context:")
            for key, val in self.context.items():
                if "WARNING" in key:
                    print(f"\033[31m{key}\033[0m\n{val}")
                else:
                    print(f"{key} :: {val}")
                    # (end)

    def print_report(self):  # (fold)
        if self.log == []:
            print("Log is empty.")
        else:
            for entry in self.log:
                print(entry)

    # (end)

    # internal

    def _track_context(self, key, value):  # (fold)
        self.context[key] = value

    # (end)

    def _load_ninja_data(self):  # (fold)
        if not self.ninja_data.empty:
            raise RuntimeError("CygX2Analysis.ninja_data was already loaded!")
        with fits.open(self.ninja_path) as hdul:
            evt = hdul["EVENTS"].data  # type: ignore
            hdr = hdul["EVENTS"].header  # type: ignore
            mjdref = hdr.get("MJDREFI", 0) + hdr.get("MJDREFF", 0.0)
            time = evt["TIME"]
            channel = evt["PIch1"]
        time_mjd = mjdref + time / 86400.0  # seconds → days
        df = pd.DataFrame(
            {
                "mjd": np.array(time_mjd).astype(float),
                "channel": np.array(channel).astype(int),
            }
        )
        self._track_context("ninja_total_event_count", len(df))
        self.ninja_data = df
        self.log.append(f"Loaded NinjaSat data from: '{self.ninja_path}'")
        self.log.append(
            f" ~ found {len(df)} events in the timeframe: [{df["mjd"].min():.2f}, {df["mjd"].max():.2f}]"
        )
        # (end)

    def _load_tess_data(self):  # (fold)
        if not self.tess_data.empty:
            raise RuntimeError("CygX2Analysis.tess_data was already loaded!")
        with fits.open(self.tess_path) as hdul:
            evt = hdul["LIGHTCURVE"].data  # type: ignore
            hdr = hdul["LIGHTCURVE"].header  # type: ignore
            bjd = evt["TIME"]
            flux = evt["PDCSAP_FLUX"]
            flux_err = evt["PDCSAP_FLUX_ERR"]
            qlty = evt["QUALITY"]
        # drop bad events (quality != 0):
        mask = qlty == 0
        flux = flux[mask]
        flux_err = flux_err[mask]
        bjd = bjd[mask]
        # align time
        mjdrefi = hdr["BJDREFI"]
        mjdreff = hdr["BJDREFF"]
        mjd = bjd + mjdrefi + mjdreff - 2400000.5
        # pack data
        df = pd.DataFrame(
            {
                "mjd": mjd.astype(np.float64),
                "cr": flux.astype(np.float64),
                "cr_err": flux_err.astype(np.float64),
            }
        )
        self._track_context("tess_total_event_count", len(df))
        self.tess_data = df
        self.log.append(f"Loaded TESS data from: '{self.tess_path}'")
        self.log.append(
            f" ~ found {len(df)} datapoints in the timeframe: [{df["mjd"].min():.2f}, {df["mjd"].max():.2f}]"
        )
        # (end)

    def _load_ninja_gti(self):  # (fold)
        with fits.open(self.gti_path) as hdul:
            gti = hdul["STDGTI"]
            mjdref = gti.header["MJDREF"]  # type: ignore
            start = np.array(gti.data["START"])  # type: ignore
            stop = np.array(gti.data["STOP"])  # type: ignore
        intervals = np.column_stack((start, stop))
        mjd_intervals = intervals / (60 * 60 * 24) + mjdref
        self._track_context("num_gti_intervals", len(intervals))
        self.gti = mjd_intervals
        self.log.append(f"Loaded NinjaSat GTI-info from: '{self.gti_path}'")
        self.log.append(
            f" ~ found {len(mjd_intervals)} intervals, spanning the timeframe: [{mjd_intervals.min()}, {mjd_intervals.max()}]"
        )
        self.log.append(f" ~ total good time: {np.diff(mjd_intervals).sum():.2f} days")
        # (end)

    def _load_ninja_rmf(self):  # (fold)
        if self.rmf is not None:
            raise RuntimeError("CygX2Analysis.rmf was already loaded!")
        with fits.open(self.rmf_path) as hdul:
            ebounds = hdul["EBOUNDS"].data  # type: ignore
            channel = ebounds["CHANNEL"]
            e_min = ebounds["E_MIN"]
            e_max = ebounds["E_MAX"]
        e_center = 0.5 * (e_min + e_max)
        df = pd.DataFrame(
            {
                "channel": np.array(channel).astype(int),
                "energy": np.array(e_center).astype(float),
                "e_lo": np.array(e_min).astype(float),
                "e_hi": np.array(e_max).astype(float),
            }
        )
        self.rmf = df
        self.log.append(f"Loaded NinjaSat RMF-info from: '{self.rmf_path}'")
        # (end)

    def _select_good_time(self, df_name: str = "ninja_data"):  # (fold)
        if self.gti is None:
            raise RuntimeError(
                "Tried to select time inside gti, but no gti data was loaded yet!"
            )
        df = getattr(self, df_name)
        if df.empty:
            raise ValueError(f"{df_name} is empty, cannot apply GTI selection")
        mask = np.zeros(len(df), dtype=bool)
        mjd = df["mjd"].to_numpy()
        for start, stop in self.gti:
            mask |= (mjd >= start) & (mjd <= stop)
        setattr(self, df_name, df[mask])
        self._track_context("num_events_in_gti_" + df_name, mask.sum())
        self.log.append(f"Selected times inside good Time interval for {df_name}")
        dropped = len(df) - len(df[mask])
        self.log.append(f" ~ found and dropped {dropped} events outside gti")
        self.log.append(
            f" ~ {len(df[mask])} events remain ({(len(df[mask])/len(df) * 100):.0f}%)"
        )
        self._track_context("num_good_events", len(df[mask]))
        # (end)

    def _assign_ninja_channel_energy(self):  # (fold)
        if self.rmf is None:
            raise RuntimeError(
                "Tried to assign channel energy from rmf data, but no rmf data was loaded yet!"
            )
        # remove channels where channel==-1 (bad anyways):
        bad_channel = self.ninja_data.loc[self.ninja_data["channel"] == -1]
        self.ninja_data = self.ninja_data.loc[self.ninja_data["channel"] != -1]
        # add energy value to ninja_data
        self.ninja_data = self.ninja_data.merge(
            self.rmf[["channel", "energy"]], on="channel", how="left"
        )
        if bool(self.ninja_data["energy"].isna().any()):
            missing_channels = self.ninja_data.loc[
                self.ninja_data["energy"].isna(), "channel"
            ]
            self._track_context(
                "WARNING: Found channels without energy:", missing_channels
            )
            self.log.append(
                "Tried to assign channel energy from rmf data but found hanging channels"
            )
        else:
            self.log.append(
                "Assigned channel-energy information from rmf data successfully"
            )
        if len(bad_channel > 0):
            self.log.append(
                f" ~ found and dropped {len(bad_channel)} events with channel no. '-1'"
            )
            self.log.append(f" ~ {len(self.ninja_data)} events remain ")
            self._track_context("num_good_events", len(self.ninja_data))
            # (end)

    def _mask_non_overlaping_gtis(self):  # (fold)
        if self.gti is None:
            raise RuntimeError(
                "Tried to overlap counts inside gti, but no gti data was loaded yet!"
            )
        ninja_t = self.ninja_data["mjd"].to_numpy()
        tess_t = self.tess_data["mjd"].to_numpy()
        ninja_mask = np.zeros(len(ninja_t), dtype=bool)
        tess_mask = np.zeros(len(tess_t), dtype=bool)

        for start, stop in self.gti:
            ninja_in = (ninja_t >= start) & (ninja_t <= stop)
            tess_in = (tess_t >= start) & (tess_t <= stop)

            if tess_in.any():
                ninja_mask |= ninja_in

            if ninja_in.any():
                tess_mask |= tess_in

        self.log.append(
            f"Masked events in ninja and tess data where no simultaneous observation happened"
        )
        self.log.append(
            f" ~ remaining events in ninja: {ninja_mask.sum()}; - datapoints in tess: {tess_mask.sum()}"
        )
        self.ninja_data = self.ninja_data.loc[ninja_mask]
        self.tess_data = self.tess_data.loc[tess_mask]
        self._track_context("num_good_events", len(self.ninja_data))
        self._track_context("num_good_datapoints_tess", len(self.tess_data))
        # (end)

    ############################################
    ########    Interactive Functions   ########
    ############################################

    def assign_ninja_colorbands(self, colorbands):  # (fold)
        self.colorbands = colorbands
        self.ninja_data["band"] = pd.NA
        for name, (e_lo, e_hi) in colorbands.items():
            mask = (self.ninja_data["energy"] > e_lo) & (
                self.ninja_data["energy"] <= e_hi
            )
            self.ninja_data.loc[mask, "band"] = name
        outside_bands = self.ninja_data["band"].isna()
        drp_bins = sorted(
            set([drp_bin for band in self.colorbands.values() for drp_bin in band])
        )
        drp_bins = np.insert(drp_bins, 0, 0)
        drp_bins = np.append(drp_bins, 500)
        n_dropped, _ = np.histogram(
            self.ninja_data.loc[outside_bands, "energy"], drp_bins
        )
        self.log.append(f"Assigned colorbands to ninja data")
        self.log.append(
            f" ~ found {outside_bands.sum()} events outside of the provided colorband-energyrange ({n_dropped[0]} below, {n_dropped[-1]} above)."
        )
        remaining = self.context["num_good_events"] - outside_bands.sum()
        self.log.append(f" ~ {remaining} events remain")
        self._track_context("num_events_in_colorband_range", remaining)
        # (end)

    def make_timebins(self, binsize_sec):  # (fold)
        if self.gti is None:
            raise RuntimeError("GTI not loaded yet!")
        self.binsize_sec = binsize_sec
        dt = binsize_sec / 86400  # convert to days
        edges = []
        for start, end in self.gti:
            local_edges = np.arange(start, end, dt)
            if local_edges[-1] < end:
                local_edges = np.append(local_edges, end)
            edges.append(local_edges)
        edges = np.unique(np.concatenate(edges))
        self.time_bins = edges
        self.log.append(
            f"Binned {len(self.gti)} GTI intervals into {self.binsize_sec}s time bins"
        )
        binsizes_sec = np.diff(edges) * 86400
        self.log.append(f" ~ yielded {(binsizes_sec < 601).sum()} valid time bins")
        self._track_context("num_bins", len(self.time_bins))
        # (end)

    def bin_ninja_lightcurve(self):  # (fold)
        if self.time_bins is None:
            raise RuntimeError(
                "Found no time bins! Please run bin_gti() or provide you own bins."
            )
        if self.colorbands is None:
            raise RuntimeError("Found no colorbands! Please provide some colorbands.")

        df = self.ninja_data
        bins = self.time_bins
        bin_widths_sec = np.diff(bins) * 86400
        self._track_context(
            "num_gap_bins(larger_than_600s)", (bin_widths_sec > 601).sum()
        )
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        rows = []
        counts, _ = np.histogram(df["mjd"], self.time_bins)
        rate = counts / bin_widths_sec
        rate_err = np.sqrt(counts) / bin_widths_sec
        for t, r, r_err in zip(bin_centers, rate, rate_err):
            rows.extend(
                [
                    {
                        "name": "ninja",
                        "band": "all",
                        "mjd": t,
                        "cr": r,
                        "cr_err": r_err,
                    }
                ]
            )
        df2 = pd.DataFrame(rows)
        df2 = df2[df2["cr"] > 0].reset_index(drop=True)

        if hasattr(self, "lightcurve_data") and not self.lightcurve_data.empty:
            self.lightcurve_data = pd.concat(
                [self.lightcurve_data, df2], ignore_index=True
            )
        else:
            self.lightcurve_data = df2
        self.log.append(f"Calculated ninjasat lightcurve")
        first_band = next(iter(self.colorbands))
        self.log.append(
            f" ~ got a total of {df2[df2['band'] == first_band].shape[0]} datapoints per band"
        )
        self._track_context("num_lightcurve_bins", len(df2))
        # (end)

    def bin_ninja_colorbands(self, colorbands: dict | None = None):  # (fold)
        if self.time_bins is None:
            raise RuntimeError(
                "Found no time bins! Please run bin_gti() or provide you own bins."
            )
        if colorbands:
            self.colorbands = colorbands

        if self.colorbands is None:
            raise RuntimeError("Found no colorbands! Please provide some colorbands.")

        df = self.ninja_data
        bins = self.time_bins
        bin_widths_sec = np.diff(bins) * 86400
        self._track_context(
            "num_gap_bins(larger_than_600s)", (bin_widths_sec > 601).sum()
        )
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        rows = []
        for band in self.colorbands.keys():
            evts_in_band = df.loc[df["band"] == band, "mjd"].to_numpy()
            counts, _ = np.histogram(evts_in_band, self.time_bins)
            rate = counts / bin_widths_sec
            rate_err = np.sqrt(counts) / bin_widths_sec
            for t, r, r_err in zip(bin_centers, rate, rate_err):
                rows.extend(
                    [
                        {
                            "name": "ninja",
                            "band": band,
                            "mjd": t,
                            "cr": r,
                            "cr_err": r_err,
                        }
                    ]
                )
        df2 = pd.DataFrame(rows)
        df2 = df2[df2["cr"] > 0].reset_index(drop=True)

        if hasattr(self, "lightcurve_data") and not self.lightcurve_data.empty:
            self.lightcurve_data = pd.concat(
                [self.lightcurve_data, df2], ignore_index=True
            )
        else:
            self.lightcurve_data = df2
        self.log.append(f"Calculated ninjasat lightcurve")
        first_band = next(iter(self.colorbands))
        self.log.append(
            f" ~ got a total of {df2[df2['band'] == first_band].shape[0]} datapoints per band"
        )
        self._track_context("num_lightcurve_bins", len(df2))
        # (end)

    def rebin_tess_lightcurve(self):  # (fold)
        """
        Rebins the tess-lightcurve while propagating the inverse-variance
        weighted mean error provided by tess.
        """
        df = self.tess_data
        if self.time_bins is None:
            raise RuntimeError(
                "Found no time bins! Please run bin_gti() or provide you own bins."
            )
        bins = self.time_bins
        bin_idx = np.digitize(df["mjd"], bins) - 1

        result = []
        for i in range(len(bins) - 1):
            mask = bin_idx == i
            sub = df[mask]

            if len(sub) == 0:
                result.append(
                    {
                        "name": "tess",
                        "band": "optical",
                        "mjd": 0.5 * (bins[i] + bins[i + 1]),
                        "cr": np.nan,
                        "cr_err": np.nan,
                    }
                )
                continue
            w = 1.0 / (sub["cr_err"] ** 2)

            flux = np.sum(w * sub["cr"]) / np.sum(w)
            flux_err = np.sqrt(1.0 / np.sum(w))

            result.append(
                {
                    "name": "tess",
                    "band": "optical",
                    "mjd": 0.5 * (bins[i] + bins[i + 1]),
                    "cr": flux,
                    "cr_err": flux_err,
                }
            )

        df2 = pd.DataFrame(result)
        if hasattr(self, "lightcurve_data") and not self.lightcurve_data.empty:
            self.lightcurve_data = pd.concat(
                [self.lightcurve_data, df2], ignore_index=True
            )
        else:
            self.lightcurve_data = df2
        self.log.append(f"Calculated tess lightcurve")
        # (end)

    def plot_lc(  # (fold)
        self, ninja: bool = True, tess: bool = True, gti: bool = False, ax=None
    ):

        if not hasattr(self, "lightcurve_data"):
            raise RuntimeError("Data hasn't been analyzed yet.")

        import matplotlib.pyplot as plt

        axpassed = True
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 5))
            axpassed = False
        if ninja and hasattr(self, "lightcurve_data"):
            df = self.lightcurve_data
            df = df[df["name"] == "ninja"]
            mjd = df["mjd"]
            c = df["cr"]
            c_err = df["cr_err"]
            ax.errorbar(
                mjd,
                c,
                yerr=c_err,
                label="NinjaSat",
                fmt=".",
                alpha=0.5,
            )
        if tess and hasattr(self, "lightcurve_data"):
            df = self.lightcurve_data
            df = df[df["name"] == "tess"]
            mjd = df["mjd"]
            c = df["cr"]
            c_err = df["cr_err"]
            ax.errorbar(
                mjd,
                c,
                yerr=c_err,
                label="TESS",
                fmt=".",
                alpha=0.5,
            )
        if gti and hasattr(self, "gti"):
            for start, stop in self.gti:
                plt.axvspan(start, stop, color="orange", alpha=0.3)
        ax.set_xlabel("Time [mjd]")
        ax.set_ylabel("Count Rate [photons/s]")
        ax.legend()

        if not axpassed:
            plt.show()
        else:
            return fig, ax
            # (end)


ninja_path = "../../autodata/out/merged.evt"
tess_path = "../../data/CygnusX-2/TESS/tess2024249191853-s0083-0000000468511196-0280-a_fast-lc.fits"
gti_path = "../../autodata/tmp/CygX2.gti"
rmf_path = "../../autodata/out/CygX2.rmf"

test = CygX2Analysis(
    ninja_path=ninja_path, tess_path=tess_path, gti_path=gti_path, rmf_path=rmf_path
)


ninja_bands1 = {
    "soft": (1, 4),
    "med": (4, 8),
    "hard": (8, 20),
}
test.assign_ninja_colorbands(ninja_bands1)
test.make_timebins(binsize_sec=600)
test.bin_ninja_lightcurve()
test.rebin_tess_lightcurve()
test.print_report()

test.plot_lc(gti=True)

# n = test.ninja_data
# print(n)
# for band in ninja_bands1.keys():
#     print(n.loc[n["band"] == band, "mjd"])
