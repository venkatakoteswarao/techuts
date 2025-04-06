from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'suraboinakoteswarao@gmail.com'

# Database configuration (Neon.tech)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_lxvZiEAG0tW7@ep-delicate-sun-a134x7s4-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------- MODELS ----------
class Carousel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    link = db.Column(db.String(255))

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

class InstagramPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    instagram_link = db.Column(db.String(255))

class TechUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)

# ---------- USER ROUTES ----------
@app.route('/')
def home():
    carousels = Carousel.query.all()
    words = Word.query.order_by(Word.id.desc()).all()
    return render_template('user/index1.html', carousels=carousels, words=words)

@app.route('/about')
def about():
    about_content = About.query.first()
    return render_template('user/about.html', content=about_content)

@app.route('/contact')
def contact():
    return render_template('user/contact.html')

@app.route('/techupdates')
def techupdates():
    updates = TechUpdate.query.all()
    return render_template('user/techupdates.html', updates=updates)

@app.route('/instagram')
def instagram():
    posts = InstagramPost.query.all()
    return render_template('user/instagram_feed.html', posts=posts)

# ---------- ADMIN ROUTES ----------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'gopiSankarnelluRI' and password == 'gopicseaiml.2K22':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('admin/adminlogin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    carousels = Carousel.query.all()
    posts = InstagramPost.query.all()
    updates = TechUpdate.query.all()
    about_content = About.query.first()
    words = Word.query.order_by(Word.id.desc()).all()
    return render_template('admin/admin1.html', carousels=carousels, posts=posts, updates=updates, about=about_content, words=words)

@app.route('/upload_carousel', methods=['POST'])
def upload_carousel():
    if 'image' not in request.files:
        return redirect(url_for('admin_dashboard'))

    image = request.files['image']
    link = request.form.get('link')

    if image.filename != '':
        filename = secure_filename(image.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(path)
        url = f'/static/uploads/{filename}'
        new_image = Carousel(image_url=url, link=link)
        db.session.add(new_image)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_carousel/<int:id>')
def delete_carousel(id):
    item = Carousel.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_post', methods=['POST'])
def upload_post():
    image = request.files['image']
    description = request.form['description']
    instagram_link = request.form['instagram_link']

    if image.filename != '':
        filename = secure_filename(image.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(path)
        url = f'/static/uploads/{filename}'
        post = InstagramPost(image_url=url, description=description, instagram_link=instagram_link)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_post/<int:id>')
def delete_post(id):
    post = InstagramPost.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_update', methods=['POST'])
def upload_update():
    title = request.form['title']
    description = request.form['description']
    update = TechUpdate(title=title, description=description)
    db.session.add(update)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_update/<int:id>')
def delete_update(id):
    update = TechUpdate.query.get(id)
    if update:
        db.session.delete(update)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_about', methods=['POST'])
def update_about():
    content = request.form['content']
    existing = About.query.first()
    if existing:
        existing.content = content
    else:
        new_about = About(content=content)
        db.session.add(new_about)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_word', methods=['POST'])
def add_word():
    word = request.form['word']
    meaning = request.form['meaning']
    new_word = Word(word=word, meaning=meaning)
    db.session.add(new_word)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_word', methods=['POST'])
def delete_word():
    word_id = request.form['id']
    word = Word.query.get(word_id)
    if word:
        db.session.delete(word)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# ---------- RUN ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ✅ Creates Word table and others if missing
    app.run(debug=True)

