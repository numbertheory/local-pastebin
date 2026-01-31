import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from jinja2 import Environment, FileSystemLoader
from backend.models import db, Paste
from backend.api import remove_paste
from utils.utilities import generate_id, is_url, set_to_timezone

app = Flask(__name__)
app.jinja_env.tests['url'] = is_url

# Database configuration
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = '/data' if os.path.exists('/data') else base_dir
db_path = os.path.join(data_dir, 'pastes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PASTES_PER_PAGE'] = 10

db.init_app(app)

# Initialize DB
with app.app_context():
    db.create_all()

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    
    # Subquery to find the latest version for each paste
    subquery = db.session.query(Paste.id, db.func.max(Paste.version).label('max_version')).group_by(Paste.id).subquery()
    
    # Join to get only the latest versions
    pagination = Paste.query.join(subquery, (Paste.id == subquery.c.id) & (Paste.version == subquery.c.max_version)).order_by(Paste.created_at.desc()).paginate(page=page, per_page=app.config['PASTES_PER_PAGE'], error_out=False)

    recent_pastes = [
        {"id": x.id, "content": x.content, "version": x.version,
        "created_at": set_to_timezone(x.created_at)} for x in pagination.items]
    for i in range(0, len(recent_pastes)):
        pastes = Paste.query.filter_by(id=recent_pastes[i]["id"]).order_by(Paste.version.desc()).all()
        history = [{'version': p.version, 'created_at': set_to_timezone(p.created_at)} for p in pastes]
        recent_pastes[i]["max_versions"] = len(history)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            return render_template('index.html', error="Content cannot be empty", recent_pastes=recent_pastes, pagination=pagination)
        
        paste_id = generate_id(Paste)
        new_paste = Paste(id=paste_id, content=content)
        db.session.add(new_paste)
        db.session.commit()
        
        return redirect(url_for('view_paste', paste_id=paste_id))
    return render_template('index.html', recent_pastes=recent_pastes, pagination=pagination)

@app.route('/modify/<paste_id>', methods=['POST'])
def modify_paste(paste_id):
    # Get the latest version to increment
    latest_paste = Paste.query.filter_by(id=paste_id).order_by(Paste.version.desc()).first_or_404()
    content = request.form.get('content')
    if content:
        new_version = latest_paste.version + 1
        new_paste = Paste(id=paste_id, version=new_version, content=content)
        db.session.add(new_paste)
        db.session.commit()
    return redirect(url_for('view_paste', paste_id=paste_id))

@app.route('/delete/<paste_id>', methods=['POST'])
def delete_paste(paste_id):
    remove_paste(Paste, db, paste_id)
    return redirect(url_for('index'))

@app.route('/<paste_id>')
def view_paste(paste_id):
    version = request.args.get('version', type=int)
    pastes = Paste.query.filter_by(id=paste_id).order_by(Paste.version.desc()).all()
    if not pastes:
        abort(404)

    if version:
        paste = next((p for p in pastes if p.version == version), None)
        if not paste:
            abort(404)
    else:
        paste = pastes[0]

    dict_paste = paste.to_dict()
    dict_paste["created_at"] = set_to_timezone(paste.created_at)
    
    history = [{'version': p.version, 'created_at': set_to_timezone(p.created_at)} for p in pastes]
    return render_template('view.html', paste=dict_paste, history=history)

@app.route('/raw/<paste_id>')
def view_raw(paste_id):
    paste = Paste.query.filter_by(id=paste_id).order_by(Paste.version.desc()).first_or_404()
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

    paste_id = generate_id(Paste)
    new_paste = Paste(id=paste_id, content=content)
    db.session.add(new_paste)
    db.session.commit()

    return jsonify({
        'id': paste_id,
        'url': url_for('view_paste', paste_id=paste_id, _external=True),
        'raw_url': url_for('view_raw', paste_id=paste_id, _external=True)
    }), 201

@app.route('/api/paste/<paste_id>', methods=['GET'])
def api_get_paste(paste_id):
    if request.method == "GET":
        paste = Paste.query.filter_by(id=paste_id).order_by(Paste.version.desc()).first_or_404()
        return jsonify(paste.to_dict())

if __name__ == '__main__':
    # Running on 0.0.0.0 to be accessible from outside the container
    app.run(host='0.0.0.0', port=3636)
