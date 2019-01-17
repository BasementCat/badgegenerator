from collections import OrderedDict
import os
import imghdr

from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField
from flask_admin.form import rules as r

from flask import current_app
from flask_login import current_user

from wtforms import ValidationError

from markupsafe import Markup

from app import admin
from app import models

from app import db


class CustomModelView(ModelView):
    def is_accessible(self):
        # TODO: check whether user can access admin
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user.login'))


class FlagLevelModelView(CustomModelView):
    form_excluded_columns = ['badge_templates', 'badges']


class BadgeTemplateModelView(CustomModelView):
    def _image_validator(form, field):
        if field.data:
            if isinstance(field.data, str):
                return True

            ext = imghdr.what(field.data)
            if not ext:
                raise ValidationError("Not an image")

            return True

    def _image_formatter(view, context, model, name):
        if model.image:
            return Markup('<a target="_blank" href="{}">{}</a>'.format(
                model.image_url,
                model.image
            ))

    form_overrides = {
        'image': FileUploadField,
    }
    form_args = {
        'image': {
            'base_path': lambda: current_app.config['UPLOAD_PATH'],
            'validators': [_image_validator],
        }
    }
    column_formatters = {
        'image': _image_formatter,
    }
    column_exclude_list = ['badge_name_top', 'badge_name_left', 'badge_name_width',
        'badge_name_height', 'badge_number_top', 'badge_number_left', 'badge_number_width',
        'badge_number_height', 'level_top', 'level_left', 'level_width', 'level_height',
        'timestamp_format', 'timestamp_top', 'timestamp_left', 'timestamp_width',
        'timestamp_height', 'arbitrary_text', 'arbitrary_text_top', 'arbitrary_text_left',
        'arbitrary_text_width', 'arbitrary_text_height', 'css', 'timestamp_append_to_level',
        'arbitrary_text_override_level']

    form_create_rules = [
        r.FieldSet(
            [
                r.Text("Basic badge properties"),
                'name',
                'description',
                'extends',
                'image',
            ],
            header='Base'
        ),
        r.FieldSet(
            [
                r.Text("Determine how badge templates are matched to badges, the most specific matching template is applied"),
                'no_match',
                'min_age',
                'max_age',
                'levels',
                'flags',
            ],
            header='Targeting'
        ),

        r.FieldSet(
            [
                r.Text("Where elements are positioned.  All positions are in inches."),
                r.FieldSet(
                    [
                        'badge_name_top',
                        'badge_name_left',
                        'badge_name_width',
                        'badge_name_height',
                    ],
                    header='Badge Name'
                ),

                r.FieldSet(
                    [
                        'badge_number_top',
                        'badge_number_left',
                        'badge_number_width',
                        'badge_number_height',
                    ],
                    header='Badge Number'
                ),

                r.FieldSet(
                    [
                        'level_top',
                        'level_left',
                        'level_width',
                        'level_height',
                    ],
                    header='Badge Level'
                ),

                r.FieldSet(
                    [
                        'timestamp_format',
                        'timestamp_append_to_level',
                        'timestamp_top',
                        'timestamp_left',
                        'timestamp_width',
                        'timestamp_height',
                    ],
                    header='Date/Time'
                ),

                r.FieldSet(
                    [
                        'arbitrary_text',
                        'arbitrary_text_override_level',
                        'arbitrary_text_top',
                        'arbitrary_text_left',
                        'arbitrary_text_width',
                        'arbitrary_text_height',
                    ],
                    header='Arbitrary Text'
                ),

                r.FieldSet(
                    [
                        r.Text("Classes that can be controlled are: page, badge, badge_name, badge_number, level, timestamp, arbitrary_text"),
                        'css',
                    ],
                    header='Additional CSS'
                ),
            ],
            header='Position and Style'
        ),
    ]
    form_edit_rules = form_create_rules


views = OrderedDict([
    ('Flag', FlagLevelModelView(models.Flag, db.session, endpoint='admin.flag', url='flag')),
    ('Level', FlagLevelModelView(models.Level, db.session, endpoint='admin.level', url='level')),
    ('BadgeTemplate', BadgeTemplateModelView(models.BadgeTemplate, db.session, endpoint='admin.badge_template', url='badge_template')),
    ('Badge', CustomModelView(models.Badge, db.session, endpoint='admin.badge', url='badge')),
])

for view in views.values():
    admin.add_view(view)
