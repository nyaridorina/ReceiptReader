from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        # Handle file upload
        file = request.files['file']
        if file and file.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Process the image with Tesseract OCR
            text = pytesseract.image_to_string(Image.open(filepath))
            lines = text.splitlines()

            # Insert recognized data into the database
            conn = sqlite3.connect('db.sqlite')
            c = conn.cursor()
            for line in lines:
                parts = line.split()
                if len(parts) > 1:
                    item = ' '.join(parts[:-1])
                    try:
                        price = float(parts[-1].replace('Ft', '').replace(',', '.'))
                        c.execute("INSERT INTO transactions (date, item, price) VALUES (date('now'), ?, ?)", (item, price))
                    except ValueError:
                        continue
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    # Query data for the chart
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT item, SUM(price) FROM transactions GROUP BY item")
    data = c.fetchall()
    conn.close()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT variable
    app.run(host='0.0.0.0', port=port)
