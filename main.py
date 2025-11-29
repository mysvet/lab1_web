from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from utils import draw_cross, plot_histograms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcitBssAAAAACF5YxswyTkubRaRMyUjfE296Dy5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcitBssAAAAAKStyJEGMpGRU7tJqp-EXiS5rTGM'

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

UPLOAD_FOLDER = 'static/uploaded'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class CrossForm(FlaskForm):
    orientation = SelectField('Ориентация креста', choices=[
        ('vertical', 'Вертикальный'),
        ('horizontal', 'Горизонтальный')
    ], validators=[DataRequired()])
    color_r = StringField('Красный (0–255)', default='255')
    color_g = StringField('Зелёный (0–255)', default='0')
    color_b = StringField('Синий (0–255)', default='0')
    recaptcha = RecaptchaField()
    submit = SubmitField('Применить')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CrossForm()
    original = processed = hist_orig = hist_proc = None
    if form.validate_on_submit():
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            original = f'uploaded/{filename}'

            try:
                r = max(0, min(255, int(form.color_r.data)))
                g = max(0, min(255, int(form.color_g.data)))
                b = max(0, min(255, int(form.color_b.data)))
                color = (r, g, b)
            except:
                color = (255, 0, 0)

            proc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + filename)
            draw_cross(filepath, proc_path, form.orientation.data, color)
            processed = 'uploaded/result_' + filename

            plot_histograms(
                filepath, proc_path,
                os.path.join(app.config['UPLOAD_FOLDER'], 'hist_orig_' + filename),
                os.path.join(app.config['UPLOAD_FOLDER'], 'hist_proc_' + filename)
            )
            hist_orig = 'uploaded/hist_orig_' + filename
            hist_proc = 'uploaded/hist_proc_' + filename

    return render_template('index.html', form=form, original=original,
                           processed=processed, hist_orig=hist_orig, hist_proc=hist_proc)

if __name__ == '__main__':
    app.run(debug=True)
