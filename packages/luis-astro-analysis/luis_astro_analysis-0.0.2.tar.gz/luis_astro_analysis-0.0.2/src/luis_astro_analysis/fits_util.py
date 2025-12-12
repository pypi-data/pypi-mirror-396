import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from astropy.io import fits


def read_evt_times(path: str, evt_hdu: str = "EVENTS") -> np.ndarray:  # (fold)
    """
    Extracts mjd-time of all photon events from a fits file at path

    Returns
    -------
    numpy.ndarray
        1D array containing event times in mjd format
    """
    with fits.open(path) as hdul:
        evt = hdul[evt_hdu].data
        hdr = hdul[evt_hdu].header

    mjdref = hdr["MJDREF"]
    time = evt["TIME"]
    time_mjd = mjdref + time / 86400.0  # sec -> day

    return time_mjd
    # (end)


def extract_spectrum(
    spec_path, bckgrnd_path="", arf_path="", rmf_path="", model=False, plot=False
):  # (fold)

    final_df = pd.DataFrame()
    with fits.open(spec_path) as hdul:
        spec = hdul["SPECTRUM"].data
        hd_s = hdul["SPECTRUM"].header

        counts_spec = spec["COUNTS"]
        channels = spec["CHANNEL"]
        expo_spec = hd_s["EXPOSURE"]

        cr_spec = counts_spec / expo_spec

        final_df["cr_raw"] = cr_spec
        final_df["channel"] = channels

    if bckgrnd_path != "":
        with fits.open(bckgrnd_path) as hdul:
            back = hdul["SPECTRUM"].data
            hd_b = hdul["SPECTRUM"].header

            counts_back = back["COUNTS"]
            expo_back = hd_b["EXPOSURE"]

            cr_back = counts_back / expo_back

            cr_b_corr = counts_spec / expo_spec - counts_back / expo_back

            final_df["cr_bck_corr"] = cr_b_corr

    if model:
        if rmf_path != "":
            with fits.open(rmf_path) as hdul:
                ebounds = hdul["EBOUNDS"].data
                matrix = hdul["MATRIX"].data

            n_energy = len(matrix)
            n_channels = len(ebounds)

            e_lo = matrix["ENERG_LO"]
            e_hi = matrix["ENERG_HI"]

            # decompress rmf matrix
            R = np.zeros((n_energy, n_channels), dtype=np.float32)

            for i, row in enumerate(matrix):
                n_grp = row["N_GRP"]
                f_chan = np.atleast_1d(row["F_CHAN"])  # ensure array
                n_chan = np.atleast_1d(row["N_CHAN"])
                vals = row["MATRIX"]

                offset = 0
                for g in range(n_grp):
                    start = f_chan[g] - 1  # FITS uses 1-based indexing
                    end = start + n_chan[g]
                    R[i, start:end] = vals[offset : offset + n_chan[g]]
                    offset += n_chan[g]

            # PLOT RMF(fold)
            # plt.imshow(R, origin="lower", aspect="auto",
            #            extent=[0, n_channels, 0, n_energy])
            # plt.xlabel("Channel")
            # plt.ylabel("Energy bin")
            # plt.title("Redistribution Matrix (RMF)")
            # plt.colorbar(label="Response probability")
            # plt.show()(end)

            if arf_path != "":
                with fits.open(arf_path) as hdul:
                    arf = hdul["SPECRESP"].data

                energy_lo = arf["ENERG_LO"]
                energy_hi = arf["ENERG_HI"]
                eff_area = arf["SPECRESP"]

                # PLOT EFF AREA(fold)
                # energy_mid = 0.5 * (energy_lo + energy_hi)
                # plt.figure(figsize=(7, 4))
                # plt.plot(energy_mid, area, lw=1.2)
                # plt.xlabel("Energy (keV)")
                # plt.ylabel("Effective Area (cm²)")
                # plt.title("Auxiliary Response (ARF)")
                # plt.grid(alpha=0.3)
                # plt.tight_layout()
                # plt.show()(end)

                # combine eff_area and rmf
                R_full = R * eff_area[:, np.newaxis]

                # PLOT EFF AREA + RESPONSE(fold)
            # plt.imshow(R_full, origin="lower", aspect="auto", extent=[0, n_channels, 0, n_energy])
            # plt.xlabel("Channel")
            # plt.ylabel("Energy bin")
            # plt.title("Full Response (ARF × RMF)")
            # plt.colorbar(label="Effective response")
            # plt.show()(end)

    else:
        if rmf_path != "":
            with fits.open(rmf_path) as hdul:
                ebounds = hdul["EBOUNDS"].data

            ch = ebounds["CHANNEL"]
            e_lo = ebounds["E_MIN"]
            e_hi = ebounds["E_MAX"]

            e_mid = 0.5 * (e_lo + e_hi)

            final_df["energy"] = e_mid

            # ch_min, ch_max = 20, 200
            #
            # ch_start = spec["CHANNEL"][0]  # e.g. 1
            # e_mid_cut = e_mid[(20 - ch_start) : (200 - ch_start + 1)]
            # counts_cut = cr_spec[(20 - ch_start) : (200 - ch_start + 1)]

            if plot:

                plt.figure()
                sns.set_style("whitegrid")
                plt.step(e_mid_cut, counts_cut, where="mid", label="countrate")

                if bckgrnd_path != "":
                    bckgnd_cut = cr_back[(20 - ch_start) : (200 - ch_start + 1)]
                    corr_cut = cr_b_corr[(20 - ch_start) : (200 - ch_start + 1)]
                    plt.step(e_mid_cut, bckgnd_cut, where="mid", label="background")
                    plt.step(e_mid_cut, corr_cut, where="mid", label="corrected")

                plt.xlabel("Energy (keV)")
                plt.ylabel("Counts")
                # plt.xscale("log")   # optional
                # plt.yscale("log")   # optional
                plt.title("observed spectrum vs. energy")
                plt.show()

    def p():
        plt.figure(figsize=(8, 5))

        plt.step(channels[20:200], cr_spec[20:200], where="mid")
        if bckgrnd_path != "":
            plt.step(channels[20:200], cr_back[20:200], where="mid")
            plt.step(channels[20:200], cr_b_corr[20:200], where="mid")

        plt.xlabel("PI channel")
        plt.ylabel("Counts")
        plt.title("Spectrum")
        plt.grid(True)
        plt.legend()
        plt.show()

    if plot:
        # p()
        pass

    return final_df


# (end)


# data_dir = "../data/CygnusX-2/NinjaSat"
# extract_spectrum(f"{data_dir}/CygX2.pha",
#                  bckgrnd_path=f"{data_dir}/Background.pha",
#                  rmf_path=f"{data_dir}/CygX2.rmf",
#                  arf_path=f"{data_dir}/CygX2.arf"
# )


def read_rmf_ebounds(rmf_path) -> pd.DataFrame:  # (fold)
    """
    Extracts the energy boundaries for each detector channel from the rmf-fits
    file a path

    Returns
    -------
    pd.DataFrame
        Columns:
        - "channel" : int
        - "energy"  : float
        - "e_lo"    : float
        - "e_hi"    : float
    """
    with fits.open(rmf_path) as hdul:
        ebounds = hdul["EBOUNDS"].data
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

    return df  # (end)


def read_mjd_channel(path: str) -> pd.DataFrame:  # (fold)
    """
    Extracts mjd-time and channel of all photon events from a fits file at path

    Returns
    -------
    pd.DataFrame
        Columns:
        - "mjd" : float
        - "channel" : int
    """
    with fits.open(path) as hdul:
        evt = hdul["EVENTS"].data
        hdr = hdul["EVENTS"].header

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

    return df  # (end)


def read_gti_intervals(path: str) -> np.ndarray:  # (fold)
    """
    Extracts the gti (good-time-intervals) im mjd-format
    from the fits file at path.

    Returns
    -------
    numpy.ndarray
        2D array of shape (N, 2)
        - Column 0: start times
        - Column 1: stop times
    """
    with fits.open(path) as hdul:
        gti = hdul["STDGTI"]

        mjdref = gti.header["MJDREF"]

        start = np.array(gti.data["START"])
        stop = np.array(gti.data["STOP"])

        intervals = np.column_stack((start, stop))
        mjd_intervals = intervals / (60 * 60 * 24) + mjdref

        return mjd_intervals


# (end)


def select_good_time(mjd: np.ndarray, gti: np.ndarray):  # (fold)
    """
    Extracts the event-times that lie inside the good-time-intervals
    Returns
    -------
    numpy.ndarray
        1D array (bool-mask)
    """
    mask = np.zeros(len(mjd), dtype=bool)
    for start, stop in gti:
        mask |= (mjd >= start) & (mjd <= stop)

    return mask


# (end)


def bin_gti(gti: np.ndarray, binsize_sec: float) -> np.ndarray:  # (fold)
    """
    Create time bins inside the GTIs, allowing partial bins
    for handling short GTIs.

    Parameters
    ----------
    gti : np.ndarray, shape (N,2)
        Array of GTIs, each row = [start, end] (in MJD)
    binsize_sec : int
        Desired bin width in seconds

    Returns
    -------
    bin_edges : np.ndarray
        Concatenated array of bin edges for all GTIs
    """
    binsize_day = binsize_sec / (60 * 60 * 24)
    edges = [0]

    for idx, (start, end) in enumerate(gti):

        # ---- 1) Insert gap between GTIs as a big bin ----
        if idx > 0:
            prev_end = gti[idx - 1, 1]
            if start > prev_end:
                # Add the gap as a single bin
                edges.append(prev_end)
                edges.append(start)

        # ---- 2) Make fine bins inside the GTI ----
        interval_edges = np.arange(start, end, binsize_day)

        # Ensure last edge is exactly the GTI end
        if interval_edges[-1] != end:
            interval_edges = np.append(interval_edges, end)

        # Append edges
        edges.extend(interval_edges)

    # Remove duplicates from gap insertion
    return np.unique(np.array(edges))


# (end)


def bin_lightcurve(  # (fold)
    evt_times: np.ndarray, binsize_sec: int, gti: np.ndarray | None = None
) -> pd.DataFrame:
    """
    Compute count_rate and poisson error for event times.
    Can be given a a gti-array, shape (N,2), to select only gti-valid events.
    Pack the results into a pandas DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns:
        - "t"   : time-centers of bins
        - "cr"  : count rate inside each bin
        - "err" : Poisson error of the count rate
    """
    binsize_day = binsize_sec / 86400

    if gti is not None:
        mask = select_good_time(evt_times, gti)
        good_mjd = evt_times[mask]
        print(
            f"Total events: {len(evt_times)}, Inside GTI: {len(good_mjd)} ({(len(good_mjd)/len(evt_times) * 100):.0f}%)"
        )
        mjd = good_mjd

        bins = bin_gti(gti, binsize_day)

        durations = gti[:, 1] - gti[:, 0]
        print(f"Total good time: {durations.sum()}")
        print(f"Average gti-size: {durations.sum()/len(gti)}")
        print(f"expected amount of bins in gti: {durations.sum()/len(gti)/binsize_day}")

    else:
        mjd = evt_times
        t_min, t_max = mjd.min(), mjd.max()
        bins = np.arange(t_min, t_max + binsize_day, binsize_day)

    # NOTE: np.histogram() doesn't know about the gti, so it also counts
    # inbeween the gti. This is not gave however, since we omitted all counts
    # outside the gti, so the counts there will just total to zero and can be
    # masked easily.
    counts, edges = np.histogram(mjd, bins=bins)
    mjd_center = 0.5 * (edges[1:] + edges[:-1])

    # handle uneven bins (in case of gti)
    bin_widths = np.diff(edges)
    bin_widths_sec = bin_widths * 86400

    # mask zero-events ()
    mask_zero = counts > 0
    counts = counts[mask_zero]
    bin_widths_sec = bin_widths_sec[mask_zero]
    mjd_center = mjd_center[mask_zero]

    rate = counts / bin_widths_sec
    rate_err = np.sqrt(counts) / bin_widths_sec

    df = pd.DataFrame({"t": mjd_center, "cr": rate, "err": rate_err}).astype(float)
    return df


# (end)


def plot_lightcurve(df, t_start=None, t_stop=None, ax=None):  # (fold)
    if t_start:
        if t_start >= df["t"].min():
            df = df[df["t"] >= t_start]

    if t_stop:
        if t_stop <= df["t"].max():
            df = df[df["t"] <= t_stop]

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    sns.lineplot(data=df)
    ax.set_ylabel("Counts [s]")
    ax.set_xlabel("Time [mjd]")

    return ax


# (end)
