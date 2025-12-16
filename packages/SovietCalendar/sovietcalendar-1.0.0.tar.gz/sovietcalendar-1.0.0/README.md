# Soviet Calendar for Python

A lightweight Python utility to interpret Gregorian dates within the historical context of the **Soviet work-week experiments (1929–1940)**. It does **not** convert to a new calendar system—because none existed—but computes the *Soviet 5-day and 6-day work-week cycles** that were officially used during that period.

---

## 📜 What Was the Soviet Calendar?

The USSR **never replaced** the Gregorian calendar for civil dating. Instead, from **1929 to 1940**, it experimented with **alternative weekly cycles** to increase industrial productivity and weaken religious observance:

- **1929–1931**: A **5-day continuous work week**—each worker assigned one of five rest days (no common weekend).
- **1931–1940**: A **6-day work week** with a common rest day (usually the 6th day).
All official documents, laws, and newspapers continued to **use standard Gregorian dates (YYYY-MM-DD)**. The “Soviet calendar” refers only to this restructured **weekly rhythm**, not a new month/day/year system.

🔗 **Learn more**: [Soviet Calendar – Wikipedia](https://en.wikipedia.org/wiki/Soviet_calendar)

---

## 📦 Installation

### PIP Installation

```bash
pip install SovietCalendar
```

### UV Installation

```bash
uv add SovietCalendar
```

### As a Standalone File (Recommended for most users)

Simply copy `soviet_calendar.py` into your project directory and import it:

```python
from soviet_calendar import SovietCalendar
```

### As a pip Package (Development Install)

If you have the source locally:

```bash
pip install -e .
```

### With uv (Modern Python Package Manager)

Install the project in editable mode:

```bash
uv pip install -e .
```

Or add it to your project dependencies:

```bash
uv add -e .
```

---

## 🛠️ Usage & Use Cases

### 1. Historical Analysis

Compute which Soviet work-day a historical date fell on.

```python
from datetime import date
from soviet_calendar import SovietCalendar

sc = SovietCalendar(date(1930, 5, 1))
print(sc.five_day_week_day)  # → 1 (1st day of 5-day cycle)
print(sc.six_day_week_day)   # → 2 (2nd day of 6-day cycle)
```

### 2. Education & Visualization

Use in Jupyter notebooks or history apps to illustrate how Soviet timekeeping worked.

```python
print(sc)
# Output: SovietCalendar(1930-05-01, 5-day: 1, 6-day: 2)
```

### 3. Date Validation

Ensure dates fall within the active Soviet calendar period (1929–1940):

```python
try:
    SovietCalendar(date(1928, 12, 31))
except ValueError as e:
    print(e)  # "Soviet calendar system was only used from 1929-01-01 to 1940-06-26"
```

> ⚠️ **Note**: The class **does not support** dates outside 1929–1940, as the system was abolished in June 1940.

---

## 🧪 Testing

Run the full test suite with:

```bash
# With pytest
pytest

# Or with unittest
python -m unittest
```

All dates are handled in **ISO 8601 format** (`YYYY-MM-DD`).

---

## 🤝 Contributing (with uv)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/soviet-calendar.git
cd soviet-calendar
```

### 2. Install in editable mode with uv

```bash
uv sync --all-extras
```

### 3. Make your changes

Edit `soviet_calendar.py` and update tests in `test_soviet_calendar.py`.

### 4. Run tests

```bash
uv run pytest
```

### 5. Submit a PR

Push your branch and open a pull request!

---

> ✨ **Remember**:
> This project reflects **historical timekeeping experiments**, not an alternative civil calendar. All dates remain Gregorian—only the weekly cycle is reinterpreted.

---

## ⚖️ [Licence GNU GPLv3](./LICENSE)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
