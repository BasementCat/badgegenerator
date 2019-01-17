import os
import json
import hashlib
import pickle
import logging

from flask import (
    Flask,
    Blueprint,
    render_template,
    flash,
    current_app,
    )
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


apps = {}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy()
admin = Admin(name='BadgeGenerator', template_mode='bootstrap3', base_template='flask_admin_base.jinja.html')
login_manager = LoginManager()
bootstrap = Bootstrap()


login_manager.login_view = "user.login"


class Config(object):
    CONFIG_DIRS = [
        os.path.join(os.sep, 'etc', 'badgegenerator'),
        os.path.expanduser(os.path.join('~', '.config', 'badgegenerator')),
        os.path.join(os.path.dirname(__file__), '..', 'config'),
    ]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_dicts(self, *dicts):
        conf = {}
        for dict_ in dicts:
            conf.update(dict_)
        assert conf, "No configuration to load"
        return self(**conf)

    @classmethod
    def from_files(self, *filenames):
        configs = []
        for filename in filenames:
            with open(filename, 'r') as fp:
                configs.append(json.load(fp))
        assert configs, "No files to load config from"
        return self.from_dicts(*configs)

    @classmethod
    def from_env(self, env=None):
        if env is None:
            env = os.getenv('CON_QUEST_ENV', 'dev')

        files = []
        for dirname in self.CONFIG_DIRS:
            basefile = os.path.join(dirname, 'config-base.json')
            envfile = os.path.join(dirname, 'config-' + env + '.json')
            if os.path.exists(basefile):
                files.append(basefile)
            if os.path.exists(envfile):
                files.append(envfile)
        assert files, "No files to load config from for env: " + env
        return self.from_files(*files)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from app.views import admin as admin_view

    from app.views import (
        index as index_view,
        user as user_view,
        badge as badge_view,
        api as api_view,
        )

    app.register_blueprint(index_view.app)
    app.register_blueprint(user_view.app, url_prefix='/user')
    app.register_blueprint(badge_view.app, url_prefix='/badge')
    for route, view in api_view.views.items():
        app.add_url_rule(route, view_func=view)

    return app


def get_app(config=None, env=None, force_new=False):
    global apps

    if config is None:
        config = Config.from_env(env=env)

    key = hashlib.sha256(pickle.dumps(config)).hexdigest()
    if force_new or key not in apps:
        apps[key] = create_app(config)
    return apps[key]
