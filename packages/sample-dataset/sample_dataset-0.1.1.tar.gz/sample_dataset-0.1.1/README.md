# sample-dataset

- [sample-dataset](#sample-dataset)
	- [Features](#features)
	- [Installation](#installation)
	- [Quick Start](#quick-start)
		- [Import your data](#import-your-data)
		- [Define the bucket structure + minima](#define-the-bucket-structure--minima)
		- [Assign buckets](#assign-buckets)
		- [Multiple randomized balanced samples](#multiple-randomized-balanced-samples)
	- [How it works](#how-it-works)
	- [Requirements](#requirements)
	- [Links](#links)


sample-dataset is a small library for generating balanced, constraint-driven samples from tabular data, using:

- pandas for data handling
- Google OR-Tools CP-SAT for constraint optimization

It allows you to divide your dataset into buckets (e.g., train/test × attribute combinations) while respecting arbitrary minimum size requirements provided by the user.

This is useful for:

- Train/test splits with structural constraints
- Balanced dataset construction
- Controlled sampling for linguistic, NLP, or behavioral datasets
- Any application where "random sampling" must satisfy non-trivial rules

## Features

- Constraint-based sampling using OR-Tools
- Flexible bucket definitions via a separate minima dataframe
- Supports arbitrary bucket-defining columns (e.g., split, feature_a, feature_b, split1, split2, ...)
- Automatically infers which dataset rows are eligible for which buckets
- Guarantees minimum bucket sizes
- Supports multiple randomized feasible solutions
- Simple API (assign_buckets, assign_buckets_multiple)

## Installation

```bash
pip install sample-dataset
```

## Quick Start

### Import your data

```python
import pandas as pd
from sample_dataset import assign_buckets
```

Your dataset (df) might look like:

```python
df = pd.DataFrame({
    "ID": [1, 2, 3, 4],
    "feature_a": ["a", "a", "su", "su"],
    "feature_b": ["yes", "no", "yes", "no"],
    "context": ["...", "...", "...", "..."],
})
```

### Define the bucket structure + minima

```python
df_minima = pd.DataFrame({
    "split": ["train", "test", "train", "test"],
    "feature_a": ["a", "a", "su", "su"],
    "feature_b": ["yes", "yes", "no", "no"],
    "min_required": [150, 50, 150, 50],
})
```

Each row represents a bucket.
All columns except min_required define the bucket identity.

### Assign buckets

```python
df_out = assign_buckets(df, df_minima, verbose=True)
print(df_out.head())
```

Output:
```
   ID feature_a feature_b   context      bucket
0   1        a       yes       ...   train|a|yes
1   2        a        no       ...    test|a|no
2   3       su       yes       ...  train|su|yes
3   4       su        no       ...   test|su|no
```

### Multiple randomized balanced samples

To generate N different feasible assignments, use:

```python
from sample_dataset import assign_buckets_multiple

df_samples = assign_buckets_multiple_wide(df, df_minima, n_samples=3)
print(df_samples.head())
```

You’ll get:

```
bucket_0      bucket_1      bucket_2
train|a|yes   test|a|yes    test|a|yes
...
```


## How it works

- The code interprets df_minima as the full set of buckets.
- Matches rows to buckets when all key_cols match
- Enforces minimum bucket sizes
- Forces each row to belong to exactly one bucket
- Uses a randomized objective to obtain diverse feasible assignments
- Solved using OR-Tools’ CP-SAT engine

## Requirements

* Python ≥ 3.9
* pandas
* numpy
* ortools

These are installed automatically.

## Links

* Source code: [https://github.com/LaboratorioSperimentale/sample-dataset]
* Issues: [https://github.com/LaboratorioSperimentale/sample-dataset/issues]
* PyPI: [https://pypi.org/project/sample-dataset/]