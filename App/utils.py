import os
import numpy as np
from models import Dataset
import config as C

def build_system():
    if not os.path.exists(C.DATASET_PATH):
        os.makedirs(C.DATASET_PATH)
    if not os.path.exists(C.SYNTHETIC_PATH):
        os.makedirs(C.SYNTHETIC_PATH)
    if not os.path.exists(C.PLOT_PATH):
        os.makedirs(C.PLOT_PATH)

def get_regression_line(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    return slope, intercept

def load_dataset(dataset_id):
    return Dataset.query.get(int(dataset_id))