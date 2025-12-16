import pandas as pd
from sample_dataset import assign_buckets
import sys

df = pd.read_csv(sys.argv[1], sep=";")
df_with_buckets = assign_buckets(df, min_train=120, min_test=30)
print(df_with_buckets.head())