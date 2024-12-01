from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import pytesseract
from PIL import Image

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Specify the Tesseract executable path (if required)
# Change this path based on where Tesseract is installed in your environment
# For Render, this is usually not needed unless it’s installed in a non-standard path.
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

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

# Call the database initialization function
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        if file and file.filename:
            # Save the uploaded file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            try:
                # Process the image with Tesseract OCR
                text = pytesseract.image_to_string(Image.open(filepath))
                print("OCR Output:", text)  # Debugging: Print OCR output to logs

                # Extract and insert recognized data into the database
                conn = sqlite3.connect('db.sqlite')
                c = conn.cursor()

                for line in text.splitlines():
                    parts = line.split()
                    if len(parts) > 1:
                        item = ' '.join(parts[:-1])
                        try:
                            price = float(parts[-1].replace('Ft', '').replace(',', '.'))
                            c.execute("INSERT INTO transactions (date, item, price) VALUES (date('now'), ?, ?)", (item, price))
                        except ValueError:
                            # Skip lines that do not end with a valid price
                            continue

                conn.commit()
                conn.close()

                return redirect(url_for('index'))

            except TesseractNotFoundError:
                return "Error: Tesseract is not installed or not configured properly. Please contact the administrator.", 500

            except Exception as e:
                print(f"Error processing the image: {e}")
                return "An error occurred while processing the image. Please try again later.", 500

    # Fetch data from the database for visualization
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT item, SUM(price) FROM transactions GROUP BY item")
    data = c.fetchall()
    conn.close()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT environment variable
    app.run(host='0.0.0.0', port=port)
