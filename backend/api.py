from flask import redirect, abort, url_for

def remove_paste(Paste, db, paste_id):
    pastes = Paste.query.filter_by(id=paste_id).all()
    if not pastes:
        abort(404)
    for paste in pastes:
        db.session.delete(paste)
    db.session.commit()