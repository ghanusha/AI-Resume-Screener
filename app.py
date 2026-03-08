import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import  secure_filename
import json

from database import get_db_connection, init_db
from parser import extract_text
from skill_extractor import extract_skills
from matcher import match_skills

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_resume_screener'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure DB is initialized
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/")
def home():
    return "Hello"
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user_exists = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user_exists:
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    candidates = conn.execute('SELECT * FROM candidates WHERE username = ? ORDER BY date DESC', (session['username'],)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', candidates=candidates)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        job_skills_input = request.form['job_skills']
        if not job_skills_input:
            flash('Please specify required job skills.', 'danger')
            return redirect(url_for('upload'))
            
        job_skills = [s.strip().lower() for s in job_skills_input.split(',')]
        
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload'))
            
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload'))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Application Logic
            text = extract_text(filepath)
            resume_skills = extract_skills(text)
            match_result = match_skills(resume_skills, job_skills)
            
            # Save to Database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO candidates (username, skills, matched, missing, score, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['username'],
                json.dumps(resume_skills),
                json.dumps(match_result['matched']),
                json.dumps(match_result['missing']),
                match_result['score'],
                match_result['status']
            ))
            candidate_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return redirect(url_for('result', candidate_id=candidate_id))
            
    return render_template('upload.html')

@app.route('/result/<int:candidate_id>')
def result(candidate_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    candidate = conn.execute('SELECT * FROM candidates WHERE id = ? AND username = ?', (candidate_id, session['username'])).fetchone()
    conn.close()
    
    if candidate is None:
        flash('Result not found', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('result.html', candidate=candidate, 
                           resume_skills=json.loads(candidate['skills']),
                           matched_skills=json.loads(candidate['matched']),
                           missing_skills=json.loads(candidate['missing']))

if __name__ == '__main__':
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
