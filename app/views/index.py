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
    request,
    )
from flask_login import current_user, login_required

from app.models import Badge, BadgeTemplate, BadgePrint
from app import db


app = Blueprint('index', __name__)
mimetypes.init()


def match_templates(single=False):
    templates = BadgeTemplate.query.all()
    badges = Badge.query.filter(Badge.print_queued == True).all()
    badge_templates = {}
    for badge in badges:
        tpl_match = [(t, t.matches(badge)) for t in templates]
        if tpl_match:
            tpl_match = list(sorted(tpl_match, key=lambda v: v[1]))
            tpl_match = [v[0] for v in tpl_match if v[1] > 0 and v[1] == tpl_match[-1][1]]
        badge_templates[badge.id] = tpl_match[-1] if single else tpl_match
    return badges, badge_templates


def group_count(data, n):
    out = []
    for v in data:
        out.append(v)
        if len(out) == n:
            yield out
            out = []
    if out:
        yield out


@app.route('/', methods=['GET'])
@login_required
def index():
    root_templates = BadgeTemplate.query.filter(BadgeTemplate.extends == None).all()
    badges, badge_templates = match_templates()
    return render_template('index.jinja.html', root_templates=root_templates, badges=badges, badge_templates=badge_templates)


@app.route('/queue', methods=['POST'])
@login_required
def queue():
    if request.form.get('action') == 'queue-unprinted':
        unprinted = [b for b in Badge.query if not b.print_queued and not b.prints]
        for b in unprinted:
            b.print_queued = True
            b.print_queued_by = current_user
        db.session.commit()
        flash("Queued {} badges for printing".format(len(unprinted)), 'success')
    elif request.form.get('action') == 'queue-all':
        unprinted = [b for b in Badge.query if not b.print_queued]
        for b in unprinted:
            b.print_queued = True
            b.print_queued_by = current_user
        db.session.commit()
        flash("Queued {} badges for printing".format(len(unprinted)), 'success')
    elif request.form.get('action') == 'queue':
        badge = Badge.query.filter(Badge.print_queued == False, Badge.id == request.form.get('id')).first()
        if badge:
            badge.print_queued = True
            badge.print_queued_by = current_user
            db.session.commit()
            flash("Queued {} for printing".format(badge.name), 'success')
        else:
            flash("No such badge", 'danger')
    elif request.form.get('action') == 'unqueue':
        badges = Badge.query.filter(Badge.print_queued == True)
        if request.form.get('id'):
            badges = badges.filter(Badge.id == request.form.get('id'))
        badges = badges.all()

        for b in badges:
            b.print_queued = False
            b.print_queued_by = None

        db.session.commit()
        flash("Unqueued {} badges".format(len(badges)), 'success')
    else:
        flash("Invalid action", 'danger')

    return redirect(request.form.get('next') or url_for('.index'))


@app.route('/print', methods=['GET'])
@login_required
def print():
    root_templates = BadgeTemplate.query.filter(BadgeTemplate.extends == None).all()
    if request.args.get('tpl'):
        badge_templates = {0: BadgeTemplate.query.get(request.args['tpl'])}
        badges = [
            {
                'id': 0,
                'name': '',
                'level': '',
            }
            for _ in range(int(request.args['count']))
        ]
    else:
        badges, badge_templates = match_templates(single=True)
        for b in badges:
            db.session.add(BadgePrint(
                badge=b,
                queued_by=b.print_queued_by,
                printed_by=current_user,
            ))
        db.session.commit()
    badges = list(group_count(badges, 6))
    badges = list(map(lambda g: list(group_count(g, 3)), badges))
    return render_template('badge/print.jinja.html', root_templates=root_templates, badges=badges, badge_templates=badge_templates)


@app.route('/<path:filename>', methods=['GET'])
def upload(filename):
    mime, _ = mimetypes.guess_type(os.path.basename(filename), strict=False)
    with open(os.path.join(current_app.config['UPLOAD_PATH'], filename), 'rb') as fp:
        content = fp.read()
    return Response(content, mimetype=mime)
