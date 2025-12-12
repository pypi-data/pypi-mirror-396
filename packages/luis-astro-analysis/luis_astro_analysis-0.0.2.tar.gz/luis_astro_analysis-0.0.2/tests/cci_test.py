# TESTING
import src.luis_astro_analysis.cci_analyzer as cci
import src.luis_astro_analysis.fits_util as f

ninja_path = "../../../../autodata/out/merged.evt"
gti_path = "../../../../autodata/tmp/CygX2.gti"
rmf_path = "../../../../autodata/out/CygX2.rmf"

ninja_bands = {
    "soft": (2, 4),
    "med": (4, 8),
    "hard": (8, 20),
}

events = f.read_mjd_channel(ninja_path)
total_evts = len(events)
rmf_info = f.read_rmf_ebounds(rmf_path)
gti = f.read_gti_intervals(gti_path)
df = events.merge(rmf_info[["channel", "energy"]], on="channel", how="left")
mask = f.select_good_time(df["mjd"].to_numpy(), gti)
df = df[mask]
binsize_sec = 600
binsize_day = binsize_sec / 86400
bins = f.bin_gti(gti, binsize_day)

checksum = len(df)
durations = np.diff(gti)
print(f"  Total good time: {durations.sum():.2f} days")
print(f"  Total events: {total_evts}, Inside GTI: {checksum}")
print(f"  Dropping {total_evts-checksum} events (-{(checksum/total_evts * 100):.0f}%).")

print(f"########################################")


CCI = cci.CCI_Analyzer()

CCI.load_data(df)
CCI.load_gti(gti)
CCI.set_colorbands(ninja_bands)
CCI.set_bins(600)
CCI.set_bin_bounds(1, 1000)
CCI.select_bins_and_colors()
CCI.select_branches()
# CCI.plot_color_intensity()
# CCI.plot_color_color()

df = CCI.get_colored_data()

print(df)
