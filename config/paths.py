import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_DATA_DIR = Path(os.getenv("RAVEN_UCI_HAR_PATH", BASE_DIR / "UCI-HAR_Dataset"))
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

def get_uci_har_train_path():
    return EXTERNAL_DATA_DIR / "train"

def get_uci_har_test_path():
    return EXTERNAL_DATA_DIR / "test"
