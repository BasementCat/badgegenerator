import csv
import io
import re

from flask import Blueprint, render_template, flash

from flask_login import current_user, login_required

from app.forms.csv_upload import CSVUploadForm
from app.models import Level, Flag, Badge
from app import db


app = Blueprint('badge', __name__)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    levels = {l.name: l for l in Level.query.all()}
    flags = {f.name: f for f in Flag.query.all()}

    form = CSVUploadForm()
    if form.validate_on_submit():
        with db.session.no_autoflush:
            if form.csv_file.data:
                reader = csv.DictReader(form.csv_file.data.stream, dialect='excel')
            else:
                reader = csv.DictReader(io.StringIO(form.raw_csv.data), delimiter='\t')
            ok = True
            for idx, row in enumerate(reader):
                adj_idx = idx + 2
                for field in ('name', 'level', 'age'):
                    if not row.get(field):
                        flash(f"Row {adj_idx} is missing required field {field}, aborting", 'danger')
                        ok = False
                        break
                if row.get('level') not in levels:
                    flash(f"Row {adj_idx} has an invalid level, aborting", 'danger')
                    ok = False
                    break
                if row.get('flags'):
                    row['flags'] = re.split(r'\s+', row['flags'])
                    for flag in row['flags']:
                        if flag not in flags:
                            flash(f"Row {adj_idx} has an invalid flag, aborting", 'danger')
                            ok = False
                            break

                if not ok:
                    break

                row['level'] = levels[row['level']]
                row['flags'] = [flags[f] for f in row['flags']] if row.get('flags') else []
                row['age'] = int(row['age'])
                badge = Badge(**row)

                if form.queue.data:
                    badge.print_queued = True
                    badge.print_queued_by = current_user

                db.session.add(badge)

            if ok:
                db.session.commit()
                flash("Uploaded {} records".format(idx + 1), 'success')
                form.csv_file.data = None
                form.raw_csv.data = None
            else:
                db.session.rollback()

    valid_levels = ', '.join(levels.keys())
    valid_flags = ', '.join(flags.keys())
    return render_template('badge/upload.jinja.html', form=form, valid_levels=valid_levels, valid_flags=valid_flags)
