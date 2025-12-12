import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class CCI_Analyzer:
    def __init__(self) -> None:  # (fold)
        # DataFrames
        self._raw_data: pd.DataFrame | None = None
        self._banded_data: pd.DataFrame | None = None
        self._binned_data: pd.DataFrame | None = None
        self._colored_data: pd.DataFrame | None = None
        # Bins and Colors util
        self._colorbands: dict | None = None
        self._gti: np.ndarray | None = None
        self._bins: np.ndarray | None = None
        self.binsize_upper_threshold: int | None = None
        self.binsize_lower_threshold: int | None = None
        self._binsize_sec: int | None = None
        self._binsize_day: float | None = None
        self.markers = {
            "Horizontal": "^",
            "Normal": "s",
            "Flaring": "o",
            "unclassified": "x",
        }
        self.branch_colors = {
            "Horizontal": "tab:blue",
            "Normal": "tab:green",
            "Flaring": "tab:red",
            "unclassified": "gray",
        }
        # Information
        self._num_events: int | None = None
        self._num_good_events: int | None = None

    # (end)

    @property
    def raw_data(self):
        if self._raw_data is None:
            raise RuntimeError("No data loaded yet!")
        return self._raw_data

    @property
    def num_events(self):
        if self._num_events is None:
            raise RuntimeError("No data loaded yet!")
        return self._num_events

    @property
    def num_good_events(self):
        if self._num_good_events is None:
            raise RuntimeError("No data loaded yet!")
        return self._num_good_events

    @property
    def colorbands(self):
        if self._colorbands is None:
            raise RuntimeError("No colorbands loaded yet!")
        return self._colorbands

    @property
    def binsize_sec(self):
        if self._binsize_sec is None:
            raise RuntimeError("No binsize specified yet")
        return self._binsize_sec

    @property
    def binsize_day(self):
        if self._binsize_day is None:
            raise RuntimeError("No binsize specified yet")
        return self._binsize_day

    @property
    def bins(self):
        if self._bins is None:
            raise RuntimeError("Bins not loaded yet!")
        return self._bins

    @property
    def banded_data(self):
        if self._banded_data is None:
            raise RuntimeError("No Colorbands have been assigned yet!")
        return self._banded_data

    @property
    def binned_data(self):
        if self._binned_data is None:
            raise RuntimeError("Data has not been binned yet!")
        return self._binned_data

    @property
    def gti(self):  # (fold)
        if self._gti is None:
            raise RuntimeError("No gti array loaded yet!")  # (end)
        return self._gti

    @property
    def colored_data(self):
        if self._colored_data is None:
            raise RuntimeError("Data has not been 'colored' yet!")
        return self._colored_data

    def load_data(self, df: pd.DataFrame) -> None:  # (fold)
        """
        Load the data that is to be analyzed in form of a dataframe.
        Expected format:
        df = {
            "mjd"       : float
            "channel"   : int
        }
        """
        missing = {"mjd", "energy"} - set(df.columns)
        if missing:
            raise ValueError(f"The provided DataFrame has missing columns: {missing}")
        self._raw_data = df
        self._num_events = len(df)  # (end)

    def load_gti(self, gti: np.ndarray):  # (fold)
        """
        Load gti-information for binning-purposes, as a np.ndarray.
        Expected format:
        2D array of shape (N, 2)
        - Column 0 : start times
        - Column 1 : stop times
        """
        if not isinstance(gti, np.ndarray):
            raise TypeError("gti has to be of type numpy.ndarray")
        self._gti = gti  # (end)

    def load_bins(self, bins: np.ndarray) -> None:  # (fold)
        """
        Load a bin-array (np.ndarray). Only really useful for simple
        analysis.
        """
        if not isinstance(bins, np.ndarray):
            raise TypeError("bins must be a numpy ndarray")
        self._bins = bins  # (end)

    def set_bin_bounds(self, lower: int, upper: int):  # (fold)
        """
        Set boundaries for the bin-slider in the interactive window.
        If none are set, a default interval of [60, 2000] is used.
        """
        self.binsize_lower_threshold = lower
        self.binsize_upper_threshold = upper
        # (end)

    def set_colorbands(self, colorbands: dict) -> None:  # (fold)
        """
        Load and set a colorbands dictionary. The lower value of the soft band
        and the higher value of the hard band will be used as the boundaries
        for the band-selection sliders.
        Expected format:
        colorbands = {
            "soft": (lower:float, higher:float),
            "med": (lower:float, higher:float),
            "hard": (lower:float, higher:float),
        }
        """
        missing = {"soft", "hard", "med"} - colorbands.keys()
        if missing:
            raise ValueError(
                f"The provided colorbands-dict has missing items: {missing}"
            )
        df = self.raw_data
        self._colorbands = colorbands
        df["colorband"] = pd.NA
        for name, (e_lo, e_hi) in colorbands.items():
            mask = (df["energy"] > e_lo) & (df["energy"] <= e_hi)
            df.loc[mask, "colorband"] = name
        # check unassigned events
        outside_bands = df["colorband"].isna()
        drp_bins = sorted(
            set([drp_bin for band in colorbands.values() for drp_bin in band])
        )
        drp_bins = np.insert(drp_bins, 0, 0)
        drp_bins = np.append(drp_bins, 500)
        n_dropped, _ = np.histogram(df.loc[outside_bands, "energy"], drp_bins)
        print("Assigning Colorbands")
        print(
            f"  Dropping {outside_bands.sum()} (-{(outside_bands.sum() / self.num_events *
            100):.0f}%) events ({n_dropped[0]} below, {n_dropped[-1]} above band-energy-range)."
        )
        self._num_good_events = self.num_events - outside_bands.sum()
        print(
            f"  {self.num_good_events} events remain. ({(self.num_good_events/self.num_events*100):.0f}% of total events)"
        )
        df = df.dropna(subset=["colorband"])
        self._banded_data = df.copy()  # (end)

    def set_bins(self, binsize_sec: int):  # (fold)
        """
        This function checks whether a gti array was provided.
        If not, the whole time-axis will be binned using the specified width.
        Otherwise, bins will only be created inside the gti, stating
        at the left edge. If the next bin would reach outside the gti,
        it will be truncated to the right edge of the gti.
        Bins in between gti will have the same size as the gap.
        IMPORTANT:
        If gti has been loaded, the data has to be gti-corrected
        before this method can be applied.
        """
        binsize_day = binsize_sec / (60 * 60 * 24)
        if self._gti is None:
            print("WARNING: No bins were provided. Binning whole mjd axis.")
            t = self.raw_data["mjd"]
            t_min, t_max = t.min(), t.max()
            bins = np.arange(t_min, t_max + binsize_day, binsize_day)
            self.load_bins(bins)
        else:
            edges = [0]
            for idx, (start, end) in enumerate(self.gti):
                # Insert gap between GTIs as one big bin
                if idx > 0:
                    prev_end = self.gti[idx - 1, 1]
                    if start > prev_end:
                        # Add the gap as a single bin
                        edges.append(prev_end)
                        edges.append(start)
                # Make fine bins inside the GTI
                interval_edges = np.arange(start, end, binsize_day)
                # Ensure last edge is exactly the GTI end
                if interval_edges[-1] != end:
                    interval_edges = np.append(interval_edges, end)
                edges.extend(interval_edges)
            # Remove duplicates from gap insertion
            bins = np.unique(np.array(edges))
            self._bins = bins  # (end)

    def calculate_countrates(self) -> None:  # (fold)
        """
        This function uses a bin-array (with type numpy.ndarray) to
        calculate countrates for each colorband. Uneven bins are respected.
        Errors are calculated as the poisson-error, i.e. the sqrt of the couts.
        """
        df = self.banded_data
        bins = self.bins
        data = []
        for band in self.colorbands.keys():
            counts, edges = np.histogram(df.loc[df["colorband"] == band, "mjd"], bins)
            mjd_center = (edges[:-1] + edges[1:]) / 2
            # handle uneven bins
            bin_widths = np.diff(edges)
            bin_widths_sec = bin_widths * 86400
            # mask zero-events:
            mask_zero = counts > 0
            counts = counts[mask_zero]
            bin_widths_sec = bin_widths_sec[mask_zero]
            mjd_center = mjd_center[mask_zero]
            # assign countrates etc.
            rate = counts / bin_widths_sec
            rate_err = np.sqrt(counts) / bin_widths_sec
            for t, c, r, r_err in zip(mjd_center, counts, rate, rate_err):
                row = {
                    "colorband": band,
                    "mjd": t,
                    "c": c,
                    "c_err": np.sqrt(c),
                    "cr": r,
                    "cr_err": r_err,
                }
                data.append(row)
        df2 = pd.DataFrame(data)
        self._binned_data = df2
        print(
            f"  Binning yielded {len(df2)} datapoints. ({len(bins)} bins in total)"
        )  # (end)

    def calculate_color_ratios(  # (fold)
        self, error_threshold: float | None = None
    ) -> None:
        """
        This function calculates the color ratios
         - soft_color = med_counts/soft_counts
         - hard_color = hard_counts/med_counts
        with their respective errors and formats a dataframe containing
        all relevant data for the color-color and color-intensity
        analysis.
        """
        df = self.binned_data
        missing = {"colorband"} - set(df.columns)
        if missing:
            raise RuntimeError(
                f"The banded_data DataFrame has no assigned colorbands yet. Please assign colors first"
            )

        def pick(band, col):
            return df.loc[df["colorband"] == band, col].to_numpy()

        soft_c = pick("soft", "c")
        med_c = pick("med", "c")
        hard_c = pick("hard", "c")
        soft_err = pick("soft", "c_err")
        med_err = pick("med", "c_err")
        hard_err = pick("hard", "c_err")
        soft_intensity = pick("soft", "cr")
        hard_intensity = pick("hard", "cr")
        soft_intensity_error = pick("soft", "cr_err")
        hard_intensity_error = pick("hard", "cr_err")
        mjd = pick("soft", "mjd")
        if not (len(med_c) == len(soft_c) == len(hard_c)):
            raise ValueError(
                f"Bad Binsize: produced mismatched arrays "
                f"(med={len(med_c)}, soft={len(soft_c)}, hard={len(hard_c)}). "
                "Please try a different binsize."
            )
        soft_color = med_c / soft_c
        hard_color = hard_c / med_c
        # propagate errors:
        soft_color_error = (
            np.sqrt((soft_c * med_err) ** 2 + (med_c * soft_err) ** 2) / soft_c**2
        )
        hard_color_error = (
            np.sqrt((hard_c * med_err) ** 2 + (med_c * hard_err) ** 2) / med_c**2
        )
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
        for band, (e_lo, e_hi) in self.colorbands.items():
            count = df.loc[df["colorband"] == band, "c"]
            print(
                f"  {band}\t({e_lo} - {e_hi}) keV\t: events: {count.sum()}; Avg counts/bin: {count[count > 0].mean():.2f}"
            )
            check += count.sum()
        data = {
            "mjd": mjd,
            "soft_intensity": soft_intensity,
            "hard_intensity": hard_intensity,
            "soft_intensity_error": soft_intensity_error,
            "hard_intensity_error": hard_intensity_error,
            "soft_color": soft_color,
            "hard_color": hard_color,
            "soft_color_error": soft_color_error,
            "hard_color_error": hard_color_error,
        }
        self._colored_data = pd.DataFrame(data)  # (end)

    def select_bins_and_colors(self) -> None:  # (fold)
        """
        Interactively select the binsize (in seconds) and colorband-boundaries
        using sliders on a matplotlib figure.
        Updates self.colorbands and self.binsize_sec, when figure is closed.
        """
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Slider

        def draw_plots():  # (fold)
            df = self.colored_data
            axs[0].clear()
            axs[1].clear()
            axs[2].clear()

            # Softness-Intensity
            axs[0].errorbar(
                df["soft_intensity"],
                df["soft_color"],
                xerr=df["soft_intensity_error"],
                yerr=df["soft_color_error"],
                fmt="o",
                alpha=0.6,
            )
            axs[0].set_xlabel("Soft Intensity")
            axs[0].set_ylabel("Soft Color")
            axs[0].set_title("Softness-Intensity")

            # Hardness-Intensity
            axs[1].errorbar(
                df["hard_intensity"],
                df["hard_color"],
                xerr=df["hard_intensity_error"],
                yerr=df["hard_color_error"],
                fmt="o",
                alpha=0.6,
            )
            axs[1].set_xlabel("Hard Intensity")
            axs[1].set_ylabel("Hard Color")
            axs[1].set_title("Hardness-Intensity")

            # Color-Color
            axs[2].errorbar(
                df["soft_color"],
                df["hard_color"],
                xerr=df["soft_color_error"],
                yerr=df["hard_color_error"],
                fmt="o",
                alpha=0.6,
            )
            axs[2].set_xlabel("Soft Color")
            axs[2].set_ylabel("Hard Color")
            axs[2].set_title("Color-Color Diagram")
            # (end)

        # called by on_slider_change
        def refresh(val=None):  # (fold)
            self.set_bins(int(slider_bins.val))
            new_bands = {
                "soft": (self.colorbands["soft"][0], slider_soft_med.val),
                "med": (slider_soft_med.val, slider_med_hard.val),
                "hard": (slider_med_hard.val, self.colorbands["hard"][1]),
            }
            self.set_colorbands(new_bands)
            self.calculate_countrates()
            self.calculate_color_ratios(error_threshold=0.5)
            draw_plots()
            fig.canvas.draw_idle()
            # (end)

        # set colorbands to slider values on plot_close
        def on_close(event=None):  # (fold)
            self._colorbands = {
                "soft": (self.colorbands["soft"][0], slider_soft_med.val),
                "med": (slider_soft_med.val, slider_med_hard.val),
                "hard": (slider_med_hard.val, self.colorbands["hard"][1]),
            }
            self._binsize_sec = int(slider_bins.val)
            print("Final colorbands set to:", self.colorbands)
            print("Final binsize set to ", self.binsize_sec, "sec")
            # (end)

        # Initialize selection plot
        if self.binsize_upper_threshold is None:
            self.set_bin_bounds(60, 1000)
        self.calculate_countrates()
        self.calculate_color_ratios()  # initial calculation
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        plt.subplots_adjust(bottom=0.25)
        draw_plots()
        axcolor = "steelblue"
        ax_soft_med = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor=axcolor)
        ax_med_hard = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor=axcolor)
        slider_ax = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)

        slider_soft_med = Slider(
            ax_soft_med,
            "Soft-Med",
            valmin=self.colorbands["soft"][0],
            valmax=self.colorbands["med"][1],
            valinit=self.colorbands["soft"][1],
        )

        slider_med_hard = Slider(
            ax_med_hard,
            "Med-Hard",
            valmin=self.colorbands["med"][0],
            valmax=self.colorbands["hard"][1],
            valinit=self.colorbands["med"][1],
        )

        slider_bins = Slider(
            slider_ax,
            "Binsize (sec)",
            valmin=self.binsize_lower_threshold,
            valmax=self.binsize_upper_threshold,
            valstep=1,
            valinit=binsize_sec,
        )

        slider_bins.on_changed(refresh)
        slider_soft_med.on_changed(refresh)
        slider_med_hard.on_changed(refresh)
        fig.canvas.mpl_connect("close_event", on_close)
        plt.show()
        # (end)

    def select_branches(self) -> None:  # (fold)
        """
        Interactively group the datapoints into three branches, on a
        color-color diagram, by setting vertecies with mouseclicks that form a
        path on the diagram. Each path will be selected on a new diagram that
        displays the last selection. The selection is confirmed as soon as the
        path is closed, i.e. when the first vertex is clicked twice.
        """
        from matplotlib.path import Path
        from matplotlib.widgets import PolygonSelector

        df = self.colored_data
        missing = {
            "mjd",
            "soft_intensity",
            "hard_intensity",
            "soft_intensity_error",
            "hard_intensity_error",
            "soft_color",
            "hard_color",
            "soft_color_error",
            "hard_color_error",
        } - set(df.columns)
        if missing:
            raise RuntimeError(
                f"The colored_data DataFrame has missing fields: {missing}"
            )
        branches = np.array(["unclassified"] * len(df))
        branch_names = ["Horizontal", "Normal", "Flaring"]
        branch_polys = {}
        datapoints = np.vstack([df["soft_color"], df["hard_color"]]).T

        # visualize previous selections
        def plot_existing(ax):
            for branch in branch_names + ["unclassified"]:
                mask = branches == branch
                if mask.any():
                    ax.scatter(
                        df["soft_color"][mask],
                        df["hard_color"][mask],
                        s=40,
                        marker=self.markers[branch],
                        color=self.branch_colors[branch],
                        alpha=0.4,
                        label=branch,
                    )
            for polys in branch_polys.values():
                for verts in polys:
                    xs, ys = zip(*verts)
                    ax.plot(
                        xs + (xs[0],), ys + (ys[0],), "--", color="black", linewidth=1
                    )
            ax.legend()

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
            ax.set_xlabel("Soft color (M/S)")
            ax.set_ylabel("Hard color (H/M)")
            ax.set_title(f"Draw polygon for {branch_name}")
            plot_existing(ax)
            selector = PolygonSelector(ax, onselect)
            plt.show()
            branches[selected_indices] = branch_name
            print(f"{branch_name}: selected {len(selected_indices)} points")

        for branch in branch_names:
            select_branch(branch)
            self.colored_data["branch"] = branches  # (end)

    def _plot_ci(  # (fold)
        self, ax, x, xerr, y, yerr, colors, ylabel, title, marker_size=40
    ):
        """
        Internal helper function to plot color-intensity dat
        """
        ax.errorbar(
            x,
            y,
            xerr=xerr,
            yerr=yerr,
            fmt="none",
            ecolor="gray",
            alpha=0.6,
            capsize=2,
            zorder=1,
        )

        # scatter points (branch-separated)
        if "branch" in self.colored_data:
            last_scatter = None
            for branch, marker in self.markers.items():
                mask = self.colored_data["branch"] == branch
                last_scatter = ax.scatter(
                    x[mask],
                    y[mask],
                    c=colors[mask],
                    cmap="viridis",
                    s=marker_size,
                    marker=marker,
                    edgecolors="k",
                    alpha=0.8,
                    label=branch,
                    zorder=2,
                )
        else:
            last_scatter = ax.scatter(
                x,
                y,
                c=colors,
                cmap="viridis",
                s=marker_size,
                edgecolors="k",
                alpha=0.8,
                zorder=2,
            )

        ax.set_xlabel("Intensity [counts/sec]")
        ax.set_ylabel(ylabel)
        ax.set_title(title, y=1.05)
        ax.legend(title="Branch")
        ax.grid(True, alpha=0.3)

        return ax, last_scatter

    # (end)

    def plot_softness_intensity(self, ax=None):  # (fold)
        import matplotlib.pyplot as plt

        df = self.colored_data
        plot_self = False
        if ax is None:
            plot_self = True
            fig, ax = plt.subplots(figsize=(6, 5))

        ax, sc = self._plot_ci(
            ax,
            x=df["soft_intensity"],
            xerr=df["soft_intensity_error"],
            y=df["soft_color"],
            colors=df["mjd"],
            yerr=df["soft_color_error"],
            ylabel="Soft color (M/S)",
            title="Softness-Intensity",
            marker_size=40,
        )

        if sc is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label("MJD")

        if plot_self:
            plt.show()
        else:
            return ax

    # (end)

    def plot_hardness_intensity(self, ax=None):  # (fold)
        import matplotlib.pyplot as plt

        df = self.colored_data
        plot_self = False
        if ax is None:
            plot_self = True
            fig, ax = plt.subplots(figsize=(6, 5))

        ax, sc = self._plot_ci(
            ax,
            x=df["hard_intensity"],
            xerr=df["hard_intensity_error"],
            y=df["hard_color"],
            colors=df["mjd"],
            yerr=df["hard_color_error"],
            ylabel="Hard color (M/S)",
            title="Hardness-Intensity",
            marker_size=40,
        )

        if sc is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label("MJD")

        if plot_self:
            plt.show()
        else:
            return ax

    # (end)

    def plot_color_color(self, ax=None):  # (fold)
        import matplotlib.pyplot as plt

        df = self.colored_data
        plot_self = True
        if ax is None:
            plot_self = True
            fig, ax = plt.subplots(figsize=(6, 5))

        x = df["soft_color"]
        y = df["hard_color"]
        xerr = df["soft_color_error"]
        yerr = df["hard_color_error"]
        c = df["mjd"]

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

        if "branch" in df.columns:
            for branch, marker in self.markers.items():
                mask = self.colored_data["branch"] == branch
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
        else:
            sc = ax.scatter(
                x,
                y,
                c=c,
                cmap="viridis",
                s=40,
                edgecolors="k",
                alpha=0.8,
                zorder=2,
            )

        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("MJD")

        ax.set_xlabel("Soft color (M/S)")
        ax.set_ylabel("Hard color (H/M)")
        if "branch" in df.columns:
            ax.legend(title="Branch")
        ax.set_title("Color–Color")
        ax.grid(True, alpha=0.3)

        plt.show()

        # (end)

    def plot_color_intensity(self):  # (fold)
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        self.plot_softness_intensity(ax=axs[0])
        self.plot_hardness_intensity(ax=axs[1])
        plt.show()

    # (end)


# TESTING
# import fits_util as f
#
# ninja_path = "../../../autodata/out/merged.evt"
# gti_path = "../../../autodata/tmp/CygX2.gti"
# rmf_path = "../../../autodata/out/CygX2.rmf"
#
# ninja_bands = {
#     "soft": (2, 4),
#     "med": (4, 8),
#     "hard": (8, 20),
# }
#
# events = f.read_mjd_channel(ninja_path)
# total_evts = len(events)
# rmf_info = f.read_rmf_ebounds(rmf_path)
# gti = f.read_gti_intervals(gti_path)
# df = events.merge(rmf_info[["channel", "energy"]], on="channel", how="left")
# mask = f.select_good_time(df["mjd"].to_numpy(), gti)
# df = df[mask]
# binsize_sec = 600
# binsize_day = binsize_sec / 86400
# bins = f.bin_gti(gti, binsize_day)
#
# checksum = len(df)
# durations = np.diff(gti)
# print(f"  Total good time: {durations.sum():.2f} days")
# print(f"  Total events: {total_evts}, Inside GTI: {checksum}")
# print(f"  Dropping {total_evts-checksum} events (-{(checksum/total_evts * 100):.0f}%).")
#
# print(f"########################################")
#
#
# CCI = CCI_Analyzer()
#
# CCI.load_data(df)
# CCI.load_gti(gti)
# CCI.set_colorbands(ninja_bands)
# CCI.set_bins(600)
# CCI.set_bin_bounds(1, 1000)
# CCI.select_bins_and_colors()
# CCI.select_branches()
# CCI.plot_color_intensity()
# CCI.plot_color_color()
