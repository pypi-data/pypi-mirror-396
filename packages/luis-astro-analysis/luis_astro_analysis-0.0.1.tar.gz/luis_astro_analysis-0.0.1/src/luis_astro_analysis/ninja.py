import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.path import Path
from matplotlib.widgets import PolygonSelector

import fits_util.fits_util as f


def color_color_intensity(  # (fold)
    evt_path: str = "",
    rmf_path: str = "",
    gti_path: str = "",
    bands=None,
    binsize_sec=600,
    plt_cc=True,
    plt_ci=True,
    error_threshold=None,
):
    """
    Plot Colour-Colour and Colour-Intensity plots from event-, rmf, and gti
    files.
    Colourbands have to be specified in the form of a python dictionary:
    bands = {
        "band1" : (e_low1, e_high1)
        ...
    }
    For now, only three bands are supported.
    -------
    Returns
    Nothing.
    """

    if not bands:
        print("please provide colorbands")
        return 0

    # load necessary data
    events = f.read_mjd_channel(evt_path)
    total_evts = len(events)
    rmf_info = f.read_rmf_ebounds(rmf_path)
    gti = f.read_gti_intervals(gti_path)
    print(len(gti))

    df = events.merge(rmf_info[["channel", "energy"]], on="channel", how="left")

    # select events inside gti
    print("Step 1: Filter GTI")
    mask = f.select_good_time(df["mjd"].to_numpy(), gti)
    df = df[mask]

    checksum = len(df)
    durations = np.diff(gti)
    print(f"  Total good time: {durations.sum():.2f} days")
    print(f"  Total events: {total_evts}, Inside GTI: {checksum}")
    print(
        f"  Dropping {total_evts-checksum} events (-{(checksum/total_evts * 100):.0f}%)."
    )

    # assign colorband to energy
    print("Step 2: Assign Color-bands")
    df["band"] = pd.NA
    for name, (e_lo, e_hi) in bands.items():
        mask = (df["energy"] > e_lo) & (df["energy"] <= e_hi)
        df.loc[mask, "band"] = name

    # check unassigned events (update checksum)
    outside_bands = df["band"].isna()
    drp_bins = sorted(set([drp_bin for band in bands.values() for drp_bin in band]))
    drp_bins = np.insert(drp_bins, 0, 0)
    drp_bins = np.append(drp_bins, 500)
    n_dropped, _ = np.histogram(df.loc[outside_bands, "energy"], drp_bins)
    print(
        f"  Dropping another {outside_bands.sum()} (-{(outside_bands.sum() / checksum *
        100):.0f}%) events ({n_dropped[0]} below, {n_dropped[-1]} above band-energy-range)."
    )
    checksum_2 = checksum - outside_bands.sum()
    print(
        f"  {checksum_2} events remain. ({(checksum_2/total_evts*100):.0f}% of total events)"
    )
    df = df.dropna(subset=["band"])

    # time-binning
    print("Step 3: Time-binning")
    binsize_day = binsize_sec / 86400
    bins = f.bin_gti(gti, binsize_day)

    data = []

    for band in bands.keys():
        counts, edges = np.histogram(df.loc[df["band"] == band, "mjd"], bins)
        mjd_center = (edges[:-1] + edges[1:]) / 2

        # handle uneven bins (due to gti)
        bin_widths = np.diff(edges)
        bin_widths_sec = bin_widths * 86400

        # mask zero-events:
        mask_zero = counts > 0
        counts = counts[mask_zero]
        bin_widths_sec = bin_widths_sec[mask_zero]
        mjd_center = mjd_center[mask_zero]

        rate = counts / bin_widths_sec
        rate_err = np.sqrt(counts) / bin_widths_sec

        for t, c, r, r_err in zip(mjd_center, counts, rate, rate_err):
            row = {
                "band": band,
                "mjd": t,
                "count": c,
                "count_err": np.sqrt(c),
                "count_rate": r,
                "count_rate_err": r_err,
            }
            data.append(row)

    df2 = pd.DataFrame(data)

    # df2 = df2.sort_values(by="mjd")
    # for i in range(len(df2)):
    #     print(df2.iloc[i])

    # for band in bands.keys():
    #     print(f" Counts in {band}-band: {df2.loc[df2["band"] == band, "counts"].sum()}")

    print(
        f"  Binning with binsize {binsize_sec} s yielded {len(df2)} datapoints. ({len(bins)} bins in total)"
    )

    print("Step 4: Calculate Color-ratios")
    if len(bands) == 4:  # (fold)
        s_mask = df2["band"] == "soft"
        m1_mask = df2["band"] == "med"
        m2_mask = df2["band"] == "med2"
        h_mask = df2["band"] == "hard"

        soft_color = df2.loc[m1_mask, "counts"] / df2.loc[s_mask, "counts"]
        hard_color = df2.loc[h_mask, "counts"] / df2.loc[m2_mask, "counts"]

        # propagate errors:
        # for F=A/B -> s_R**2 = (delR/delA * s_A)**2 + (delR/delB * s_B)**2
        # <-> s_R = R * sqrt(s_A**2 / A**2 + s_B**2 / B**2)
        soft_color_error = soft_color * np.sqrt(
            (df2.loc[m1_mask, "errs"] / df2.loc[m1_mask, "counts"]) ** 2
            + (df2.loc[s_mask, "errs"] / df2.loc[s_mask, "counts"]) ** 2
        )
        hard_color_error = hard_color * np.sqrt(
            (df2.loc[h_mask, "errs"] / df2.loc[h_mask, "counts"]) ** 2
            + (df2.loc[m2_mask, "errs"] / df2.loc[m2_mask, "counts"]) ** 2
        )

        soft_intensity = df2.loc[s_mask, "counts"] / binsize_sec
        hard_intensity = df2.loc[h_mask, "counts"] / binsize_sec

        soft_intensity_err = np.sqrt(df2.loc[s_mask, "counts"]) / binsize_sec
        hard_intensity_err = np.sqrt(df2.loc[h_mask, "counts"]) / binsize_sec

        mjd = df2.loc[s_mask, "mjd_binned"]  # entries same for each band

        cc_df = pd.DataFrame(
            {
                "mjd": df2.loc[s_mask, "mjd_binned"].values,
                "soft_color": soft_color.values,
                "soft_color_err": soft_color_error.values,
                "hard_color": hard_color.values,
                "hard_color_err": hard_color_error.values,
                "soft_intensity": soft_intensity.values,
                "soft_intensity_err": soft_intensity_err.values,
                "hard_intensity": hard_intensity.values,
                "hard_intensity_err": hard_intensity_err.values,
            }
        )

        ci_df = pd.DataFrame(
            {
                "mjd": df2.loc[s_mask, "mjd_binned"].values,
                "soft_intensity": soft_intensity.values,
                "hard_intensity": hard_intensity.values,
                "soft_intensity_err": soft_intensity_err.values,
                "hard_intensity_err": hard_intensity_err.values,
            }
        )
    # (end)

    # if len(bands) == 3:
    else:
        s_mask = df2["band"] == "soft"
        m_mask = df2["band"] == "med"
        h_mask = df2["band"] == "hard"

        soft_c = df2.loc[s_mask, "count"].to_numpy()
        med_c = df2.loc[m_mask, "count"].to_numpy()
        hard_c = df2.loc[h_mask, "count"].to_numpy()

        soft_err = df2.loc[s_mask, "count_err"].to_numpy()
        med_err = df2.loc[m_mask, "count_err"].to_numpy()
        hard_err = df2.loc[h_mask, "count_err"].to_numpy()

        soft_color = med_c / soft_c
        hard_color = hard_c / med_c

        # propagate errors:
        soft_color_error = (
            np.sqrt((soft_c * med_err) ** 2 + (med_c * soft_err) ** 2) / soft_c**2
        )
        hard_color_error = (
            np.sqrt((hard_c * med_err) ** 2 + (med_c * hard_err) ** 2) / med_c**2
        )

        soft_intensity = df2.loc[s_mask, "count_rate"]
        hard_intensity = df2.loc[h_mask, "count_rate"]

        soft_intensity_error = df2.loc[s_mask, "count_rate_err"]
        hard_intensity_error = df2.loc[h_mask, "count_rate_err"]

        mjd = df2.loc[s_mask, "mjd"].to_numpy()

        if error_threshold:  # (fold)

            stacked = np.column_stack(
                [
                    soft_color,
                    soft_color_error,
                    hard_color,
                    hard_color_error,
                    soft_intensity,
                    soft_intensity_error,
                    hard_intensity,
                    hard_intensity_error,
                    mjd,
                ]
            )

            mask = (
                (stacked[:, 1] < error_threshold)
                & (stacked[:, 3] < error_threshold)
                & (stacked[:, 5] < error_threshold)
                & (stacked[:, 7] < error_threshold)
            )

            print(
                f"Removing large errors (>{error_threshold}) in soft/hard color and intensity; removed {mask.sum()}"
            )

            stacked = stacked[mask]

            (
                soft_color,
                soft_color_error,
                hard_color,
                hard_color_error,
                soft_intensity,
                soft_intensity_error,
                hard_intensity,
                hard_intensity_error,
                mjd,
            ) = stacked.T
        # (end)

    print("\nEvent count per band:")
    check = 0
    for band, (e_lo, e_hi) in bands.items():
        count = df2.loc[df2["band"] == band, "count"]
        print(
            f"  {band}\t({e_lo} - {e_hi}) keV\t: events: {count.sum()}; Avg counts/bin: {count[count > 0].mean():.2f}"
        )
        check += count.sum()
    passed = (
        "passed, no unexpected event losses"
        if checksum_2 == check
        else f"failed: expected {checksum_2}, found {check}"
    )
    print(f"Checksum {passed}")
    print(f"Binsize (sec): {binsize_sec}; N Bins: {len(bins)}")

    # categorize into branches:
    branches = np.array(["unclassified"] * len(mjd))
    branch_names = ["Horizontal", "Normal", "Flaring"]
    datapoints = np.vstack([soft_color, hard_color]).T
    markers = {"Horizontal": "^", "Normal": "s", "Flaring": "o", "unclassified": "x"}
    branch_polys = {}

    # Interactive selection function
    def select_branch(branch_name):
        selected_indices = []
        verts_store = []

        def onselect(verts):
            path = Path(verts)
            mask = path.contains_points(datapoints)
            selected_indices.extend(np.where(mask)[0])
            verts_store.extend([verts])
            plt.close()  # close after drawing polygon

        fig, ax = plt.subplots()
        ax.scatter(soft_color, hard_color, s=40, c="gray", alpha=0.6)
        ax.set_xlabel("Soft color (M/S)")
        ax.set_ylabel("Hard color (H/M)")
        ax.set_title(f"Draw polygon for {branch_name}")

        selector = PolygonSelector(ax, onselect)
        plt.show()

        # Assign branch labels
        branches[selected_indices] = branch_name
        print(f"{branch_name}: selected {len(selected_indices)} points")

    # Loop over branches
    for branch in branch_names:
        select_branch(branch)

    def plot_ci(interactive=True):  # (fold)
        sns.set_style("whitegrid")
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        x_s = soft_intensity
        x_s_err = soft_intensity_error
        y_s = soft_color
        y_s_err = soft_color_error

        x_h = hard_intensity
        x_h_err = hard_intensity_error
        y_h = hard_color
        y_h_err = hard_color_error

        c_s = c_h = mjd

        axs[0].errorbar(
            x_s,
            y_s,
            xerr=x_s_err,
            yerr=y_s_err,
            fmt="none",  # don't draw additional points
            ecolor="gray",  # color of the errorbars
            alpha=0.6,  # transparency
            capsize=2,  # small caps at ends
            zorder=1,
        )

        if interactive:
            for branch, marker in markers.items():
                mask = branches == branch
                sc = axs[0].scatter(
                    x_s[mask],
                    y_s[mask],
                    c=c_s[mask],
                    cmap="viridis",
                    s=40,
                    marker=marker,
                    edgecolors="k",
                    alpha=0.8,
                    label=branch,
                    zorder=2,
                )

            for branch, verts in branch_polys.items():
                poly = patches.Polygon(
                    verts,
                    closed=True,
                    fill=False,
                    edgecolor="k",
                    linewidth=2,
                    alpha=0.5,
                    zorder=3,
                )
                axs[0].add_patch(poly)
        else:
            sc = axs[0].scatter(
                x_s,
                y_s,
                c=c_s,
                cmap="viridis",
                s=40,
                alpha=0.8,
                edgecolors="none",
                zorder=2,
            )

        cbar = plt.colorbar(sc, ax=axs[0])
        cbar.set_label("MJD")

        axs[0].set_ylabel("Soft color (M/S)")
        axs[0].set_xlabel("Intensity [counts/sec]")
        axs[0].legend(title="Branch")
        axs[0].set_title("Softness–Intensity Diagram", y=1.05)
        axs[0].grid(True, alpha=0.3)

        axs[1].errorbar(
            x_h,
            y_h,
            xerr=x_h_err,
            yerr=y_h_err,
            fmt="none",  # don't draw additional points
            ecolor="gray",  # color of the errorbars
            alpha=0.6,  # transparency
            capsize=2,  # small caps at ends
            zorder=1,
        )

        if interactive:
            for branch, marker in markers.items():
                mask = branches == branch
                sc = axs[1].scatter(
                    x_h[mask],
                    y_h[mask],
                    c=c_h[mask],
                    cmap="viridis",
                    s=60,
                    marker=marker,
                    edgecolors="k",
                    alpha=0.8,
                    label=branch,
                    zorder=2,
                )

        else:
            sc = axs[1].scatter(
                x_h,
                y_h,
                c=c_h,
                cmap="viridis",
                s=40,
                alpha=0.8,
                edgecolors="none",
                zorder=2,
            )

        cbar = plt.colorbar(sc, ax=axs[1])
        cbar.set_label("MJD")

        axs[1].set_ylabel("Hard color (M/S)")
        axs[1].set_xlabel("Intensity [counts/sec]")
        axs[1].legend(title="Branch")
        axs[1].set_title("Hardness–Intensity Diagram", y=1.05)
        axs[1].grid(True, alpha=0.3)

        fig.suptitle("Color-Intensity Diagram")
        plt.subplots_adjust(wspace=0.8)
        plt.show()

    # (end)

    def plot_cc(interactive=True):  # (fold)

        sns.set_style("whitegrid")
        fig, ax = plt.subplots(figsize=(6, 5))

        x = soft_color
        y = hard_color
        xerr = soft_color_error
        yerr = hard_color_error
        c = mjd

        ax.errorbar(
            x,
            y,
            xerr=xerr,
            yerr=yerr,
            fmt="none",  # don't draw additional points
            ecolor="gray",  # color of the errorbars
            alpha=0.6,  # transparency
            capsize=2,  # small caps at ends
            zorder=1,
        )

        if interactive:
            for branch, marker in markers.items():
                mask = branches == branch
                sc = ax.scatter(
                    x[mask],
                    y[mask],
                    c=c[mask],
                    cmap="viridis",
                    s=40,
                    marker=marker,
                    edgecolors="k",
                    alpha=0.8,
                    label=branch,
                    zorder=2,
                )

            for branch, verts in branch_polys.items():
                poly = patches.Polygon(
                    verts,
                    closed=True,
                    fill=True,
                    edgecolor="k",
                    linewidth=2,
                    alpha=0.3,
                    zorder=3,
                )
                ax.add_patch(poly)
        else:
            sc = ax.scatter(
                x, y, c=c, cmap="viridis", s=40, alpha=0.8, edgecolors="none", zorder=2
            )

        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("MJD (binned)")

        ax.set_xlabel("Soft color (M/S)")
        ax.set_ylabel("Hard color (H/M)")
        ax.legend(title="Branch")
        ax.set_title("Color–Color Diagram")
        ax.grid(True, alpha=0.3)

        plt.show()

    if plt_cc:
        plot_cc()
    if plt_ci:
        plot_ci()
    # (end)


# (end)


def extract_lightcurve(
    evt_path: str, binsize_sec: int, gti_path: str | None = None
) -> pd.DataFrame:
    """
    This function serves as a shortcut to extract lightcurve-data from NinjaSat-fits files.
    GTI will be taken into account, if specified.
    -------
    Returns:
    pandas.DataFrame with columns:
    - "t"
    - "cr"
    - "err"
    """
    evt_times = f.read_evt_times(evt_path)
    gti = f.read_gti_intervals(gti_path)

    lc = f.bin_lightcurve(evt_times, binsize_sec, gti=gti)

    return lc
