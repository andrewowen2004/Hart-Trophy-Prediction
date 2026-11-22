import pandas as pd

# load the file into a table called df
df = pd.read_csv("data/raw/hart_2024.csv")

print("Rows and columns:", df.shape)
print()
print("Column names:")
print(list(df.columns))
print()
print("First 5 rows:")
print(df.head())
print()
print("Blank cells per column:")
print(df.isna().sum())

