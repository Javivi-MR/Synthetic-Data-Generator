import os
import numpy as np
from models import Dataset, User
from app import bcrypt
import config as C
import csv

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

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None

def has_header(file):
    # Check if the file is a FileStorage object (uploaded file)
    if hasattr(file, 'stream'):
        read_method = file.stream.readline
    else:  # The file is a regular file object
        read_method = file.readline

    # Read the first 3 lines of the file
    first_lines = [read_method().decode('utf-8') for _ in range(3)]
    sample = ''.join(first_lines)

    # If the file is a FileStorage object, reset the stream position
    if hasattr(file, 'stream'):
        file.stream.seek(0)

    # Use csv.Sniffer to check if the file has a header
    sniffer = csv.Sniffer()
    has_header = sniffer.has_header(sample)

    return has_header

def separate_with_comma(file):
    # Check if the file is a FileStorage object (uploaded file)
    if hasattr(file, 'stream'):
        read_method = file.stream.readline
    else:  # The file is a regular file object
        read_method = file.readline

    # Read the first 3 lines of the file
    first_lines = [read_method().decode('utf-8') for _ in range(3)]
    sample = ''.join(first_lines)

    # If the file is a FileStorage object, reset the stream position
    if hasattr(file, 'stream'):
        file.stream.seek(0)

    # Use csv.Sniffer to check if the file has a header
    sniffer = csv.Sniffer()

    # Use csv.Sniffer to check the delimiter
    dialect = sniffer.sniff(sample)

    return dialect.delimiter == ','