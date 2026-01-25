import os
import random
import string
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Database configuration
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = '/data' if os.path.exists('/data') else base_dir
db_path = os.path.join(data_dir, 'pastes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PASTES_PER_PAGE'] = 10

db = SQLAlchemy(app)

# Model
class Paste(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

def generate_id(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        new_id = ''.join(random.choice(characters) for _ in range(length))
        if not Paste.query.get(new_id):
            return new_id

# Initialize DB
with app.app_context():
    db.create_all()

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Paste.query.order_by(Paste.created_at.desc()).paginate(page=page, per_page=app.config['PASTES_PER_PAGE'], error_out=False)
    recent_pastes = pagination.items

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            return render_template('index.html', error="Content cannot be empty", recent_pastes=recent_pastes, pagination=pagination)
        
        paste_id = generate_id()
        new_paste = Paste(id=paste_id, content=content)
        db.session.add(new_paste)
        db.session.commit()
        
        return redirect(url_for('view_paste', paste_id=paste_id))
    
    return render_template('index.html', recent_pastes=recent_pastes, pagination=pagination)

@app.route('/<paste_id>')
def view_paste(paste_id):
    paste = Paste.query.get_or_404(paste_id)
    return render_template('view.html', paste=paste)

@app.route('/raw/<paste_id>')
def view_raw(paste_id):
    paste = Paste.query.get_or_404(paste_id)
    return paste.content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

# API Routes
@app.route('/api/paste', methods=['POST'])
def api_create_paste():
    data = request.get_json(silent=True)
    
    # Handle form data or JSON
    if data and 'content' in data:
        content = data['content']
    elif request.form.get('content'):
        content = request.form.get('content')
    else:
        # If raw body is sent as text/plain, use that
        if request.mimetype == 'text/plain':
             content = request.data.decode('utf-8')
        else:
             return jsonify({'error': 'Content is required. Send JSON {"content": "..."}, form data, or raw text.'}), 400

    if not content:
        return jsonify({'error': 'Content cannot be empty'}), 400

    paste_id = generate_id()
    new_paste = Paste(id=paste_id, content=content)
    db.session.add(new_paste)
    db.session.commit()

    return jsonify({
        'id': paste_id,
        'url': url_for('view_paste', paste_id=paste_id, _external=True),
        'raw_url': url_for('view_raw', paste_id=paste_id, _external=True)
    }), 201

@app.route('/api/paste/<paste_id>', methods=['GET', 'DELETE'])
def api_get_paste(paste_id):
    if request.method == "GET":
        paste = Paste.query.get_or_404(paste_id)
        return jsonify(paste.to_dict())
    if request.method == "DELETE":
        paste = Paste.query.get_or_404(paste_id)
        db.session.delete(paste)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    # Running on 0.0.0.0 to be accessible from outside the container
    app.run(host='0.0.0.0', port=3636)
