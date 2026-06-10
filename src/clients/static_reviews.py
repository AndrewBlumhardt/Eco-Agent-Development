# src/clients/static_reviews.py
"""
Static reviews client — loads the Kaggle TripAdvisor Hotel Reviews dataset
(tripadvisor_hotel_reviews.csv) and provides keyword search + rating filtering.

Dataset: https://www.kaggle.com/datasets/andrewmvd/trip-advisor-hotel-reviews
Columns: Review (str), Rating (int 1–5)
Rows: ~20,000

Download the CSV once using kagglehub (see data/README.md), then this client
reads it at startup with no API key required.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_CSV_PATH = Path(__file__).parents[2] / "data" / "tripadvisor_hotel_reviews.csv"

# Keywords associated with low-crowd / peaceful stays
LOW_CROWD_KEYWORDS = [
    "quiet", "peaceful", "serene", "not crowded", "uncrowded", "tranquil",
    "relaxed", "calm", "private", "secluded", "off the beaten", "hidden gem",
    "no crowds", "empty", "peaceful retreat", "low-key",
]

# Keywords that signal high-crowd / busy conditions
HIGH_CROWD_KEYWORDS = [
    "crowded", "busy", "loud", "noisy", "tourist trap", "overrun",
    "packed", "long lines", "wait", "chaotic", "overwhelming", "too many people",
]


class StaticReviewsClient:
    """
    Loads the static TripAdvisor hotel reviews CSV and provides search helpers.

    Parameters
    ----------
    csv_path : Path, optional
        Path to tripadvisor_hotel_reviews.csv. Defaults to data/ in project root.
    """

    def __init__(self, csv_path: Path = DEFAULT_CSV_PATH) -> None:
        self._path = csv_path
        self._df: pd.DataFrame = self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> pd.DataFrame:
        if not self._path.exists():
            return pd.DataFrame(columns=["Review", "Rating"])
        df = pd.read_csv(self._path)
        # Normalise column names to title case regardless of source
        df.columns = [c.strip().title() for c in df.columns]
        df["Review"] = df["Review"].fillna("").astype(str)
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0).astype(int)
        return df

    @property
    def is_available(self) -> bool:
        """True if the CSV was found and loaded."""
        return len(self._df) > 0

    @property
    def total_reviews(self) -> int:
        return len(self._df)

    # ------------------------------------------------------------------
    # Public search API
    # ------------------------------------------------------------------

    def search_by_keywords(
        self,
        keywords: list[str],
        min_rating: int = 1,
        max_rating: int = 5,
        limit: int = 5,
    ) -> list[dict]:
        """
        Return reviews that contain ANY of the given keywords (case-insensitive),
        optionally filtered by rating range.

        Parameters
        ----------
        keywords : list[str]
            Keywords to search for in review text.
        min_rating : int
            Minimum rating to include (1–5).
        max_rating : int
            Maximum rating to include (1–5).
        limit : int
            Maximum number of results to return.

        Returns
        -------
        list[dict]
            Each dict has keys: ``review`` (str), ``rating`` (int), ``snippet`` (str).
        """
        if not self.is_available:
            return []

        mask = self._df["Rating"].between(min_rating, max_rating)
        filtered = self._df[mask].copy()

        pattern = "|".join(keywords)
        matches = filtered[
            filtered["Review"].str.contains(pattern, case=False, na=False, regex=True)
        ]

        results = []
        for _, row in matches.head(limit).iterrows():
            text = row["Review"]
            results.append({
                "review": text,
                "rating": int(row["Rating"]),
                "snippet": text[:200] + ("..." if len(text) > 200 else ""),
            })
        return results

    def search_low_crowd_reviews(self, limit: int = 5) -> list[dict]:
        """Return high-rated reviews (4–5) that mention quiet/uncrowded language."""
        return self.search_by_keywords(
            keywords=LOW_CROWD_KEYWORDS, min_rating=4, max_rating=5, limit=limit
        )

    def search_high_crowd_reviews(self, limit: int = 5) -> list[dict]:
        """Return lower-rated reviews (1–3) that mention crowded/busy language."""
        return self.search_by_keywords(
            keywords=HIGH_CROWD_KEYWORDS, min_rating=1, max_rating=3, limit=limit
        )

    def get_rating_distribution(self) -> dict[int, int]:
        """Return a dict mapping rating (1–5) to count of reviews."""
        if not self.is_available:
            return {}
        return self._df["Rating"].value_counts().sort_index().to_dict()

    def get_summary_stats(self) -> dict:
        """Return a compact stats summary for display in notebooks."""
        if not self.is_available:
            return {
                "available": False,
                "message": "tripadvisor_hotel_reviews.csv not found. See data/README.md.",
            }
        dist = self.get_rating_distribution()
        avg = self._df["Rating"].mean()
        low_crowd_count = len(
            self._df[
                self._df["Review"].str.contains(
                    "|".join(LOW_CROWD_KEYWORDS), case=False, na=False, regex=True
                )
            ]
        )
        high_crowd_count = len(
            self._df[
                self._df["Review"].str.contains(
                    "|".join(HIGH_CROWD_KEYWORDS), case=False, na=False, regex=True
                )
            ]
        )
        return {
            "available": True,
            "total_reviews": self.total_reviews,
            "avg_rating": round(avg, 2),
            "rating_distribution": dist,
            "low_crowd_mentions": low_crowd_count,
            "high_crowd_mentions": high_crowd_count,
        }
