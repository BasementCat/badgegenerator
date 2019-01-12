import mimetypes
import os

from flask import (
    Blueprint,
    url_for,
    render_template,
    redirect,
    flash,
    current_app,
    Response,
    )
from flask_login import current_user, login_required

from app.models import Badge, BadgeTemplate


app = Blueprint('index', __name__)
mimetypes.init()


@app.route('/', methods=['GET'])
@login_required
def index():
    templates = BadgeTemplate.query.all()
    badges = Badge.query.filter(Badge.print_queued == True).all()
    badge_templates = {}
    for badge in badges:
        tpl_match = [(t, t.matches(badge)) for t in templates]
        if tpl_match:
            tpl_match = list(sorted(tpl_match, key=lambda v: v[1]))
            tpl_match = [v[0] for v in tpl_match if v[1] > 0 and v[1] == tpl_match[-1][1]]
        badge_templates[badge.id] = tpl_match
    return render_template('index.jinja.html', badges=badges, badge_templates=badge_templates)


@app.route('/<path:filename>', methods=['GET'])
def upload(filename):
    mime, _ = mimetypes.guess_type(os.path.basename(filename), strict=False)
    with open(os.path.join(current_app.config['UPLOAD_PATH'], filename), 'rb') as fp:
        content = fp.read()
    return Response(content, mimetype=mime)
