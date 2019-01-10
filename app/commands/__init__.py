from flask_script import Manager as ScriptManager

from app import get_app


script_manager = ScriptManager(get_app())
