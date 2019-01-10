from flask_wtf import Form

import wtforms as wtf
import wtforms.validators as v


class LoginForm(Form):
    username = wtf.TextField('Username', validators=[v.Required()])
    password = wtf.PasswordField('Password', validators=[v.Required()])
    remember_me = wtf.BooleanField('Remember Me', description="Keeps you logged in after you close the browser window.  Don't check this box on shared computers.")

    submit_login = wtf.SubmitField('Log In')
