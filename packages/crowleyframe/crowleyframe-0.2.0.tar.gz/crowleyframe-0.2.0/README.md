Here’s an updated `README.md` you can drop in as-is, with:

* A **“What’s new in v0.2”** section
* All verbs from v0.1 + v0.2 described with **syntax**, **behavior**, and **examples**
* Examples aligned with your current tests

---

# 📦 **crowley-frame**

### *A Rust-powered, tidyverse-inspired DataFrame manipulation library for Python*

**crowley-frame** brings the ergonomics of **dplyr/tidyr** to Python—backed by **Rust** for safety, speed, and expressive semantics.

If you know **R’s tidyverse**, this feels natural.
If you know **pandas**, this gives you a more composable, readable syntax with a proper grammar of data manipulation. 

---

## 📌 Status

* **Version:** 0.2.x (early but already useful)
* **Backend:** Rust + Polars core (exposed via a Python façade)
* **Tests:** ✅ **22 tests passing** across:

  * column selection & selectors
  * mutate + lag/lead + rolling
  * count
  * slice_* verbs
  * pivot_longer / pivot_wider
  * separate / unite
  * pipes + group_by / summarise
  * joins (left_join, inner_join)

---

## 🆕 What’s new in **v0.2**

Building on the v0.1 core (select, mutate, filter, basic pivoting), v0.2 adds a lot of real tidyverse ergonomics:

**New verbs / capabilities:**

* **`rename()`** – rename columns by mapping `new_name="old_name"`.
* **`relocate()`** – move columns before/after others or to the front.
* **`distinct()`** – row de-duplication by columns (with `keep=` semantics).
* **`count()`** – frequency tables + `prop=` (proportions) + `sort=`. 
* **Slice family:** `slice_head()`, `slice_tail()`, `slice_sample()`, `slice_max()`, `slice_min()`. 
* **Tidyr-style:**

  * `separate()` – split one column into several.
  * `unite()` – combine several columns into one, with NA semantics. 
* **Reshaping:**

  * `pivot_longer()` – long format via tidy-style selectors.
  * `pivot_wider()` – wide format, round-tripping from `pivot_longer`. 
* **Joins:**

  * `left_join()` and `inner_join()` matching pandas’ behavior, including suffixes and NaN key quirks, locked down via tests. 
* **Selectors expanded:**

  * `col.where_numeric()`, `col.where_string()`, `col.everything()` in addition to `starts_with`, `ends_with`, `contains`, `matches`. 
* **Pipe ergonomics:**

  * `Frame.__rshift__` + `pipe.*` namespace lets you write actual tidyverse-style pipelines in Python, including `group_by` + `summarise`. 

---

# ✅ Features Proven by the Test Suite (v0.2, 22 tests)

The following features are not theoretical — they are **fully implemented and validated** by your test suite.

---

## 🔍 Column Selection + Tidy Selectors

Supported selectors (via `crowley_frame.col`):

* `col("name")` / plain strings
* `col.starts_with("prefix")`
* `col.ends_with("suffix")`
* `col.contains("substring")`
* `col.matches(r"regex")`
* `col.where_numeric()` – all numeric columns
* `col.where_string()` – object/string columns
* `col.everything()` – all columns

**Syntax**

```python
from crowley_frame import df, col

cf.select(
    "user_id",
    col.starts_with("score"),
    col.where_numeric(),
)
```

**Example**

```python
cf = df({"user_id": [1, 2, 3],
         "score_a": [10, 20, 30],
         "score_b": [5, 7, 9],
         "group": ["a", "b", "a"]})

num_out = cf.select(col.where_numeric()).to_pandas()
```

**Possible output**

````text
   user_id  score_a  score_b
0        1       10        5
1        2       20        7
2        3       30        9
``` :contentReference[oaicite:11]{index=11}  

---

## ✨ `mutate()`, `lag()`, `lead()`, `rolling_mean()`

### `mutate(**new_columns)`

- **Strings** are evaluated as pandas expressions in DataFrame context.
- Non-strings are treated as literal sequences/scalars.

```python
cf = df({"x": [1, 2, 3, 4, 5]})

out = cf.mutate(
    double="x * 2",
    z="x ** 2 + 1",
).to_pandas()
````

**Example output**

````text
   x  double   z
0  1       2   2
1  2       4   5
2  3       6  10
3  4       8  17
4  5      10  26
``` :contentReference[oaicite:12]{index=12}  

### `lag(col, n=1, default=None)` / `lead(col, n=1, default=None)`

Helpers that return `pd.Series` to be plugged into `mutate` or used directly.

```python
cf = df({"val": [10, 20, 30]})

cf.mutate(
    lag_val=cf.lag("val", 1),
    lead_val=cf.lead("val", 1),
).to_pandas()
````

**Output**

````text
   val  lag_val  lead_val
0   10      NaN      20.0
1   20     10.0      30.0
2   30     20.0       NaN
``` :contentReference[oaicite:13]{index=13}  

### `rolling_mean(col, window, min_periods=None)`

```python
cf = df({"val": [1.0, 2.0, 3.0, 4.0]})

cf.mutate(
    roll3=cf.rolling_mean("val", window=3, min_periods=2),
).to_pandas()
````

**Output**

````text
   val  roll3
0  1.0    NaN
1  2.0    1.5
2  3.0    2.0
3  4.0    3.0
``` :contentReference[oaicite:14]{index=14}  

---

## 🔗 Pipe Syntax (`>>`) + `group_by()` → `summarise()`

You get **real tidyverse pipes** in Python via `pipe.*` and `Frame.__rshift__`. :contentReference[oaicite:15]{index=15}  

**Syntax**

```python
from crowley_frame import df, pipe

(
    cf
    >> pipe.group_by("user_id")
    >> pipe.summarise(
        mean_score=("score", "mean"),
        n=("score", "count"),
    )
).to_pandas()
````

**Example**

```python
cf = df({"user_id": [1, 2, 1],
         "score":   [5, 7, 9]})

out = (
    cf
    >> pipe.group_by("user_id")
    >> pipe.summarise(
        mean_score=("score", "mean"),
        n=("score", "count"),
    )
).to_pandas()
```

**Output**

````text
   user_id  mean_score  n
0        1         7.0  2
1        2         7.0  1
``` :contentReference[oaicite:16]{index=16}  

> **Note:** Use parentheses around the whole pipe chain before calling `.to_pandas()`, so Python’s precedence doesn’t bind `.to_pandas()` to the last pipe function.

---

## 🔢 `count()` – frequencies and proportions

**Syntax**

```python
Frame.count(
    *cols: str,
    sort: bool = False,
    prop: bool = False,
    name: str = "n",
)
````

* No `cols` → total row count.
* With `cols` → grouped counts.
* `prop=True` → add `prop` column with relative frequencies.
* `sort=True` → sort by `n` descending. 

**Example**

```python
cf = df({"grp": ["a", "a", "b", "b", "b"]})

cf.count("grp", prop=True, sort=True).to_pandas()
```

**Output**

````text
  grp  n  prop
0   b  3  0.60
1   a  2  0.40
``` :contentReference[oaicite:18]{index=18}  

---

## ✂️ Slice verbs: `slice_head`, `slice_tail`, `slice_sample`, `slice_max`, `slice_min`

These mirror dplyr / tidyr slice semantics. :contentReference[oaicite:19]{index=19}  

### `slice_head(n=5)` / `slice_tail(n=5)`

```python
cf = df({"x": [1, 2, 3, 4, 5]})

head3 = cf.slice_head(3).to_pandas()
tail2 = cf.slice_tail(2).to_pandas()
````

**head3**

```text
   x
0  1
1  2
2  3
```

**tail2**

````text
   x
0  4
1  5
``` :contentReference[oaicite:20]{index=20}  

### `slice_sample(n=None, prop=None, replace=False, random_state=None)`

- Provide **exactly one** of `n` or `prop`.

```python
cf = df({"x": list(range(10))})

s1 = cf.slice_sample(n=3, random_state=42).to_pandas()
s2 = cf.slice_sample(prop=0.3, random_state=42).to_pandas()
````

### `slice_max(order_by, n=5)` / `slice_min(order_by, n=5)`

Uses `nlargest` / `nsmallest` to get top/bottom rows by a column. 

```python
cf = df({"x": [1, 5, 3, 9, 2],
         "y": ["a", "b", "c", "d", "e"]})

max2 = cf.slice_max("x", n=2).to_pandas()
min2 = cf.slice_min("x", n=2).to_pandas()
```

**max2**

```text
   x  y
0  9  d
1  5  b
```

**min2**

````text
   x  y
0  1  a
1  2  e
``` :contentReference[oaicite:22]{index=22}  

---

## 🔄 `pivot_longer()` and `pivot_wider()`

Round-trippable reshaping modeled after tidyr. :contentReference[oaicite:23]{index=23}  

### `pivot_longer`

**Syntax**

```python
Frame.pivot_longer(
    *cols,                      # tidy selectors
    cols: Sequence[Any] | None = None,
    names_to: str = "name",
    values_to: str = "value",
    names_prefix: str | None = None,
)
````

You can pass selectors positionally:

```python
cf = df({
    "id": [1, 2],
    "year_2023": [10, 30],
    "year_2024": [11, 31],
})

long = cf.pivot_longer(
    col.matches(r"^year_"),
    names_to="year",
    values_to="value",
).to_pandas()
```

**Output**

````text
   id       year  value
0   1  year_2023     10
1   2  year_2023     30
2   1  year_2024     11
3   2  year_2024     31
``` :contentReference[oaicite:24]{index=24}  

### `pivot_wider`

**Syntax**

```python
Frame.pivot_wider(
    names_from: str,
    values_from: str,
    values_fill: Any = None,
    sep: str = "_",
)
````

```python
wide = (
    long
    .pivot_wider(
        names_from="year",
        values_from="value",
        values_fill=None,
    )
    .to_pandas()
    .sort_values("id")
    .reset_index(drop=True)
)
```

**Output**

````text
   id  year_2023  year_2024
0   1         10         11
1   2         30         31
``` :contentReference[oaicite:25]{index=25}  

---

## 🔬 `separate()` & `unite()` with proper NA semantics

Modeled on tidyr’s `separate` and `unite`, including behavior around missing values. :contentReference[oaicite:26]{index=26}  

### `separate(col, into, sep=r"\s+", remove=True, convert=False)`

```python
cf = df({
    "id": [1, 2, 3],
    "coords": ["1,2", "10,20", "5,7"],
})

out = (
    cf
    .separate("coords", into=["x", "y"], sep=",")
    .to_pandas()
    .sort_values("id")
    .reset_index(drop=True)
)
````

**Output**

````text
   id   x   y
0   1   1   2
1   2  10  20
2   3   5   7
``` :contentReference[oaicite:27]{index=27}  

### `unite(col, cols, sep="_", remove=True, na_rm=False)`

```python
cf = df({
    "first": ["Ada", None, "Charlie"],
    "last":  ["Lovelace", "Smith", None],
})

out_default = cf.unite("full_name", ["first", "last"], sep=" ").to_pandas()
````

**Output (default `na_rm=False`)**

````text
      full_name
0  Ada Lovelace
1          <NA>
2          <NA>
``` :contentReference[oaicite:28]{index=28}  

With `na_rm=True`, NAs are treated as empty strings and trimmed from ends.

---

## 🧱 `rename()`, `relocate()`, and `distinct()`

### `rename(**mapping)`

```python
cf = df({"user_id": [1, 2, 3], "user_score": [5, 7, 9]})

cf.rename(user="user_id", score="user_score").to_pandas()
````

**Output**

````text
   user  score
0     1      5
1     2      7
2     3      9
``` :contentReference[oaicite:29]{index=29}  

### `relocate(*cols, before=None, after=None)`

Moves one or more columns relative to others.

```python
cf = df({
    "user_id": [1, 2, 3],
    "user_score": [5, 7, 9],
    "other": [0, 0, 1],
})

cf.relocate("user_score", before="user_id").to_pandas()
````

**Output**

````text
   user_score  user_id  other
0           5        1      0
1           7        2      0
2           9        3      1
``` :contentReference[oaicite:30]{index=30}  

If neither `before` nor `after` is given, selected columns are moved to the **front**.

### `distinct(*cols, keep="first" | "last" | False)`

```python
cf = df({
    "user": [1, 1, 2, 3],
    "score": [5, 5, 7, 7],
    "other": [0, 1, 0, 1],
})

# distinct users, keep first occurrence
cf.distinct("user").to_pandas()
````

**Output**

````text
   user  score  other
0     1      5      0
1     2      7      0
2     3      7      1
``` :contentReference[oaicite:31]{index=31}  

---

## 🤝 Joins: `left_join()` and `inner_join()`

Joins are defined in `Frame` and exercised heavily in `test_joins.py`. :contentReference[oaicite:32]{index=32}  

**Syntax**

```python
Frame.left_join(
    other: Frame,
    on: str | Sequence[str] | None = None,
    left_on: str | Sequence[str] | None = None,
    right_on: str | Sequence[str] | None = None,
    suffixes: tuple[str, str] = ("_x", "_y"),
    validate: str | None = None,
)

Frame.inner_join( ...same signature... )
````

### Basic left join

```python
from crowley_frame import df

left = df({"id": [1, 2, 3], "x": [10, 20, 30]})
right = df({"id": [2, 3, 4], "y": [200, 300, 400]})

out = left.left_join(right, on="id").to_pandas()
```

**Output**

````text
   id   x      y
0   1  10    NaN
1   2  20  200.0
2   3  30  300.0
``` :contentReference[oaicite:33]{index=33}  

### Basic inner join

```python
inner = left.inner_join(right, on="id").to_pandas()
````

**Output**

````text
   id   x    y
0   2  20  200
1   3  30  300
``` :contentReference[oaicite:34]{index=34}  

### Overlapping column names + suffixes

```python
left = df({"id": [1, 2], "val": [10, 20]})
right = df({"id": [2, 3], "val": [200, 300]})

out = left.left_join(right, on="id", suffixes=("_left", "_right")).to_pandas()
````

Gives `val_left` / `val_right` columns, matching pandas. 

### NaN key behavior

Joins with NaN keys are explicitly locked to whatever pandas does on the version you’re running:

```python
left_pdf = pd.DataFrame({"id": [1.0, float("nan"), 3.0], "x": [10, 20, 30]})
right_pdf = pd.DataFrame({"id": [float("nan"), 3.0], "y": [200, 300]})

left = df(left_pdf)
right = df(right_pdf)

out_left = left.left_join(right, on="id").to_pandas()
out_inner = left.inner_join(right, on="id").to_pandas()
```

Both are tested against `pd.merge` with the same options. 

---

# 📥 Installation

### For contributors (local dev)

```bash
maturin develop --release
```

### (Future) PyPI install

```bash
pip install crowley-frame
```

---

# 🚀 Usage Overview (Quick Tour)

```python
from crowley_frame import df, col, pipe
import pandas as pd

pdf = pd.DataFrame({"user_id":[1,2,1,3],
                    "user_score":[5,7,9,7],
                    "other":[0,0,1,1]})

cf = df(pdf)
```

### 1. Select

```python
cf.select("user_id", col.starts_with("user_")).to_pandas()
```

### 2. Mutate

```python
cf.mutate(
    z="(user_score - user_score.mean()) / user_score.std()"
).to_pandas()
```

### 3. Group + summarise with pipes

```python
(
    cf
    >> pipe.group_by("user_id")
    >> pipe.summarise(
        mean_score=("user_score", "mean"),
        n=("user_score", "count"),
    )
).to_pandas()
```

### 4. Reshape

```python
wide = df({
    "id":[1,2],
    "year_2023":[10,30],
    "year_2024":[11,31],
})

long = wide.pivot_longer(
    col.matches(r"^year_"),
    names_to="year",
    values_to="value",
)

roundtrip = long.pivot_wider(
    names_from="year",
    values_from="value",
)
```

### 5. Join

```python
left  = df({"id":[1,2,3], "x":[10,20,30]})
right = df({"id":[2,3,4], "y":[200,300,400]})

left.left_join(right, on="id").to_pandas()
```

---

# 🧭 Roadmap

Planned next steps (v0.2.x → v0.3):

* Complete join family: `right_join`, `full_join`, `semi_join`, `anti_join`.
* More tidyverse verbs:

  * `across()`, `case_when()`, `if_else()`
  * `drop_na`, `fill`, `complete`, `expand`, `nest` / `unnest`
* Crowley-specific features:

  * Stronger expression engine for `mutate` / `filter`.
  * Optional lazy mode over Polars / Arrow.
* Rust side:

  * More kernels pushed down into `_crowley.Frame` for performance.
  * SIMD and parallelization for heavy verbs.

---

# 📄 License

MIT License — free to use, modify, and distribute.
