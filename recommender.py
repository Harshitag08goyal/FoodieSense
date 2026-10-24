"""
ML Recommender for foodieSense
--------------------------------
Model: Gradient Boosting Classifier
Per-user model stored as model_<user_id>.pkl
Falls back to cosine similarity if not enough feedback.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import pickle

from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

DATA_PATH    = os.path.join(os.path.dirname(__file__), "data", "foods.csv")
DB_PATH      = os.path.join(os.path.dirname(__file__), "feedback.db")
MODELS_DIR   = os.path.join(os.path.dirname(__file__), "models")
MIN_FEEDBACK = 5

LEVEL = {"low": 0, "medium": 1, "high": 2}
FEATURE_COLS = [
    "spicy_enc", "sweet_enc", "savory_enc",
    "veg_enc", "cuisine_enc", "category_enc",
    "calories_norm", "rating",
    "cal_per_rating",
    "is_street_food", "is_dessert", "is_breakfast", "is_main",
]

os.makedirs(MODELS_DIR, exist_ok=True)

_le_cuisine  = LabelEncoder()
_le_category = LabelEncoder()
_fitted      = False


def _fit_encoders(df):
    global _fitted
    _le_cuisine.fit(df["cuisine"])
    _le_category.fit(df["category"])
    _fitted = True


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    global _fitted
    df = df.copy()
    df["spicy_enc"]  = df["spicy"].map(LEVEL).fillna(1)
    df["sweet_enc"]  = df["sweet"].map(LEVEL).fillna(0)
    df["savory_enc"] = df["savory"].map(LEVEL).fillna(1)
    df["veg_enc"]    = (df["veg"] == "yes").astype(int)
    if not _fitted:
        _fit_encoders(df)
    df["cuisine_enc"]  = _le_cuisine.transform(df["cuisine"])
    df["category_enc"] = _le_category.transform(df["category"])
    c_min, c_max = df["calories"].min(), df["calories"].max()
    df["calories_norm"]  = (df["calories"] - c_min) / (c_max - c_min + 1e-9)
    df["cal_per_rating"] = df["calories"] / (df["rating"] + 0.1)
    df["is_street_food"] = (df["category"] == "Street Food").astype(int)
    df["is_dessert"]     = (df["category"] == "Dessert").astype(int)
    df["is_breakfast"]   = (df["category"] == "Breakfast").astype(int)
    df["is_main"]        = (df["category"] == "Main Course").astype(int)
    return df


def _load_foods() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    _fit_encoders(df)
    return _encode(df)


def _model_path(user_id: int) -> str:
    return os.path.join(MODELS_DIR, f"model_user{user_id}.pkl")


def train_model(user_id: int = 0) -> dict:
    """Train a personal model for user_id."""
    from auth import get_user_feedback
    feedback = get_user_feedback(user_id)

    if len(feedback) < MIN_FEEDBACK:
        return {
            "trained": False,
            "samples": len(feedback),
            "message": f"Need {MIN_FEEDBACK} feedbacks (have {len(feedback)})"
        }

    foods  = _load_foods()
    merged = feedback.merge(foods, left_on="food_name", right_on="name", how="inner")

    if len(merged) < MIN_FEEDBACK:
        return {"trained": False, "samples": len(merged),
                "message": "Not enough matched feedback rows"}
    if len(merged["liked"].unique()) < 2:
        return {"trained": False, "samples": len(merged),
                "message": "Need both 👍 and 👎 feedbacks to train"}

    X = merged[FEATURE_COLS].values
    y = merged["liked"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42,
        stratify=y if len(y) >= 10 else None
    )

    # XGBoost — faster and more accurate than Gradient Boosting on tabular data
    clf = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test) if len(X_test) > 0 else None

    importance   = dict(zip(FEATURE_COLS, clf.feature_importances_))
    top_features = sorted(importance.items(), key=lambda x: -x[1])[:4]

    with open(_model_path(user_id), "wb") as f:
        pickle.dump({"clf": clf, "feature_cols": FEATURE_COLS}, f)

    return {
        "trained": True, "samples": len(merged),
        "accuracy": round(acc * 100, 1) if acc is not None else "N/A",
        "top_features": top_features,
        "message": f"Personal model trained on {len(merged)} samples",
    }


def load_model(user_id: int = 0):
    path = _model_path(user_id)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


def get_recommendations(preferences: dict, top_n: int = 6, user_id: int = 0) -> pd.DataFrame:
    foods    = _load_foods()
    filtered = foods.copy()

    if preferences.get("veg"):
        filtered = filtered[filtered["veg"] == "yes"]
    if preferences.get("max_calories"):
        filtered = filtered[filtered["calories"] <= preferences["max_calories"]]
    if preferences.get("category") and preferences["category"] != "Any":
        filtered = filtered[filtered["category"] == preferences["category"]]
    if filtered.empty:
        filtered = foods.copy()

    bundle = load_model(user_id)

    if bundle is not None:
        clf  = bundle["clf"]
        cols = bundle.get("feature_cols", FEATURE_COLS)
        X    = filtered[cols].values
        proba    = clf.predict_proba(X)
        like_idx = list(clf.classes_).index(1) if 1 in clf.classes_ else 0
        filtered = filtered.copy()
        filtered["ml_score"]   = proba[:, like_idx]
        filtered["score"]      = filtered["ml_score"] * 0.7 + (filtered["rating"] / 5.0) * 0.3
        filtered["model_used"] = "ML"
    else:
        user_vec = np.array([
            LEVEL.get(preferences.get("spicy",  "medium"), 1),
            LEVEL.get(preferences.get("sweet",  "low"),    0),
            1 if preferences.get("veg") else 0,
        ]).reshape(1, -1)
        food_mat = filtered[["spicy_enc", "sweet_enc", "veg_enc"]].values
        sims     = cosine_similarity(user_vec, food_mat)[0]
        filtered = filtered.copy()
        filtered["score"]      = sims * 0.6 + (filtered["rating"] / 5.0) * 0.4
        filtered["model_used"] = "similarity"

    return filtered.sort_values("score", ascending=False).head(top_n)
