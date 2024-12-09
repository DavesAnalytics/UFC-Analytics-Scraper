# UFC-Analytics-Scraper

A scraper that retrieves UFC and Pride fighting data with round-by-round analytics.

**Author:** Dave Yount

## Overview

The **UFC Analytics Scraper** is a Python tool designed to scrape detailed fight and fighter statistics directly from [UFCStats.com](http://ufcstats.com). It extracts both aggregate fight-level data and round-by-round statistics, including strikes, takedowns, submissions, reversals, and control time for both the main fighter and their opponents.

Additionally, this scraper includes data from UFC and Pride events (note: Pride data integrated on UFCStats is limited). The output is a comprehensive CSV file suitable for advanced analytics, predictive modeling, and data visualization.

## Features

- **Fighter Search:** Input a fighter's name (e.g., "Israel Adesanya" or "Jim Miller"), and the tool will find the corresponding fighter profile URL on UFCStats, even if multiple fighters share the same surname.
- **Complete Fight History:** Retrieves each fight for the specified fighter, including event details, fight outcome, methods, and basic stats.
- **Round-by-Round Analysis:** Extracts granular per-round totals and significant strike data, including head/body/leg strikes, takedowns, submissions, reversals, and control time.
- **Data Cleaning & Formatting:** 
  - Converts times from mm:ss to total seconds for easier numeric analysis.
  - Splits "X of Y" strike/takedown attempts into separate landed, attempted, and percentage columns.
  - Removes redundant columns and merges duplicated fields (e.g., `method_main_x` and `method_main_y` into `method_main`).
  - Replaces `---` with `NaN` for uniform missing data representation.
  - Rounds numerical columns to two decimal places where applicable.

## Requirements

- Python 3.7+
- Dependencies: 
  - `requests`
  - `beautifulsoup4`
  - `pandas`

You can install dependencies via:
```bash
pip install requests beautifulsoup4 pandas

