import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import glob


DATASET_DIR = Path("datasets/asteroids_neows")

# Most recent csv
csv_files = sorted(glob.glob(str(DATASET_DIR / "neows_*.csv")))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {DATASET_DIR}")

df = pd.read_csv(csv_files[-1], parse_dates=['date'])
print(f"Loaded: {csv_files[-1]}  ({len(df)} asteroids)")

sns.set_theme(style="darkgrid")

fig, ax = plt.subplots(figsize=(12, 5))

sns.scatterplot(
    data=df,
    x="date",
    y="miss_distance_km",
    hue="is_potentially_hazardous",
    palette={True: "#e74c3c", False: "#3498db"},
    alpha=0.7,
    ax=ax,
)

ax.set_title("Near-Earth Asteroids — Miss Distance Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Miss Distance (km)")
ax.legend(title="Potentially Hazardous")

plt.tight_layout()
plt.show()