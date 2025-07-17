# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask import render_template
import config
import google.generativeai as genai
from flask import Flask, request, jsonify, redirect, render_template

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")


app = Flask(__name__)
CORS(app)

# === MySQL Configuration ===
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# === File Upload Config ===
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Helper: File Extension Check ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Helper: Extract text from PDF ===
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_ai_suggestion(item_name):
    prompt = f"""Suggest a greener and more sustainable alternative to '{item_name}' in 1–2 short sentences.
Explain why it's better for the environment in a simple, beginner-friendly way.
Avoid long paragraphs or technical details."""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        return None



def parse_items_from_text(text):
    items = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    i = 0
    while i < len(lines) - 2:
        name_line = lines[i]
        sku_line = lines[i+1]
        price_line = lines[i+2]

        if re.match(r'^\d+(\.\d{2})?$', price_line.replace('$', '')) and sku_line.isdigit():
            try:
                price = float(price_line.replace('$', ''))
                items.append({
                    'item_name': name_line,
                    'sku': sku_line,
                    'price': price,
                    'category': None,
                    'eco_score': None
                })
                i += 3  # Skip the next two since we processed them
            except:
                i += 1
        else:
            i += 1

    print(f"[INFO] Extracted {len(items)} items using 3-line strategy")
    return items


def get_ai_eco_score(item_name):
    prompt = f"""You're an environmental sustainability expert.
Assign a sustainability score to this item: "{item_name}".
Respond with just an integer between 0 (worst) and 100 (best) without any explanation."""
    try:
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        score = int(re.findall(r'\d+', score_text)[0])
        return max(0, min(score, 100))
    except Exception as e:
        print("Eco Score AI error:", e)
        return None
    
def assign_eco_scores(items):
    for item in items:
        item['eco_score'] = get_ai_eco_score(item['item_name'])
        item['ai_tip'] = get_ai_suggestion(item['item_name'])
    return items




# === Basic API Test Route ===
@app.route('/')
def home():
    return redirect('/login-page')


# === Upload and Process PDF ===
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'user_id' not in request.form:
        return jsonify({'error': 'File and user_id are required'}), 400

    file = request.files['file']
    user_id = request.form['user_id']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # === Extract and Analyze PDF ===
        extracted_text = extract_text_from_pdf(save_path)
        items = parse_items_from_text(extracted_text)
        items = assign_eco_scores(items)

        # === Insert receipt into receipts table ===
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO receipts (user_id, filename) VALUES (%s, %s)",
            (user_id, filename)
        )
        receipt_id = cur.lastrowid  # ✅ Now receipt_id is available

        # === Insert each item into items table ===
        for item in items:
            cur.execute("INSERT INTO items (receipt_id, item_name, price, category, eco_score, ai_tip) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                receipt_id,
                item['item_name'],
                item['price'],
                item.get('category'),
                item.get('eco_score'),
                 item.get('ai_tip')
                )
            )


        mysql.connection.commit()
        cur.close()

        return jsonify({
            'message': 'Receipt and items saved successfully',
            'receipt_id': receipt_id,
            'items': items
        }), 200

    return jsonify({'error': 'Only PDF files are allowed'}), 400


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Please fill all fields'}), 400

    hashed_password = generate_password_hash(password)

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                    (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):
        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'name': user[1]
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/upload', methods=['GET'])
def serve_upload_page():
    return render_template('upload.html')


@app.route('/receipts/<int:user_id>', methods=['GET'])
def get_user_receipts(user_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT r.id, r.filename, r.upload_date,
            COALESCE(ROUND(AVG(i.eco_score), 2), 0) AS avg_eco_score
        FROM receipts r
        LEFT JOIN items i ON r.id = i.receipt_id
        WHERE r.user_id = %s
        GROUP BY r.id
        ORDER BY r.upload_date DESC
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()

    receipts = []
    for row in rows:
        receipts.append({
            'receipt_id': row[0],
            'filename': row[1],
            'upload_date': str(row[2]),  # convert datetime to string
            'eco_score_avg': float(row[3])
        })

    return jsonify(receipts), 200

@app.route('/receipt/<int:receipt_id>', methods=['GET'])
def get_receipt_items(receipt_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT item_name, price, eco_score, ai_tip
        FROM items
        WHERE receipt_id = %s
    """, (receipt_id,))

    rows = cur.fetchall()
    cur.close()

    items = []
    for row in rows:
        items.append({
            'item_name': row[0],
            'price': float(row[1]),
            'eco_score': row[2],
            'ai_tip': row[3]
        })

    return jsonify({'receipt_id': receipt_id, 'items': items}), 200



@app.route('/login-page')
def login_page():
    return render_template('login.html')


@app.route('/register')
def serve_register_page():
    return render_template('register.html')

@app.route('/login')
def serve_login_page():
    return render_template('login.html')

@app.route('/history')
def serve_history_page():
    return render_template('history.html')  

#Average eco score
@app.route('/dashboard/eco-score-over-time/<int:user_id>')
def eco_score_over_time(user_id):
    cursor = mysql.connection.cursor()
    query = """
    SELECT DATE(r.upload_date) as date, AVG(i.eco_score) as avg_score
    FROM receipts r
    JOIN items i ON r.id = i.receipt_id
    WHERE r.user_id = %s
    GROUP BY DATE(r.upload_date)
    ORDER BY DATE(r.upload_date)
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    return jsonify(data)

#Top eco friendly items
@app.route('/dashboard/top-eco-items/<int:user_id>')
def top_eco_items(user_id):
    cursor = mysql.connection.cursor()
    query = """
    SELECT i.item_name, AVG(i.eco_score) as avg_score
    FROM receipts r
    JOIN items i ON r.id = i.receipt_id
    WHERE r.user_id = %s
    GROUP BY i.item_name
    ORDER BY avg_score DESC
    LIMIT 5
    """
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchall())

#low eco score items
@app.route('/dashboard/low-eco-items/<int:user_id>')
def low_eco_items(user_id):
    cursor = mysql.connection.cursor()
    query = """
    SELECT i.item_name, i.eco_score
    FROM receipts r
    JOIN items i ON r.id = i.receipt_id
    WHERE r.user_id = %s AND i.eco_score < 50
    ORDER BY i.eco_score ASC
    LIMIT 5
    """
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchall())

#total receipt count
@app.route('/dashboard/receipt-count/<int:user_id>')
def receipt_count(user_id):
    cursor = mysql.connection.cursor()
    query = "SELECT COUNT(*) as total FROM receipts WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchone())


@app.route('/dashboard')
def serve_dashboard_page():
    return render_template('dashboard.html')


# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
