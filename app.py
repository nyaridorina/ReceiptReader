from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            item TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Ensure table is created

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # File upload logic here...
        pass

    # Query data for the chart
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT item, SUM(price) FROM transactions GROUP BY item")
    data = c.fetchall()
    conn.close()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
