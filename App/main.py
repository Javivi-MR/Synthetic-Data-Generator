from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

from sdv.lite import SingleTablePreset
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, CopulaGANSynthesizer, TVAESynthesizer
from sdmetrics.reports.single_table import QualityReport
from sdmetrics.visualization import get_column_plot
import pandas as pd

import os
import config as C

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = C.DATA_BASE_URI
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = C.SECRET_KEY
app.config['EXECUTOR_TYPE'] = 'process'
app.config['EXECUTOR_MAX_WORKERS'] = C.WORKERS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def load_dataset(dataset_id):
    return Dataset.query.get(int(dataset_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"dataset('{self.name}', '{self.path}')"

class Register(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "password"})

    submit = SubmitField('SignUp')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose a different one.')

class Login(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "password"})

    submit = SubmitField('LogIn')


with app.app_context():
    if not os.path.exists('database.db'):
        db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['POST', 'GET'])
def login():
    loginform = Login()
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, loginform.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=loginform, user=current_user)

@app.route('/forgot', methods=['POST', 'GET'])
def forgot():
    return render_template('forgot.html', user=current_user)

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    registerform = Register()

    if registerform.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(registerform.password.data)
        user = User(username=registerform.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=registerform, user=current_user)


@app.route('/generate', methods=['POST', 'GET'])
@login_required
def generate():
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    datasets_objs = []
    for dataset in datasets:
        datasets_objs.append(pd.read_csv(dataset.path))
    return render_template('generate.html',user=current_user, datasets=datasets, datasets_objs=datasets_objs)

@app.route('/generate/<id>', methods=['POST', 'GET'])
@login_required
def generate_id(id):
    if request.method == 'POST':
        dataset = load_dataset(id)
        real_data = pd.read_csv(dataset.path)

        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(real_data)
        synthetic_data = None

        if request.form['synthetizer'] == 'fast_ml':
            synthesizer = SingleTablePreset(metadata, name='FAST_ML')
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows']))

        elif request.form['synthetizer'] == 'copulagan':
            synthesizer = CopulaGANSynthesizer(metadata)
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows']))

        elif request.form['synthetizer'] == 'ctgan':
            synthesizer = CTGANSynthesizer(metadata)
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows']))

        elif request.form['synthetizer'] == 'gaussian_copula':
            synthesizer = GaussianCopulaSynthesizer(metadata)
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows']))

        elif request.form['synthetizer'] == 'tvae':
            synthesizer = TVAESynthesizer(metadata)
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows']))

        synthetic_data.to_csv(C.SYNTHETIC_PATH + str(id) + '_s_' + dataset.name, index=False)
        return render_template('showdata.html', id=id, user=current_user ,file_name=dataset.name, real_data=real_data, synthetic_data=synthetic_data)
    else:
        return redirect(url_for('generate'))


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        if 'dataset' not in request.files:
            return render_template('error.html', user=current_user, error='No selected file.')

        file = request.files['dataset']

        if file.filename == '':
            return render_template('error.html', user=current_user, error='No selected file.')

        if file.filename.split('.')[-1] != 'csv':
            return render_template('error.html', user=current_user, error='The file must be a csv file.')


        last_dataset = db.session.query(Dataset).order_by(Dataset.id.desc()).first()

        # Check if a dataset was returned
        if last_dataset is not None:
            id = last_dataset.id + 1
        else:
            id = 1

        # Especifica la ubicación donde deseas almacenar el archivo
        file.save(C.DATASET_PATH + str(id) + '_' + file.filename)

        dataset = Dataset(id=id, name=file.filename, path=C.DATASET_PATH + str(id) + '_' + file.filename, user_id=current_user.id)
        db.session.add(dataset)
        db.session.commit()

        return redirect(url_for('generate'))

    else:
        return render_template('upload.html', user=current_user)

@app.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    if request.method == 'POST':
        dataset = load_dataset(id)
        db.session.delete(dataset)
        db.session.commit()
        return redirect(url_for('generate'))
    else:
        return redirect(url_for('generate'))

@app.route('/evaluate/<id>', methods=['POST', 'GET'])
@login_required
def evaluate(id):
    #check if the dataset exists and if it belongs to the user
    dataset = load_dataset(id)
    if dataset is None or dataset.user_id != current_user.id:
        return redirect(url_for('generate'))

    real_data = pd.read_csv(dataset.path)
    synthetic_data = pd.read_csv(C.DATASET_PATH + str(id) + '_s_' + dataset.name)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)

    report = QualityReport()
    report.generate(real_data, synthetic_data,metadata.to_dict())

    for column in real_data.columns:
        plot = get_column_plot(real_data, synthetic_data, column)
        plot.write_image(C.PLOT_PATH + str(id) + column + '.png')

    num_columns = len(real_data.columns) # Número de columnas en el dataset
    column_pairs = [(real_data.columns[i], real_data.columns[j]) # Pares de columnas para obtener la covarianza
                    for i in range(num_columns)
                    for j in range(i + 1, num_columns)
                    if real_data[real_data.columns[i]].dtype in ['int64', 'float64'] and
                    real_data[real_data.columns[j]].dtype in ['int64', 'float64']]

    return render_template('evaluate.html',user=current_user,file_name=dataset.name,id=id,score=report.get_score(),real_data=real_data,synthetic_data=synthetic_data, column_pairs=column_pairs)

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html' , user=current_user)

if __name__ == '__main__':
    app.run(debug=True)