import functools
import logging
import hashlib
import hmac
import re

from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from flask.views import MethodView
from flask import request, jsonify, current_app

from app import db
from app.models import Level, Flag, Badge


logger = logging.getLogger(__name__)


def authenticated(callback):
    @functools.wraps(callback)
    def authenticated_impl(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized("No authorization provided")

        match = re.match(r'^HMAC ([^\s]+)$', auth_header)
        if not match:
            raise Unauthorized("Invalid authorization header")

        given_hash = match.group(1)

        h = hmac.new(
            current_app.config.get('API_SECRET').encode('utf-8'),
            digestmod=getattr(hashlib, current_app.config.get('API_HMAC_HASH'))
        )
        h.update(request.method.upper().encode('utf-8'))
        h.update(request.url.encode('utf-8'))
        h.update(request.get_data())
        h = h.hexdigest()
        if not hmac.compare_digest(h, given_hash):
            raise Unauthorized("Invalid authorization provided")

        return callback(*args, **kwargs)
    return authenticated_impl


def returns_json(callback):
    @functools.wraps(callback)
    def returns_json_impl(*args, **kwargs):
        try:
            res = callback(*args, **kwargs)
            return jsonify({'result': res})
        except HTTPException as e:
            return jsonify({
                'error': {
                    'message': e.description,
                    'code': e.code
                }
            }), e.code
        except:
            logger.error("An API request failed", exc_info=True)
            return jsonify({'error': {'message': "Internal server error", 'code': 500}}), 500
    return returns_json_impl


class APIView(MethodView):
    decorators = [authenticated, returns_json]


class BadgeView(APIView):
    def post(self):
        data = request.json
        for key in ('foreign_id', 'name', 'level', 'age'):
            if not data.get(key):
                raise BadRequest("Missing property: " + key)

        level = Level.query.filter(Level.name == data['level']).first()
        if not level:
            raise BadRequest("Invalid level")

        flags = []
        if data.get('flags'):
            flags = Flag.query.filter(Flag.name.in_(data['flags'])).all()
            missing_flags = set(data['flags']) - set([f.name for f in flags])
            if missing_flags:
                raise BadRequest("Invalid flags: " + ', '.join(missing_flags))

        badge = Badge.query.filter(Badge.foreign_id == data['foreign_id']).first()
        if not badge:
            badge = Badge(foreign_id=data['foreign_id'])

        badge.name = data['name']
        badge.level = level
        badge.age = data['age']
        badge.flags = flags
        badge.print_queued = data.get('queue', True)

        db.session.add(badge)
        db.session.commit()
        return {'badge_number': badge.id}


views = {
    '/api/badge': BadgeView.as_view('api.badge'),
}
