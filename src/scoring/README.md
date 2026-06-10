# src/scoring/

Crowd scoring engine. Takes normalized signals from the API clients and produces a
single 0–100 crowd likelihood score per hotel result.

## Files

| File | Purpose |
|---|---|
| `crowd_scorer.py` | `calculate_crowd_score()` function + `explain_crowd_factors()` helper |
| `__init__.py` | Package marker |

## How the score is calculated

Five signals are combined into a weighted score. **Lower score = less crowded.**

| Signal | Weight | Source |
|---|---|---|
| Hotel availability % | 35% | Amadeus API |
| Average nightly rate vs. baseline | 20% | Amadeus API |
| Local events magnitude | 25% | PredictHQ API |
| Seasonal demand factor | 10% | Hardcoded calendar heuristic |
| Weather suitability | 10% | OpenWeatherMap API |

### Score thresholds

| Score | Crowd level | Meaning |
|---|---|---|
| < 35 | Low | Excellent — little competition for rooms |
| 35–59 | Medium | Moderate — expect some crowds |
| ≥ 60 | High | Busy — consider nearby alternatives |

## Crowd reason generation

`explain_crowd_factors()` returns a human-readable sentence listing the specific signals
that drove a high score (e.g. "Hotel rooms are limited; A large festival is scheduled nearby").
These reasons are surfaced in the agent's chat response.
