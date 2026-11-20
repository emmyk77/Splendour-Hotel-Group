"""Predict cancellations and rank the drivers (gradient boosting vs logistic regression)."""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from config import CLEAN_FILE, TABLES, RANDOM_STATE

df = pd.read_csv(CLEAN_FILE)
FEATURES = ["hotel", "distribution_channel", "customer_type", "country", "deposit_type",
            "lead_time", "nights", "guests", "adr", "arrival_month", "arrival_year"]
CATEGORICAL = ["hotel", "distribution_channel", "customer_type", "country", "deposit_type"]


def design_matrix(data):
    X = data[FEATURES].copy()
    top = data.country.value_counts().head(20).index
    X["country"] = X.country.where(X.country.isin(top), "Other")
    return pd.get_dummies(X, columns=CATEGORICAL, dtype=float)


def evaluate(data, label):
    X, y = design_matrix(data), data.canceled
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y)
    gb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, random_state=RANDOM_STATE).fit(Xtr, ytr)
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
    pg, pl = gb.predict_proba(Xte)[:, 1], lr.predict_proba(Xte)[:, 1]
    rows = [
        (label, "Gradient boosting", roc_auc_score(yte, pg), accuracy_score(yte, pg >= .5), precision_score(yte, pg >= .5), recall_score(yte, pg >= .5)),
        (label, "Logistic regression", roc_auc_score(yte, pl), accuracy_score(yte, pl >= .5), precision_score(yte, pl >= .5), recall_score(yte, pl >= .5)),
    ]
    return rows, gb, Xte, yte, pg


rows, gb, Xte, yte, pg = evaluate(df, "all rows")
rows_dd, *_ = evaluate(df[df.is_duplicate == 0], "duplicates removed")
metrics = pd.DataFrame(rows + rows_dd, columns=["data", "model", "auc", "accuracy", "precision", "recall"])
metrics.round(4).to_csv(TABLES / "70_model_metrics.csv", index=False)

# Importance of each original feature: drop in AUC when its columns are shuffled
rng, base, imp = np.random.RandomState(0), roc_auc_score(yte, pg), {}
for f in FEATURES:
    cols = [c for c in Xte.columns if c == f or c.startswith(f + "_")]
    drops = []
    for _ in range(3):
        Xp = Xte.copy()
        Xp[cols] = Xte[cols].values[rng.permutation(len(Xp))]
        drops.append(base - roc_auc_score(yte, gb.predict_proba(Xp)[:, 1]))
    imp[f] = np.mean(drops)
pd.Series(imp).sort_values(ascending=False).round(4).to_frame("auc_drop").to_csv(TABLES / "71_model_feature_importance.csv")
print(metrics.round(3).to_string(index=False))
print(pd.Series(imp).sort_values(ascending=False).round(3).to_string())
