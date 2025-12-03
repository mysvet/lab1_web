# Импорты Flask и необходимых расширений
from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField  # Flask-WTF для работы с формами и reCAPTCHA
from wtforms import SelectField, StringField, SubmitField  # Поля формы
from wtforms.validators import DataRequired  # Валидатор для обязательных полей
from werkzeug.utils import secure_filename  # Защита от опасных имён файлов
import os

# Утилиты для обработки изображений (предполагаются реализованными в файле utils.py)
from utils import draw_cross, plot_histograms

# Создаём экземпляр Flask-приложения
app = Flask(__name__)

# Секретный ключ для защиты CSRF-токенов и сессий
app.config['SECRET_KEY'] = 'your-super-secret-key'

# Ключи reCAPTCHA (Google reCAPTCHA v2) для защиты от ботов
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcitBssAAAAACF5YxswyTkubRaRMyUjfE296Dy5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcitBssAAAAAKStyJEGMpGRU7tJqp-EXiS5rTGM'

# Подключаем Bootstrap для стилизации через Flask-Bootstrap
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

# Папка для загрузки пользовательских изображений
UPLOAD_FOLDER = 'static/uploaded'
# Создаём папку, если её ещё нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Регистрируем папку в конфигурации приложения
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Класс формы для настройки параметров креста
class CrossForm(FlaskForm):
    # Выбор ориентации креста (вертикальный или горизонтальный)
    orientation = SelectField('Ориентация креста', choices=[
        ('vertical', 'Вертикальный'),
        ('horizontal', 'Горизонтальный')
    ], validators=[DataRequired()])  # Поле обязательно для заполнения

    # Поля для ввода RGB-компонентов цвета креста (с значениями по умолчанию — красный)
    color_r = StringField('Красный (0–255)', default='255')
    color_g = StringField('Зелёный (0–255)', default='0')
    color_b = StringField('Синий (0–255)', default='0')

    # Поле reCAPTCHA для защиты от автоматических ботов
    recaptcha = RecaptchaField()

    # Кнопка отправки формы
    submit = SubmitField('Применить')


# Главная страница приложения: обрабатывает GET (отображение формы) и POST (обработку загрузки и обработки изображения)
@app.route('/', methods=['GET', 'POST'])
def index():
    # Создаём экземпляр формы
    form = CrossForm()

    # Инициализируем переменные для путей к изображениям (оригинал, обработанное, гистограммы)
    original = processed = hist_orig = hist_proc = None

    # Если форма успешно прошла валидацию (включая reCAPTCHA)
    if form.validate_on_submit():
        # Получаем загруженный файл изображения
        file = request.files['image']

        # Проверяем, что файл действительно загружен
        if file and file.filename:
            # Защищаем имя файла от потенциально опасных символов
            filename = secure_filename(file.filename)
            # Формируем путь для сохранения исходного изображения
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Сохраняем файл на диск
            file.save(filepath)
            # Путь для отображения в шаблоне (относительно static/)
            original = f'uploaded/{filename}'

            # Преобразуем введённые значения цвета в корректный RGB-кортеж
            try:
                # Ограничиваем значения от 0 до 255 и конвертируем в int
                r = max(0, min(255, int(form.color_r.data)))
                g = max(0, min(255, int(form.color_g.data)))
                b = max(0, min(255, int(form.color_b.data)))
                color = (r, g, b)
            except (ValueError, TypeError):
                # Если ввод некорректный — используем цвет по умолчанию (красный)
                color = (255, 0, 0)

            # Путь для сохранения обработанного изображения
            proc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + filename)
            # Рисуем крест на изображении (функция из utils.py)
            draw_cross(filepath, proc_path, form.orientation.data, color)
            # Путь для отображения в шаблоне
            processed = 'uploaded/result_' + filename

            # Генерируем гистограммы яркости/цветов для исходного и обработанного изображений
            plot_histograms(
                filepath, proc_path,
                os.path.join(app.config['UPLOAD_FOLDER'], 'hist_orig_' + filename),
                os.path.join(app.config['UPLOAD_FOLDER'], 'hist_proc_' + filename)
            )
            # Пути к гистограммам для отображения в шаблоне
            hist_orig = 'uploaded/hist_orig_' + filename
            hist_proc = 'uploaded/hist_proc_' + filename

    # Отображаем главную страницу с формой и, при наличии, результатами обработки
    return render_template('index.html', form=form, original=original,
                           processed=processed, hist_orig=hist_orig, hist_proc=hist_proc)


# Точка входа при запуске напрямую (например, локально)
if __name__ == '__main__':
    # Получаем порт из переменной окружения (важно для хостингов типа Render)
    port = int(os.environ.get('PORT', 5000))
    # Запускаем сервер: host='0.0.0.0' — чтобы приложение было доступно извне
    app.run(host='0.0.0.0', port=port, debug=False)