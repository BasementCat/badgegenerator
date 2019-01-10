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


app = Blueprint('index', __name__)
mimetypes.init()


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.jinja.html')


@app.route('/<path:filename>', methods=['GET'])
def upload(filename):
    mime, _ = mimetypes.guess_type(os.path.basename(filename), strict=False)
    with open(os.path.join(current_app.config['UPLOAD_PATH'], filename), 'rb') as fp:
        content = fp.read()
    return Response(content, mimetype=mime)
