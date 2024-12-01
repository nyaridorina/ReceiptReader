from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import pytesseract
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Adatbázis inicializálása
def init_db():
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT,
            item TEXT,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Kép feltöltése
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # OCR feldolgozás
            text = pytesseract.image_to_string(Image.open(filepath))
            lines = text.splitlines()

            # Tétel és ár mentése adatbázisba
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
    
    # Tranzakciók lekérdezése
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT item, SUM(price) FROM transactions GROUP BY item")
    data = c.fetchall()
    conn.close()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
