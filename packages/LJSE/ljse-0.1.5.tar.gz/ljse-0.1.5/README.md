# LJSE

A lightweight Python package for downloading stock market data from the Ljubljana Stock Exchange (LJSE).  
Provides a simple interface for retrieving the list of all listed equities and fetching historical price data for any LJSE ticker.

---

## Features

- Fetch a complete list of currently listed LJSE equities
- Retrieve historical **last-price** data for any ticker
- Automatically resolves ISIN and listing date
- Supports trading model selection (`CT`, `AUCT`, `BLOCK`, `ALL`)
- Returns clean pandas DataFrames

---

## Installation

```bash
pip install ljse
