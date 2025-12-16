# your_theme_package.py
from pathlib import Path

def setup(app):
    app.add_html_theme('psychopy', Path(__file__).resolve().parent)