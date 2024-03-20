import pandas as pd

df = pd.read_csv("Data/DrugRating.csv")

print(df.columns)

new_header = df.iloc[1]
df = df[2:]
df.columns = new_header

print(df.columns)

print(df.head())

print(df["Genus"], df["DrugName"], df["Category"], df["Benefit"])
