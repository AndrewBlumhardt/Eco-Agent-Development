# data/

Local data files used by the agent. This folder is mostly empty in the repo — you
download the one required file manually (it is too large for git).

## Files

| File | Size | Source | Required? |
|---|---|---|---|
| `cities500.txt` | ~50 MB | GeoNames | Yes — needed for `find_nearby_destinations` tool |
| `.gitkeep` | 0 bytes | — | Keeps this folder tracked by git when empty |

> `cities500.txt` is listed in `.gitignore` and will never be committed to the repo.

## Downloading cities500.txt

Run this once from the project root in PowerShell:

```powershell
Invoke-WebRequest -Uri "https://download.geonames.org/export/dump/cities500.zip" -OutFile "data/cities500.zip"
Expand-Archive -Path "data/cities500.zip" -DestinationPath "data/" -Force
Remove-Item "data/cities500.zip"
```

After this, `data/cities500.txt` should exist (~50 MB).

## What is GeoNames cities500.txt?

A tab-delimited text file containing every city in the world with a population over 500.
| `tripadvisor_hotel_reviews.csv` | ~15 MB | Kaggle | Recommended — enables EDA and `search_reviews` agent tool |
The agent uses it to find towns within a given radius of the user's destination and
estimate crowd levels based on population size:

| Population | Crowd indicator |
|---|---|
| < 10,000 | low |
| 10,000–99,999 | medium |
| ≥ 100,000 | high |

The file is read once at startup by `GeoNamesClient` and held in memory.
No API key or internet connection is required after download.

## Planned additions

A static hotel/travel reviews dataset (e.g. TripAdvisor reviews from Kaggle or
Hugging Face) may be added here to support vector search and EDA in the notebooks.
See the project README for dataset recommendations.
---

## Downloading tripadvisor_hotel_reviews.csv

**Option A — kagglehub (recommended, no CLI needed):**

```python
# Run once in a notebook cell or Python script
import kagglehub, shutil, pathlib
path = kagglehub.dataset_download("andrewmvd/trip-advisor-hotel-reviews")
# Move CSV into data/
src = next(pathlib.Path(path).glob("*.csv"))
shutil.copy(src, "data/tripadvisor_hotel_reviews.csv")
print("Done:", src.name)
```

**Option B — Kaggle CLI:**

```powershell
# Requires KAGGLE_USERNAME and KAGGLE_KEY set in environment or ~/.kaggle/kaggle.json
kaggle datasets download -d andrewmvd/trip-advisor-hotel-reviews -p data/ --unzip
```

After download, `data/tripadvisor_hotel_reviews.csv` should exist (~15 MB).

## What the reviews dataset contains

| Column | Type | Description |
|---|---|---|
| `Review` | string | Full text of the guest review |
| `Rating` | integer (1–5) | Star rating given by the guest |

No hotel names, locations, or dates — the dataset is useful as a **sentiment and
language grounding source**. The agent uses it to:
- Find real guest descriptions of quiet/peaceful stays (`search_reviews` tool, `sentiment="low_crowd"`)
- Find examples of crowded/noisy complaints (`sentiment="high_crowd"`)
- Search any custom keyword (e.g. `"mountain view"`, `"breakfast included"`)
