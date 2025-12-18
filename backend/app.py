# backend/app.py

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mail import Mail
import os
import json
import joblib
import pandas as pd
import numpy as np
import logging
import traceback
import importlib
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUTH_HTML = os.path.join(STATIC_DIR, "auth.html")
DASHBOARD_HTML = os.path.join(STATIC_DIR, "dashboard.html")
MODEL_PATH = os.path.join(BASE_DIR, "models", "rf_zfail.joblib")
STATS_JSON = os.path.join(BASE_DIR, "stats_table.json")

FEATURES = ["TP2", "TP3", "H1", "Oil_temperature", "DV_pressure"]

# Z-score / probability tuning
Z_THRESHOLD = 3.0
ALPHA = 1.2
Z0 = 1.5

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------
# MAIL SETUP
# --------------------------------------------------
app.config.update({
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 465,
    "MAIL_USE_SSL": True,
    "MAIL_USE_TLS": False,
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
    "MAIL_DEFAULT_SENDER": os.getenv(
        "MAIL_DEFAULT_SENDER",
        os.getenv("MAIL_USERNAME")
    ),
})

mail = Mail(app)
app.mail = mail

# --------------------------------------------------
# AUTH BLUEPRINT
# --------------------------------------------------
try:
    auth_module = importlib.import_module("routes.auth")

    auth_bp = getattr(auth_module, "auth_bp", None)
    if auth_bp:
        app.register_blueprint(auth_bp, url_prefix="/auth")
        logging.info("Auth blueprint registered at /auth")
    else:
        logging.error("auth_bp not found in routes.auth")
except Exception as e:
    logging.error("Auth blueprint load failed: %s", e)
    traceback.print_exc()

# --------------------------------------------------
# FRONTEND ROUTES
# --------------------------------------------------
@app.route("/")
def auth_page():
    return send_file(AUTH_HTML)

@app.route("/dashboard")
def dashboard_page():
    return send_file(DASHBOARD_HTML)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))

def safe_load_model(path):
    if not os.path.exists(path):
        logging.error("❌ Model file not found: %s", path)
        return None
    try:
        model = joblib.load(path)
        logging.info("✅ ML model loaded")
        return model
    except Exception:
        logging.exception("❌ Failed to load model")
        return None

def load_stats():
    if not os.path.exists(STATS_JSON):
        raise RuntimeError(
            "❌ stats_table.json NOT FOUND. "
            "Create it from training data. No fallback allowed."
        )
    with open(STATS_JSON, "r") as f:
        stats = json.load(f)
    logging.info("✅ Stats loaded from stats_table.json")
    return stats

def z_score_for_row(row, stats):
    z_scores = {}
    for f in FEATURES:
        mu = stats[f]["mean"]
        sd = stats[f]["std"] if stats[f]["std"] != 0 else 1.0
        z_scores[f] = (row[f] - mu) / sd
    return z_scores

def compute_prob_within_2months(max_abs_z, rf_prob):
    base_risk = logistic(ALPHA * (max_abs_z - Z0))
    w_rf = 0.45 if rf_prob is not None else 0.0
    w_z = 1.0 - w_rf
    combined = w_z * base_risk + (w_rf * rf_prob if rf_prob else 0.0)
    return float(np.clip(combined, 0.0, 1.0))

# --------------------------------------------------
# LOAD MODEL & STATS (FAIL FAST)
# --------------------------------------------------
model = safe_load_model(MODEL_PATH)
stats = load_stats()

# --------------------------------------------------
# PREDICT (REAL LOGIC — NOT HARDCODED)
# --------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
        raw_inputs = {}

        for f in FEATURES:
            if f not in payload:
                return jsonify({
                    "status": "Abnormal",
                    "warnings": [f"Missing:{f}"],
                    "prob_within_2months": 1.0,
                    "raw_inputs": payload
                }), 400
            raw_inputs[f] = float(payload[f])

        warnings_list = []
        processed = raw_inputs.copy()

        for f in FEATURES:
            if raw_inputs[f] < stats[f]["min"] or raw_inputs[f] > stats[f]["max"]:
                warnings_list.append(f)
            processed[f] = max(
                stats[f]["min"],
                min(raw_inputs[f], stats[f]["max"])
            )

        z_scores = z_score_for_row(processed, stats)
        max_abs_z = max(abs(v) for v in z_scores.values())
        status = "Abnormal" if max_abs_z > Z_THRESHOLD else "Normal"

        rf_prob = None
        if model and hasattr(model, "predict_proba"):
            X = pd.DataFrame([[processed[f] for f in FEATURES]], columns=FEATURES)
            proba = model.predict_proba(X)[0]
            if 1 in list(model.classes_):
                rf_prob = float(proba[list(model.classes_).index(1)])

        prob = compute_prob_within_2months(max_abs_z, rf_prob)

        return jsonify({
            "status": status,
            "warnings": warnings_list,
            "prob_within_2months": prob,
            "raw_inputs": raw_inputs
        }), 200

    except Exception:
        logging.exception("Unhandled error in /predict")
        return jsonify({"status": "Abnormal"}), 500

# --------------------------------------------------
# STATS ENDPOINT (REAL DATA)
# --------------------------------------------------
@app.route("/stats")
def stats_endpoint():
    return jsonify(stats), 200

# --------------------------------------------------
# START SERVER
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
