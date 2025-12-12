import pandas as pd, json, os

DATASET = os.path.join("data", "dataset_train.csv")

FEATURES = ["TP2", "TP3", "H1", "Oil_temperature", "DV_pressure"]

df = pd.read_csv(DATASET)

stats = {}
for f in FEATURES:
    stats[f] = {
        "mean": float(df[f].mean()),
        "std": float(df[f].std() if df[f].std() != 0 else 1.0),
        "min": float(df[f].min()),
        "max": float(df[f].max())
    }

with open("stats_table.json", "w") as fh:
    json.dump(stats, fh, indent=4)

print("Saved stats_table.json")