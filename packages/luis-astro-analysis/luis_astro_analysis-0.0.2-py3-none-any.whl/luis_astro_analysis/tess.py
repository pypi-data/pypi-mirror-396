import numpy as np
import pandas as pd
from astropy.io import fits


def extract_lightcurve(path):
    with fits.open(path) as hdul:
        evt = hdul["LIGHTCURVE"].data
        hdr = hdul["LIGHTCURVE"].header

        bjd = evt["TIME"]

        flux = evt["PDCSAP_FLUX"]
        flux_err = evt["PDCSAP_FLUX_ERR"]
        qlty = evt["QUALITY"]

    # drop bad events (quality != 0):
    mask = qlty == 0

    flux = flux[mask]
    flux_err = flux_err[mask]
    bjd = bjd[mask]

    mjdrefi = hdr["BJDREFI"]
    mjdreff = hdr["BJDREFF"]

    mjd = bjd + mjdrefi + mjdreff - 2400000.5

    df = pd.DataFrame(
        {
            "mjd": mjd.astype(np.float64),
            "flux": flux.astype(np.float64),
            "error": flux_err.astype(np.float64),
        }
    )

    return df


# df = extract_lightcurve(
#     "../../data/CygnusX-2/TESS/tess2024249191853-s0083-0000000468511196-0280-a_fast-lc.fits"
# )
# print(df)
