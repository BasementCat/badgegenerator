import arrow

import sqlalchemy_utils as sau

from flask import url_for

from app import (
    db,
    login_manager,
    )


sau.force_auto_coercion()


class Model(db.Model):
    __abstract__ = True


class TimestampMixin(object):
    created_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow)
    updated_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow, onupdate=arrow.utcnow)


class User(TimestampMixin, Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.Unicode(128), nullable=False)
    password = db.Column(sau.PasswordType(schemes=['bcrypt'], bcrypt__min_rounds=12))

    def __str__(self):
        return self.username

    # Stuff for flask login
    @staticmethod
    @login_manager.user_loader
    def flask_login__load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            pass

        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Flag(Model):
    __tablename__ = 'flag'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(32), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())

    def __str__(self):
        return self.name


class Level(Model):
    __tablename__ = 'level'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(32), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())

    def __str__(self):
        return self.name


class BadgeTemplateToFlag(Model):
    __tablename__ = 'badge_template_to_flag'
    __table_args__ = (db.PrimaryKeyConstraint('badge_template_id', 'flag_id'),)

    badge_template_id = db.Column(db.BigInteger(), db.ForeignKey('badge_template.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    flag_id = db.Column(db.BigInteger(), db.ForeignKey('flag.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)


class BadgeTemplateToLevel(Model):
    __tablename__ = 'badge_template_to_level'
    __table_args__ = (db.PrimaryKeyConstraint('badge_template_id', 'level_id'),)

    badge_template_id = db.Column(db.BigInteger(), db.ForeignKey('badge_template.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    level_id = db.Column(db.BigInteger(), db.ForeignKey('level.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)


class BadgeTemplate(TimestampMixin, Model):
    __tablename__ = 'badge_template'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.UnicodeText(), nullable=False)
    description = db.Column(db.UnicodeText())
    extends_id = db.Column(db.BigInteger(), db.ForeignKey('badge_template.id', onupdate='CASCADE', ondelete='RESTRICT'))
    extends = db.relationship('BadgeTemplate', remote_side=[id], backref='extended_by')
    min_age = db.Column(db.Integer())
    max_age = db.Column(db.Integer())
    image = db.Column(db.UnicodeText())

    badge_name_top = db.Column(db.Float())
    badge_name_left = db.Column(db.Float())
    badge_name_width = db.Column(db.Float())
    badge_name_height = db.Column(db.Float())

    badge_number_top = db.Column(db.Float())
    badge_number_left = db.Column(db.Float())
    badge_number_width = db.Column(db.Float())
    badge_number_height = db.Column(db.Float())

    level_top = db.Column(db.Float())
    level_left = db.Column(db.Float())
    level_width = db.Column(db.Float())
    level_height = db.Column(db.Float())

    timestamp_format = db.Column(db.UnicodeText())
    timestamp_append_to_level = db.Column(db.Boolean(), nullable=False, default=False)
    timestamp_top = db.Column(db.Float())
    timestamp_left = db.Column(db.Float())
    timestamp_width = db.Column(db.Float())
    timestamp_height = db.Column(db.Float())

    arbitrary_text = db.Column(db.UnicodeText())
    arbitrary_text_override_level = db.Column(db.Boolean(), nullable=False, default=False)
    arbitrary_text_top = db.Column(db.Float())
    arbitrary_text_left = db.Column(db.Float())
    arbitrary_text_width = db.Column(db.Float())
    arbitrary_text_height = db.Column(db.Float())

    css = db.Column(db.UnicodeText())

    flags = db.relationship('Flag', secondary=BadgeTemplateToFlag.__table__, backref='badge_templates')
    levels = db.relationship('Level', secondary=BadgeTemplateToLevel.__table__, backref='badge_templates')

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return url_for('index.upload', filename=self.image)


class BadgeToFlag(Model):
    __tablename__ = 'badge_to_flag'
    __table_args__ = (db.PrimaryKeyConstraint('badge_id', 'flag_id'),)

    badge_id = db.Column(db.BigInteger(), db.ForeignKey('badge.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    flag_id = db.Column(db.BigInteger(), db.ForeignKey('flag.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)


class Badge(TimestampMixin, Model):
    __tablename__ = 'badge'

    id = db.Column(db.BigInteger(), primary_key=True)
    foreign_id = db.Column(db.String(64), unique=True)
    name = db.Column(db.UnicodeText(), nullable=False)
    level_id = db.Column(db.BigInteger(), db.ForeignKey('level.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    level = db.relationship('Level')
    real_age = db.Column(db.Integer())
    under_18 = db.Column(db.Boolean(), nullable=False, default=False)
    under_13 = db.Column(db.Boolean(), nullable=False, default=False)
    print_queued = db.Column(db.Boolean(), nullable=False, default=False, index=True)
    print_queued_by_id = db.Column(db.BigInteger(), db.ForeignKey('user.id', onupdate='CASCADE', ondelete='SET NULL'))
    print_queued_by = db.relationship('User')

    flags = db.relationship('Flag', secondary=BadgeToFlag.__table__)

    @property
    def age(self):
        """\
        Returns an adjusted age - a real age, if set, otherwise a fake age corresponding to another age group
        """
        if self.under_13:
            return 12
        elif self.under_18:
            return 17
        return self.real_age

    @age.setter
    def age(self, value):
        if value < 13:
            self.under_13 = True
            self.under_18 = True
            self.real_age = None
        elif value < 18:
            self.under_13 = False
            self.under_18 = True
            self.real_age = None
        else:
            self.under_13 = False
            self.under_18 = False
            self.real_age = value


class BadgePrint(TimestampMixin, Model):
    __tablename__ = 'badge_print'

    id = db.Column(db.BigInteger(), primary_key=True)
    badge_id = db.Column(db.BigInteger(), db.ForeignKey('badge.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    badge = db.relationship('Badge', backref='prints')
    queued_by_id = db.Column(db.BigInteger(), db.ForeignKey('user.id', onupdate='CASCADE', ondelete='SET NULL'))
    queued_by = db.relationship('User', foreign_keys=[queued_by_id])
    printed_by_id = db.Column(db.BigInteger(), db.ForeignKey('user.id', onupdate='CASCADE', ondelete='SET NULL'))
    printed_by = db.relationship('User', foreign_keys=[printed_by_id])