#! /usr/bin/env python

import sys

from flask.ext.script import Server
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand

from app import (
    get_app,
    db,
    )
from app.commands import (
    script_manager,
    user,
    internals,
    )

if __name__ == '__main__':
    app = get_app()

    migrate = Migrate(app, db)
    script_manager.add_command('db', MigrateCommand)

    script_manager.run()
