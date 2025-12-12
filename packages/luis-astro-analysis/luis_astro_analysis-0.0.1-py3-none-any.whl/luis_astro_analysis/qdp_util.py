import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def read(fname: str, colmap: dict, verbose=False) -> pd.DataFrame:

    with open(fname, "r") as f:
        lines = f.readlines()

    # To skip header, find first data-row
    data_start = 0
    for i, line in enumerate(lines):
        # Skip comment, QDP commands, and blank lines
        if line.startswith("!") and lines[i + 1].startswith("!"):
            data_start = i + 2

    # Read data from that line onward
    df = pd.read_csv(
        fname,
        sep=r"\s+",
        comment="!",
        skiprows=data_start,
        header=None,
    )

    df = df.iloc[:-1].astype(float)

    df.columns = colmap2header(colmap)

    if verbose:
        print(df)
    return df


def colmap2header(colmap):
    columns = [key for key, val in colmap.items() if isinstance(val, int)]
    columns.remove("n_bands")
    return sorted(columns, key=lambda k: colmap[k])


def get_binsize(df):
    if df.shape[0] < 2:
        raise ValueError("DataFrame must have at least 2 rows to calculate binsize.")

    time = df.iloc[:, 0].values
    binsize = time[1] - time[0]
    if time[1] + binsize == time[2]:
        return binsize
    else:
        raise ValueError


def to_seaborn(df, colmap) -> pd.DataFrame:
    out = pd.DataFrame()

    for i in range(1, colmap["n_bands"] + 1):
        tmp = pd.DataFrame(
            {
                "t": df["t"],
                "t_err_pos": df["t_err_pos"],
                "t_err_neg": df["t_err_neg"],
                "cr": df[f"cr{i}"],
                "err": df[f"cr{i}_err"],
                "band": colmap[f"cr{i}_band"],
            }
        )
        out = pd.concat([out, tmp], ignore_index=True)

    return out


def plot(df, t_start=None, t_stop=None, fig=None, axes=None):

    if t_start:
        if t_start >= df["t"].min():
            df = df[df["t"] >= t_start]

    if t_stop:
        if t_stop <= df["t"].max():
            df = df[df["t"] <= t_stop]

    n_series = df["band"].nunique()

    if axes is not None:
        fig, axes = plt.subplots(n_series, 1, figsize=(8, 2 * n_series), sharex=True)

    for i, (series, group) in enumerate(df.groupby("band")):
        ax = axes[i] if n_series > 1 else axes  # if only 1 series, axes is not a list
        sns.lineplot(data=group, x="t", y="cr", ax=ax)
        ax.fill_between(
            group["t"],
            group["cr"] - group["err"],
            group["cr"] + group["err"],
            alpha=0.3,
        )
        ax.set_title(f"Band {group['band'].iloc[0]}")
        ax.set_ylabel("Counts [s]")

    return fig, axes


if __name__ == "__main__":
    colmap = {
        "n_bands": 4,
        "t": 0,
        "t_err_pos": 1,
        "t_err_neg": 2,
        "cr1": 3,
        "cr1_err": 4,
        "cr1_band": "2-20 keV",
        "cr2": 5,
        "cr2_err": 6,
        "cr2_band": "2-4 keV",
        "cr3": 7,
        "cr3_err": 8,
        "cr2_band": "4-10 keV",
        "cr4": 9,
        "cr4_err": 10,
        "cr4_band": "10-20 keV",
    }
    df = read("../data/CygnusX-2/Maxi/glcscan_lcbg_gsc0124578.qdp", colmap)
    print(df)
