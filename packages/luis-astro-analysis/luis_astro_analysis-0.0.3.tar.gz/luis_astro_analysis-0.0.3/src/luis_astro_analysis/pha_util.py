import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.optimize import curve_fit


def gaussian(x, A, mu, sig, C):
    return A * np.exp(-((x - mu) ** 2) / (2 * sig**2)) + C


def extract_spectrum(
    spec_path: str,
    bckgrnd_path="",
    arf_path="",
    rmf_path="",
    model=False,
    plot=False,
):  # (fold)

    final_df = pd.DataFrame()

    with fits.open(spec_path) as hdul:
        spec = hdul["SPECTRUM"].data
        hd_s = hdul["SPECTRUM"].header

        counts_spec = spec["COUNTS"].astype(int)
        channels = spec["CHANNEL"].astype(float)
        expo_spec = hd_s["EXPOSURE"]

        cr_spec = counts_spec / expo_spec

        final_df["channel"] = channels
        final_df["counts"] = counts_spec
        final_df["cr"] = cr_spec

    if bckgrnd_path != "":
        with fits.open(bckgrnd_path) as hdul:
            back = hdul["SPECTRUM"].data
            hd_b = hdul["SPECTRUM"].header

            back_df = pd.DataFrame(
                {
                    "channel": back["CHANNEL"].astype(int),
                    "cr_raw": back["COUNTS"].astype(float),
                }
            )
            back_df["cr"] = back_df["cr_raw"] / hd_b["EXPOSURE"]

            merged = pd.merge(final_df, back_df, on="channel", suffixes=("_s", "_b"))
            merged["diff"] = merged["cr_s"] - merged["cr_b"]

            final_df["cr_bck_corr"] = merged["diff"]

    if model:  # (fold)
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
        # (end)

    else:
        if rmf_path != "":
            with fits.open(rmf_path) as hdul:
                ebounds = hdul["EBOUNDS"].data

            ebounds_df = pd.DataFrame(
                {
                    "channel": ebounds["CHANNEL"].astype(int),
                    "e_lo": ebounds["E_MIN"].astype(float),
                    "e_hi": ebounds["E_MAX"].astype(float),
                }
            )

            # ebounds_df["e_mid"] = 0.5 * (ebounds_df["e_lo"] + ebounds_df["e_hi"])

            merged = pd.merge(final_df, ebounds_df, on="channel", suffixes=("_s", "_e"))
            merged["e_mid"] = 0.5 * (merged["e_lo"] + merged["e_hi"])

            final_df["energy"] = merged["e_mid"]

            # ch_min, ch_max = 20, 200
            # ch_start = spec["CHANNEL"][0]  # e.g. 1
            # e_mid_cut = e_mid[(20 - ch_start) : (200 - ch_start + 1)]
            # counts_cut = cr_spec[(20 - ch_start) : (200 - ch_start + 1)]
            #
            # plt.figure()
            # sns.set_style("whitegrid")
            # plt.step(e_mid_cut, counts_cut, where="mid", label="countrate")

            # if bckgrnd_path != "":
            #     bckgnd_cut = cr_back[(20 - ch_start) : (200 - ch_start + 1)]
            #     corr_cut = cr_b_corr[(20 - ch_start) : (200 - ch_start + 1)]
            #     plt.step(e_mid_cut, bckgnd_cut, where="mid", label="background")
            #     plt.step(e_mid_cut, corr_cut, where="mid", label="corrected")
            #
            # plt.xlabel("Energy (keV)")
            # plt.ylabel("Counts")
            # # plt.xscale("log")   # optional
            # # plt.yscale("log")   # optional
            # plt.title("observed spectrum vs. energy")
            # plt.show()

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
        p()

    return final_df


# (end)


def test():
    path = "/Users/lui/NinjaSat/python/test/CygX2.pha"
    with fits.open(path) as hdul:
        hdul.info()
        spec = hdul[1]
        for name in spec.columns.names:
            print(name)

        channels = spec.data["CHANNEL"]
        counts = spec.data["COUNTS"]

        channels, counts = channels[20:200], counts[20:200]

        # for a, b in zip(channels[::10], counts[::10]):
        #     print(a, ',', b)

        popt, pcov = curve_fit(gaussian, channels, counts, p0=[1400, 45, 20, 0])
        A, mu, sig, C = popt
        print(f"A={A:.1f}, mu={mu:.1f}, sig={sig:.1f}, C={C:.1f}")

        x_fit = np.linspace(min(channels), max(channels), 500)
        y_fit = gaussian(x_fit, *popt)

        plt.scatter(channels, counts)
        plt.plot(x_fit, y_fit)
        plt.yscale("log")
        plt.show()
