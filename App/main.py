from app import app
import os
from utils import build_system

if __name__ == '__main__':
    build_system()
    app.run(debug=True)