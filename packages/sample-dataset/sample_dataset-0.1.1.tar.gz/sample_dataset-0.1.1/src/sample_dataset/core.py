import sys
from typing import Iterable, Tuple, Hashable, Optional, Sequence, List, Dict, Any

import pandas as pd
import numpy as np
from ortools.sat.python import cp_model


def assign_buckets_multiple(
    df: pd.DataFrame,
    df_minima: pd.DataFrame,
    n_samples: int,
    key_cols: Optional[Sequence[str]] = None,
    min_required_col: str = "min_required",
    time_limit: Optional[float] = 240.0,
    base_seed: Optional[int] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Compute multiple (possibly different) bucket assignments by solving the model
    several times with different random seeds.

    Returns a single DataFrame with an extra column 'sample_id' indicating
    which run each row comes from.
    """
# Start from a clean copy of the original data
    out = df.copy().reset_index(drop=True)

    for k in range(n_samples):
        seed = None if base_seed is None else base_seed + k

        df_k = assign_buckets(
            df=df,
            df_minima=df_minima,
            key_cols=key_cols,
            min_required_col=min_required_col,
            time_limit=time_limit,
            random_seed=seed,
            verbose=verbose,
        )

        # df_k is a copy with a 'bucket' column; we only need that column
        out[f"bucket_{k}"] = df_k["bucket"].values

    return out

def assign_buckets(
    df: pd.DataFrame,
    df_minima: pd.DataFrame,
    key_cols: Optional[Sequence[str]] = None,
    min_required_col: str = "min_required",
    time_limit: Optional[float] = 240.0,
    random_seed: Optional[int] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Assign rows of `df` to buckets defined in `df_minima` via constraint optimization.

    Parameters
    ----------
    df : pd.DataFrame
        The dataset.
        Must contain at least the columns that are in `key_cols`
        (or, if key_cols is None, the intersection of df and df_minima columns
        except `min_required_col`).
    df_minima : pd.DataFrame
        Table specifying buckets and their required minimum sizes.
        Must contain:
        - `min_required_col` (e.g. 'min_required')
        - other columns that define the buckets (e.g. 'split', 'preposition', 'construction').
    key_cols : sequence of str, optional
        Columns used to match dataset rows to buckets. If None, this is inferred
        as the intersection of df and df_minima columns, excluding `min_required_col`.
        Example: ['preposition', 'construction'].
    min_required_col : str, default 'min_required'
        Name of the column in df_minima containing the required minimum size.
    time_limit : float or None, default 240.0
        Max solving time in seconds. If None, no time limit.
    random_seed : int or None, default None
        Seed used to randomize the objective and the solver.
        Different seeds can give different feasible assignments.
    verbose : bool, default True
        If True, prints a bit of diagnostic information.

    Returns
    -------
    pd.DataFrame
        A copy of `df` with an extra column:
        - 'bucket' : string identifying the full bucket, e.g. 'train|a|no'
                     (all bucket-defining columns joined by '|').

    Notes
    -----
    - Bucket-defining columns are all columns in df_minima except `min_required_col`.
      They can include several “split-like” dimensions (e.g. split1, split2).
    - Only the key_cols are used to check whether a row can be assigned to a bucket.
    - If df_minima has bucket columns that are NOT in df, they still define different
      buckets and enforce different minima via `min_required_col`. They just don't
      participate in the row matching unless you add them to df or to key_cols explicitly.
    """

    if min_required_col not in df_minima.columns:
        raise ValueError(f"min_required_col '{min_required_col}' not found in df_minima")

    # All columns except min_required are considered bucket-defining
    bucket_cols: List[str] = [c for c in df_minima.columns if c != min_required_col]
    if not bucket_cols:
        raise ValueError("df_minima must have at least one bucket-defining column.")

    # Infer key columns if not provided: intersection of df and df_minima (excluding min_required)
    if key_cols is None:
        common = set(df.columns) & set(bucket_cols)
        key_cols = sorted(common)

    key_cols = list(key_cols)

    if not key_cols:
        raise ValueError(
            "No key_cols provided and no common columns between df and df_minima "
            f"(excluding '{min_required_col}')."
        )

    # Basic column checks
    for col in key_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' from key_cols not found in df")
        if col not in df_minima.columns:
            raise ValueError(f"Column '{col}' from key_cols not found in df_minima")

    # Work on copies with clean integer indexes
    df = df.copy().reset_index(drop=True)
    df_minima = df_minima.copy().reset_index(drop=True)

    indices: List[int] = list(df.index)          # 0..n_rows-1
    buckets: List[int] = list(df_minima.index)   # 0..n_buckets-1

    if verbose:
        sys.stderr.write("---- assign_buckets() ----\n")
        sys.stderr.write(f"Bucket-defining columns: {bucket_cols}\n")
        sys.stderr.write(f"Key columns used for matching: {key_cols}\n")
        sys.stderr.write(f"Number of dataset rows: {len(df)}\n")
        sys.stderr.write(f"Number of buckets: {len(buckets)}\n")
        sys.stderr.write(f"Bucket minima:")
        sys.stderr.write(f"{df_minima[[*bucket_cols, min_required_col]]}\n")
        sys.stderr.write(f"-------------------------------------------------\n")

    model = cp_model.CpModel()

    # Precompute attributes
    bucket_min_required: Dict[int, int] = {
        b: int(df_minima.loc[b, min_required_col]) for b in buckets
    }

    # Decision variables y[(i, b)]
    y: Dict[tuple, cp_model.IntVar] = {}
    bucket_to_rows: Dict[int, List[int]] = {b: [] for b in buckets}

    for i in indices:
        any_match = False
        for b in buckets:
            # Check if row i can belong to bucket b: all key_cols must match
            row_matches = all(
                df.loc[i, col] == df_minima.loc[b, col] for col in key_cols
            )
            if row_matches:
                var = model.NewBoolVar(f"y_{i}_{b}")
                y[(i, b)] = var
                bucket_to_rows[b].append(i)
                any_match = True
            else:
                y[(i, b)] = model.NewConstant(0)

        if not any_match:
            raise ValueError(
                f"Row {i} (values {df.loc[i, key_cols].to_dict()}) "
                "does not match any bucket in df_minima based on key_cols."
            )

    # Each row goes to exactly one bucket
    for i in indices:
        model.Add(sum(y[(i, b)] for b in buckets) == 1)

    # Minimum size constraints from df_minima[min_required_col]
    for b in buckets:
        rows = bucket_to_rows[b]

        if not rows:
            # No dataset row can belong to this bucket: skip to avoid impossible constraints.
            continue

        bucket_size = sum(y[(i, b)] for i in rows)
        min_required = bucket_min_required[b]

        model.Add(bucket_size >= min_required)

    # --- Random objective to diversify solutions ---
    if random_seed is not None:
        rng = np.random.RandomState(random_seed)
    else:
        rng = np.random.RandomState()

    n_rows = len(indices)
    n_buckets = len(buckets)
    # weights[i, jb] is the weight for row i, bucket index jb
    weights = rng.rand(n_rows, n_buckets)

    objective_terms = []
    for jb, b in enumerate(buckets):
        for i in bucket_to_rows[b]:  # only rows that can actually go to this bucket
            objective_terms.append(weights[i, jb] * y[(i, b)])

    if objective_terms:
        model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = float(time_limit)
    if random_seed is not None:
        solver.parameters.random_seed = int(random_seed)

    status = solver.Solve(model)

    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        raise RuntimeError(f"No feasible solution: {solver.StatusName(status)}")

    if verbose:
        sys.stderr.write(f"Status: {solver.StatusName(status)}\n")

    # Extract assignments
    buckets_out: List[str] = []

    for i in indices:
        assigned_b: Optional[int] = None
        for b in buckets:
            if solver.Value(y[(i, b)]) == 1:
                assigned_b = b
                break

        if assigned_b is None:
            raise RuntimeError(f"No bucket assigned for row {i}")

        # Build human-readable bucket label from all bucket-defining columns
        parts = [str(df_minima.loc[assigned_b, col]) for col in bucket_cols]
        buckets_out.append("|".join(parts))

    df["bucket"] = buckets_out

    if verbose:
        sys.stderr.write(f"Final bucket distribution:\n")
        sys.stderr.write(f"{df.groupby('bucket').size()}\n")
        sys.stderr.write(f"---- end assign_buckets() ----\n")

    return df

if __name__ == "__main__":
    import sys

    df = pd.read_csv(sys.argv[1], sep=";")

    df_minima = pd.DataFrame(
    {
        "split": [
            "train", "test",
            "train", "test",
            "train", "test",
            "train", "test",
        ],
        "preposition": ["a", "a", "a", "a", "su", "su", "su", "su"],
        "construction": ["no", "no", "yes", "yes", "no", "no", "yes", "yes"],
        "min_required": [120, 30, 120, 30, 120, 30, 120, 30],
    }
    )

    df_many = assign_buckets_multiple(
    df,
    df_minima,
    n_samples=5,
    base_seed=42,      # or None if you don’t care about reproducibility
    )

    # df_out = assign_buckets(df, df_minima)
    df_many.to_csv(sys.argv[2])
