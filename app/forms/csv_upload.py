from flask_wtf import Form

import wtforms as wtf
import wtforms.validators as v


class CSVUploadForm(Form):
    raw_csv = wtf.TextAreaField('CSV Data', description="Paste in a raw CSV file")
    csv_file = wtf.FileField('CSV File', description="Upload a CSV file from your computer")
    queue = wtf.BooleanField('Queue for Printing', default=True, description="Queue these badges for printing now")
    submit = wtf.SubmitField('Upload Data')
