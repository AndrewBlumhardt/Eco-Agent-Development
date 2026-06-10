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
