from getpass import getpass

from tabulate import tabulate

from . import script_manager

from app import db

from app.models import (
    User,
    )


@script_manager.option('-a', '--add', help="Add a user with this username")
@script_manager.option('-e', '--edit', help="Edit the user with this username")
@script_manager.option('--delete', help="PERMANENTLY DELETE the user with this username")
@script_manager.option('--username', help="Change the user's username")
@script_manager.option('--password', help="User's password")
@script_manager.option('--ask-password', action='store_true', help="Ask for the user's password")
def user(add, edit, delete, username, password, ask_password):
    if add or edit:
        with db.session.no_autoflush:
            if add:
                user = User(username=add)
            elif edit:
                user = User.query.filter(User.has_username_slug(edit.decode('utf-8'))).one()

            if username:
                user.username = username

            if not password and ask_password:
                password = getpass("Password: ")
                if password != getpass("Password, again: "):
                    raise ValueError("Passwords must match")

            if password:
                user.password = password

            db.session.add(user)
            db.session.commit()
    elif delete:
        user = User.query.filter(User.has_username_slug(delete.decode('utf-8'))).one()
        if raw_input("Are you sure you want to PERMANENTLY DELETE '{}'? Type 'YES' to confirm, there is no undo! ".format(user.username)) != 'YES':
            print("Deletion cancelled.")
            return

        db.session.delete(user)
        db.session.commit()
    else:
        print(User.query.all())
        print(tabulate(
            [
                [
                    u.id,
                    u.username,
                    'Yes' if u.password else 'No',
                ]
                for u in User.query.all()
            ],
            headers=['ID', 'Username', 'Password']
        ))
