# from StringIO import StringIO

from flask import (
    Blueprint,
    url_for,
    render_template,
    flash,
    redirect,
    )
from flask_login import login_user, logout_user, current_user

from app.forms.user import (
    LoginForm,
    )

from app.models import User

app = Blueprint('user', __name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if form.submit_login.data:
            user = User.query.filter(User.username.like(form.username.data)).first()
            if user and user.password == form.password.data:
                login_user(user, remember=True if form.remember_me.data else False)
                return redirect(url_for('index.index'))
            else:
                flash("Invalid username or password", 'danger')
        else:
            flash("No action", 'danger')

    return render_template('user/login.jinja.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index.index'))
